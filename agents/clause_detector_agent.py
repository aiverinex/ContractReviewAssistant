import os
import json
from crewai import Agent
from openai import OpenAI

class ClauseDetectorAgent:
    """
    Agent responsible for detecting and mapping key legal clauses in contracts.
    Identifies critical clauses like indemnity, termination, exclusivity, etc.
    """
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.agent = Agent(
            role="Legal Clause Detection Specialist",
            goal="Identify and extract key legal clauses from contract text with precise location mapping",
            backstory="""You are an expert legal analyst specializing in contract clause identification.
            You have extensive experience in parsing complex legal documents and identifying critical
            contractual provisions. Your expertise includes recognizing indemnity clauses, termination
            provisions, exclusivity agreements, liability limitations, and other essential contract elements.""",
            verbose=True,
            allow_delegation=False
        )
    
    def detect_clauses(self, contract_text: str) -> dict:
        """
        Analyze contract text and identify key legal clauses.
        
        Args:
            contract_text (str): The full contract text to analyze
            
        Returns:
            dict: Structured mapping of detected clauses with their content and locations
        """
        try:
            prompt = f"""
            Analyze the following contract text and identify key legal clauses. 
            Focus on finding these critical clause types:
            
            1. Indemnity/Indemnification clauses
            2. Termination clauses
            3. Exclusivity clauses
            4. Liability limitation clauses
            5. Force majeure clauses
            6. Governing law clauses
            7. Dispute resolution clauses
            8. Confidentiality/Non-disclosure clauses
            9. Intellectual property clauses
            10. Payment terms clauses
            
            For each clause found, provide:
            - clause_type: The type of clause
            - clause_text: The exact text of the clause
            - location_context: Surrounding context to help locate the clause
            - importance_level: High/Medium/Low based on legal significance
            
            Respond in JSON format with this structure:
            {{
                "detected_clauses": [
                    {{
                        "clause_type": "string",
                        "clause_text": "string", 
                        "location_context": "string",
                        "importance_level": "string"
                    }}
                ],
                "clause_summary": {{
                    "total_clauses_found": number,
                    "high_importance_count": number,
                    "coverage_assessment": "string"
                }}
            }}
            
            Contract text:
            {contract_text}
            """
            
            # Using GPT-4o-mini for cost-effective contract analysis
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a legal expert specializing in contract analysis and clause detection."
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
                "error": f"Failed to detect clauses: {str(e)}",
                "detected_clauses": [],
                "clause_summary": {
                    "total_clauses_found": 0,
                    "high_importance_count": 0,
                    "coverage_assessment": "Analysis failed due to error"
                }
            }
    
    def get_clause_recommendations(self, detected_clauses: list) -> dict:
        """
        Provide recommendations for missing or incomplete clauses.
        
        Args:
            detected_clauses (list): List of detected clauses
            
        Returns:
            dict: Recommendations for clause improvements
        """
        clause_types_found = [clause.get("clause_type", "") for clause in detected_clauses]
        
        essential_clauses = [
            "Indemnity", "Termination", "Liability Limitation", 
            "Governing Law", "Dispute Resolution"
        ]
        
        missing_clauses = []
        for essential in essential_clauses:
            if not any(essential.lower() in clause_type.lower() for clause_type in clause_types_found):
                missing_clauses.append(essential)
        
        return {
            "missing_essential_clauses": missing_clauses,
            "completeness_score": len(essential_clauses - len(missing_clauses)) / len(essential_clauses) * 100,
            "recommendations": [
                f"Consider adding a {clause} clause for better protection" 
                for clause in missing_clauses
            ]
        }
