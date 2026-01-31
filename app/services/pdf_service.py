"""PDF generation service using reportlab."""
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from app.models import ClaimResponse
from datetime import datetime
import os


class PDFService:
    """Service for generating claim offer letter PDFs."""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_offer_letter(self, claim: ClaimResponse) -> str:
        """Generate PDF offer letter for the claim."""
        filename = f"claim_{claim.claim_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
        )
        story.append(Paragraph("Claim Offer Letter", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Claim information
        story.append(Paragraph(f"<b>Claim ID:</b> {claim.claim_id}", styles['Normal']))
        story.append(Paragraph(f"<b>Date:</b> {claim.created_at.strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        story.append(Paragraph(f"<b>Policy ID:</b> {claim.policy_info.policy_id}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Damage Analysis Section
        story.append(Paragraph("<b>Damage Analysis</b>", styles['Heading2']))
        damage_data = [
            ['Damage Type:', claim.damage_analysis.damage_type.title()],
            ['Severity:', claim.damage_analysis.severity.replace('_', ' ').title()],
            ['Estimated Cost:', f"${claim.damage_analysis.estimated_cost:,.2f}"],
            ['Confidence:', f"{claim.damage_analysis.confidence * 100:.0f}%"]
        ]
        damage_table = Table(damage_data, colWidths=[2*inch, 3*inch])
        damage_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(damage_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Policy Information Section
        story.append(Paragraph("<b>Policy Information</b>", styles['Heading2']))
        policy_data = [
            ['Deductible:', f"${claim.policy_info.deductible:,.2f}"],
            ['Coverage Limit:', f"${claim.policy_info.coverage_limit:,.2f}"],
            ['Coverage Status:', 'Covered' if claim.policy_info.is_covered else 'Not Covered']
        ]
        policy_table = Table(policy_data, colWidths=[2*inch, 3*inch])
        policy_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(policy_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Payout Calculation Section
        story.append(Paragraph("<b>Payout Calculation</b>", styles['Heading2']))
        payout_data = [
            ['Estimated Cost:', f"${claim.payout_calculation.estimated_cost:,.2f}"],
            ['Deductible:', f"${claim.payout_calculation.deductible:,.2f}"],
            ['Payout Amount:', f"${claim.payout_calculation.payout_amount:,.2f}"],
            ['Status:', claim.payout_calculation.status.replace('_', ' ').title()]
        ]
        payout_table = Table(payout_data, colWidths=[2*inch, 3*inch])
        payout_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('BACKGROUND', (0, 2), (-1, 2), colors.lightgreen if claim.payout_calculation.payout_amount > 0 else colors.lightcoral),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(payout_table)
        story.append(Spacer(1, 0.5*inch))
        
        # Footer
        footer_text = "This is an automated offer letter generated by ClaimFlow. " \
                     "If you have any questions, please contact our customer service."
        story.append(Paragraph(footer_text, styles['Italic']))
        
        # Build PDF
        doc.build(story)
        
        return filepath
