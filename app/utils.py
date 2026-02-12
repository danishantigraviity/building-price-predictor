import os
import threading
from flask import render_template, current_app
from flask_mail import Message
from app import mail
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO

def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Failed to send email: {e}")
            print(f"--- MOCK EMAIL ---\nTo: {msg.recipients}\nSubject: {msg.subject}\nBody: {msg.body}\n------------------")

def send_email(subject, recipient, template=None, body=None, pdf_bytes=None, pdf_name=None):
    app = current_app._get_current_object()
    msg = Message(subject, recipients=[recipient])
    
    if body:
        msg.body = body
    if template:
        msg.html = template

    if pdf_bytes and pdf_name:
        msg.attach(pdf_name, "application/pdf", pdf_bytes)

    # Threading for non-blocking email sending
    thr = threading.Thread(target=send_async_email, args=(app, msg))
    thr.start()

def generate_pdf(data):
    """
    Generates a professional PDF report using ReportLab.
    data format:
    {
        'user': {'name': str, 'email': str},
        'date': str,
        'id': int,
        'inputs': dict,
        'quantities': dict,
        'breakdown': dict,
        'total': float,
        'predicted_2026': float
    }
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor("#2c3e50"), spaceAfter=20)
    normal_style = styles["BodyText"]
    bold_style = ParagraphStyle('Bold', parent=styles['BodyText'], fontName='Helvetica-Bold')
    
    elements = []
    
    # Header
    elements.append(Paragraph("Building Cost Estimate", title_style))
    elements.append(Paragraph(f"<b>Date:</b> {data['date']}", normal_style))
    elements.append(Paragraph(f"<b>Estimator ID:</b> #{data['id']}", normal_style))
    elements.append(Paragraph(f"<b>Client:</b> {data['user']['name']} ({data['user']['email']})", normal_style))
    elements.append(Spacer(1, 10*mm))
    
    # Project Specs Table
    elements.append(Paragraph("Project Specifications", styles['Heading3']))
    inputs_data = [
        ["City", data['inputs'].get('city', 'N/A')],
        ["Quality", data['inputs'].get('quality', 'N/A')],
        ["Floors", data['inputs'].get('floors', 'N/A')],
        ["Area (sqft)", f"{data['inputs'].get('area_sqft_estimate', 'N/A')}"]
    ]
    t_inputs = Table(inputs_data, colWidths=[60*mm, 100*mm])
    t_inputs.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#ecf0f1")),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
    ]))
    elements.append(t_inputs)
    elements.append(Spacer(1, 10*mm))

    # Quantities & Costs Table
    elements.append(Paragraph("Material Breakdown", styles['Heading3']))
    
    bill_data = [["Material", "Quantity", "Estimated Cost (INR)"]]
    
    # Map keys to display names
    key_map = {
        'bricks': 'Bricks', 'cement': 'Cement', 'steel': 'Steel', 'paint': 'Paint', 'labor': 'Labor'
    }
    
    # Assuming quantities and breakdown keys align roughly or we map them
    # Let's just list cost breakdown items
    total_est = 0
    for k, cost in data['breakdown'].items():
        name = key_map.get(k, k.capitalize())
        # Try to find qty
        qty_val = "-"
        if k == 'bricks': qty_val = f"{data['quantities'].get('bricks_count', 0):,.0f} Units"
        elif k == 'cement': qty_val = f"{data['quantities'].get('cement_bags', 0):,.0f} Bags"
        elif k == 'steel': qty_val = f"{data['quantities'].get('steel_kg', 0):,.0f} Kg"
        elif k == 'paint': qty_val = f"{data['quantities'].get('paint_liters', 0):,.0f} L"
        elif k == 'labor': qty_val = f"{data['quantities'].get('worker_days', 0):,.0f} Days"
        
        bill_data.append([name, qty_val, f"Rs. {cost:,.2f}"])
        total_est += cost
        
    bill_data.append(["TOTAL ESTIMATE", "", f"Rs. {data['total']:,.2f}"])
    
    t_bill = Table(bill_data, colWidths=[60*mm, 60*mm, 40*mm])
    t_bill.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2c3e50")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#dff9fb")),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    elements.append(t_bill)
    elements.append(Spacer(1, 10*mm))
    
    # Future Prediction
    if data.get('predicted_2026'):
        elements.append(Paragraph("Future Price Forecast (2026)", styles['Heading3']))
        pred_text = f"Based on current market trends and inflation analysis, the estimated cost for this project in 2026 is approximately <b>Rs. {data['predicted_2026']:,.2f}</b>."
        elements.append(Paragraph(pred_text, normal_style))
    
    # Footer
    elements.append(Spacer(1, 20*mm))
    elements.append(Paragraph("Generated by Civil Estimator AI", ParagraphStyle('Footer', parent=normal_style, alignment=1, textColor=colors.grey)))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
