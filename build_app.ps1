# Build script for Hostel Attendance Desktop App (Windows)
# 
# Usage: Open PowerShell in this folder and run .\build_app.ps1

Write-Host "[*] Starting Desktop Build..." -ForegroundColor Cyan

# Install requirements
pip install pyinstaller pywebview flask flask-cors pandas openpyxl opencv-python numpy werkzeug

# Run PyInstaller
# --onefile : Create single exe
# --noconsole: Don't show terminal window
# --add-data: Include static/templates folders
# Note: For Windows, the separator is ; for --add-data
pyinstaller --noconsole `
            --onefile `
            --add-data "templates;templates" `
            --add-data "static;static" `
            --name "Hostel_Attendance_AI" `
            desktop_app.py

Write-Host "[+] Build Complete! Your app is in the 'dist' folder." -ForegroundColor Green
