# Contract Reviewer Crew

> AI-powered contract review system using CrewAI and OpenAI GPT-4

A production-grade, multi-agent system that automates legal contract review using specialized AI agents for clause detection, risk analysis, and redline suggestions. Built with CrewAI framework and designed for submission to the [CrewAI Marketplace](https://marketplace.crewai.com).

## 🎯 Project Purpose

Automate the legal contract review process to help legal teams scale their review capabilities:

- **Ingest contracts** from multiple formats (.txt, .pdf, .docx)
- **Identify key clauses** (indemnity, termination, exclusivity, etc.)
- **Flag risks** and vague language using AI analysis
- **Suggest redlines** and legal comments
- **Output structured** review summaries

## 🧠 AI Agent Architecture

### ClauseDetectorAgent
- **Role**: Legal Clause Detection Specialist
- **Function**: Identifies and maps critical contract clauses
- **Output**: Structured clause mapping with importance rankings

### RiskAnalysisAgent  
- **Role**: Legal Risk Assessment Specialist
- **Function**: Analyzes legal risks, vague language, and problematic provisions
- **Output**: Comprehensive risk assessment with severity ratings

### RedlineSuggesterAgent
- **Role**: Contract Redlining and Amendment Specialist
- **Function**: Generates specific redline suggestions and negotiation strategy
- **Output**: Prioritized redlines with implementation roadmap

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key
- Required Python packages (see installation below)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd contract-reviewer-crew
