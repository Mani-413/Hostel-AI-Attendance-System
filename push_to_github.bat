@echo off
echo [*] Starting GitHub Push Tool...
cd /d "c:\Users\MANIKANDAN\New folder (4)"

:: 1. Initialize and Add
echo [1] Preparing files...
git init
git add .

:: 2. Commit
echo [2] Committing changes...
git commit -m "Full AI Hostel Attendance Project Release - Mani-413"

:: 3. Remote Setup
echo [3] Setting up remote repository...
git remote remove origin 2>nul
git remote add origin https://github.com/Mani-413/Hostel-AI-Attendance-System.git
git branch -M main

:: 4. Push
echo [4] Pushing to GitHub (This will open a login window)...
git push -u origin main --force

echo.
echo [+] Done! Check your GitHub: https://github.com/Mani-413/Hostel-AI-Attendance-System
pause
