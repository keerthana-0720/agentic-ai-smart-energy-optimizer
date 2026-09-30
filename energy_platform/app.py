# ============================================================
# app.py - Main Flask Application
# AI Energy Optimization Platform - Wrapper Website
# ============================================================

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_mail import Mail, Message
from datetime import datetime
import json
import os
from functools import wraps
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
import io
from flask import send_file

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-only-change-this-secret-key')

# ============================================================
# Flask-Mail Configuration (Gmail SMTP)
# ============================================================
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'your_email@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'your_app_password')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])

mail = Mail(app)

# ============================================================
# In-memory user store (replace with DB in production)
# ============================================================
users_db = {}

# ============================================================
# Sample energy analytics data (dummy data for dashboard)
# ============================================================
SAMPLE_ENERGY_DATA = {
    "current_usage": 342.5,
    "predicted_consumption": 389.2,
    "savings_score": 78,
    "anomaly_count": 2,
    "optimization_tips": [
        "Switch to LED lighting to save up to 15% energy",
        "Schedule HVAC during off-peak hours (10PM - 6AM)",
        "Enable smart standby mode on idle devices",
        "Use solar panels to offset 20% of grid consumption",
        "Optimize industrial motor loads during peak hours"
    ],
    "ai_insights": [
        "Peak consumption detected between 2PM - 5PM",
        "Anomaly in Sector B: 23% above baseline",
        "Predicted 12% increase next week due to weather",
        "Energy efficiency improved by 8% this month"
    ],
    "monthly_usage": [310, 295, 320, 342, 318, 355, 340, 328, 365, 342, 380, 389],
    "weekly_usage": [48, 52, 45, 61, 55, 42, 38],
    "sector_breakdown": {
        "HVAC": 35,
        "Lighting": 20,
        "Industrial": 28,
        "IT Systems": 10,
        "Others": 7
    },
    "recent_activity": [
        {"time": "10:32 AM", "event": "Anomaly detected in Sector B", "type": "alert"},
        {"time": "09:15 AM", "event": "Optimization applied to HVAC system", "type": "success"},
        {"time": "08:45 AM", "event": "Daily report generated", "type": "info"},
        {"time": "Yesterday", "event": "Energy saving score updated: 78/100", "type": "success"},
        {"time": "Yesterday", "event": "New AI prediction model deployed", "type": "info"},
    ]
}

# ============================================================
# Login required decorator
# ============================================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ============================================================
# ROUTES
# ============================================================

@app.route('/')
def index():
    """Landing / Home page"""
    return render_template('index.html')

@app.route('/about')
def about():
    """About Project page"""
    return render_template('about.html')

@app.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User Registration"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if email in users_db:
            flash('Email already registered. Please login.', 'warning')
            return redirect(url_for('login'))

        # Store user (plain text for demo; use hashing in production)
        users_db[email] = {
            'username': username,
            'email': email,
            'password': password,
            'joined': datetime.now().strftime('%B %d, %Y')
        }

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User Login"""
    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        user = users_db.get(email)
        if user and user['password'] == password:
            session['user_email']    = email
            session['user_name']     = user['username']
            session['login_time']    = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            flash(f"Welcome back, {user['username']}!", 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main user dashboard with energy analytics"""
    data = SAMPLE_ENERGY_DATA.copy()
    data['user_name']  = session.get('user_name', 'User')
    data['user_email'] = session.get('user_email', '')
    data['current_time'] = datetime.now().strftime('%A, %B %d, %Y  %I:%M %p')
    return render_template('dashboard.html', data=data)

@app.route('/energy-tool')
@login_required
def energy_tool():
    """Embed the original energy optimization tool via iframe"""
    return render_template('energy_tool.html',
                           user_name=session.get('user_name', 'User'))

@app.route('/reports')
@login_required
def reports():
    """Reports section with charts and analytics"""
    data = SAMPLE_ENERGY_DATA.copy()
    data['user_name']  = session.get('user_name', 'User')
    data['user_email'] = session.get('user_email', '')
    data['report_date'] = datetime.now().strftime('%B %d, %Y')
    return render_template('reports.html', data=data)

@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    email = session.get('user_email')
    user  = users_db.get(email, {})
    return render_template('profile.html', user=user)

