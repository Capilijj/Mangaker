#=========================================================
# This file handles the backend logic for user registration.
#=========================================================

from users_db import users_db, current_session

def register_user(email, username, password, confirm_password, image_path=None):
    #=========================================================================================
    #                                 User Registration Logic                                =
    #=========================================================================================
    # ---- Check if all required fields are filled ----
    if not email or not username or not password or not confirm_password:
        return False, "Please fill in all fields."

    # ---- Ensure a profile photo is uploaded ----
    if not image_path:
        return False, "Please upload a profile photo."

    # ---- Validate if the email is a Gmail address ----
    if not email.endswith("@gmail.com"):
        return False, "Email must be a Gmail address (ending with @gmail.com)."

    # ---- Check if passwords match ----
    if password != confirm_password:
        return False, "Passwords do not match."

    # ---- Check if the email is already registered ----
    if email in users_db:
        return False, "Email already registered."

    # ---- Store new user information in the database (users_db acts as an in-memory db) ----
    users_db[email] = {
        "username": username,
        "password": password,
        "profile_image": image_path,
        "bookmarks": [] # ---- Initialize an empty list for user bookmarks ----
    }

    # ---- Optional: Automatically log in the user after successful signup ----
    current_session["email"] = email

    return True, "Account created successfully!"