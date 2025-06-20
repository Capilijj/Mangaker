# << BACKEND NG COMICS PAGE >>

from users_db import users_db, current_session # Import users_db and current_session
from datetime import datetime, timedelta # Import datetime for handling dates

manga_list = [
    {"name": "Oshi no Ko", "chapter": 75, "genre": "Drama, Supernatural", "status": "Ongoing", "image": "image/oshi.webp"}, 
    {"name": "Solo Leveling", "chapter": 179, "genre": "Action, Fantasy", "status": "Completed", "image": "image/solo.jpg"}, 
    {"name": "Wind Breaker", "chapter": 460, "genre": "Action, Sports", "status": "Ongoing", "image": "image/braker.jfif"},
    {"name": "Pokemon", "chapter": 150, "genre": "Adventure, Fantasy", "status": "Ongoing", "image": "image/pokemon.jfif"}, 
]

# NEW: Separate list for newly added mangas that will appear as new releases
new_manga_list = [
    #=====================================================================================================
    # dito ka mag dagdag ng mga manga pre na mag didisplay sa new releas the syempre updated nasa database
    #=====================================================================================================
    # IMPORTANT: Palitan ang petsa nito para lumabas sa "NEW RELEASES" (e.g., datetime.now())
    
    #example:
    #{"name": "Green Green Greens", "chapter": 26, "genre": "Sports, Drama, Slice of life", "status": "Ongoing", "image": "image/greens.jfif", "release_date": datetime.now()},    
]

def get_manga_list():
    """Returns the current list of all default mangas."""
    return manga_list

# You can add new manga here
def add_manga(manga_details):
    """
    Adds a new manga to the new_manga_list.
    Automatically assigns the current date as 'release_date'.
    Checks for duplicates across both manga_list and new_manga_list.
    """
    # ---- Check if the manga already exists in either list to prevent duplicates ----
    all_current_mangas = [m.get("name") for m in manga_list] + [m.get("name") for m in new_manga_list]
    if manga_details.get("name") in all_current_mangas:
        return False, "Manga with this name already exists in either default or new releases."

    # ---- Add current datetime as release_date if not provided ----
    if "release_date" not in manga_details:
        manga_details["release_date"] = datetime.now()

    new_manga_list.append(manga_details) # Add to the new_manga_list
    print(f"Added new manga to new_manga_list: {manga_details.get('name')} with release date {manga_details.get('release_date').strftime('%Y-%m-%d')}")
    return True, "New manga added successfully to releases!"


def get_new_releases_backend(days_ago=30, limit=None):
    """
    Retrieves mangas from new_manga_list that have been released within the last 'days_ago' days.
    Can also limit the number of results returned.
    """
    new_releases = []
    # ---- Calculate the threshold date ----
    threshold_date = datetime.now() - timedelta(days=days_ago)

    # ---- Iterate through new_manga_list for new releases ----
    for manga in new_manga_list:
        release_date = manga.get("release_date")
        # ---- Ensure release_date exists and is a datetime object for comparison ----
        if isinstance(release_date, datetime) and release_date >= threshold_date:
            new_releases.append(manga)

    # ---- Sort new releases by date, most recent first ----
    new_releases.sort(key=lambda x: x.get("release_date", datetime.min), reverse=True)

    # ---- Apply limit if specified ----
    if limit is not None and isinstance(limit, int) and limit > 0:
        return new_releases[:limit]

    return new_releases

# --- Bookmarking functions (no change, as they operate on specific manga details) ---
def bookmark_manga_admin(manga_to_bookmark):
    """Bookmarks a manga for the current logged-in user, converting to homeBackend's manga format."""
    email = current_session.get("email")
    if not email or email not in users_db:
        return "No user logged in."

    user_bookmarks = users_db[email].get("bookmarks", [])

    # ---- Convert admin's manga format (name, image) to homeBackend's format (title, image_path) ----
    # ---- Add placeholders for summary and author to match the structure in homeBackend.py ----
    converted_manga = {
        "title": manga_to_bookmark.get("name"),
        "genre": manga_to_bookmark.get("genre"),
        "summary": "N/A", # Placeholder to match homeBackend's manga structure
        "status": manga_to_bookmark.get("status"),
        "author": "N/A", # Placeholder to match homeBackend's manga structure
        "image_path": manga_to_bookmark.get("image"),
        "chapter": manga_to_bookmark.get("chapter")
    }

    # ---- Check if manga is already bookmarked using its 'title' ----
    if any(bm.get("title") == converted_manga.get("title") for bm in user_bookmarks):
        return "Manga already bookmarked."

    # ---- Enforce the 50-bookmark limit from homeBackend ----
    if len(user_bookmarks) >= 50:
        return "You have reached the maximum of 50 bookmarks."

    user_bookmarks.append(converted_manga)
    users_db[email]["bookmarks"] = user_bookmarks
    return "Manga bookmarked successfully!"

def remove_bookmark_admin(manga_to_remove):
    """Removes a manga bookmark for the current logged-in user."""
    email = current_session.get("email")
    if not email or email not in users_db:
        return "No user logged in."

    user_bookmarks = users_db[email].get("bookmarks", [])

    initial_count = len(user_bookmarks)
    users_db[email]["bookmarks"] = [
        bm for bm in user_bookmarks if bm.get("title") != manga_to_remove.get("name") # Compare with manga_to_remove's 'name'
    ]

    if len(users_db[email]["bookmarks"]) < initial_count:
        return "Bookmark removed successfully!"
    return "Bookmark not found."