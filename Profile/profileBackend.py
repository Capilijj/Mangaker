from users_db import users_db, current_session

def get_user_prof():
    email = current_session.get("email")
    if email and email in users_db:
        return {
            "email": email,
            "username": users_db[email]["username"],
            "profile_image": users_db[email]["profile_image"]
        }
    return {
        "email": "unknown@gmail.com",
        "username": "Unknown User",
        "profile_image": None
    }

def save_user_prof(profile):
    email = current_session.get("email")
    if email and email in users_db:
        users_db[email].update(profile)
