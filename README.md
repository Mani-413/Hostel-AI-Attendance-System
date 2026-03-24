# 🏤 AI-Based Hostel Attendance Management System (HostelAI)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask-lightgrey.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Face-Recognition](https://img.shields.io/badge/AI-Face--Recognition-orange.svg)](https://github.com/ageitgey/face_recognition)

A state-of-the-art, **Excel-powered** AI attendance system designed for hostels and institutions. This project replaces traditional manual registers with real-time face detection, a premium glassmorphic dashboard, and smart mobile integration.

---

## 🌟 Key Features

### 💻 Smart Recognition & Logic
- **Real-Time Face Scan**: Powered by Dlib and OpenCV for high-accuracy matching.
- **Automated Late Logic**: Smart detection (e.g., "Present" before 9:00 AM, "Late" after).
- **Duplicate Prevention**: Intelligently prevents double-marking for the same student in a day.
- **Hardware Agnostic**: Integrated support for R307/R305 Fingerprint sensors via Serial Monitor.

### 📊 Modern Dashboard
- **Glassmorphism Design**: A premium, dark-themed UI with translucent cards and smooth animations.
- **AJAX Live Update**: Real-time logs and statistics (Present/Late counts) update automatically every 2 seconds.
- **Student CRM**: Manage student profiles, email IDs, and image datasets directly from the browser.

### 📱 Mobile & Desktop Versatility
- **PWA (Progressive Web App)**: Install it on any Android or iOS device as a standalone app.
- **Easy Connect (QR Code)**: Dynamically generated QR code on the dashboard for instant mobile connection.
- **Desktop Launcher**: Includes a dedicated `desktop_app.py` wrapper for a native Windows window experience.

### 📁 Zero Database Architecture
- No MySQL, MongoDB, or SQL required!
- **Excel Storage**: All master records and attendance logs are managed via elegantly structured `.xlsx` files.

---

## 🚀 Quick Start

### 1. Prerequisites
Ensure you have Python 3.8+ installed.

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/Mani-413/Hostel-AI-Attendance-System.git
cd Hostel-AI-Attendance-System

# Install dependencies
pip install -r requirements.txt
```
*Note: Face-recognition requires Visual Studio C++ Build Tools on Windows.*

### 3. Running the System
Choose your preferred mode:

- **Web Mode**: `python app.py` (Access via browser at `http://localhost:5000`)
- **Desktop Mode**: `python desktop_app.py` (Launches as a standalone window)
- **Mobile Mode**: Scan the QR code on the dashboard while the server is running.

---

## 🛠️ Tech Stack & Architecture

- **Backend**: Python, Flask, Flask-CORS
- **AI Core**: Face-Recognition (dlib), OpenCV
- **Data Layer**: Pandas, OpenPyXL (Excel-based)
- **Frontend**: TailwindCSS, Phosphor Icons, Glassmorphism UI
- **Deployment**: Localtunnel (Remote access), PyWebView (Desktop), PWA (Mobile)

---

## 📂 Folder Structure
```text
├── dataset/             # Student face images (SID.jpg)
├── services/            # Core logic (Excel, AI, Firebase, Email)
│   ├── excel_handler.py     # Master Data Logic
│   └── face_recognition.py  # Recognition Service
├── static/              # CSS, JS, QR Codes, PWA Manifest
├── templates/           # HTML Templates (Tailwind & Jinja2)
├── app.py               # Main Flask Server
├── desktop_app.py       # Desktop App Wrapper
└── build_app.ps1        # PowerShell script to build .EXE
```

---

## 🛡️ License
Distrubuted under the MIT License. See `LICENSE` for more information.

## 🤝 Contributing
Contributions are welcome! Please fork the repo and submit a pull request.

---

**Developed with ❤️ by [Mani-413](https://github.com/Mani-413)**
