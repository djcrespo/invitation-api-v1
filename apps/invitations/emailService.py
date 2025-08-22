import smtplib
from email.message import EmailMessage
import os

def send_email(text):
    msg = EmailMessage()
    msg.set_content(text)
    msg['Subject'] = 'Nueva confirmación!'
    msg['From'] = os.getenv('SMTP_USER')
    msg['To'] = os.getenv('EMAIL_TO')

    try:
        with smtplib.SMTP(os.getenv('SMTP_SERVER'), os.getenv('SMTP_PORT')) as server:
            server.starttls()
            server.login(os.getenv('SMTP_USER'), os.getenv('SMTP_PASSWORD'))
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
    