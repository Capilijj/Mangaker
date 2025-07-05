# profileBackend.py

# === Import current_session for session management ===
from users_db import current_session
import sqlite3

# === Import database-related functions ===
from user_model import get_user_by_email, update_user_profile

def get_user_prof():
    """
    Retrieves the profile information of the currently logged-in user from the database.
    """
    email = current_session.get("email")
    if not email:
        # Return default values if no one is logged in
        return {
            "email": "unknown@gmail.com",
            "username": "Unknown User",
            "profile_image": None
        }

    # Fetch user data from the database using the email
    user = get_user_by_email(email)
    if user:
        # Update current session to keep values fresh
        current_session.update({
            "email": user["email"],
            "username": user["username"],
            "user_id": user["id"],
            "profile_image": user["profile_image"],
            "created_at": user.get("created_at")
        })
        return {
            "email": user["email"],
            "username": user["username"],
            "profile_image": user["profile_image"]
        }

    # Fallback if user not found in the database
    return {
        "email": "unknown@gmail.com",
        "username": "Unknown User",
        "profile_image": None
    }

def save_user_prof(profile):
    """
    Saves changes to the currently logged-in user's profile to the database.
    The 'profile' parameter is a dictionary of fields to update, such as:
    {"username": "new_name", "profile_image": "new/path.png"}
    """
    old_email = current_session.get("email")
    if not old_email:
        return False, "No user logged in."

    # Update user profile in the database
    success, message = update_user_profile(old_email, profile)

    # If successful and email was changed, refresh session data
    if success:
        new_email = profile.get("email", old_email)
        updated_user = get_user_by_email(new_email)
        if updated_user:
            current_session.update({
                "email": updated_user["email"],
                "username": updated_user["username"],
                "user_id": updated_user["id"],
                "profile_image": updated_user["profile_image"],
                "created_at": updated_user.get("created_at")
            })

    return success, message
#=====================================================================================
#===== Dito  kukunin yung data na ilalapag sa database request manga ====
#==================================================================================

def add_manga_request(request_text):

    #  Store the request with user email
    connection = sqlite3.connect('user.db')
    cursor = connection.cursor()

    cursor.execute("INSERT INTO Requests (userId, request_title) VALUES (?, ?)", (current_session["user_id"], request_text))
    
    connection.commit()
    connection.close()

    return True, "Manga has now been request to admin."
