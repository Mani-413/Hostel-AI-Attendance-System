import pandas as pd
from datetime import datetime, timedelta
import random

# DEMO POPULATOR
STUDENTS_FILE = "students.xlsx"
ATTENDANCE_FILE = "attendance.xlsx"

# 1. Populate Students
students = [
    {"Student ID": "1001", "Name": "Manikandan S"},
    {"Student ID": "1002", "Name": "Arun Kumar"},
    {"Student ID": "1003", "Name": "Priya Darshini"},
    {"Student ID": "1004", "Name": "Sanjay Ram"},
    {"Student ID": "1005", "Name": "Divya Krishnan"}
]
pd.DataFrame(students).to_excel(STUDENTS_FILE, index=False)
print("[+] Students populated")

# 2. Populate Attendance (last few days + today)
attendance = []
today = datetime.now()

for i in range(5): # last 5 days
    day = (today - timedelta(days=i)).strftime("%Y-%m-%d")
    for s in students:
        # 80% chance of being present
        if random.random() < 0.8:
            # random time between 8am and 10am
            h = random.choice([8, 9])
            m = random.randint(0, 59)
            time_str = f"{h:02d}:{m:02d}:00"
            status = "Present" if h == 8 else "Late"
            
            attendance.append({
                "Date": day,
                "Student ID": s["Student ID"],
                "Name": s["Name"],
                "Time": time_str,
                "Status": status
            })

pd.DataFrame(attendance).to_excel(ATTENDANCE_FILE, index=False)
print("[+] Attendance logs populated")
