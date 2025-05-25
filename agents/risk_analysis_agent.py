import os
import json
from crewai import Agent
from openai import OpenAI

class RiskAnalysisAgent:
    """
    Agent responsible for analyzing contract risks, identifying vague language,
    and flagging potentially problematic clauses.
    """
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.agent = Agent(
            role="Legal Risk Assessment Specialist",
            goal="Identify legal risks, vague language, and one-sided provisions in contract clauses",
            backstory="""You are a seasoned legal risk analyst with deep expertise in contract law.
            You specialize in identifying potential legal exposures, ambiguous language that could
            lead to disputes, and clauses that create unfair advantages for one party. Your analysis
            helps organizations understand and mitigate contractual risks before signing agreements.""",
            verbose=True,
            allow_delegation=False
        )
    
    def analyze_risks(self, contract_text: str, detected_clauses: list) -> dict:
        """
        Analyze contract for various types of legal and business risks.
        
        Args:
            contract_text (str): Full contract text
            detected_clauses (list): Previously detected clauses
            
        Returns:
            dict: Comprehensive risk analysis with severity levels
        """
        try:
            clause_context = "\n".join([
                f"- {clause.get('clause_type', 'Unknown')}: {clause.get('clause_text', '')[:200]}..."
                for clause in detected_clauses[:10]  # Limit for token management
            ])
            
            prompt = f"""
            Perform a comprehensive risk analysis of this contract. Analyze both the full contract
            and the specific clauses provided. Focus on identifying:
            
            1. Vague or ambiguous language that could lead to disputes
            2. One-sided provisions that favor one party unfairly  
            3. Excessive liability exposure
            4. Inadequate termination protections
            5. Missing risk mitigation clauses
            6. Unreasonable obligations or commitments
            7. Intellectual property risks
            8. Compliance and regulatory risks
            
            Key detected clauses for context:
            {clause_context}
            
            For each risk identified, provide:
            - risk_type: Category of risk
            - risk_description: Detailed explanation of the risk
            - severity_level: High/Medium/Low
            - affected_clause: Which clause creates this risk
            - potential_impact: Business/legal consequences
            - likelihood: High/Medium/Low probability of occurrence
            
            Respond in JSON format:
            {{
                "risk_analysis": [
                    {{
                        "risk_type": "string",
                        "risk_description": "string",
                        "severity_level": "string",
                        "affected_clause": "string", 
                        "potential_impact": "string",
                        "likelihood": "string"
                    }}
                ],
                "overall_risk_assessment": {{
                    "total_risks_identified": number,
                    "high_severity_count": number,
                    "medium_severity_count": number,
                    "low_severity_count": number,
                    "overall_risk_score": number,
                    "key_concerns": ["string"],
                    "recommended_action": "string"
                }}
            }}
            
            Contract text (first 3000 characters):
            {contract_text[:3000]}
            """
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a legal risk assessment expert with expertise in contract analysis and risk mitigation."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            return {
                "error": f"Failed to analyze risks: {str(e)}",
                "risk_analysis": [],
                "overall_risk_assessment": {
                    "total_risks_identified": 0,
                    "high_severity_count": 0,
                    "medium_severity_count": 0,
                    "low_severity_count": 0,
                    "overall_risk_score": 0,
                    "key_concerns": ["Risk analysis failed due to error"],
                    "recommended_action": "Manual review required - automated analysis unavailable"
                }
            }
    
    def assess_language_clarity(self, contract_text: str) -> dict:
        """
        Specifically analyze language clarity and identify vague terms.
        
        Args:
            contract_text (str): Contract text to analyze
            
        Returns:
            dict: Analysis of language clarity issues
        """
        try:
            prompt = f"""
            Analyze the language clarity of this contract. Identify:
            
            1. Vague or ambiguous terms that need clarification
            2. Undefined technical terms or jargon
            3. Inconsistent terminology usage
            4. Overly complex sentences that could be simplified
            5. Missing definitions for key terms
            
            Provide specific examples and suggestions for improvement.
            
            Respond in JSON format:
            {{
                "clarity_issues": [
                    {{
                        "issue_type": "string",
                        "problematic_text": "string",
                        "explanation": "string",
                        "suggested_improvement": "string"
                    }}
                ],
                "clarity_score": number,
                "summary": "string"
            }}
            
            Contract text:
            {contract_text[:2000]}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            return {
                "error": f"Failed to assess language clarity: {str(e)}",
                "clarity_issues": [],
                "clarity_score": 0,
                "summary": "Language clarity analysis failed"
            }
