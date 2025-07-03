# === BACKEND NG COMICS PAGE ===

from datetime import datetime, timedelta
from users_db import current_session
from user_model import add_bookmark, remove_bookmark_db, get_bookmarks_by_email
import sqlite3

connection = sqlite3.connect('user.db')
cursor = connection.cursor()
cursor.execute("SELECT mangaId, title, latest, status, img_path, description, update_date FROM Manga")

manga_rows = cursor.fetchall()

all_manga = [] # List to store all manga data

for rows in manga_rows:
    manga_id, title, latest, status, img_path, description, update_date = rows
    cursor.execute("SELECT genre FROM Genres WHERE mangaId = ?", (manga_id,))
    genres = [g[0] for g in cursor.fetchall()]  # Fetching genres for each manga
    genre_str = ', '.join(genres)  # Combining genres into a single string

    all_manga.append({
        "mangaId": manga_id,
        "name": title,
        "chapter": latest,
        "genre": genre_str,
        "status": status,
        "image": img_path,
        "summary": description,
        "update_date": update_date
    })


# === Returns static manga list ===
def get_manga_list():
    return all_manga

# === Returns new manga list added via add_manga ===
def get_new_manga_list():
    return all_manga

# === Combine both static and new manga into one ===
def get_all_manga():
    """Returns all manga from both lists."""
    return all_manga
"""
# === Adds a new manga into new_manga_list with release date ===
def add_manga(manga_details):
    all_current_mangas = [m.get("name") for m in manga_list] + [m.get("name") for m in new_manga_list]
    if manga_details.get("name") in all_current_mangas:
        return False, "Manga with this name already exists."

    manga_details.setdefault("release_date", datetime.now())
    new_manga_list.append(manga_details)
    return True, "New manga added successfully!"

# === Filters newly added manga based on recent release dates ===
def get_new_releases_backend(days_ago=30, limit=None):
    threshold_date = datetime.now() - timedelta(days=days_ago)
    new_releases = [
        m for m in new_manga_list
        if isinstance(m.get("release_date"), datetime) and m["release_date"] >= threshold_date
    ]
    new_releases.sort(key=lambda x: x.get("release_date", datetime.min), reverse=True)
    return new_releases[:limit] if limit else new_releases
"""
# === Bookmarks a manga for the currently logged-in user ===
def bookmark_manga_admin(manga_to_bookmark):
    email = current_session.get("email")
    if not email:
        return "No user logged in."

    title = manga_to_bookmark.get("name")
    if not title:
        return "Manga title missing."

    existing = get_bookmarks_by_email(email)
    if title in existing:
        return "Manga already bookmarked."

    success, msg = add_bookmark(email, title)
    return msg

# === Removes a bookmarked manga for the current user ===
def remove_bookmark_admin(manga_to_remove):
    email = current_session.get("email")
    if not email:
        return "No user logged in."

    title = manga_to_remove.get("name")
    if not title:
        return "Manga title missing."

    removed = remove_bookmark_db(email, title)
    return "Bookmark removed successfully!" if removed else "Bookmark not found."