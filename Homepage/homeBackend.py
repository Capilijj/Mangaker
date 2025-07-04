import sqlite3

# ==== Import necessary user functions ====
from user_model import get_user_by_email, add_bookmark, remove_bookmark_db, get_bookmarks_by_email, clear_bookmarks
# ==== Import the current user session ====
from users_db import current_session  # assuming you moved current_session here from users_db

# ==== Import functions from Admin backend ====
from Comics.ComicsBackend import get_manga_list, new_manga_list, get_new_releases_backend


# ==== Fetching Manga from the Database ==== 
connection = sqlite3.connect('user.db')
cursor = connection.cursor()

cursor.execute("SELECT * FROM Manga") # fetching all manga from db
manga_rows = cursor.fetchall()

mangas = [] # list to store manga data 

for row in manga_rows:
    manga_id, title, author, latest, status, img_path, description, update_date = row # unpacking tuple manga data
    cursor.execute("SELECT genre FROM Genres WHERE mangaId = ?", (manga_id,))
    genres = [g[0] for g in cursor.fetchall()] # fetching genres for each manga
    genre_str = ', '.join(genres) # combining genres into a single string

    mangas.append({
        "mangaId": manga_id,
        "title": title,
        "author": author,
        "chapter": latest,
        "genre": genre_str, 
        "status": status,
        "image": img_path,
        "summary": description,
    }) # appending manga data to the list as dictionary

connection.close()

# ==== Fetch basic manga list ====
def get_mangas():
    return mangas

def get_display_manga():
    display_manga = [] # List to store manga data for display
    i = 0 # counter for manga display
    for manga in mangas:
        if i < 10: # Limit to 10 manga for display
            display_manga.append({
                "title": manga["title"],
                "author": manga["author"],
                "chapter": manga["chapter"],
                "genre": manga["genre"],
                "status": manga["status"],
                "image": manga["image"],
                "summary": manga["summary"]
            })
            i += 1
        else:
            break

    return display_manga

# ==== Completed manga section ====
def get_completed_manga():
    i = 0 # counter to limit the number of completed manga fetched
    connection = sqlite3.connect('user.db')
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM Manga WHERE status = 'Completed'") 
    manga_rows = cursor.fetchall()

    completed_manga = []

    for row in manga_rows:
        if i < 5:  # Limit to 5 completed manga
            manga_id, title, author, latest, status, img_path, description, update_date = row

            cursor.execute("SELECT genre FROM Genres WHERE mangaId = ?", (manga_id,))
            genres = [g[0] for g in cursor.fetchall()] 
            genre_str = ', '.join(genres) 

            completed_manga.append({
                "mangaId": manga_id,
                "title": title,
                "author": author,
                "chapter": latest,
                "genre": genre_str, 
                "status": status,
                "image": img_path,
                "summary": description,
            })

            i += 1

        else:
            break

    connection.close()

    return completed_manga

#latest manga updates
def get_latest_update(): 
    limit = 9  # Limit to 9 latest updates

    connection = sqlite3.connect('user.db')
    cursor = connection.cursor()
    
    cursor.execute(""" 
        SELECT mangaId, title, author, latest, status, img_path, description, update_date 
        FROM Manga
        ORDER BY update_date DESC
        LIMIT ?
    """, (limit,))  # Fetching latest updates with a limit

    manga_rows = cursor.fetchall()
    
    latest_updates = [] # stores latest updates to display
    
    for row in manga_rows:
        manga_id, title, author, latest, status, img_path, description, update_date = row

        cursor.execute("SELECT genre FROM Genres WHERE mangaId = ?", (manga_id,))
        genres = [g[0] for g in cursor.fetchall()] 
        genre_str = ', '.join(genres) 

        latest_updates.append({
            "mangaId": manga_id,
            "title": title,
            "author": author,
            "chapter": latest,
            "genre": genre_str, 
            "status": status,
            "image": img_path,
            "summary": description,
        })
    
    connection.close()
    
    return latest_updates

# ==== Get logged-in user profile ====
def get_user_prof():
    email = current_session.get("email")
    if not email:
        return {
            "username": "Unknown User",
            "email": "unknown@gmail.com",
            "profile_image": None
        }

    user = get_user_by_email(email)
    if user:
        return {
            "username": user["username"],
            "email": user["email"],
            "profile_image": user["profile_image"]
        }

    return {
        "username": "Unknown User",
        "email": "unknown@gmail.com",
        "profile_image": None
    }

# ==== Genre Filter Options ====
def get_genres():
    return [
        "Action", "Adventure", "Comedy", "Drama", "Fantasy", "Romance",
        "Shounen", "Shoujo", "Seinen", "Josei", "Sci-Fi", "Horror",
        "Sports", "Slice of Life", "Mystery", "Mecha", "Supernatural",
        "Historical", "Ecchi", "Isekai"
    ]

# ==== Status Filter Options ====
def get_status_options():
    return ["All", "Ongoing", "Completed", "Hiatus"]

# ==== Sorting Filter Options ====
def get_order_options():
    return ["Popular", "A-Z", "Z-A", "Update", "Unupdated", "Added"]

# ==== Bookmark: Add manga to user’s bookmarks ====
def bookmark_manga(manga):
    email = current_session.get("email")
    if not email:
        return "No user logged in."

    title = manga.get("title") or manga.get("name")

    # Ensure title is a string before proceeding
    if not isinstance(title, str):
        return "Invalid manga title for bookmarking."
        
    return add_bookmark(email, title)

# ==== Bookmark: Remove manga from bookmarks ====
def remove_bookmark(manga):
    email = current_session.get("email")
    if not email:
        return "No user logged in."

    title = manga.get("title") or manga.get("name")

    # Ensure title is a string before removing
    if not isinstance(title, str):
        return "Invalid manga title for removing bookmark."

    return remove_bookmark_db(email, title)

# ==== Bookmark: Get full manga info for all user bookmarks ====
def get_bookmarked_mangas():
    email = current_session.get("email")
    if not email:
        return []

    bookmarked_titles = get_bookmarks_by_email(email)

    # Combine manga from all potential sources
    all_manga = []
    all_manga.extend(mangas)  # From local static list
    all_manga.extend(get_completed_manga())
    all_manga.extend(get_latest_update())
    all_manga.extend(get_manga_list())  # Admin backend
    all_manga.extend(new_manga_list)    # Dynamic additions
    all_manga.extend(get_new_releases_backend())  # Admin new releases

    # Deduplicate manga entries using their titles
    seen_identifiers = set()
    unique_all_manga = []
    for m in all_manga:
        identifier = (m.get("title") or m.get("name") or "").strip().lower()
        if identifier and identifier not in seen_identifiers:
            unique_all_manga.append(m)
            seen_identifiers.add(identifier)

    # Match bookmarked titles with unique manga
    resolved_bookmarks = []
    for m in unique_all_manga:
        title_or_name = (m.get("title") or m.get("name") or "").strip()
        if title_or_name in bookmarked_titles:
            resolved_bookmarks.append(m)

    return resolved_bookmarks


