import os
import logging

logger = logging.getLogger("AppLogger")

try:
    import firebase_admin  # type: ignore
    from firebase_admin import credentials, firestore  # type: ignore
    FIREBASE_INSTALLED = True
except ImportError:
    FIREBASE_INSTALLED = False

class FirebaseService:
    def __init__(self):
        self.db = None
        self.initialized = False
        
        if not FIREBASE_INSTALLED:
            logger.warning("Firebase Admin SDK not installed. Skipping Firebase sync.")
            return
            
        cred_path = "firebase_credentials.json"
        
        if os.path.exists(cred_path):
            try:
                if not firebase_admin._apps:
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                self.db = firestore.client()
                self.initialized = True
                logger.info("Firebase Firestore connected successfully! Dual-sync active.")
            except Exception as e:
                logger.error(f"Error initializing Firebase: {str(e)}")
        else:
            logger.warning(f"Firebase credentials not found at {cred_path}. Firebase sync disabled.")
            print("\n[🔥 FIREBASE SETUP REQUIRED]")
            print("1. Go to Firebase Console -> Project Settings -> Service Accounts")
            print("2. Click 'Generate new private key'")
            print("3. Rename the downloaded file to 'firebase_credentials.json' and place it in the root folder.\n")

    def sync_student(self, student_id, name, email):
        db = self.db
        if db is not None:
            try:
                db.collection('students').document(str(student_id)).set({
                    'student_id': str(student_id),
                    'name': str(name),
                    'email': str(email)
                })
                logger.info(f"Firebase Sync: Student {student_id} saved.")
            except Exception as e:
                logger.error(f"Firebase Sync Error (Student): {str(e)}")

    def delete_student(self, student_id):
        db = self.db
        if db is not None:
            try:
                db.collection('students').document(str(student_id)).delete()
                logger.info(f"Firebase Sync: Student {student_id} deleted.")
            except Exception as e:
                logger.error(f"Firebase Sync Error (Delete Student): {str(e)}")

    def log_attendance(self, student_id, name, date, time_str, status):
        db = self.db
        if db is not None:
            try:
                record_id = f"{date}_{student_id}"
                db.collection('attendance').document(record_id).set({
                    'date': str(date),
                    'time': str(time_str),
                    'student_id': str(student_id),
                    'name': str(name),
                    'status': str(status)
                })
                logger.info(f"Firebase Sync: Attendance marked for {student_id}.")
            except Exception as e:
                logger.error(f"Firebase Sync Error (Attendance): {str(e)}")
