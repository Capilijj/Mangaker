from users_db import users_db, current_session

def register_user(email, username, password, confirm_password, image_path=None):
    if not email or not username or not password or not confirm_password:
        return False, "Please fill in all fields."

    if not image_path:
        return False, "Please upload a profile photo."

    if not email.endswith("@gmail.com"):
        return False, "Email must be a Gmail address (ending with @gmail.com)."

    if password != confirm_password:
        return False, "Passwords do not match."

    if email in users_db:
        return False, "Email already registered."

    users_db[email] = {
        "username": username,
        "password": password,
        "profile_image": image_path,
        "bookmarks": []
    }

    # Optional: auto-login after signup
    current_session["email"] = email

    return True, "Account created successfully!"
