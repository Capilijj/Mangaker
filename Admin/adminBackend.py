# === BACKEND NG COMICS PAGE ===

from datetime import datetime, timedelta
from users_db import current_session
from user_model import add_bookmark, remove_bookmark_db, get_bookmarks_by_email

# === STATIC MANGA LIST (existing content) ===
manga_list = [
    {"name": "Oshi no Ko", "chapter": 75, "genre": "Drama, Supernatural", "status": "Ongoing", "image": "image/oshi.webp"},
    {"name": "Green Green Greens", "chapter": 26, "genre": "Sports, Drama", "status": "Ongoing", "image": "image/greens.jfif"},
    {"name": "Wind Breaker", "chapter": 460, "genre": "Action, Sports", "status": "Ongoing", "image": "image/braker.jfif"},
    {"name": "Pokemon", "chapter": 150, "genre": "Adventure, Fantasy", "status": "Ongoing", "image": "image/pokemon.jfif"},
]

# === DYNAMICALLY ADDED NEW MANGA LIST ===
new_manga_list = [
    #sample new manga entries
     {"name": "The Days of Diamond", "chapter": "85", "genre": "Sports, Drama","status": "Ongoing","image": "image/Ace.jpg","release_date": datetime.now()},
]

# === Returns static manga list ===
def get_manga_list():
    return manga_list

# === Returns new manga list added via add_manga ===
def get_new_manga_list():
    return new_manga_list

# === Combine both static and new manga into one ===
def get_all_manga():
    """Returns all manga from both lists."""
    return manga_list + new_manga_list

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
