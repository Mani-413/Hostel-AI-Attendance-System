import threading
import time
import webview  # type: ignore
from app import app  # type: ignore

def run_flask():
    # Run flask in a separate thread
    # We use a non-reloader mode because we are inside a GUI app
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    # 1. Start Flask thread
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

    # 2. Wait for server to start
    time.sleep(2)

    # 3. Open PyWebView window
    # You can customize title, icon, and window size here
    webview.create_window(
        'Hostel Attendance System AI',
        'http://127.0.0.1:5000',
        width=1200,
        height=800,
        resizable=True,
        min_size=(800, 600)
    )
    webview.start()
