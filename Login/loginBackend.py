from user_model import get_user_by_email, CURRENT_USER
from users_db import current_session
import hashlib

def authenticate(email, password):
    if not email:
        return False, "Please enter your email."
    if not password:
        return False, "Please enter your password."

    user = get_user_by_email(email)
    if not user:
        return False, "Email not registered."
    # Hash the entered password for comparison
    hashed_input = hashlib.sha256(password.encode()).hexdigest()
    if user["password"] != hashed_input:
        return False, "Incorrect password."

    current_session["email"] = email

    # Set CURRENT_USER for the rest of the app
    CURRENT_USER["username"] = user["username"]
    CURRENT_USER["email"] = user["email"]
    CURRENT_USER["role"] = user.get("role", "user")
    CURRENT_USER["profile_image"] = user.get("profile_image", None)

    return True, "Login successful."

def get_user_prof():
    email = current_session.get("email")
    user = get_user_by_email(email) if email else None

    if user:
        return {
            "username": user["username"],
            "email": user["email"],
            "profile_image": user["profile_image"]
        }

    return {
        "username": "Unknown User",
        "email": "unknown@gmail.com",
        "profile_image": None
    }