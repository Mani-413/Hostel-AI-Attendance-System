import time
from services.excel_handler import ExcelHandler

try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False


# OPTIONAL: Fingerprint Integration
# Note: Requires a real Arduino connected to the PC via USB

class FingerprintMonitor:
    def __init__(self, port='COM3', baudrate=9600, db_manager=None):
        self.port = port
        self.baudrate = baudrate
        self.db = db_manager or ExcelHandler()
        self.running = False

    def start_monitoring(self):
        """Starts a loop to listen for Fingerprint ID from Serial."""
        try:
            ser = serial.Serial(self.port, self.baudrate, timeout=1)
            self.running = True
            print(f"[*] Started Serial Monitor on {self.port}...")
            
            while self.running:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()
                    if line.startswith("ID:"):
                        # Expected Serial format from Arduino: "ID:1001"
                        student_id = line.split(':')[1]
                        
                        # Fetch student name from Excel
                        students = self.db.get_all_students()
                        student_name = "Fingerprint User"
                        for s in students:
                            if str(s['Student ID']) == student_id:
                                student_name = s['Name']
                                break
                                
                        # Mark Attendance
                        from datetime import datetime
                        now = datetime.now()
                        status = "Present" if now.hour < 9 else "Late"
                        
                        marked, msg = self.db.mark_attendance(student_id, student_name, status)
                        print(f"[!] Fingerprint {student_id} recognized. Status: {status}. Msg: {msg}")
                        
                time.sleep(0.1)
        except Exception as e:
            print(f"[!] Serial Monitor Error (Check port/hardware): {e}")

if __name__ == "__main__":
    monitor = FingerprintMonitor()
    monitor.start_monitoring()
