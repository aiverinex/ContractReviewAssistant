import os
import json
from crewai import Agent
from openai import OpenAI

class RedlineSuggesterAgent:
    """
    Agent responsible for suggesting specific redlines, amendments, and improvements
    to contract clauses based on risk analysis and best practices.
    """
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.agent = Agent(
            role="Contract Redlining and Amendment Specialist", 
            goal="Provide specific, actionable redline suggestions and contract improvements",
            backstory="""You are an expert contract attorney specializing in contract negotiation
            and redlining. You have extensive experience in drafting protective language, negotiating
            terms, and ensuring contracts serve your client's best interests. Your redlines are
            precise, legally sound, and strategically focused on risk mitigation and value protection.""",
            verbose=True,
            allow_delegation=False
        )
    
    def generate_redlines(self, contract_text: str, risk_analysis: dict, detected_clauses: list) -> dict:
        """
        Generate specific redline suggestions based on risk analysis and clause detection.
        
        Args:
            contract_text (str): Full contract text
            risk_analysis (dict): Risk analysis results
            detected_clauses (list): Detected clauses
            
        Returns:
            dict: Detailed redline suggestions and amendments
        """
        try:
            # Extract high-risk items for focused redlining
            high_risks = [
                risk for risk in risk_analysis.get("risk_analysis", [])
                if risk.get("severity_level", "").lower() == "high"
            ]
            
            risk_context = "\n".join([
                f"- {risk.get('risk_type', 'Unknown Risk')}: {risk.get('risk_description', '')}"
                for risk in high_risks[:5]
            ])
            
            clause_context = "\n".join([
                f"- {clause.get('clause_type', 'Unknown')}: {clause.get('clause_text', '')[:150]}..."
                for clause in detected_clauses[:8]
            ])
            
            prompt = f"""
            Based on the risk analysis and contract clauses, provide specific redline suggestions
            to improve this contract. Focus on addressing the identified high-risk areas.
            
            High-priority risks to address:
            {risk_context}
            
            Key contract clauses:
            {clause_context}
            
            For each redline suggestion, provide:
            1. The specific text to be changed/added/deleted
            2. The proposed replacement or addition
            3. Rationale for the change
            4. Risk mitigation achieved
            5. Priority level (Critical/High/Medium/Low)
            
            Also suggest:
            - Missing clauses that should be added
            - Language that should be clarified
            - Terms that need better definition
            - Protective provisions that should be strengthened
            
            Respond in JSON format:
            {{
                "redline_suggestions": [
                    {{
                        "change_type": "string", 
                        "original_text": "string",
                        "proposed_text": "string", 
                        "rationale": "string",
                        "risk_addressed": "string",
                        "priority": "string",
                        "section_reference": "string"
                    }}
                ],
                "new_clauses_needed": [
                    {{
                        "clause_type": "string",
                        "proposed_language": "string",
                        "justification": "string",
                        "priority": "string"
                    }}
                ],
                "negotiation_strategy": {{
                    "key_positions": ["string"],
                    "fallback_options": ["string"], 
                    "deal_breakers": ["string"]
                }},
                "summary": {{
                    "total_suggestions": number,
                    "critical_changes": number,
                    "estimated_risk_reduction": "string"
                }}
            }}
            
            Contract text (first 3000 characters):
            {contract_text[:3000]}
            """
            
            # Using GPT-4o-mini for cost-effective contract analysis
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert contract attorney specializing in protective redlining and risk mitigation."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            return {
                "error": f"Failed to generate redlines: {str(e)}",
                "redline_suggestions": [],
                "new_clauses_needed": [],
                "negotiation_strategy": {
                    "key_positions": ["Manual review required due to analysis error"],
                    "fallback_options": [],
                    "deal_breakers": []
                },
                "summary": {
                    "total_suggestions": 0,
                    "critical_changes": 0,
                    "estimated_risk_reduction": "Unable to assess - analysis failed"
                }
            }
    
    def prioritize_changes(self, redline_suggestions: list) -> dict:
        """
        Prioritize redline suggestions based on risk impact and negotiation feasibility.
        
        Args:
            redline_suggestions (list): List of redline suggestions
            
        Returns:
            dict: Prioritized changes with implementation strategy
        """
        try:
            critical_changes = [r for r in redline_suggestions if r.get("priority", "").lower() == "critical"]
            high_changes = [r for r in redline_suggestions if r.get("priority", "").lower() == "high"]
            
            return {
                "implementation_phases": {
                    "phase_1_critical": {
                        "changes": critical_changes,
                        "timeline": "Address before any signing",
                        "negotiation_approach": "Non-negotiable positions"
                    },
                    "phase_2_high": {
                        "changes": high_changes,
                        "timeline": "Primary negotiation focus", 
                        "negotiation_approach": "Strong preference, willing to trade"
                    },
                    "phase_3_medium": {
                        "changes": [r for r in redline_suggestions if r.get("priority", "").lower() == "medium"],
                        "timeline": "Secondary negotiation items",
                        "negotiation_approach": "Nice to have improvements"
                    }
                },
                "negotiation_roadmap": {
                    "must_have_count": len(critical_changes),
                    "high_priority_count": len(high_changes),
                    "total_items": len(redline_suggestions)
                }
            }
            
        except Exception as e:
            return {
                "error": f"Failed to prioritize changes: {str(e)}",
                "implementation_phases": {},
                "negotiation_roadmap": {}
            }