# ============================================================
# API: Send Email Report
# ============================================================
@app.route('/send-report', methods=['POST'])
@login_required
def send_report():
    """Send energy report to logged-in user's email"""
    try:
        user_email = session.get('user_email')
        user_name  = session.get('user_name', 'User')
        data       = SAMPLE_ENERGY_DATA
        now        = datetime.now().strftime('%B %d, %Y at %I:%M %p')

        msg = Message(
            subject='⚡ Your AI Energy Optimization Report',
            recipients=[user_email]
        )

        msg.html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background: #0a0a1a; color: #e0e0e0; padding: 20px;">
          <div style="max-width:600px; margin:auto; background:#111827; border-radius:12px;
                      border:1px solid #00ff88; padding:30px;">
            <h1 style="color:#00ff88; text-align:center;">⚡ AI Energy Report</h1>
            <p style="color:#aaa; text-align:center;">Generated on {now}</p>
            <hr style="border-color:#00ff8844;">

            <h2 style="color:#00d4ff;">Hello, {user_name}!</h2>
            <p>Here is your personalized energy optimization report:</p>

            <table style="width:100%; border-collapse:collapse; margin:20px 0;">
              <tr style="background:#1a2744;">
                <td style="padding:12px; color:#00ff88; font-weight:bold;">Current Energy Usage</td>
                <td style="padding:12px; color:#fff;">{data['current_usage']} kWh</td>
              </tr>
              <tr style="background:#0f1f3d;">
                <td style="padding:12px; color:#00d4ff; font-weight:bold;">Predicted Consumption</td>
                <td style="padding:12px; color:#fff;">{data['predicted_consumption']} kWh</td>
              </tr>
              <tr style="background:#1a2744;">
                <td style="padding:12px; color:#ffd700; font-weight:bold;">Energy Saving Score</td>
                <td style="padding:12px; color:#fff;">{data['savings_score']}/100</td>
              </tr>
              <tr style="background:#0f1f3d;">
                <td style="padding:12px; color:#ff4444; font-weight:bold;">Anomalies Detected</td>
                <td style="padding:12px; color:#fff;">{data['anomaly_count']}</td>
              </tr>
            </table>

            <h3 style="color:#00ff88;">🔧 Optimization Recommendations</h3>
            <ul style="color:#ccc;">
              {''.join(f'<li style="margin:8px 0;">{tip}</li>' for tip in data['optimization_tips'][:3])}
            </ul>

            <h3 style="color:#00d4ff;">🤖 AI Insights</h3>
            <ul style="color:#ccc;">
              {''.join(f'<li style="margin:8px 0;">{insight}</li>' for insight in data['ai_insights'][:3])}
            </ul>

            <hr style="border-color:#00ff8844; margin-top:30px;">
            <p style="color:#666; text-align:center; font-size:12px;">
              AI Energy Optimization Platform &bull; Powered by Groq AI<br>
              This report was automatically generated for {user_email}
            </p>
          </div>
        </body>
        </html>
        """

        mail.send(msg)
        return jsonify({'status': 'success', 'message': f'Report sent to {user_email}'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============================================================
# API: Download PDF Report
# ============================================================
@app.route('/download-pdf')
@login_required
def download_pdf():
    """Generate and download PDF energy report"""
    try:
        buffer = io.BytesIO()
        doc    = SimpleDocTemplate(buffer, pagesize=letter,
                                   rightMargin=72, leftMargin=72,
                                   topMargin=72, bottomMargin=18)
        styles = getSampleStyleSheet()
        story  = []

        # Title
        title_style = ParagraphStyle('Title', parent=styles['Title'],
                                     textColor=colors.HexColor('#00ff88'),
                                     fontSize=24, spaceAfter=12)
        story.append(Paragraph("⚡ AI Energy Optimization Report", title_style))
        story.append(Spacer(1, 0.2*inch))

        # Meta info
        meta_style = ParagraphStyle('Meta', parent=styles['Normal'],
                                    textColor=colors.grey, fontSize=10)
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')} | "
            f"User: {session.get('user_name')} | Email: {session.get('user_email')}",
            meta_style))
        story.append(Spacer(1, 0.3*inch))

        # Energy Summary Table
        summary_data = [
            ['Metric', 'Value'],
            ['Current Energy Usage', f"{SAMPLE_ENERGY_DATA['current_usage']} kWh"],
            ['Predicted Consumption', f"{SAMPLE_ENERGY_DATA['predicted_consumption']} kWh"],
            ['Energy Saving Score', f"{SAMPLE_ENERGY_DATA['savings_score']}/100"],
            ['Anomalies Detected', str(SAMPLE_ENERGY_DATA['anomaly_count'])],
        ]
        table = Table(summary_data, colWidths=[3*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#00ff88')),
            ('TEXTCOLOR',  (0,0), (-1,0), colors.black),
            ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',   (0,0), (-1,0), 12),
            ('ROWBACKGROUNDS', (0,1), (-1,-1),
             [colors.HexColor('#1a1a2e'), colors.HexColor('#16213e')]),
            ('TEXTCOLOR',  (0,1), (-1,-1), colors.white),
            ('GRID',       (0,0), (-1,-1), 0.5, colors.HexColor('#00ff8844')),
            ('PADDING',    (0,0), (-1,-1), 10),
        ]))
        story.append(table)
        story.append(Spacer(1, 0.3*inch))

        # Optimization Tips
        h2_style = ParagraphStyle('H2', parent=styles['Heading2'],
                                  textColor=colors.HexColor('#00d4ff'))
        story.append(Paragraph("Optimization Recommendations", h2_style))
        for tip in SAMPLE_ENERGY_DATA['optimization_tips']:
            story.append(Paragraph(f"• {tip}", styles['Normal']))
            story.append(Spacer(1, 0.05*inch))

        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("AI Insights", h2_style))
        for insight in SAMPLE_ENERGY_DATA['ai_insights']:
            story.append(Paragraph(f"• {insight}", styles['Normal']))
            story.append(Spacer(1, 0.05*inch))

        doc.build(story)
        buffer.seek(0)

        return send_file(buffer, as_attachment=True,
                         download_name=f"energy_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                         mimetype='application/pdf')
    except Exception as e:
        flash(f'PDF generation error: {str(e)}', 'danger')
        return redirect(url_for('reports'))

# ============================================================
# API: Get chart data (JSON)
# ============================================================
@app.route('/api/chart-data')
@login_required
def chart_data():
    return jsonify(SAMPLE_ENERGY_DATA)

# ============================================================
# Run
# ============================================================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
