from user_model import add_user, get_user_by_email, get_user_by_username
from users_db import current_session
import hashlib
import smtplib

# === Email credentials now in backend ===
SENDER_EMAIL = "justinecapili92@gmail.com"
APP_PASSWORD = "cwua dtpq cfns eehf"

# ✅ Step 1: Validation only (no save yet)
def validate_user_data(email, username, password, confirm_password, image_path=None):
    if not email or not username or not password or not confirm_password:
        return False, "Please fill in all fields."
    if not image_path:
        return False, "Please upload a profile photo."
    if not (6 <= len(password) <= 8):
        return False, "Password must be 6 char/num."
    if not email.endswith("@gmail.com"):
        return False, "Please use a Valid Gmail address."
    if password != confirm_password:
        return False, "Passwords do not match."
    if get_user_by_email(email):
        return False, "Email already registered."
    if get_user_by_username(username):
        return False, "Username already taken."
    return True, "Validated"

# ✅ Step 2: Save user after OTP is verified
def finalize_registration(email, username, password, image_path):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    success, message = add_user(email, username, hashed_password, image_path)
    if success:
        current_session["email"] = email
    return success, message

# ✅ Send OTP Email

def send_otp_email(email, otp):
    try:
        subject = "Your OTP Verification Code"
        body = f"Your OTP is: {otp}\n\nThis OTP is valid for 5 minutes."
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
