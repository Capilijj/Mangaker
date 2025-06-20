from users_db import users_db, current_session

def authenticate(email, password):
    #=========================================================================================
    #                                 User Authentication Logic                              =
    #=========================================================================================
    # ---- Check if email field is empty ----
    if not email:
        return False, "Please enter your email."
    # ---- Check if password field is empty ----
    if not password:
        return False, "Please enter your password."
    # ---- Check if email is registered in the database ----
    if email not in users_db:
        return False, "Email not registered."
    # ---- Verify if the provided password matches the registered password ----
    if users_db[email]["password"] != password:
        return False, "Incorrect password."

    # ---- Set the current session email upon successful login ----
    current_session["email"] = email
    return True, "Login successful."

def get_user_prof():
    #=========================================================================================
    #                                 Retrieve User Profile Information                     =
    #=========================================================================================
    email = current_session.get("email") # ---- Get the email from the current session ----
    if email in users_db:
        # ---- Return user's username, email, and profile image if found ----
        return {
            "username": users_db[email].get("username", "Unknown User"),
            "email": email,
            "profile_image": users_db[email].get("profile_image", None)
        }
    # ---- Return default values if user email is not in session or not found in db ----
    return {
        "username": "Unknown User",
        "email": "unknown@gmail.com",
        "profile_image": None
    }