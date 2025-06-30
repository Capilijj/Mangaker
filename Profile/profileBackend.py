# profileBackend.py

# === Import current_session for session management ===
from users_db import current_session

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
#===== Dito mo kukunin yung data pre na ilalapag sa database request manga ====
#==================================================================================
# === Store manga requests temporarily in memory ===
_manga_request_buffer = []

def buffer_manga_request(request_text, email):
    """
    Temporarily holds the manga request in memory.
    This function should be replaced with a DB insert for production use.
    """
    if not request_text:
        return False, "Request is empty."

    if len(request_text) > 15:
        return False, "Request exceeds 15 characters."

    # ✅ Store the request with user email
    _manga_request_buffer.append({
        "email": email,
        "request_text": request_text
    })

    return True, "Manga request buffered (not yet saved to database)."

def get_buffered_requests():
    """
    Returns the current list of buffered manga requests (for preview or admin moderation).
    """
    return _manga_request_buffer
