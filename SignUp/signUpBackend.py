from user_model import add_user, get_user_by_email, get_user_by_username
from users_db import current_session
import hashlib
import smtplib
import os
from dotenv import load_dotenv  # ✅ import this

# ✅ Load environment variables
load_dotenv()

# ✅ Fetch from environment
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")

# --- Validation logic (no changes needed here) ---
def validate_user_data(email, username, password, confirm_password, image_path=None):
    if not email or not username or not password or not confirm_password:
        return False, "Please fill in all fields."
    if not image_path:
        return False, "Please upload a profile photo."
    if not (6 <= len(password) <= 15):
        return False, "Password must be 15 char/num."
    if not email.endswith("@gmail.com"):
        return False, "Please use a Valid Gmail address."
    if password != confirm_password:
        return False, "Passwords do not match."
    if get_user_by_email(email):
        return False, "Email already registered."
    if get_user_by_username(username):
        return False, "Username already taken."
    return True, "Validated"

# --- Finalize registration ---
def finalize_registration(email, username, password, image_path):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    success, message = add_user(email, username, hashed_password, image_path)
    if success:
        current_session["email"] = email
    return success, message

# --- Send OTP ---
def send_otp_email(email, otp):
    try:
        if not SENDER_EMAIL or not APP_PASSWORD:
            raise ValueError("Missing email credentials in .env")

        subject = "Your OTP Verification Code"
        body = (
            "Welcome to James Mangaker!\n\n"
            "Thank you for signing up.\n\n"
            f"Your OTP is: {otp}\n\n"
            "This OTP is valid for 5 minutes."
        )
        msg = f"Subject: {subject}\n\n{body}"

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, email, msg)
        server.quit()
        return True
    except Exception as e:
        print("Failed to send OTP email:", e)
        return False