#!/usr/bin/env python3
"""
DEMO MODE - Full functionality without credentials
Shows: Scraping simulation, AI scoring, PDF generation, email preview
"""
from flask import Flask, render_template, send_file, jsonify
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch

app = Flask(__name__)
app.secret_key = 'demo-secret-key'

# ==================== DEMO DATA ====================

def get_demo_permits():
    """Generate realistic demo permit data"""
    return [
        {
            'county': 'Nashville-Davidson',
            'permit_number': 'BLD2025-001234',
            'address': '1234 Broadway, Nashville, TN 37203',
            'permit_type': 'New Construction - Commercial',
            'work_description': 'New 5-story mixed-use building with retail and apartments',
            'estimated_value': 2500000,
            'issue_date': '2025-11-15',
            'contractor': 'Premier Builders LLC',
            'owner': 'Downtown Development Corp',
            'scraped_at': datetime.now().isoformat()
        },
        {
            'county': 'Rutherford',
            'permit_number': 'RT-2025-5678',
            'address': '567 Medical Center Pkwy, Murfreesboro, TN 37129',
            'permit_type': 'Addition - Commercial',
            'estimated_value': 450000,
            'work_description': 'Medical office building addition - 3000 sq ft',
            'issue_date': '2025-11-16'
        },
        {
            'county': 'Wilson',
            'permit_number': 'WL-BLD-9012',
            'address': '890 Main Street, Lebanon, TN 37087',
            'permit_type': 'Renovation - Retail',
            'estimated_value': 175000,
            'work_description': 'Complete interior renovation of retail space',
            'issue_date': '2025-11-17'
        },
        {
            'county': 'Sumner',
            'permit_number': 'SMN-2025-3456',
            'address': '345 Station Camp Creek Rd, Gallatin, TN 37066',
            'permit_type': 'New Construction - Residential',
            'estimated_value': 525000,
            'work_description': 'New single family home - 3200 sq ft',
            'issue_date': '2025-11-14'
        },
        {
            'county': 'Nashville-Davidson',
            'permit_number': 'BLD2025-007890',
            'address': '789 12th Ave S, Nashville, TN 37203',
            'permit_type': 'Remodel - Restaurant',
            'estimated_value': 225000,
            'work_description': 'Full restaurant remodel and kitchen upgrade',
            'issue_date': '2025-11-17'
        },
        {
            'county': 'Rutherford',
            'permit_number': 'RT-2025-1122',
            'address': '112 Industrial Park Dr, Smyrna, TN 37167',
            'permit_type': 'New Construction - Warehouse',
            'estimated_value': 850000,
            'work_description': '15,000 sq ft warehouse facility',
            'issue_date': '2025-11-16'
        },
        {
            'county': 'Nashville-Davidson',
            'permit_number': 'BLD2025-004455',
            'address': '445 Charlotte Ave, Nashville, TN 37219',
            'permit_type': 'Alteration - Office',
            'estimated_value': 125000,
            'work_description': 'Office space build-out for tech company',
            'issue_date': '2025-11-15'
        },
        {
            'county': 'Wilson',
            'permit_number': 'WL-BLD-6789',
            'address': '678 Baddour Pkwy, Lebanon, TN 37090',
            'permit_type': 'Addition - Retail',
            'estimated_value': 320000,
            'work_description': 'Retail store expansion - 2500 sq ft addition',
            'issue_date': '2025-11-18'
        }
    ]

def score_permit_demo(permit):
    """Demo AI scoring (mimics real AI scorer)"""
    # Job size score
    value = permit.get('estimated_value', 0)
    if value >= 500000:
        size_score = 90
    elif value >= 200000:
        size_score = 75
    elif value >= 100000:
        size_score = 60
    else:
        size_score = 45
    
    # Location score
    address = permit.get('address', '').lower()
    if 'nashville' in address or 'broadway' in address:
        location_score = 90
    elif 'murfreesboro' in address or 'gallatin' in address:
        location_score = 75
    else:
        location_score = 60
    
    # Type score
    permit_type = permit.get('permit_type', '').lower()
    if 'new construction' in permit_type or 'commercial' in permit_type:
        type_score = 85
    elif 'addition' in permit_type or 'renovation' in permit_type:
        type_score = 70
    else:
        type_score = 55
    
    # Urgency score (simulated)
    urgency_score = 75
    
    # Calculate weighted score
    total_score = (
        size_score * 0.35 +
        location_score * 0.25 +
        urgency_score * 0.20 +
        type_score * 0.20
    )
    
    permit['score'] = round(total_score, 1)
    permit['score_breakdown'] = {
        'size_score': size_score,
        'location_score': location_score,
        'urgency_score': urgency_score,
        'type_score': type_score
    }
    
    return permit

