import re

# Simple in-memory user storage
users_db = {}

def is_valid_email(email):
  # Basic email format check with regex
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def authenticate(email, password):
    if email not in users_db:
        return False, "Email not registered."
    if users_db[email]["password"] != password:
        return False, "Incorrect password."
    return True, "Login successful."

def register_user(email, username, password):
    if email in users_db:
        return False, "Email already registered."
    if not is_valid_email(email):
        return False, "Invalid email format."
    # Save user info in dictionary
    users_db[email] = {
        "username": username,
        "password": password
    }
    return True, "Registration successful."
