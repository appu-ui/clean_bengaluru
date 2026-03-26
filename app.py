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

# Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Email Config
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'your_email@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'your_password')
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']

db.init_app(app)
mail = Mail(app)

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ----------------- ROUTES -----------------

@app.route('/')
def index():
    return render_template('index.html', google_maps_api_key=os.environ.get('GOOGLE_MAPS_API_KEY', ''))

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/reports', methods=['GET'])
def get_reports():
    reports = Report.query.all()
    return jsonify([report.to_dict() for report in reports])

@app.route('/api/reports', methods=['POST'])
def create_report():
    if 'before_image' not in request.files:
        return jsonify({'error': 'No before_image part'}), 400
    file = request.files['before_image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only JPG and PNG are allowed.'}), 400

    lat = request.form.get('lat')
    lng = request.form.get('lng')
    description = request.form.get('description', '')

    if not lat or not lng:
        return jsonify({'error': 'Missing coordinates'}), 400

    filename = secure_filename(f"{int(datetime.datetime.now().timestamp())}_{file.filename}")
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    new_report = Report(
        lat=float(lat),
        lng=float(lng),
        before_image=filename,
        description=description,
        status='Pending'
    )
    db.session.add(new_report)
    db.session.commit()

    return jsonify(new_report.to_dict()), 201

@app.route('/api/reports/<int:report_id>/resolve', methods=['POST'])
def resolve_report(report_id):
    report = Report.query.get_or_404(report_id)
    if report.status == 'Resolved':
        return jsonify({'error': 'Report is already resolved'}), 400

    if 'after_image' not in request.files:
        return jsonify({'error': 'No after_image part'}), 400
    file = request.files['after_image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only JPG and PNG are allowed.'}), 400

    filename = secure_filename(f"after_{int(datetime.datetime.now().timestamp())}_{file.filename}")
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    report.after_image = filename
    report.status = 'Resolved'
    db.session.commit()

    return jsonify(report.to_dict()), 200

# ----------------- SCHEDULER -----------------

def check_pending_reports():
    with app.app_context():
        now = datetime.datetime.utcnow()
        pending_reports = Report.query.filter_by(status='Pending').all()
        for report in pending_reports:
            days_pending = (now - report.created_at).days
            
            target_level = 0
            recipients = []
            subject = ""
            
            if days_pending >= 7 and report.notification_level < 3:
                target_level = 3
                recipients = ['spcomswm@bbmp.gov.in', 'specialswmbbmp@gmail.com']
                subject = f"ESCALATION: Unresolved Garbage Spot Report #{report.id}"
            elif days_pending >= 4 and report.notification_level < 2:
                target_level = 2
                recipients = ['specialswmbbmp@gmail.com']
                subject = f"Follow-up: Unresolved Garbage Spot Report #{report.id} (4 days)"
            elif days_pending >= 2 and report.notification_level < 1:
                target_level = 1
                recipients = ['specialswmbbmp@gmail.com']
                subject = f"Reminder: Unresolved Garbage Spot Report #{report.id} (2 days)"

            if target_level > 0:
                try:
                    msg = Message(subject, recipients=recipients)
                    msg.body = f"Report ID: {report.id}\nLocation: {report.lat}, {report.lng}\nDescription: {report.description}\nPending for: {days_pending} days.\nView: http://localhost:5000/static/uploads/{report.before_image}"
                    
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], report.before_image)
                    if os.path.exists(image_path):
                        with app.open_resource(image_path) as fp:
                            ext = report.before_image.rsplit('.', 1)[1].lower()
                            content_type = 'image/jpeg' if ext in ['jpg', 'jpeg'] else 'image/png'
                            msg.attach(report.before_image, content_type, fp.read())

                    mail.send(msg)
                    report.notification_level = target_level
                    db.session.commit()
                    print(f"Sent email for report {report.id} at level {target_level}")
                except Exception as e:
                    print(f"Failed to send email for report {report.id}: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(func=check_pending_reports, trigger="interval", days=1)
scheduler.start()

# A hook to gracefully shutdown the scheduler when app exits
import atexit
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
