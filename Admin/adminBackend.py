# << BACKEND NG COMICS PAGE >>

from datetime import datetime, timedelta
from users_db import current_session  # still used to get current email
from user_model import get_user_by_email, update_user_profile  # <-- Import the DB helper functions

manga_list = [
    {"name": "Oshi no Ko", "chapter": 75, "genre": "Drama, Supernatural", "status": "Ongoing", "image": "image/oshi.webp"},
    {"name": "Solo Leveling", "chapter": 179, "genre": "Action, Fantasy", "status": "Completed", "image": "image/solo.jpg"},
    {"name": "Wind Breaker", "chapter": 460, "genre": "Action, Sports", "status": "Ongoing", "image": "image/braker.jfif"},
    {"name": "Pokemon", "chapter": 150, "genre": "Adventure, Fantasy", "status": "Ongoing", "image": "image/pokemon.jfif"},
]

new_manga_list = [
    # Example new release:
    # {"name": "Green Green Greens", "chapter": 26, "genre": "Sports, Drama", "status": "Ongoing", "image": "image/greens.jfif", "release_date": datetime.now()},
]

def get_manga_list():
    return manga_list

def add_manga(manga_details):
    all_current_mangas = [m.get("name") for m in manga_list] + [m.get("name") for m in new_manga_list]
    if manga_details.get("name") in all_current_mangas:
        return False, "Manga with this name already exists."

    manga_details.setdefault("release_date", datetime.now())
    new_manga_list.append(manga_details)
    return True, "New manga added successfully!"

def get_new_releases_backend(days_ago=30, limit=None):
    threshold_date = datetime.now() - timedelta(days=days_ago)
    new_releases = [
        m for m in new_manga_list
        if isinstance(m.get("release_date"), datetime) and m["release_date"] >= threshold_date
    ]
    new_releases.sort(key=lambda x: x.get("release_date", datetime.min), reverse=True)
    return new_releases[:limit] if limit else new_releases

def bookmark_manga_admin(manga_to_bookmark):
    email = current_session.get("email")
    if not email:
        return "No user logged in."

    user = get_user_by_email(email)
    if not user:
        return "User not found."

    user_bookmarks = user.get("bookmarks", [])

    converted_manga = {
        "title": manga_to_bookmark.get("name"),
        "genre": manga_to_bookmark.get("genre"),
        "summary": "N/A",
        "status": manga_to_bookmark.get("status"),
        "author": "N/A",
        "image_path": manga_to_bookmark.get("image"),
        "chapter": manga_to_bookmark.get("chapter")
    }

    if any(bm.get("title") == converted_manga["title"] for bm in user_bookmarks):
        return "Manga already bookmarked."

    if len(user_bookmarks) >= 50:
        return "You have reached the maximum of 50 bookmarks."

    user_bookmarks.append(converted_manga)
    update_user_profile(email, {"bookmarks": user_bookmarks})
    return "Manga bookmarked successfully!"

def remove_bookmark_admin(manga_to_remove):
    email = current_session.get("email")
    if not email:
        return "No user logged in."

    user = get_user_by_email(email)
    if not user:
        return "User not found."

    user_bookmarks = user.get("bookmarks", [])
    updated_bookmarks = [bm for bm in user_bookmarks if bm.get("title") != manga_to_remove.get("name")]

    if len(updated_bookmarks) == len(user_bookmarks):
        return "Bookmark not found."

    update_user_profile(email, {"bookmarks": updated_bookmarks})
    return "Bookmark removed successfully!"
