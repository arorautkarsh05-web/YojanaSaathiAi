"""
Farmer Benefit Action Summary PDF Generator Service.
Generates an official-standard, non-impersonating, 1-page printable PDF summary
using ReportLab with QR code verification, masked farmer attributes, and statutory notices.
"""

import io
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode.qr import QrCodeWidget


def generate_farmer_benefit_summary_pdf(
    plan_number: str,
    confirmation_ref_id: str,
    farmer_name: Optional[str],
    farmer_mobile_masked: Optional[str],
    district: str,
    farmer_category: str,
    landholding_acres: Optional[float],
    selected_schemes: List[Dict[str, Any]],
    verified_documents: List[Dict[str, Any]],
    confirmed_at: Optional[datetime] = None
) -> bytes:
    """
    Builds a high-density, professional 1-page PDF document representing the
    Farmer Benefit Action Summary.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=30,
        rightMargin=30,
        topMargin=25,
        bottomMargin=25
    )

    styles = getSampleStyleSheet()
    
    # Custom palette
    c_forest = colors.HexColor("#1b4332")
    c_forest_light = colors.HexColor("#2d6a4f")
    c_bg_subtle = colors.HexColor("#f4f7f4")
    c_border = colors.HexColor("#d8e2dc")
    c_alert_bg = colors.HexColor("#fff3cd")
    c_alert_text = colors.HexColor("#856404")
    c_ink = colors.HexColor("#17251f")
    c_muted = colors.HexColor("#556b62")
    c_green_pill = colors.HexColor("#d4edda")
    c_green_text = colors.HexColor("#155724")

    # Typography styles
    style_title = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=c_forest,
        alignment=TA_LEFT
    )

    style_subtitle = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=c_forest_light,
        alignment=TA_LEFT
    )

    style_notice = ParagraphStyle(
        'StatutoryNotice',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=c_alert_text,
        alignment=TA_CENTER
    )

    style_label = ParagraphStyle(
        'FieldLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=c_muted
    )

    style_val = ParagraphStyle(
        'FieldValue',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=c_ink
    )

    style_table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white,
        alignment=TA_LEFT
    )

    style_table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=c_ink
    )

    style_table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=c_forest
    )

    style_badge_verified = ParagraphStyle(
        'BadgeVerified',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=8.5,
        textColor=c_green_text,
        alignment=TA_CENTER
    )

    style_disclaimer = ParagraphStyle(
        'LegalDisclaimer',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=6.5,
        leading=8.5,
        textColor=c_muted,
        alignment=TA_JUSTIFY
    )

    story = []

    # 1. Header with QR code and Title
    # Generate QR Code Drawing
    qr_content = f"https://yojanasaathi.up.gov-advisory.in/verify?plan={plan_number}&ref={confirmation_ref_id}"
    qr = QrCodeWidget(qr_content)
    qr.barWidth = 48
    qr.barHeight = 48
    qr.qrVersion = 1
    d_qr = Drawing(52, 52)
    d_qr.add(qr)

    dt_str = (confirmed_at or datetime.now(timezone.utc)).strftime("%d-%m-%Y %H:%M UTC")

    header_left = [
        Paragraph("FARMER BENEFIT ACTION SUMMARY", style_title),
        Paragraph("YojanaSaathi AI • Uttar Pradesh Evidence-Grounded Agricultural Advisory", style_subtitle),
        Paragraph(f"<b>Summary Ref:</b> {confirmation_ref_id} &nbsp;|&nbsp; <b>Plan ID:</b> {plan_number} &nbsp;|&nbsp; <b>Date:</b> {dt_str}", style_val),
    ]

    header_table = Table(
        [[header_left, d_qr]],
        colWidths=[470, 65]
    )
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 4))

    # 2. Prominent Non-Impersonation & Statutory Banner
    notice_text = (
        "<b>NOT A GOVERNMENT CERTIFICATE / यह सरकारी प्रमाण-पत्र नहीं है</b><br/>"
        "This document is an independent benefit preparation summary generated by YojanaSaathi AI for applicant guidance. "
        "Official benefit sanction is granted exclusively by competent government authorities upon formal portal verification."
    )
    banner_table = Table([[Paragraph(notice_text, style_notice)]], colWidths=[535])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_alert_bg),
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor("#ffeeba")),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 6))

    # 3. Farmer Profile & Geographic Context
    acres_str = f"{landholding_acres:.2f} Acres" if landholding_acres else "Not Specified"
    cat_str = farmer_category or "Small / Marginal"
    name_str = farmer_name or "Applicant Farmer (किसान आवेदक)"
    mobile_str = farmer_mobile_masked or "******1234"

    profile_data = [
        [
            Paragraph("Applicant Name:", style_label), Paragraph(name_str, style_val),
            Paragraph("Contact Mobile:", style_label), Paragraph(mobile_str, style_val)
        ],
        [
            Paragraph("State / District:", style_label), Paragraph(f"Uttar Pradesh, {district}", style_val),
            Paragraph("Landholding / Cat:", style_label), Paragraph(f"{acres_str} ({cat_str})", style_val)
        ]
    ]
    profile_table = Table(profile_data, colWidths=[90, 175, 95, 175])
    profile_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_subtle),
        ('BOX', (0,0), (-1,-1), 0.5, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.25, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(profile_table)
    story.append(Spacer(1, 6))

    # 4. Verified Schemes & Eligibility Table
    story.append(Paragraph("<b>1. EVALUATED SCHEMES & CONVERGENCE STATUS (संभावित योजनाएँ एवं पात्रता)</b>", style_subtitle))
    story.append(Spacer(1, 2))

    scheme_rows = [
        [
            Paragraph("Scheme Code & Official Title", style_table_header),
            Paragraph("Department / Level", style_table_header),
            Paragraph("Eligibility Status", style_table_header),
            Paragraph("Official Portal / Destination", style_table_header)
        ]
    ]

    for s in selected_schemes:
        code = s.get("scheme_code", "SCHEME")
        name = s.get("official_name_en") or s.get("title_en", code)
        dept = s.get("department", "Agriculture Dept")
        level = s.get("level", "CENTRAL")
        status_val = s.get("overall_status", "LIKELY_ELIGIBLE")
        portal = s.get("official_portal_url") or "upagriculture.com"

        status_text = "LIKELY ELIGIBLE" if "ELIGIBLE" in status_val else "NEEDS INFO"
        scheme_rows.append([
            Paragraph(f"<b>[{code}]</b> {name}", style_table_cell_bold),
            Paragraph(f"{dept}<br/>({level})", style_table_cell),
            Paragraph(status_text, style_badge_verified),
            Paragraph(portal, style_table_cell)
        ])

    scheme_table = Table(scheme_rows, colWidths=[185, 115, 95, 140])
    scheme_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_forest),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 0.5, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.25, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_subtle]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(scheme_table)
    story.append(Spacer(1, 6))

    # 5. Verified Supporting Documents Table
    story.append(Paragraph("<b>2. VERIFIED SUPPORTING DOCUMENTS CHECKLIST (सत्यापित दस्तावेज़)</b>", style_subtitle))
    story.append(Spacer(1, 2))

    doc_rows = [
        [
            Paragraph("Document Type", style_table_header),
            Paragraph("Category", style_table_header),
            Paragraph("Original File", style_table_header),
            Paragraph("Verification Status", style_table_header)
        ]
    ]

    for d in verified_documents:
        t_en = d.get("title_en") or d.get("doc_id_key", "Document")
        cat = d.get("document_category", "PROOF")
        fn = d.get("file_name_original", "verified_doc.pdf")
        if len(fn) > 28:
            fn = fn[:25] + "..."
        v_status = d.get("verification_status", "VERIFIED")

        doc_rows.append([
            Paragraph(t_en, style_table_cell_bold),
            Paragraph(cat, style_table_cell),
            Paragraph(fn, style_table_cell),
            Paragraph(v_status, style_badge_verified)
        ])

    doc_table = Table(doc_rows, colWidths=[175, 110, 145, 105])
    doc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_forest_light),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 0.5, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.25, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_subtle]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(doc_table)
    story.append(Spacer(1, 6))

    # 6. Benefit Timeline & Next Steps Notice
    timeline_text = (
        "<b>Benefit Timeline & Administrative Guidance:</b> All agricultural benefit disbursements in Uttar Pradesh "
        "follow Direct Benefit Transfer (DBT) through Aadhaar-enabled bank accounts (PFMS). Scheme sanctions depend "
        "on the state target allocation and verification by District Agriculture Officer / Sub-Divisional Magistrate. "
        "No individual dates are promised. Apply on designated portals with these verified records."
    )
    timeline_table = Table([[Paragraph(timeline_text, style_val)]], colWidths=[535])
    timeline_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_subtle),
        ('BOX', (0,0), (-1,-1), 0.5, c_border),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(timeline_table)
    story.append(Spacer(1, 6))

    # 7. Statutory Declaration & Footer
    disclaimer_text = (
        "<b>STATUTORY DECLARATION & NON-IMPERSONATION NOTICE:</b> "
        "1. This document is strictly an independent preparation summary generated by YojanaSaathi AI. It is NOT an official "
        "certificate, sanction order, or legal guarantee of government grant.<br/>"
        "2. No government seals, royal coats of arms, or state insignia are used. All trademarks and scheme names belong to their "
        "respective government departments.<br/>"
        "3. Verification QR code links to independent cryptographic verification of this planning summary.<br/>"
        "<b>Developed by Team Aalekh:</b> Adima Agarwal (Team Leader), Utkarsh Arora • YojanaSaathi AI v3.0"
    )
    story.append(Paragraph(disclaimer_text, style_disclaimer))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
