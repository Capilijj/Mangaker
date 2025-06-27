import sqlite3

DB_NAME = "user.db" # The name of your existing SQLite database file

def get_connection():
    """
    Establishes and returns a connection to the SQLite database.
    This function is now solely responsible for connecting.
    """
    return sqlite3.connect(DB_NAME)

def init_user_db():
    """
    This function will now only perform operations necessary for
    initializing a connection if the DB file exists, or ensuring
    basic PRAGMAs are set. It explicitly AVOIDS creating tables.
    """
    print(f"Attempting to initialize connection to {DB_NAME}...")
    try:
        with get_connection() as conn:
            # You might want to run some PRAGMA commands here if needed,
            # e.g., to ensure foreign key constraints are enforced.
            # For example:
            # cursor = conn.cursor()
            # cursor.execute("PRAGMA foreign_keys = ON;")
            # print("Foreign key enforcement enabled.")
            print(f"Successfully connected to existing database: {DB_NAME}")
    except sqlite3.Error as e:
        print(f"Error connecting to database {DB_NAME}: {e}")
        # Handle the error appropriately, maybe exit the app or show a message
    # No table creation SQL here anymore.
    # We assume tables 'users' and 'bookmarks' already exist in user.db

# --- Existing functions for user and bookmark operations (remain unchanged) ---

def get_next_available_user_id():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users ORDER BY id ASC")
        ids = [row[0] for row in cursor.fetchall()]
        expected_id = 1
        for actual_id in ids:
            if actual_id != expected_id:
                return expected_id
            expected_id += 1
        return expected_id

def add_user(email, username, password, image_path):
    try:
        user_id = get_next_available_user_id()
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (id, email, username, password, profile_image)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, email, username, password, image_path))
            conn.commit()
            return True, "User registered successfully!"
    except sqlite3.IntegrityError:
        return False, "Email or username already registered."
    except sqlite3.Error as e:
        return False, f"Database error: {e}"

def get_user_by_email(email):
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row  # This makes rows behave like dictionaries
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user_data = cursor.fetchone()
        return dict(user_data) if user_data else None

def get_user_by_username(username):
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user_data = cursor.fetchone()
        return dict(user_data) if user_data else None

def update_user_profile(email, updates):
    with get_connection() as conn:
        cursor = conn.cursor()
        set_clauses = []
        values = []
        for key, value in updates.items():
            set_clauses.append(f"{key} = ?")
            values.append(value)
        values.append(email)

        query = f"UPDATE users SET {', '.join(set_clauses)} WHERE email = ?"
        cursor.execute(query, tuple(values))
        conn.commit()
        return True, "Profile updated successfully!"

def get_next_available_bookmark_id():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM bookmarks ORDER BY id ASC")
        ids = [row[0] for row in cursor.fetchall()]
        expected_id = 1
        for actual_id in ids:
            if actual_id != expected_id:
                return expected_id
            expected_id += 1
        return expected_id

def add_bookmark(email, manga_title):
    try:
        next_id = get_next_available_bookmark_id()
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO bookmarks (id, email, manga_title)
                VALUES (?, ?, ?)
            ''', (next_id, email, manga_title))
            conn.commit()
            return True, "Manga bookmarked successfully!"
    except sqlite3.IntegrityError:
        return False, "Manga is already bookmarked."
    except sqlite3.Error as e:
        return False, f"Database error: {e}"


def remove_bookmark_db(email, manga_title):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM bookmarks
            WHERE email = ? AND manga_title = ?
        ''', (email, manga_title))
        conn.commit()
        return True

def get_bookmarks_by_email(email):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT manga_title FROM bookmarks
            WHERE email = ?
        ''', (email,))
        rows = cursor.fetchall()
        return [row[0] for row in rows]

def clear_bookmarks(email):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM bookmarks
            WHERE email = ?
        ''', (email,))
        conn.commit()
        return True