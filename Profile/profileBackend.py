# profileBackend.py

# Import ang current_session mula sa users_db (para sa session management)
from users_db import current_session
# Import ang mga functions na nakikipag-ugnayan sa SQLite database
from user_model import get_user_by_email, update_user_profile

def get_user_prof():
    """
    Kinukuha ang profile information ng kasalukuyang naka-login na user mula sa database.
    """
    email = current_session.get("email")
    if not email:
        # Return default values if no user is logged in
        return {
            "email": "unknown@gmail.com",
            "username": "Unknown User",
            "profile_image": None
        }

    # Kumuha ng user data mula sa SQLite database
    user = get_user_by_email(email)
    if user:
        # Ibalik ang user data mula sa database
        return {
            "email": user["email"],
            "username": user["username"],
            "profile_image": user["profile_image"]
        }

    # Fallback if user is not found in DB despite session
    return {
        "email": "unknown@gmail.com",
        "username": "Unknown User",
        "profile_image": None
    }

def save_user_prof(profile):
    """
    Ini-save ang mga pagbabago sa profile ng kasalukuyang naka-login na user sa database.
    Ang 'profile' ay isang dictionary (e.g., {"username": "new_name", "profile_image": "new/path.png"}).
    """
    email = current_session.get("email")
    if not email:
        return False, "No user logged in."

    # I-update ang user profile sa SQLite database
    return update_user_profile(email, profile)