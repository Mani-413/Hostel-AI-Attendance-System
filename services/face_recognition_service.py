import cv2  # type: ignore
import os
import numpy as np  # type: ignore
import logging
from datetime import datetime

try:
    import face_recognition  # type: ignore
    FACE_REC_AVAILABLE = True
except Exception:
    FACE_REC_AVAILABLE = False


class FaceRecognitionService:
    DEFAUT_DATASET_DIR = "dataset"

    def __init__(self, excel_handler, late_cutoff_hour=9):
        self.logger = logging.getLogger("AppLogger")
        self.db = excel_handler
        self.late_cutoff_hour = late_cutoff_hour
        
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_emails = []
        self.known_face_ids = []
        
        if not os.path.exists(self.DEFAUT_DATASET_DIR):
            os.makedirs(self.DEFAUT_DATASET_DIR)
            
        self.load_known_faces()

    def load_known_faces(self):
        if not FACE_REC_AVAILABLE:
            self.logger.warning("face_recognition not installed, skipping load.")
            return

        self.logger.info("Loading known faces...")
        new_encodings = []
        new_names = []
        new_emails = []
        new_ids = []
        
        all_students = self.db.get_all_students()
        student_dict = {str(s['Student ID']).split('.')[0].strip(): {'Name': s['Name'], 'Email': str(s.get('Email', ''))} for s in all_students}
        
        for filename in os.listdir(self.DEFAUT_DATASET_DIR):
            if filename.endswith(('.jpg', '.png', '.jpeg')):
                student_id = filename.split('.')[0].split('_')[0].strip()
                
                if student_id in student_dict:
                    name = student_dict[student_id]['Name']
                    email = student_dict[student_id]['Email']
                    img_path = os.path.join(self.DEFAUT_DATASET_DIR, filename)
                    try:
                        image = face_recognition.load_image_file(img_path)
                        encodings = face_recognition.face_encodings(image)
                        if len(encodings) > 0:
                            new_encodings.append(encodings[0])
                            new_names.append(name)
                            new_emails.append(email)
                            new_ids.append(student_id)
                        else:
                            self.logger.warning(f"No face found in {filename}")
                    except Exception as e:
                        self.logger.error(f"Error loading {filename}: {str(e)}")
        
        # Atomically swap the lists to prevent the video thread from failing
        self.known_face_encodings = new_encodings
        self.known_face_names = new_names
        self.known_face_emails = new_emails  # type: ignore
        self.known_face_ids = new_ids  # type: ignore
        
        self.logger.info(f"Loaded {len(self.known_face_encodings)} face(s).")

    def recognize_face(self, frame):
        if not FACE_REC_AVAILABLE:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                cv2.putText(frame, "AI Lib Missing", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
            return frame, []

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        recognized_students = []

        for face_encoding, face_location in zip(face_encodings, face_locations):
            top, right, bottom, left = face_location
            
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.55)
            name = "Unknown"
            student_id = None
            email_addr = None
            
            if len(self.known_face_encodings) > 0:
                face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
                    student_id = self.known_face_ids[best_match_index]
                    email_addr = self.known_face_emails[best_match_index]
                    
            color = (0, 0, 255)
            if name != "Unknown":
                color = (0, 255, 0)
                now = datetime.now()
                cutoff = now.replace(hour=self.late_cutoff_hour, minute=0, second=0, microsecond=0)
                status = "Present" if now <= cutoff else "Late"
                
                marked, msg = self.db.mark_attendance(student_id, name, status)
                recognized_students.append({"name": name, "id": student_id, "status": status, "marked": marked})
                
                if marked:
                    if email_addr and str(email_addr).lower() != 'nan':
                        from services.email_service import send_email  # type: ignore
                        import threading
                        subject = f"Hostel Attendance Alert: {status}"
                        msg_text = f"Dear {name},\n\nYou have been successfully marked as {status} for today at {now.strftime('%I:%M %p')}.\n\nBest regards,\nHostelAI Administrator"
                        threading.Thread(target=send_email, args=(email_addr, subject, msg_text)).start()
            
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)

        return frame, recognized_students
