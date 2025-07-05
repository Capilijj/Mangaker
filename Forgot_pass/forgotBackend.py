import smtplib
from email.message import EmailMessage
import os

def send_otp_email(email, otp):
    msg = EmailMessage()
    msg['Subject'] = "Your OTP Code"
    msg['From'] = "Mangaker Support <jamesmangaker@gmail.com>" 
    msg['To'] = email
    msg.set_content(f"Your OTP is: {otp}")

    # Kunin ang credentials mula sa environment variable o diretso dito
    sender_email = os.getenv("SENDER_EMAIL", "your_email@gmail.com")
    app_password = os.getenv("APP_PASSWORD", "your_app_password")

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send OTP email: {e}")
        return False