import sqlite3
from datetime import datetime, timedelta
import hashlib # For password hashing
import os # To check for database file existence

DB_NAME = "user.db"

# Global variable to store the current logged-in user's information
CURRENT_USER = {"username": None, "email": None, "role": None, "profile_image": None}

def get_connection():
    """Establishes a connection to the SQLite database."""
    return sqlite3.connect(DB_NAME)

def init_user_db():
    """
    Initializes the user database, creating tables if they don't exist
    and ensuring the 'role' column is present in the 'users' table.
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            # Enable foreign key support
            cursor.execute("PRAGMA foreign_keys = ON;")

            # Create users table if not exists with 'role' column
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, -- AUTOINCREMENT for easier ID management
                    email TEXT UNIQUE NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    profile_image TEXT,
                    role TEXT DEFAULT 'user' NOT NULL, -- New 'role' column with default 'user'
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Check if 'role' column exists, add if not
            cursor.execute("PRAGMA table_info(users);")
            columns = [row[1] for row in cursor.fetchall()]
            if "role" not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user' NOT NULL")
                print("Added 'role' column to 'users' table.")
            
            # Check if 'created_at' column exists (from your original code)
            if "created_at" not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
                cursor.execute("UPDATE users SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
                print("Added 'created_at' column to 'users' table.")

            # Create bookmarks table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bookmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    manga_title TEXT NOT NULL,
                    UNIQUE(email, manga_title),
                    FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
                )
            ''')
            
            conn.commit()
            # print(f" Database {DB_NAME} initialized successfully with required tables.") # Removed

            # ANG SEKSIYON NA NAGDADAGDAG NG DEFAULT ADMIN USER AY INALIS DITO.
            # Kung kailangan mo ng admin account, siguraduhin na manual mo itong idadagdag (sa pamamagitan ng sign-up page)
            # o sa ibang paraan.

    except sqlite3.Error as e:
        print(f" Error initializing database {DB_NAME}: {e}")

# --- USER OPERATIONS ---

def hash_password(password):
    """Hashes a password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(email, username, password, image_path, role='user'):
    """
    Adds a new user to the database.
    Passwors are hashed before storing.
    Default role is 'user'.
    """
    try:
        hashed_password = hash_password(password)
        
        # Get Philippine time (UTC+8)
        ph_time = datetime.utcnow() + timedelta(hours=8)
        ph_timestamp = ph_time.strftime('%Y-%m-%d %H:%M:%S')

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (email, username, password, profile_image, role, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (email, username, hashed_password, image_path, role, ph_timestamp))
            conn.commit()
            return True, "User registered successfully!"
    except sqlite3.IntegrityError:
        return False, "Email or username already registered."
    except sqlite3.Error as e:
        return False, f"Database error: {e}"

def authenticate_user(username, password):
    """
    Authenticates a user against the database.
    If successful, sets the CURRENT_USER global variable.
    """
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row # Allows accessing columns by name
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user_data = cursor.fetchone()

        if user_data:
            hashed_password = hash_password(password)
            if user_data["password"] == hashed_password:
                # Set the global CURRENT_USER
                CURRENT_USER["username"] = user_data["username"]
                CURRENT_USER["email"] = user_data["email"]
                CURRENT_USER["role"] = user_data["role"]
                CURRENT_USER["profile_image"] = user_data["profile_image"]
                return True
        return False

def get_user_by_email(email):
    """Retrieves user data by email."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user_data = cursor.fetchone()
        return dict(user_data) if user_data else None

def get_user_by_username(username):
    """Retrieves user data by username."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user_data = cursor.fetchone()
        return dict(user_data) if user_data else None

def update_user_profile(email, updates):
    """Updates a user's profile information."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            set_clauses = []
            values = []
            for key, value in updates.items():
                if key == "password": # Hash password if it's being updated
                    value = hash_password(value)
                set_clauses.append(f"{key} = ?")
                values.append(value)
            values.append(email)

            query = f"UPDATE users SET {', '.join(set_clauses)} WHERE email = ?"
            cursor.execute(query, tuple(values))
            conn.commit()
            
            # Update CURRENT_USER if the logged-in user's profile is updated
            if CURRENT_USER["email"] == email:
                for key, value in updates.items():
                    if key in CURRENT_USER:
                        CURRENT_USER[key] = value

            return True, "Profile updated successfully!"
    except sqlite3.Error as e:
        return False, f"Database error: {e}"

def update_user_password(email, new_password):
    """Updates a user's password."""
    return update_user_profile(email, {"password": new_password})
    
def user_exists(email):
    """Checks if a user with the given email exists."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()
        return result is not None

def get_current_user_role():
    """Returns the role of the currently logged-in user."""
    return CURRENT_USER["role"]

def get_current_username():
    """Returns the username of the currently logged-in user."""
    return CURRENT_USER["username"]

def get_current_user_email():
    """Returns the email of the currently logged-in user."""
    return CURRENT_USER["email"]

def clear_current_user():
    """Clears the current user's session."""
    CURRENT_USER["username"] = None
    CURRENT_USER["email"] = None
    CURRENT_USER["role"] = None
    CURRENT_USER["profile_image"] = None

def get_user_prof():
    """
    Returns the profile information for the current user from the global CURRENT_USER.
    This avoids direct DB query for every profile icon refresh.
    """
    if CURRENT_USER["username"]:
        return {
            "username": CURRENT_USER["username"],
            "email": CURRENT_USER["email"],
            "role": CURRENT_USER["role"],
            "profile_image": CURRENT_USER["profile_image"]
        }
    return {"profile_image": "image/default_profile.png"} # Default if no user logged in

# --- BOOKMARK OPERATIONS ---

def add_bookmark(email, manga_title):
    """Adds a manga to a user's bookmarks."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM bookmarks WHERE email = ?", (email,))
            count = cursor.fetchone()[0]
            if count >= 50:
                return False, "Bookmark limit reached (max 50)."

            # Check if already exists
            cursor.execute("SELECT 1 FROM bookmarks WHERE email = ? AND manga_title = ?", (email, manga_title))
            if cursor.fetchone():
                return False, "Manga is already bookmarked."

            cursor.execute('''
                INSERT INTO bookmarks (email, manga_title)
                VALUES (?, ?)
            ''', (email, manga_title))
            conn.commit()
            return True, "Manga bookmarked successfully!"
    except sqlite3.Error as e:
        return False, f"Database error: {e}"

def remove_bookmark_db(email, manga_title):
    """Removes a manga from a user's bookmarks."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM bookmarks
            WHERE email = ? AND manga_title = ?
        ''', (email, manga_title))
        conn.commit()
        return True

def get_bookmarks_by_email(email):
    """Retrieves all bookmarks for a given email."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT manga_title FROM bookmarks
            WHERE email = ?
            ORDER BY LOWER(manga_title) ASC
        ''', (email,))
        rows = cursor.fetchall()
        return [row[0] for row in rows]

def clear_bookmarks(email):
    """Clears all bookmarks for a given email."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM bookmarks
            WHERE email = ?
        ''', (email,))
        conn.commit()
        return True

def get_all_bookmarks_grouped_by_email():
    """Retrieves all bookmarks, grouped by email."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT email, GROUP_CONCAT(manga_title, ', ') as bookmarks
            FROM bookmarks
            GROUP BY email
        ''')
        rows = cursor.fetchall()

        grouped = {}
        for email, bookmark_string in rows:
            bookmarks = bookmark_string.split(', ') if bookmark_string else []
            grouped[email] = bookmarks

        return grouped