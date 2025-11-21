"""
Email service with PDF report generation
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from typing import List, Dict
from datetime import datetime
import io
import config


class EmailService:
    """Handle email sending and PDF generation"""
    
    def __init__(self):
        self.smtp_host = config.SMTP_HOST
        self.smtp_port = config.SMTP_PORT
        self.smtp_user = config.SMTP_USERNAME
        self.smtp_pass = config.SMTP_PASSWORD
        self.from_email = config.FROM_EMAIL
    
    def send_daily_leads(self, to_email: str, leads: List[Dict], date: str):
        """Send daily leads email with PDF attachment"""
        try:
            # Generate PDF
            pdf_buffer = self.generate_leads_pdf(leads, date)
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = f'Your Top 10 Contractor Leads - {date}'
            
            # Email body
            body = self.create_email_body(leads, date)
            msg.attach(MIMEText(body, 'html'))
            
            # Attach PDF
            pdf_attachment = MIMEApplication(pdf_buffer.getvalue(), _subtype='pdf')
            pdf_attachment.add_header('Content-Disposition', 'attachment', 
                                     filename=f'contractor_leads_{date}.pdf')
            msg.attach(pdf_attachment)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
            
            print(f"Sent leads email to {to_email}")
            return True
        
        except Exception as e:
            print(f"Error sending email to {to_email}: {e}")
            return False
    
    def generate_leads_pdf(self, leads: List[Dict], date: str) -> io.BytesIO:
        """Generate PDF report of top leads"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=30
        )
        
        title = Paragraph(f'Top 10 Contractor Leads - {date}', title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Add each lead
        for i, lead in enumerate(leads, 1):
            # Lead header
            lead_title = Paragraph(
                f"<b>Lead #{i} - Score: {lead.get('score', 0)}/100</b>",
                styles['Heading2']
            )
            elements.append(lead_title)
            
            # Lead details table
            data = [
                ['County:', lead.get('county', 'N/A')],
                ['Address:', lead.get('address', 'N/A')],
                ['Permit Type:', lead.get('permit_type', 'N/A')],
                ['Estimated Value:', f"${lead.get('estimated_value', 0):,.2f}"],
                ['Permit Number:', lead.get('permit_number', 'N/A')],
                ['Description:', lead.get('work_description', 'N/A')[:100]],
            ]
            
            # Score breakdown
            breakdown = lead.get('score_breakdown', {})
            if breakdown:
                data.append(['Job Size Score:', f"{breakdown.get('size_score', 0):.1f}"])
                data.append(['Location Score:', f"{breakdown.get('location_score', 0):.1f}"])
                data.append(['Urgency Score:', f"{breakdown.get('urgency_score', 0):.1f}"])
                data.append(['Type Score:', f"{breakdown.get('type_score', 0):.1f}"])
            
            table = Table(data, colWidths=[2*inch, 4.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 0.3*inch))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def create_email_body(self, leads: List[Dict], date: str) -> str:
        """Create HTML email body"""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background-color: #1a5490; color: white; padding: 20px; }}
                .lead {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; }}
                .score {{ font-size: 24px; font-weight: bold; color: #1a5490; }}
                .details {{ margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Your Daily Contractor Leads - {date}</h1>
            </div>
            <p>Here are your top 10 hottest contractor leads for today. Full details are in the attached PDF.</p>
        """
        
        for i, lead in enumerate(leads[:5], 1):  # Show top 5 in email
            html += f"""
            <div class="lead">
                <div class="score">#{i} - Score: {lead.get('score', 0)}/100</div>
                <div class="details">
                    <strong>{lead.get('county', 'N/A')}</strong> - {lead.get('address', 'N/A')}<br>
                    Type: {lead.get('permit_type', 'N/A')}<br>
                    Value: ${lead.get('estimated_value', 0):,.2f}
                </div>
            </div>
            """
        
        html += """
            <p><strong>Download the PDF for complete details on all 10 leads!</strong></p>
            <p>Questions? Reply to this email or visit your dashboard.</p>
        </body>
        </html>
        """
        
        return html


# ==================== SUBSCRIPTION EMAIL FUNCTIONS ====================

def send_permit_email(to_email, city, permit_count, csv_file):
    """Send fresh permits email with CSV attachment (for subscriptions)"""
    import os
    import base64
    from pathlib import Path
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Attachment
    
    try:
        # Read CSV file
        with open(csv_file, 'rb') as f:
            csv_data = f.read()
        
        # Encode CSV for attachment
        encoded_csv = base64.b64encode(csv_data).decode()
        
        # Create email
        message = Mail(
            from_email=Email(os.getenv('SENDGRID_FROM_EMAIL', 'leads@contractorleads.com')),
            to_emails=To(to_email),
            subject=f'🏗️ {permit_count} New Building Permits in {city}',
            html_content=f'''
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center;">
                    <h1 style="color: white; margin: 0;">🏗️ Fresh Building Permits</h1>
                    <p style="color: white; margin: 10px 0 0 0; font-size: 18px;">{city}</p>
                </div>
                
                <div style="padding: 30px; background: #f9fafb; border-radius: 10px; margin-top: 20px;">
                    <h2 style="color: #333; margin-top: 0;">You have {permit_count} new leads!</h2>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <p style="color: #666; margin: 0;">
                            <strong style="color: #333;">Scraped:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br>
                            <strong style="color: #333;">City:</strong> {city}<br>
                            <strong style="color: #333;">New Permits:</strong> {permit_count}
                        </p>
                    </div>
                    
                    <p style="color: #666; line-height: 1.6;">
                        Your fresh permits are attached as a CSV file. These are <strong>brand new leads</strong> 
                        - no duplicates, just opportunities scraped in the last few hours.
                    </p>
                    
                    <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; border-radius: 4px;">
                        <p style="color: #92400e; margin: 0; font-size: 14px;">
                            <strong>💡 Pro Tip:</strong> The earliest contractors usually win the bid. 
                            Call these leads within the hour for best results.
                        </p>
                    </div>
                </div>
                
                <div style="text-align: center; padding: 20px; color: #999; font-size: 12px;">
                    <p>You're receiving this because you subscribed to {city} building permits.</p>
                    <p>Next scrape: Every 4 hours (5:30 AM, 9:30 AM, 1:30 PM, 5:30 PM)</p>
                </div>
            </body>
            </html>
            '''
        )
        
        # Add CSV attachment
        attachment = Attachment()
        attachment.file_content = encoded_csv
        attachment.file_type = 'text/csv'
        attachment.file_name = Path(csv_file).name
        attachment.disposition = 'attachment'
        message.attachment = attachment
        
        # Send email
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        response = sg.send(message)
        
        print(f"   ✅ Email sent to {to_email} (status: {response.status_code})")
        return True
        
    except Exception as e:
        print(f"   ❌ Email error: {e}")
        return False
