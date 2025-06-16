from users_db import users_db, current_session

def authenticate(email, password):
    if not email:
        return False, "Please enter your email."
    if not password:
        return False, "Please enter your password."
    if email not in users_db:
        return False, "Email not registered."
    if users_db[email]["password"] != password:
        return False, "Incorrect password."

    current_session["email"] = email
    return True, "Login successful."

from users_db import users_db, current_session

def get_user_prof():
    email = current_session.get("email")
    if email in users_db:
        return {
            "username": users_db[email].get("username", "Unknown User"),
            "email": email,
            "profile_image": users_db[email].get("profile_image", None)
        }
    return {
        "username": "Unknown User",
        "email": "unknown@gmail.com",
        "profile_image": None
    }

