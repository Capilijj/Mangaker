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
    manga_id, title, author, latest, status, img_path, description = row

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

# ==== Popular manga section ====
def get_popular_manga():
    return [
        {
            "name": "Fullmetal Alchemist",
            "author": "Hiromu Arakawa",
            "chapter": 116,
            "genre": "Action, Adventure, Fantasy",
            "status": "Completed",
            "image": "image/fullmetal.jpg",
            "desc": "Two brothers seek the Philosopher's Stone after a failed alchemy experiment."
        },
        {
            "name": "Demon Slayer",
            "author": "Koyoharu Gotouge",
            "chapter": 205,
            "genre": "Action, Supernatural",
            "status": "Completed",
            "image": "image/demonslayer.jpg",
            "desc": "A boy joins the Demon Slayer Corps to avenge his family."
        },
        {
            "name": "Bleach",
            "author": "Tite Kubo",
            "chapter": 686,
            "genre": "Action, Supernatural",
            "status": "Completed",
            "image": "image/bleach.jpg",
            "desc": "A teenager becomes a Soul Reaper to battle evil spirits."
        },
        {
            "name": "Attack on Titan",
            "author": "Hajime Isayama",
            "chapter": 139,
            "genre": "Action, Drama, Fantasy",
            "status": "Completed",
            "image": "image/AOT.jfif",
            "desc": "Humans fight for survival against giant man-eating Titans."
        },
        {
            "name": "Solo Leveling",
            "author": "Chugong",
            "chapter": 179,
            "genre": "Action, Fantasy, Adventure",
            "status": "Completed",
            "image": "image/solo.jpg",
            "desc": "A weak hunter rises to the top with mysterious powers."
        },
        {
            "name": "Mashle",
            "author": "Hajime Komoto",
            "chapter": 162,
            "genre": "Action, Comedy, Fantasy",
            "status": "Completed",
            "image": "image/magic.jpg",
            "desc": "A magicless boy muscles through a magical world."
        },
    ]
#latest manga updates
def get_latest_update():
    return [
        {
            "name": "Kaiju No. 8",
            "author": "Naoya Matsumoto",
            "chapter": 110,
            "genre": "Action, Sci-Fi",
            "status": "Ongoing",
            "image": "image/kaiju.jfif",
            "desc": "A cleaner turns Kaiju to fight monsters threatening Japan."
        },
        {
            "name": "Berserk",
            "author": "Kentaro Miura",
            "chapter": 374,
            "genre": "Action, Dark Fantasy",
            "status": "Ongoing",
            "image": "image/berserk.jpg",
            "desc": "A lone swordsman battles demons in a dark, brutal world."
        },
        {
            "name": "Spy x Family",
            "author": "Tatsuya Endo",
            "chapter": 94,
            "genre": "Action, Comedy, Slice of Life",
            "status": "Ongoing",
            "image": "image/spyxfamily.webp",
            "desc": "A spy forms a fake family for his secret mission."
        },
        {
            "name": "Blue Lock",
            "author": "Muneyuki Kaneshiro",
            "chapter": 268,
            "genre": "Sports, Drama",
            "status": "Ongoing",
            "image": "image/blue.jpg",
            "desc": "Strikers compete in an intense soccer survival program."
        },
        {
            "name": "Frieren: Beyond Journey’s End",
            "author": "Kanehito Yamada",
            "chapter": 133,
            "genre": "Fantasy, Drama, Adventure, Slice of Life",
            "status": "Ongoing",
            "image": "image/Frieren.jpg",
            "desc": "An elf mage reflects on life after her hero’s journey."
        },
        {
            "name": "Chainsaw Man",
            "author": "Tatsuki Fujimoto",
            "chapter": 162,
            "genre": "Action, Supernatural, Horror",
            "status": "Ongoing",
            "image": "image/chainsawman.webp",
            "desc": "A devil hunter gains powers by fusing with his pet devil."
        },
        {
            "name": "Black Clover",
            "author": "Yūki Tabata",
            "chapter": 370,
            "genre": "Action, Fantasy",
            "status": "Ongoing",
            "image": "image/blackclover.jpg",
            "desc": "A magicless boy dreams of becoming the Wizard King."
        },
        {
            "name": "Four Knights of the Apocalypse",
            "author": "Nakaba Suzuki",
            "chapter": 154,
            "genre": "Action, Adventure, Fantasy",
            "status": "Ongoing",
            "image": "image/FourKnights.webp",
            "desc": "A sequel to Seven Deadly Sins with new legendary knights."
        },
        {
            "name": "Hunter x Hunter",
            "author": "Yoshihiro Togashi",
            "chapter": 400,
            "genre": "Action, Adventure, Fantasy",
            "status": "Hiatus",
            "image": "image/hunterhunter.jfif",
            "desc": "A boy embarks on a journey to find his hunter father."
        },
    ]


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
    all_manga.extend(get_popular_manga())
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

# ==== Clear all bookmarks for current user ====
def remove_all_bookmarks():
    email = current_session.get("email")
    if not email:
        return False, "No user logged in."
    return clear_bookmarks(email)
