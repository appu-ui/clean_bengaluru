import os
import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from models import db, Report
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# ----------------- CONFIG -----------------

# ✅ Use /tmp for DB (Vercel writable)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ✅ Use /tmp for uploads (VERY IMPORTANT)
UPLOAD_FOLDER = '/tmp/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ----------------- EMAIL -----------------

app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'your_email@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'your_password')
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']

# ----------------- INIT -----------------

db.init_app(app)
mail = Mail(app)

# ✅ Force DB creation (serverless fix)
with app.app_context():
    db.create_all()

# EXTRA safety (serverless)
@app.before_request
def create_tables():
    db.create_all()

# ----------------- HELPERS -----------------

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ----------------- ROUTES -----------------

@app.route('/')
def index():
    return render_template('index.html', google_maps_api_key=os.environ.get('GOOGLE_MAPS_API_KEY', ''))

# ✅ Serve uploaded files from /tmp
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/reports', methods=['GET'])
def get_reports():
    try:
        reports = Report.query.all()
        return jsonify([report.to_dict() for report in reports])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports', methods=['POST'])
def create_report():
    try:
        if 'before_image' not in request.files:
            return jsonify({'error': 'No before_image'}), 400

        file = request.files['before_image']

        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400

        lat = request.form.get('lat')
        lng = request.form.get('lng')
        description = request.form.get('description', '')
        area = request.form.get('area', '')

        if not lat or not lng:
            return jsonify({'error': 'Missing coordinates'}), 400

        filename = secure_filename(f"{int(datetime.datetime.now().timestamp())}_{file.filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        file.save(file_path)  # ✅ now works

        new_report = Report(
            lat=float(lat),
            lng=float(lng),
            before_image=filename,
            description=description,
            area=area,
            status='Pending'
        )

        db.session.add(new_report)
        db.session.commit()

        return jsonify(new_report.to_dict()), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/<int:report_id>/resolve', methods=['POST'])
def resolve_report(report_id):
    try:
        report = Report.query.get_or_404(report_id)

        if report.status == 'Resolved':
            return jsonify({'error': 'Already resolved'}), 400

        file = request.files['after_image']

        if file.filename == '':
            return jsonify({'error': 'No file'}), 400

        filename = secure_filename(f"after_{int(datetime.datetime.now().timestamp())}_{file.filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        file.save(file_path)

        report.after_image = filename
        report.status = 'Resolved'
        db.session.commit()

        return jsonify(report.to_dict()), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ----------------- SCHEDULER -----------------

def check_pending_reports():
    with app.app_context():
        now = datetime.datetime.utcnow()
        reports = Report.query.filter_by(status='Pending').all()

        for report in reports:
            days = (now - report.created_at).days

            if days >= 2 and report.notification_level < 1:
                report.notification_level = 1
            elif days >= 4 and report.notification_level < 2:
                report.notification_level = 2
            elif days >= 7 and report.notification_level < 3:
                report.notification_level = 3

        db.session.commit()

scheduler = BackgroundScheduler()
scheduler.add_job(func=check_pending_reports, trigger="interval", days=1)
scheduler.start()

import atexit
atexit.register(lambda: scheduler.shutdown())