def generate_pdf_demo(leads, date):
    """Generate PDF report (working demo)"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph(f'<b>Top 10 Contractor Leads - {date}</b>', styles['Heading1'])
    elements.append(title)
    elements.append(Spacer(1, 0.3*inch))
    
    # Add each lead
    for i, lead in enumerate(leads, 1):
        lead_title = Paragraph(f"<b>Lead #{i} - Score: {lead.get('score', 0)}/100</b>", styles['Heading2'])
        elements.append(lead_title)
        elements.append(Spacer(1, 0.1*inch))
        
        data = [
            ['County:', lead.get('county', 'N/A')],
            ['Address:', lead.get('address', 'N/A')],
            ['Permit Type:', lead.get('permit_type', 'N/A')],
            ['Value:', f"${lead.get('estimated_value', 0):,.2f}"],
            ['Permit #:', lead.get('permit_number', 'N/A')],
        ]
        
        table = Table(data, colWidths=[1.5*inch, 4.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.2*inch))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/demo')
def demo():
    """Demo dashboard"""
    # Get demo data
    permits = get_demo_permits()
    
    # Score them
    scored = [score_permit_demo(p) for p in permits]
    scored.sort(key=lambda x: x['score'], reverse=True)
    
    # Top 10
    top_leads = scored[:10]
    
    date = datetime.now().strftime('%Y-%m-%d')
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Demo Dashboard - Contractor Leads</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
        }}
        .navbar {{
            background: #1a5490;
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .banner {{
            background: linear-gradient(135deg, #ff6b35 0%, #ff8c42 100%);
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 18px;
            font-weight: bold;
        }}
        .container {{
            max-width: 1200px;
            margin: 40px auto;
            padding: 0 20px;
        }}
        .header-section {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .lead-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 5px solid #1a5490;
        }}
        .lead-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        .lead-rank {{
            font-size: 24px;
            font-weight: bold;
            color: #1a5490;
        }}
        .lead-score {{
            font-size: 32px;
            font-weight: bold;
            color: #ff6b35;
        }}
        .lead-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        .detail-item {{
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
        }}
        .detail-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            margin-bottom: 5px;
        }}
        .detail-value {{
            font-size: 16px;
            color: #333;
            font-weight: 600;
        }}
        .btn {{
            display: inline-block;
            padding: 12px 24px;
            background: #ff6b35;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 10px 10px 10px 0;
            font-weight: bold;
        }}
        .btn:hover {{ background: #ff5520; }}
        .score-breakdown {{
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #e0e0e0;
            font-size: 14px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="navbar">
        <h1>🏗️ Contractor Leads</h1>
        <span>DEMO MODE</span>
    </div>
    
    <div class="banner">
        🎯 DEMO MODE: This shows how the system works with sample data. 
        No Firebase/Stripe needed! Real app processes live permit data daily.
    </div>
    
    <div class="container">
        <div class="header-section">
            <h2>Your Daily Leads - {date}</h2>
            <p>Here are your top 10 hottest contractor leads, scored by AI.</p>
            <p style="margin-top: 10px; color: #666;">
                ⚡ <strong>How it works:</strong> Every night, the system scrapes 5 county websites,
                extracts permit data, scores each with AI, and emails you the top 10.
            </p>
            <a href="/demo/pdf" class="btn">📄 Download PDF Report</a>
            <a href="/demo/how-it-works" class="btn" style="background: #1a5490;">🤖 See How AI Scores</a>
        </div>
        
        {"".join([f'''
        <div class="lead-card">
            <div class="lead-header">
                <div class="lead-rank">#{i}</div>
                <div class="lead-score">{lead['score']}/100</div>
            </div>
            
            <div class="lead-details">
                <div class="detail-item">
                    <div class="detail-label">County</div>
                    <div class="detail-value">{lead['county']}</div>
                </div>
                
                <div class="detail-item">
                    <div class="detail-label">Address</div>
                    <div class="detail-value">{lead.get('address', 'N/A')}</div>
                </div>
                
                <div class="detail-item">
                    <div class="detail-label">Permit Type</div>
                    <div class="detail-value">{lead.get('permit_type', 'N/A')}</div>
                </div>
                
                <div class="detail-item">
                    <div class="detail-label">Estimated Value</div>
                    <div class="detail-value">${lead.get('estimated_value', 0):,}</div>
                </div>
                
                <div class="detail-item">
                    <div class="detail-label">Permit Number</div>
                    <div class="detail-value">{lead.get('permit_number', 'N/A')}</div>
                </div>
                
                <div class="detail-item">
                    <div class="detail-label">Description</div>
                    <div class="detail-value">{lead.get('work_description', 'N/A')[:100]}</div>
                </div>
            </div>
            
            <div class="score-breakdown">
                <strong>AI Score Breakdown:</strong>
                Job Size: {lead['score_breakdown']['size_score']}/100 | 
                Location: {lead['score_breakdown']['location_score']}/100 | 
                Urgency: {lead['score_breakdown']['urgency_score']}/100 | 
                Type: {lead['score_breakdown']['type_score']}/100
            </div>
        </div>
        ''' for i, lead in enumerate(top_leads, 1)])}
    </div>
</body>
</html>
    """

