import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger("AppLogger")

# ==========================================
# ⚠️ GMAIL SMTP CONFIGURATION ⚠️
# 1. Use a standard Gmail account.
# 2. Go to Google Account -> Security -> 2-Step Verification (Turn it ON)
# 3. Search for "App Passwords" in your Google Account settings and generate one for "Mail".
# 4. Paste your Email and the generated 16-character App Password below:
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_16_char_app_password"
# ==========================================

def send_email(recipient_email, subject, message_text):
    recipient_email = str(recipient_email).strip()
    
    if not recipient_email or recipient_email.lower() == 'nan' or '@' not in recipient_email:
        logger.warning(f"Invalid email '{recipient_email}'. Email skipped.")
        return False
        
    logger.info(f"Preparing Email to {recipient_email}: {subject}")
    
    # If key is not configured, we simulate it in the console!
    if SENDER_EMAIL == "your_email@gmail.com":
        logger.warning("Gmail SMTP not configured! Simulating Email delivery instead.")
        print(f"\n[📧 MOCK EMAIL SIMULATION]\nTo: {recipient_email}\nSubject: {subject}\nMessage: {message_text}\n-----------------------\n")
        return True
        
    try:
        msg = MIMEMultipart()
        msg['From'] = f"HostelAI System <{SENDER_EMAIL}>"
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(message_text, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, msg['To'], text)
        server.quit()
        
        logger.info(f"Email sent successfully to {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"Error sending Email: {str(e)}")
        return False
