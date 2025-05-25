from crewai import Task

class ContractReviewTasks:
    """
    Task definitions for the contract review process.
    Each task corresponds to a specific phase of contract analysis.
    """
    
    def __init__(self):
        """Initialize task templates for contract review workflow."""
        pass
    
    def create_clause_detection_task(self, contract_text: str, agent) -> Task:
        """
        Create a task for detecting and mapping contract clauses.
        
        Args:
            contract_text (str): The contract text to analyze
            agent: The agent responsible for clause detection
            
        Returns:
            Task: CrewAI task for clause detection
        """
        return Task(
            description=f"""
            Analyze the provided contract text and identify all key legal clauses.
            Focus on finding critical provisions including:
            - Indemnity and liability clauses
            - Termination and cancellation provisions
            - Exclusivity and non-compete clauses
            - Payment and pricing terms
            - Intellectual property provisions
            - Confidentiality agreements
            - Governing law and dispute resolution
            
            Provide a detailed mapping of each clause with:
            - Exact clause text
            - Classification and importance level
            - Location context within the contract
            
            Contract to analyze:
            {contract_text[:1500]}...
            """,
            agent=agent,
            expected_output="""
            A structured JSON report containing:
            1. List of detected clauses with full text and classifications
            2. Clause importance rankings (High/Medium/Low)
            3. Coverage assessment of essential contract elements
            4. Recommendations for missing critical clauses
            """,
            max_iterations=2
        )
    
    def create_risk_analysis_task(self, contract_text: str, detected_clauses: list, agent) -> Task:
        """
        Create a task for comprehensive risk analysis.
        
        Args:
            contract_text (str): The contract text to analyze
            detected_clauses (list): Previously detected clauses
            agent: The agent responsible for risk analysis
            
        Returns:
            Task: CrewAI task for risk analysis
        """
        clause_summary = "\n".join([
            f"- {clause.get('clause_type', 'Unknown')}: {clause.get('importance_level', 'Unknown')} priority"
            for clause in detected_clauses[:10]
        ])
        
        return Task(
            description=f"""
            Conduct a comprehensive risk analysis of the contract focusing on:
            
            1. Legal Risk Assessment:
               - Vague or ambiguous language that could lead to disputes
               - One-sided provisions favoring the counterparty
               - Excessive liability exposure or inadequate protections
               - Missing risk mitigation clauses
            
            2. Business Risk Evaluation:
               - Unreasonable obligations or commitments
               - Inadequate termination protections
               - Intellectual property vulnerabilities
               - Compliance and regulatory risks
            
            3. Language Clarity Analysis:
               - Undefined terms requiring clarification
               - Inconsistent terminology usage
               - Overly complex provisions
            
            Previously detected clauses for context:
            {clause_summary}
            
            Contract text: {contract_text[:2000]}...
            """,
            agent=agent,
            expected_output="""
            A comprehensive risk assessment report including:
            1. Detailed risk analysis with severity ratings (High/Medium/Low)
            2. Specific problematic clauses and their potential impacts
            3. Overall risk score and assessment summary
            4. Language clarity evaluation with improvement suggestions
            5. Key concerns requiring immediate attention
            """,
            max_iterations=2
        )
    
    def create_redline_suggestion_task(self, contract_text: str, risk_analysis: dict, detected_clauses: list, agent) -> Task:
        """
        Create a task for generating redline suggestions and amendments.
        
        Args:
            contract_text (str): The contract text to analyze
            risk_analysis (dict): Results from risk analysis
            detected_clauses (list): Previously detected clauses
            agent: The agent responsible for redline suggestions
            
        Returns:
            Task: CrewAI task for redline generation
        """
        high_risks = [
            risk.get('risk_description', '') for risk in risk_analysis.get('risk_analysis', [])
            if risk.get('severity_level', '').lower() == 'high'
        ][:5]
        
        risk_context = "\n".join([f"- {risk}" for risk in high_risks]) if high_risks else "No high-severity risks identified"
        
        return Task(
            description=f"""
            Generate specific, actionable redline suggestions to improve this contract based on 
            the identified risks and clause analysis. Focus on:
            
            1. Addressing High-Priority Risks:
            {risk_context}
            
            2. Specific Redline Recommendations:
               - Exact text to be modified, added, or deleted
               - Proposed replacement language
               - Clear rationale for each change
               - Risk mitigation achieved by the change
            
            3. Missing Clause Additions:
               - Essential clauses that should be added
               - Protective provisions to strengthen
               - Definitions that need clarification
            
            4. Negotiation Strategy:
               - Critical vs. nice-to-have changes
               - Fallback positions and alternatives
               - Deal-breaker issues requiring firm positions
            
            Provide prioritized recommendations focusing on maximum risk reduction
            and practical negotiation outcomes.
            
            Contract text: {contract_text[:2000]}...
            """,
            agent=agent,
            expected_output="""
            A detailed redline strategy document containing:
            1. Specific redline suggestions with original and proposed text
            2. Priority levels (Critical/High/Medium/Low) for each suggestion
            3. Missing clauses that should be added with proposed language
            4. Negotiation strategy with key positions and fallback options
            5. Summary of total changes and estimated risk reduction
            6. Implementation roadmap for contract negotiations
            """,
            max_iterations=2
        )
    
    def create_executive_summary_task(self, review_results: dict, agent) -> Task:
        """
        Create a task for generating an executive summary of the review.
        
        Args:
            review_results (dict): Complete review results
            agent: The agent responsible for summarization
            
        Returns:
            Task: CrewAI task for executive summary generation
        """
        return Task(
            description=f"""
            Generate a comprehensive executive summary of the contract review process.
            Synthesize all analysis results into a clear, actionable report for decision-makers.
            
            Include:
            1. Contract Overview: Key metrics and findings
            2. Risk Assessment: Overall risk level and critical concerns
            3. Recommended Actions: Prioritized next steps
            4. Negotiation Priorities: Must-have vs. nice-to-have changes
            5. Timeline Recommendations: Suggested review and approval process
            
            Base the summary on these analysis results:
            - Clauses found: {review_results.get('clause_detection', {}).get('clause_summary', {})}
            - Risks identified: {review_results.get('risk_analysis', {}).get('overall_risk_assessment', {})}
            - Redlines suggested: {review_results.get('redline_suggestions', {}).get('summary', {})}
            """,
            agent=agent,
            expected_output="""
            An executive summary report including:
            1. One-page contract assessment overview
            2. Key findings and recommendations
            3. Risk level determination and mitigation priorities
            4. Actionable next steps with timelines
            5. Strategic negotiation guidance
            """,
            max_iterations=1
        )