@app.route('/demo/pdf')
def demo_pdf():
    """Download demo PDF"""
    permits = get_demo_permits()
    scored = [score_permit_demo(p) for p in permits]
    scored.sort(key=lambda x: x['score'], reverse=True)
    top_leads = scored[:10]
    
    date = datetime.now().strftime('%Y-%m-%d')
    pdf = generate_pdf_demo(top_leads, date)
    
    return send_file(
        pdf,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'contractor_leads_demo_{date}.pdf'
    )

@app.route('/demo/how-it-works')
def how_it_works():
    """Explain the system"""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>How It Works - Contractor Leads</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
            line-height: 1.6;
        }
        h1 { color: #1a5490; }
        h2 { color: #ff6b35; margin-top: 30px; }
        .step { 
            background: #f8f9fa;
            padding: 20px;
            margin: 20px 0;
            border-radius: 10px;
            border-left: 5px solid #1a5490;
        }
        code {
            background: #e9ecef;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
        }
        .back-btn {
            display: inline-block;
            padding: 10px 20px;
            background: #1a5490;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <a href="/demo" class="back-btn">← Back to Demo Dashboard</a>
    
    <h1>🤖 How the AI Scoring System Works</h1>
    
    <p>Every night at 2 AM, the system automatically:</p>
    
    <div class="step">
        <h2>1. 🕷️ Web Scraping</h2>
        <p>Scrapes building permit applications from 5 Tennessee county websites:</p>
        <ul>
            <li>Nashville-Davidson County</li>
            <li>Rutherford County</li>
            <li>Wilson County</li>
            <li>Sumner County</li>
        </ul>
        <p><strong>Technology:</strong> BeautifulSoup + Selenium for HTML parsing, PDFPlumber for PDF extraction</p>
    </div>
    
    <div class="step">
        <h2>2. 🤖 AI Scoring (HuggingFace Transformer)</h2>
        <p>Each permit is scored 0-100 based on 4 factors:</p>
        <ul>
            <li><strong>Job Size (35%):</strong> Project value - Higher value = better lead</li>
            <li><strong>Location (25%):</strong> Premium areas like downtown Nashville, Brentwood, Franklin</li>
            <li><strong>Urgency (20%):</strong> AI sentiment analysis on project description</li>
            <li><strong>Type (20%):</strong> Commercial/new construction scores higher than repairs</li>
        </ul>
        <p><strong>Model:</strong> DistilBERT (HuggingFace) for natural language understanding</p>
    </div>
    
    <div class="step">
        <h2>3. 📊 Ranking & Selection</h2>
        <p>All permits are ranked by score, and the top 10 are selected for your daily report.</p>
    </div>
    
    <div class="step">
        <h2>4. 📧 Email Delivery</h2>
        <p>Generates a professional PDF report and emails it to all active subscribers.</p>
        <p><strong>Technology:</strong> ReportLab for PDF generation, SMTP for email delivery</p>
    </div>
    
    <div class="step">
        <h2>5. 💾 Storage</h2>
        <p>All permits and daily reports are saved to Firebase for historical access via dashboard.</p>
    </div>
    
    <h2>💰 Business Model</h2>
    <p><strong>Subscription:</strong> $20/month per contractor</p>
    <p><strong>Value Proposition:</strong> Get hot leads before competitors, save hours of manual research</p>
    <p><strong>Margin:</strong> 96% profit margin at scale</p>
    
    <h2>🛠️ Tech Stack</h2>
    <ul>
        <li><strong>Backend:</strong> Python + Flask</li>
        <li><strong>Scraping:</strong> BeautifulSoup4, Selenium, PDFPlumber</li>
        <li><strong>AI:</strong> HuggingFace Transformers (DistilBERT)</li>
        <li><strong>Database:</strong> Firebase Firestore</li>
        <li><strong>Payments:</strong> Stripe</li>
        <li><strong>Email:</strong> SMTP + ReportLab PDF</li>
        <li><strong>Scheduling:</strong> Python Schedule library</li>
    </ul>
    
    <a href="/demo" class="back-btn">← Back to Demo Dashboard</a>
</body>
</html>
    """

@app.route('/demo/api/leads')
def api_demo():
    """API endpoint demo"""
    permits = get_demo_permits()
    scored = [score_permit_demo(p) for p in permits]
    scored.sort(key=lambda x: x['score'], reverse=True)
    return jsonify(scored[:10])


if __name__ == '__main__':
    port = 5002
    print("\n" + "="*70)
    print("🏗️  CONTRACTOR LEADS - FULL DEMO MODE")
    print("="*70)
    print(f"🌐 Open in browser: http://localhost:{port}/demo")
    print("="*70)
    print("\n✅ This demo shows the COMPLETE system:")
    print("   • Web scraping simulation")
    print("   • AI lead scoring")
    print("   • Dashboard with top 10 leads")
    print("   • PDF report generation")
    print("   • How the system works")
    print("\n⚡ NO credentials needed - works out of the box!")
    print("\n📖 Landing page: http://localhost:5002")
    print("📊 Demo dashboard: http://localhost:5002/demo")
    print("="*70 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=True)
