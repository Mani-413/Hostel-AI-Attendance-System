import os
import time
import logging
import pandas as pd  # type: ignore
from services.firebase_service import FirebaseService  # type: ignore

class ExcelHandler:
    STUDENTS_FILE = "students.xlsx"
    ATTENDANCE_FILE = "attendance.xlsx"
    USERS_FILE = "users.xlsx"
    
    def __init__(self):
        self.logger = logging.getLogger("AppLogger")
        self.firebase = FirebaseService()
        self._initialize_files()

    def _safe_write(self, df, filename):
        if os.environ.get("VERCEL"):
            self.logger.info(f"Vercel Mode: Skipping write to {filename}")
            return True
            
        for attempt in range(5):
            try:
                df.to_excel(filename, index=False)
                return True
            except PermissionError:
                self.logger.warning(f"File locked: {filename}. Retrying {attempt+1}/5...")
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"Error writing to {filename}: {str(e)}")
                return False
        self.logger.error(f"Failed to write to {filename} after 5 attempts.")
        return False

    def _initialize_files(self):
        if not os.path.exists(self.USERS_FILE):
            df = pd.DataFrame([{"Username": "admin", "Password": "password123"}])
            self._safe_write(df, self.USERS_FILE)

        if not os.path.exists(self.STUDENTS_FILE):
            df = pd.DataFrame(columns=["Student ID", "Name", "Email", "Face_Encoding_Path"])
            self._safe_write(df, self.STUDENTS_FILE)
        else:
            try:
                df = pd.read_excel(self.STUDENTS_FILE)
                changed = False
                if 'Phone' in df.columns:
                    df.drop(columns=['Phone'], inplace=True)
                    changed = True
                if 'Email' not in df.columns:
                    df['Email'] = ''
                    changed = True
                if changed:
                    self._safe_write(df, self.STUDENTS_FILE)
            except Exception:
                pass
        
        if not os.path.exists(self.ATTENDANCE_FILE):
            df = pd.DataFrame(columns=["Date", "Student ID", "Name", "Time", "Status"])
            self._safe_write(df, self.ATTENDANCE_FILE)

    def get_all_students(self):
        try:
            return pd.read_excel(self.STUDENTS_FILE).to_dict('records')
        except Exception as e:
            self.logger.error(f"Error reading {self.STUDENTS_FILE}: {str(e)}")
            return []

    def add_student(self, student_id, name, email=""):
        student_id = str(student_id).split(".")[0].strip()
        df = pd.read_excel(self.STUDENTS_FILE)
        
        if not df.empty:
            df['Student ID'] = df['Student ID'].apply(lambda x: str(x).split('.')[0].strip())
        
        if student_id not in df['Student ID'].values:
            new_row = pd.DataFrame([{"Student ID": student_id, "Name": name, "Email": email}])
            df = pd.concat([df, new_row], ignore_index=True)
            if self._safe_write(df, self.STUDENTS_FILE):
                self.logger.info(f"Added Student {student_id}")
                self.firebase.sync_student(student_id, name, email)
                return True
        self.logger.info(f"Student {student_id} already exists")
        return False

    def delete_student(self, student_id):
        student_id = str(student_id).split(".")[0].strip()
        self.logger.info(f"Attempting to delete SID: {student_id}")
        
        try:
            df = pd.read_excel(self.STUDENTS_FILE)
            if not df.empty:
                df['Student ID'] = df['Student ID'].apply(lambda x: str(x).split(".")[0].strip())
                df = df[df['Student ID'] != student_id]
                if self._safe_write(df, self.STUDENTS_FILE):
                    self.firebase.delete_student(student_id)
        except Exception as e:
            self.logger.error(f"Error deleting from students: {str(e)}")

        try:
            df_att = pd.read_excel(self.ATTENDANCE_FILE)
            if not df_att.empty:
                df_att['Student ID'] = df_att['Student ID'].apply(lambda x: str(x).split(".")[0].strip())
                df_att = df_att[df_att['Student ID'] != student_id]
                self._safe_write(df_att, self.ATTENDANCE_FILE)
        except Exception as e:
            self.logger.error(f"Error deleting from attendance: {str(e)}")
            
        return True

    def verify_user(self, username, password):
        try:
            df = pd.read_excel(self.USERS_FILE)
            match = df[(df['Username'] == str(username)) & (df['Password'] == str(password))]
            return not match.empty
        except Exception as e:
            self.logger.error(f"Error verifying user: {str(e)}")
            return False

    def update_attendance_status(self, student_id, date, new_status):
        student_id = str(student_id).split(".")[0].strip()
        date = str(date)
        try:
            df = pd.read_excel(self.ATTENDANCE_FILE)
            if not df.empty:
                df['Student ID'] = df['Student ID'].apply(lambda x: str(x).split(".")[0].strip())
                df['Date'] = df['Date'].astype(str)
                mask = (df['Date'] == date) & (df['Student ID'] == student_id)
                if len(df[mask]) > 0:
                    df.loc[mask, 'Status'] = new_status
                    if self._safe_write(df, self.ATTENDANCE_FILE):
                        self.logger.info(f"Updated attendance for {student_id} to {new_status}")
                        return True
            return False
        except Exception as e:
            self.logger.error(f"Error manual updating: {str(e)}")
            return False

    def mark_attendance(self, student_id, name, status="Present"):
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        now_time = datetime.now().strftime("%H:%M:%S")
        student_id = str(student_id).split(".")[0].strip()
        
        try:
            df = pd.read_excel(self.ATTENDANCE_FILE)
            if not df.empty:
                df['Student ID'] = df['Student ID'].apply(lambda x: str(x).split(".")[0].strip())
            
            is_marked = len(df[(df['Date'] == str(today)) & (df['Student ID'] == student_id)]) > 0
            
            if not is_marked:
                new_record = pd.DataFrame([{
                    "Date": today,
                    "Student ID": student_id,
                    "Name": name,
                    "Time": now_time,
                    "Status": status
                }])
                df = pd.concat([df, new_record], ignore_index=True)
                if self._safe_write(df, self.ATTENDANCE_FILE):
                    self.logger.info(f"Marked attendance {status} for {student_id}")
                    self.firebase.log_attendance(student_id, name, today, now_time, status)
                    return True, f"Attendance marked as {status}"
                return False, "Failed to write attendance"
            return False, "Already marked today"
        except Exception as e:
            self.logger.error(f"Error marking attendance: {str(e)}")
            return False, str(e)

    def get_today_attendance(self):
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        try:
            df = pd.read_excel(self.ATTENDANCE_FILE)
            if df.empty: return []
            df['Date'] = df['Date'].astype(str)
            today_df = df[df['Date'] == today]
            # convert NaNs to None for JSON serializability
            today_df = today_df.where(pd.notnull(today_df), None)
            return today_df.to_dict('records')
        except Exception as e:
            self.logger.error(f"Error reading today's attendance: {str(e)}")
            return []

    def get_all_attendance(self):
        try:
            df = pd.read_excel(self.ATTENDANCE_FILE)
            df = df.where(pd.notnull(df), None)
            return df.to_dict('records')
        except Exception:
            return []
