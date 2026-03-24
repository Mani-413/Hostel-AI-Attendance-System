import os
import cv2  # type: ignore
import base64
import logging
from flask import Flask, render_template, Response, request, redirect, url_for, flash, send_file, jsonify, send_from_directory  # type: ignore
from flask_cors import CORS  # type: ignore
from services.excel_handler import ExcelHandler
from services.face_recognition_service import FaceRecognitionService  # type: ignore

import sys
import qrcode
import socket

IS_VERCEL = "VERCEL" in os.environ

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def generate_qr():
    if IS_VERCEL:
        return
    ip = get_ip()
    url = f"http://{ip}:5000"
    qr = qrcode.make(url)
    
    # Use absolute path to static folder
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "static"))
    if not os.path.exists(static_dir):
        try:
            os.makedirs(static_dir)
        except Exception:
            return
        
    qr_path = os.path.join(static_dir, "qrcode.png")
    qr.save(qr_path)
    print(f"[*] QR Code generated for: {url} at {qr_path}")

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        # Using getattr to bypass static type checking for dynamic PyInstaller attribute
        base_path = getattr(sys, '_MEIPASS')
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

app = Flask(__name__, 
            static_folder=resource_path('static'),
            template_folder=resource_path('templates'))
app.secret_key = "attendance_system_secret"
CORS(app)

# --- Configuration ---
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
DATASET_DIR = "dataset"
LATE_CUTOFF_HOUR = 11

# --- Setup Logging ---
if not IS_VERCEL:
    try:
        if not os.path.exists("logs"):
            os.makedirs("logs")
    except Exception:
        pass

logger = logging.getLogger("AppLogger")
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

if not IS_VERCEL:
    try:
        file_handler = logging.FileHandler('logs/app.log')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception:
        pass

# --- Initialize Globals ---
db = ExcelHandler()
face_mod = FaceRecognitionService(db, late_cutoff_hour=LATE_CUTOFF_HOUR)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if db.verify_user(username, password):
            logger.info(f"User {username} logged in")
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials! Please check your Excel User Database.")
    return render_template('login.html')

@app.route('/students', methods=['GET', 'POST'])
def students():
    if request.method == 'POST':
        sid = request.form['student_id'].strip()
        name = request.form['name'].strip()
        email = request.form.get('email', '').strip()
        webcam_data = request.form.get('webcam_image', '')
        file = request.files.get('image')

        if not sid or not name:
            flash("Student ID and Name are required!")
        else:
            file_path = os.path.join(DATASET_DIR, f"{sid}.jpg")
            saved = False

            if webcam_data and webcam_data.startswith('data:image'):
                header, encoded = webcam_data.split(',', 1)
                img_bytes = base64.b64decode(encoded)
                with open(file_path, 'wb') as f:
                    f.write(img_bytes)
                saved = True
            elif file and allowed_file(file.filename):
                file.save(file_path)
                saved = True

            if saved:
                if db.add_student(sid, name, email):
                    face_mod.load_known_faces()
                    flash(f"✅ Student '{name}' (ID: {sid}) registered successfully!")
                else:
                    flash(f"⚠️ Student ID {sid} already exists! Delete first to re-register.")
            else:
                flash("Please upload a photo or capture from webcam!")

    student_list = db.get_all_students()
    return render_template('students.html', students=student_list)

@app.route('/delete_student/<sid>')
def delete_student(sid):
    db.delete_student(sid)
    for ext in ['jpg', 'png', 'jpeg']:
        img_path = os.path.join(DATASET_DIR, f"{sid}.{ext}")
        if os.path.exists(img_path):
            os.remove(img_path)
    face_mod.load_known_faces()
    flash(f"🗑 Student {sid} deleted.")
    return redirect(url_for('students'))

@app.route('/dataset_img/<filename>')
def dataset_img(filename):
    return send_from_directory(DATASET_DIR, filename)  # type: ignore

@app.route('/attendance')
def attendance():
    all_data = db.get_all_attendance()
    return render_template('attendance.html', attendance=all_data)

@app.route('/attendance_data')
def attendance_data():
    today_data = db.get_today_attendance()
    stats = {
        "present": len([s for s in today_data if s['Status'] == 'Present']),
        "late": len([s for s in today_data if s['Status'] == 'Late']),
        "total": len(today_data)
    }
    return jsonify({"attendance": today_data[::-1], "stats": stats})

@app.route('/download_attendance')
def download_attendance():
    return send_file(db.ATTENDANCE_FILE, as_attachment=True)

def generate_frames():
    if IS_VERCEL:
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + b'Camera not available on cloud' + b'\r\n')
        return

    try:
        camera = cv2.VideoCapture(0)
        while True:
            success, frame = camera.read()
            if not success:
                logger.error("Camera fail")
                break
            frame, results = face_mod.recognize_face(frame)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        if 'camera' in locals():
            camera.release()

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    if not os.path.exists(DATASET_DIR):
        os.makedirs(DATASET_DIR)
    generate_qr()
    app.run(debug=True, host='0.0.0.0', port=5000)
