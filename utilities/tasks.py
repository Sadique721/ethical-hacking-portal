import os
from django.tasks import task
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

@task
def generate_pdf_report_task(title, severity, cvss_score, description, impact, remediation, filepath):
    """
    Generates a beautifully styled cybersecurity penetration testing report PDF.
    This runs inside Django 6.0's background tasks framework.
    """
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=40, leftMargin=40,
        topMargin=40, bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Styles for Cybersecurity Aesthetic (Dark slate and crimson accents)
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#0f172a'), # Slate 900
        spaceAfter=15
    )
    
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0284c7'), # Sky 600
        spaceBefore=15,
        spaceAfter=8,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'), # Slate 700
        spaceAfter=10
    )
    
    label_style = ParagraphStyle(
        'ReportLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#0f172a'),
    )

    story = []
    
    # 1. Header Band
    story.append(Paragraph("VULNERABILITY ASSESSMENT REPORT", title_style))
    story.append(Paragraph("CONFIDENTIAL // INTERNAL SECURITY ONLY", ParagraphStyle('SubHeader', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor('#ef4444'))))
    story.append(Spacer(1, 15))
    
    # 2. Metadata Table
    # Colors based on severity
    severity_colors = {
        'CRITICAL': colors.HexColor('#7f1d1d'), # Dark Red
        'HIGH': colors.HexColor('#b91c1c'),     # Red
        'MEDIUM': colors.HexColor('#d97706'),   # Amber
        'LOW': colors.HexColor('#2563eb'),      # Blue
    }
    sev_color = severity_colors.get(severity.upper(), colors.HexColor('#475569'))
    
    metadata_data = [
        [Paragraph("Vulnerability:", label_style), Paragraph(title, body_style)],
        [Paragraph("Severity Rating:", label_style), Paragraph(f"<font color='{sev_color}'><b>{severity}</b></font>", body_style)],
        [Paragraph("CVSS v3.1 Score:", label_style), Paragraph(str(cvss_score), body_style)],
        [Paragraph("Assessment Date:", label_style), Paragraph("Generated on demand", body_style)],
    ]
    
    meta_table = Table(metadata_data, colWidths=[120, 410])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 20))
    
    # 3. Vulnerability Description
    story.append(Paragraph("1. Executive Summary & Description", section_title_style))
    story.append(Paragraph(description, body_style))
    story.append(Spacer(1, 10))
    
    # 4. Technical Impact
    story.append(Paragraph("2. Technical Impact", section_title_style))
    story.append(Paragraph(impact, body_style))
    story.append(Spacer(1, 10))
    
    # 5. Remediation Plan
    story.append(Paragraph("3. Remediation & Fix Strategy", section_title_style))
    story.append(Paragraph(remediation, body_style))
    story.append(Spacer(1, 20))
    
    # 6. Footer Disclaimer
    story.append(Spacer(1, 40))
    disclaimer_text = ("<b>Disclaimer:</b> This report is generated automatically by the Ethical Hacking Portal. "
                       "All findings are simulated and intended for educational and defensive training purposes. "
                       "Unauthorised disclosure of security details is subject to strict policy guidelines.")
    story.append(Paragraph(disclaimer_text, ParagraphStyle('Disclaimer', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8, leading=10, textColor=colors.HexColor('#64748b'))))
    
    # Build Document
    doc.build(story)
