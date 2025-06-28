import sqlite3
from datetime import datetime, timedelta
DB_NAME = "user.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_user_db():
    print(f"Attempting to initialize or setup {DB_NAME}...")
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            # Enable foreign key support
            cursor.execute("PRAGMA foreign_keys = ON;")

            # Check if 'created_at' column exists
            cursor.execute("PRAGMA table_info(users);")
            columns = [row[1] for row in cursor.fetchall()]

            if "created_at" not in columns:
                # Add column without default, then update existing rows manually
                cursor.execute("ALTER TABLE users ADD COLUMN created_at DATETIME")
                cursor.execute("UPDATE users SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")

            # Create tables if not exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    profile_image TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bookmarks (
                    id INTEGER PRIMARY KEY,
                    email TEXT NOT NULL,
                    manga_title TEXT NOT NULL,
                    UNIQUE(email, manga_title)
                )
            ''')

            conn.commit()
            print(f" Database {DB_NAME} initialized successfully with required tables.")

    except sqlite3.Error as e:
        print(f" Error initializing database {DB_NAME}: {e}")

# --- USER OPERATIONS ---

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

        # Get Philippine time (UTC+8)
        ph_time = datetime.utcnow() + timedelta(hours=8)
        ph_timestamp = ph_time.strftime('%Y-%m-%d %H:%M:%S')

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (id, email, username, password, profile_image, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, email, username, password, image_path, ph_timestamp))
            conn.commit()
            return True, "User registered successfully!"
    except sqlite3.IntegrityError:
        return False, "Email or username already registered."
    except sqlite3.Error as e:
        return False, f"Database error: {e}"


def get_user_by_email(email):
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
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

# --- BOOKMARK OPERATIONS ---

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

            next_id = get_next_available_bookmark_id()
            cursor.execute('''
                INSERT INTO bookmarks (id, email, manga_title)
                VALUES (?, ?, ?)
            ''', (next_id, email, manga_title))
            conn.commit()
            return True, "Manga bookmarked successfully!"
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

def get_all_bookmarks_grouped_by_email():
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


