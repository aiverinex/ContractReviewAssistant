import os
from crewai import Crew, Process
from crewai.memory import LongTermMemory
from agents.clause_detector_agent import ClauseDetectorAgent
from agents.risk_analysis_agent import RiskAnalysisAgent  
from agents.redline_suggester_agent import RedlineSuggesterAgent
from tasks.task import ContractReviewTasks

class ContractReviewCrew:
    """
    Main CrewAI crew that orchestrates the contract review process using
    specialized agents for clause detection, risk analysis, and redline suggestions.
    """
    
    def __init__(self):
        """Initialize the crew with all required agents and tasks."""
        # Initialize agents
        self.clause_detector = ClauseDetectorAgent()
        self.risk_analyzer = RiskAnalysisAgent()
        self.redline_suggester = RedlineSuggesterAgent()
        
        # Initialize task manager
        self.task_manager = ContractReviewTasks()
        
        # Initialize the crew
        self.crew = None
        self._setup_crew()
    
    def _setup_crew(self):
        """Set up the CrewAI crew with agents and process configuration."""
        try:
            self.crew = Crew(
                agents=[
                    self.clause_detector.agent,
                    self.risk_analyzer.agent, 
                    self.redline_suggester.agent
                ],
                tasks=[],  # Tasks will be added dynamically
                process=Process.sequential,
                memory=True,
                verbose=True,
                max_iter=3,
                full_output=True
            )
        except Exception as e:
            print(f"Error setting up crew: {e}")
            self.crew = None
    
    def review_contract(self, contract_text: str) -> dict:
        """
        Execute the complete contract review process using all agents.
        
        Args:
            contract_text (str): The contract text to review
            
        Returns:
            dict: Comprehensive contract review results
        """
        if not contract_text or not contract_text.strip():
            return {
                "error": "No contract text provided for review",
                "success": False
            }
        
        try:
            print("Starting comprehensive contract review...")
            print("=" * 60)
            
            # Step 1: Clause Detection
            print("\n🔍 PHASE 1: Detecting Contract Clauses...")
            clause_results = self.clause_detector.detect_clauses(contract_text)
            
            if "error" in clause_results:
                print(f"❌ Clause detection failed: {clause_results['error']}")
                return {"error": clause_results["error"], "success": False}
            
            detected_clauses = clause_results.get("detected_clauses", [])
            print(f"✅ Found {len(detected_clauses)} key clauses")
            
            # Step 2: Risk Analysis
            print("\n⚠️  PHASE 2: Analyzing Contract Risks...")
            risk_results = self.risk_analyzer.analyze_risks(contract_text, detected_clauses)
            
            if "error" in risk_results:
                print(f"❌ Risk analysis failed: {risk_results['error']}")
                # Continue with available data
                risk_results = {"risk_analysis": [], "overall_risk_assessment": {}}
            
            risk_count = len(risk_results.get("risk_analysis", []))
            print(f"✅ Identified {risk_count} potential risks")
            
            # Step 3: Language Clarity Assessment
            print("\n📝 PHASE 3: Assessing Language Clarity...")
            clarity_results = self.risk_analyzer.assess_language_clarity(contract_text)
            
            # Step 4: Redline Suggestions
            print("\n✏️  PHASE 4: Generating Redline Suggestions...")
            redline_results = self.redline_suggester.generate_redlines(
                contract_text, risk_results, detected_clauses
            )
            
            if "error" in redline_results:
                print(f"❌ Redline generation failed: {redline_results['error']}")
                redline_results = {"redline_suggestions": [], "new_clauses_needed": []}
            
            suggestions_count = len(redline_results.get("redline_suggestions", []))
            print(f"✅ Generated {suggestions_count} redline suggestions")
            
            # Step 5: Prioritization
            print("\n📊 PHASE 5: Prioritizing Changes...")
            prioritization = self.redline_suggester.prioritize_changes(
                redline_results.get("redline_suggestions", [])
            )
            
            # Compile comprehensive results
            final_results = {
                "success": True,
                "contract_analysis": {
                    "clause_detection": clause_results,
                    "risk_analysis": risk_results,
                    "language_clarity": clarity_results,
                    "redline_suggestions": redline_results,
                    "change_prioritization": prioritization
                },
                "executive_summary": self._generate_executive_summary(
                    clause_results, risk_results, redline_results
                ),
                "next_steps": self._generate_next_steps(risk_results, redline_results)
            }
            
            print("\n✅ Contract review completed successfully!")
            return final_results
            
        except Exception as e:
            error_msg = f"Contract review failed: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "error": error_msg,
                "success": False
            }
    
    def _generate_executive_summary(self, clause_results: dict, risk_results: dict, redline_results: dict) -> dict:
        """Generate an executive summary of the contract review."""
        try:
            clause_summary = clause_results.get("clause_summary", {})
            risk_summary = risk_results.get("overall_risk_assessment", {})
            redline_summary = redline_results.get("summary", {})
            
            return {
                "contract_overview": {
                    "clauses_analyzed": clause_summary.get("total_clauses_found", 0),
                    "high_importance_clauses": clause_summary.get("high_importance_count", 0),
                    "risks_identified": risk_summary.get("total_risks_identified", 0),
                    "high_severity_risks": risk_summary.get("high_severity_count", 0),
                    "redline_suggestions": redline_summary.get("total_suggestions", 0),
                    "critical_changes_needed": redline_summary.get("critical_changes", 0)
                },
                "overall_assessment": {
                    "risk_level": self._determine_overall_risk_level(risk_summary),
                    "contract_quality": self._assess_contract_quality(clause_summary, risk_summary),
                    "recommended_action": risk_summary.get("recommended_action", "Review recommended"),
                    "key_concerns": risk_summary.get("key_concerns", [])
                }
            }
        except Exception as e:
            return {
                "error": f"Failed to generate executive summary: {str(e)}",
                "contract_overview": {},
                "overall_assessment": {}
            }
    
    def _determine_overall_risk_level(self, risk_summary: dict) -> str:
        """Determine overall risk level based on analysis results."""
        high_risks = risk_summary.get("high_severity_count", 0)
        total_risks = risk_summary.get("total_risks_identified", 0)
        
        if high_risks >= 3:
            return "HIGH"
        elif high_risks >= 1 or total_risks >= 5:
            return "MEDIUM"
        elif total_risks >= 1:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _assess_contract_quality(self, clause_summary: dict, risk_summary: dict) -> str:
        """Assess overall contract quality."""
        coverage = clause_summary.get("coverage_assessment", "").lower()
        risk_score = risk_summary.get("overall_risk_score", 0)
        
        if "comprehensive" in coverage and risk_score < 3:
            return "GOOD"
        elif "adequate" in coverage and risk_score < 5:
            return "FAIR" 
        else:
            return "NEEDS_IMPROVEMENT"
    
    def _generate_next_steps(self, risk_results: dict, redline_results: dict) -> list:
        """Generate actionable next steps based on analysis."""
        next_steps = []
        
        high_risks = risk_results.get("overall_risk_assessment", {}).get("high_severity_count", 0)
        critical_changes = redline_results.get("summary", {}).get("critical_changes", 0)
        
        if critical_changes > 0:
            next_steps.append(f"Address {critical_changes} critical redline suggestions before proceeding")
        
        if high_risks > 0:
            next_steps.append(f"Mitigate {high_risks} high-severity risks identified")
        
        next_steps.extend([
            "Review all redline suggestions with legal counsel",
            "Negotiate key terms with counterparty",
            "Obtain final legal approval before signing"
        ])
        
        return next_steps

    def get_crew_status(self) -> dict:
        """Get current status of the crew and its agents."""
        return {
            "crew_initialized": self.crew is not None,
            "agents_available": {
                "clause_detector": self.clause_detector is not None,
                "risk_analyzer": self.risk_analyzer is not None, 
                "redline_suggester": self.redline_suggester is not None
            },
            "openai_configured": bool(os.getenv("OPENAI_API_KEY"))
        }
