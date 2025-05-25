"""
Professional PDF Report Generator for Contract Reviewer Crew

Creates clean, professional PDF reports from contract analysis results.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY


class PDFReportGenerator:
    """Generates professional PDF reports for contract analysis results."""
    
    def __init__(self):
        """Initialize PDF report generator with styling."""
        self.styles = getSampleStyleSheet()
        
        # Color scheme
        self.primary_color = HexColor('#2563eb')
        self.secondary_color = HexColor('#1e40af')
        self.success_color = HexColor('#059669')
        self.warning_color = HexColor('#d97706')
        self.danger_color = HexColor('#dc2626')
        self.light_gray = HexColor('#f8fafc')
        self.dark_gray = HexColor('#64748b')
        
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Set up custom paragraph styles for the report."""
        # Check if styles already exist to avoid conflicts
        style_names = [style.name for style in self.styles.byName.values()]
        
        # Title style
        if 'ReportTitle' not in style_names:
            self.styles.add(ParagraphStyle(
                name='ReportTitle',
                parent=self.styles['Title'],
                fontSize=24,
                spaceAfter=30,
                textColor=HexColor('#1e40af'),
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            ))
        
        # Section header style
        if 'SectionHeader' not in style_names:
            self.styles.add(ParagraphStyle(
                name='SectionHeader',
                parent=self.styles['Heading1'],
                fontSize=16,
                spaceAfter=20,
                spaceBefore=30,
                textColor=HexColor('#2563eb'),
                fontName='Helvetica-Bold'
            ))
        
        # Subsection header style
        if 'SubsectionHeader' not in style_names:
            self.styles.add(ParagraphStyle(
                name='SubsectionHeader',
                parent=self.styles['Heading2'],
                fontSize=14,
                spaceAfter=15,
                spaceBefore=20,
                textColor=HexColor('#374151'),
                fontName='Helvetica-Bold'
            ))
        
        # Body text style
        if 'BodyText' not in style_names:
            self.styles.add(ParagraphStyle(
                name='BodyText',
                parent=self.styles['Normal'],
                fontSize=11,
                spaceAfter=12,
                leading=14,
                textColor=HexColor('#374151'),
                alignment=TA_JUSTIFY
            ))
        
        # Bullet point style
        if 'BulletPoint' not in style_names:
            self.styles.add(ParagraphStyle(
                name='BulletPoint',
                parent=self.styles['Normal'],
                fontSize=11,
                spaceAfter=8,
                leftIndent=20,
                bulletIndent=10,
                textColor=HexColor('#374151')
            ))
        
        # Risk level styles
        if 'HighRisk' not in style_names:
            self.styles.add(ParagraphStyle(
                name='HighRisk',
                parent=self.styles['Normal'],
                fontSize=11,
                textColor=self.danger_color,
                fontName='Helvetica-Bold'
            ))
        
        if 'MediumRisk' not in style_names:
            self.styles.add(ParagraphStyle(
                name='MediumRisk',
                parent=self.styles['Normal'],
                fontSize=11,
                textColor=self.warning_color,
                fontName='Helvetica-Bold'
            ))
        
        if 'LowRisk' not in style_names:
            self.styles.add(ParagraphStyle(
                name='LowRisk',
                parent=self.styles['Normal'],
                fontSize=11,
                textColor=self.success_color,
                fontName='Helvetica-Bold'
            ))
    
    def generate_report(self, results: Dict[Any, Any], filename: str = None) -> str:
        """
        Generate a professional PDF report from contract analysis results.
        
        Args:
            results: Contract analysis results dictionary
            filename: Optional filename for the PDF
            
        Returns:
            str: Path to the generated PDF file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"contract_analysis_report_{timestamp}.pdf"
        
        # Ensure output directory exists
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        filepath = output_dir / filename
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build document content
        story = []
        story.extend(self._create_title_page(results))
        story.append(PageBreak())
        story.extend(self._create_executive_summary(results))
        story.extend(self._create_detailed_analysis(results))
        story.extend(self._create_recommendations(results))
        
        # Build PDF
        doc.build(story)
        
        return str(filepath)
    
    def _create_title_page(self, results: Dict[Any, Any]) -> list:
        """Create the title page of the report."""
        story = []
        
        # Title
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("Contract Analysis Report", self.styles['ReportTitle']))
        story.append(Spacer(1, 0.5*inch))
        
        # Subtitle
        story.append(Paragraph("AI-Powered Legal Document Review", self.styles['Heading2']))
        story.append(Spacer(1, 1*inch))
        
        # Analysis details
        analysis_date = datetime.now().strftime("%B %d, %Y")
        story.append(Paragraph(f"<b>Analysis Date:</b> {analysis_date}", self.styles['BodyText']))
        story.append(Spacer(1, 0.2*inch))
        
        # Summary stats
        if results.get('success') and 'executive_summary' in results:
            overview = results['executive_summary'].get('contract_overview', {})
            
            summary_data = [
                ['Metric', 'Count'],
                ['Clauses Analyzed', str(overview.get('clauses_analyzed', 0))],
                ['Risks Identified', str(overview.get('risks_identified', 0))],
                ['High-Severity Risks', str(overview.get('high_severity_risks', 0))],
                ['Redline Suggestions', str(overview.get('redline_suggestions', 0))],
                ['Critical Changes Needed', str(overview.get('critical_changes_needed', 0))]
            ]
            
            summary_table = Table(summary_data, colWidths=[3*inch, 1.5*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), self.light_gray),
                ('GRID', (0, 0), (-1, -1), 1, self.dark_gray)
            ]))
            
            story.append(summary_table)
        
        # Legal Disclaimer
        story.append(Spacer(1, 1.5*inch))
        story.append(Paragraph("IMPORTANT LEGAL DISCLAIMER", self.styles['SubsectionHeader']))
        
        disclaimer_text = """
        <b>This AI-generated analysis is for informational purposes only and does not constitute legal advice.</b>
        The Contract Reviewer Crew uses artificial intelligence to analyze contracts and may contain errors, 
        omissions, or inaccuracies. Users should not rely solely on this analysis for legal decisions.
        
        <b>Key Limitations:</b><br/>
        • This tool does not replace qualified legal counsel<br/>
        • AI analysis may miss critical legal nuances<br/>
        • Contract law varies by jurisdiction<br/>
        • Results should be reviewed by a licensed attorney<br/>
        • No attorney-client relationship is created by using this tool<br/>
        
        <b>Recommendation:</b> Always consult with qualified legal professionals before making any 
        contract-related decisions or entering into legal agreements.
        """
        
        story.append(Paragraph(disclaimer_text, self.styles['BodyText']))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("Generated by Contract Reviewer Crew - AI-Powered Legal Analysis System", 
                             self.styles['Normal']))
        
        return story
    
    def _create_executive_summary(self, results: Dict[Any, Any]) -> list:
        """Create the executive summary section."""
        story = []
        
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        if not results.get('success'):
            story.append(Paragraph(f"Analysis failed: {results.get('error', 'Unknown error')}", 
                                 self.styles['BodyText']))
            return story
        
        exec_summary = results.get('executive_summary', {})
        assessment = exec_summary.get('overall_assessment', {})
        
        # Overall risk assessment
        risk_level = assessment.get('risk_level', 'Unknown')
        risk_style = self._get_risk_style(risk_level)
        
        story.append(Paragraph("Overall Risk Assessment", self.styles['SubsectionHeader']))
        story.append(Paragraph(f"Risk Level: <b>{risk_level}</b>", risk_style))
        story.append(Paragraph(f"Contract Quality: <b>{assessment.get('contract_quality', 'Unknown')}</b>", 
                             self.styles['BodyText']))
        story.append(Paragraph(f"Recommended Action: {assessment.get('recommended_action', 'Review needed')}", 
                             self.styles['BodyText']))
        story.append(Spacer(1, 0.2*inch))
        
        # Key concerns
        key_concerns = assessment.get('key_concerns', [])
        if key_concerns:
            story.append(Paragraph("Key Concerns", self.styles['SubsectionHeader']))
            for concern in key_concerns[:5]:  # Limit to top 5
                story.append(Paragraph(f"• {concern}", self.styles['BulletPoint']))
            story.append(Spacer(1, 0.2*inch))
        
        # Next steps
        next_steps = results.get('next_steps', [])
        if next_steps:
            story.append(Paragraph("Recommended Next Steps", self.styles['SubsectionHeader']))
            for i, step in enumerate(next_steps[:5], 1):
                story.append(Paragraph(f"{i}. {step}", self.styles['BulletPoint']))
        
        return story
    
    def _create_detailed_analysis(self, results: Dict[Any, Any]) -> list:
        """Create detailed analysis sections."""
        story = []
        
        if not results.get('success'):
            return story
        
        contract_analysis = results.get('contract_analysis', {})
        
        # Clause Detection Results
        story.append(PageBreak())
        story.append(Paragraph("Detailed Analysis", self.styles['SectionHeader']))
        
        clause_results = contract_analysis.get('clause_detection', {})
        detected_clauses = clause_results.get('detected_clauses', [])
        
        if detected_clauses:
            story.append(Paragraph("Detected Contract Clauses", self.styles['SubsectionHeader']))
            
            clause_data = [['Clause Type', 'Importance', 'Description']]
            for clause in detected_clauses:
                clause_type = clause.get('clause_type', 'Unknown')
                importance = clause.get('importance_level', 'Unknown')
                text = clause.get('clause_text', '')
                # Better text wrapping for descriptions
                if len(text) > 120:
                    text = text[:120] + "..."
                clause_data.append([clause_type, importance, text])
            
            clause_table = Table(clause_data, colWidths=[2.2*inch, 1.2*inch, 2.6*inch])
            clause_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), self.light_gray),
                ('GRID', (0, 0), (-1, -1), 1, self.dark_gray),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.light_gray, white]),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8)
            ]))
            story.append(clause_table)
            story.append(Spacer(1, 0.3*inch))
        
        # Risk Analysis
        risk_results = contract_analysis.get('risk_analysis', {})
        risk_analysis = risk_results.get('risk_analysis', [])
        
        if risk_analysis:
            story.append(Paragraph("Risk Analysis", self.styles['SubsectionHeader']))
            
            for i, risk in enumerate(risk_analysis[:8], 1):  # Limit to top 8 risks for better formatting
                severity = risk.get('severity_level', 'Unknown')
                risk_type = risk.get('risk_type', 'Unknown Risk')
                description = risk.get('risk_description', '')
                
                # Create a more structured risk entry
                severity_style = self._get_risk_style(severity)
                
                # Risk header with number and severity
                story.append(Paragraph(f"{i}. <b>{risk_type}</b> - <b>{severity} Risk</b>", severity_style))
                
                # Risk description with better formatting
                if description:
                    # Wrap long descriptions nicely
                    if len(description) > 400:
                        description = description[:400] + "..."
                    story.append(Paragraph(description, self.styles['BodyText']))
                
                story.append(Spacer(1, 0.15*inch))
        
        return story
    
    def _create_recommendations(self, results: Dict[Any, Any]) -> list:
        """Create recommendations and redline suggestions section."""
        story = []
        
        if not results.get('success'):
            return story
        
        contract_analysis = results.get('contract_analysis', {})
        redline_results = contract_analysis.get('redline_suggestions', {})
        suggestions = redline_results.get('redline_suggestions', [])
        
        if suggestions:
            story.append(PageBreak())
            story.append(Paragraph("Redline Suggestions", self.styles['SectionHeader']))
            
            for i, suggestion in enumerate(suggestions, 1):
                priority = suggestion.get('priority', 'Medium')
                change_type = suggestion.get('change_type', 'Modification')
                rationale = suggestion.get('rationale', '')
                
                priority_style = self._get_risk_style(priority)
                story.append(Paragraph(f"{i}. {change_type} - <b>{priority} Priority</b>", 
                                     priority_style))
                story.append(Paragraph(rationale, self.styles['BodyText']))
                story.append(Spacer(1, 0.2*inch))
        
        # New clauses needed
        new_clauses = redline_results.get('new_clauses_needed', [])
        if new_clauses:
            story.append(Paragraph("Recommended New Clauses", self.styles['SubsectionHeader']))
            
            for clause in new_clauses:
                clause_type = clause.get('clause_type', 'Unknown')
                justification = clause.get('justification', '')
                priority = clause.get('priority', 'Medium')
                
                priority_style = self._get_risk_style(priority)
                story.append(Paragraph(f"<b>{clause_type}</b> - <b>{priority} Priority</b>", 
                                     priority_style))
                story.append(Paragraph(justification, self.styles['BodyText']))
                story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _get_risk_style(self, level: str) -> ParagraphStyle:
        """Get appropriate style based on risk/priority level."""
        level_lower = level.lower()
        if level_lower in ['high', 'critical']:
            return self.styles['HighRisk']
        elif level_lower == 'medium':
            return self.styles['MediumRisk']
        else:
            return self.styles['LowRisk']
    
    def _get_table_style(self) -> TableStyle:
        """Get standard table styling."""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), self.light_gray),
            ('GRID', (0, 0), (-1, -1), 1, self.dark_gray),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 1), (-1, -1), 9)
        ])


# Global PDF generator instance
pdf_generator = PDFReportGenerator()