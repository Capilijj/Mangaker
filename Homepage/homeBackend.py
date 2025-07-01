# ==== Import necessary user functions ====
from user_model import get_user_by_email, add_bookmark, remove_bookmark_db, get_bookmarks_by_email, clear_bookmarks

# ==== Import the current user session ====
from users_db import current_session  # assuming you moved current_session here from users_db

# ==== Import functions from Admin backend ====
from Admin.adminBackend import get_manga_list, new_manga_list, get_new_releases_backend

# ==== Static manga list (used as fallback or example data) ====
mangas = [
    {
        "title": "Dragon Ball",
        "genre": "Action, Adventure, Martial Arts, Fantasy",
        "summary": "Son Goku, a young martial artist with a monkey tail, embarks on a quest to find the seven Dragon Balls",
        "status": "Completed",
        "author": "Akira Toriyama",
        "image_path": r"image/dragonball.jfif"
    },
    {
        "title": "One Piece",
        "genre": "Adventure, Fantasy, Action",
        "summary": "Monkey D. Luffy, a rubber-powered pirate, sails the seas in search of the legendary One Piece.",
        "status": "Ongoing",
        "author": "Eiichiro Oda",
        "image_path": r"image/onepiece.webp"
    },
    {
        "title": "Naruto",
        "genre": "Adventure, Martial Arts, Fantasy",
        "summary": "Naruto Uzumaki, a young ninja from the Hidden Leaf Village who dreams of becoming the Hokage.",
        "status": "Completed",
        "author": "Masashi Kishimoto",
        "image_path": r"image/naruto.jfif"
    },
    {
        "title": "Dandadan",
        "genre": "Action, Supernatural, Sci-Fi, Comedy",
        "summary": "A high school girl and a nerdy boy team up to battle supernatural threats. When strange dreams turn to real.",
        "status": "Ongoing",
        "author": "Yukinobu Tatsu",
        "image_path": r"image/dandadan.jfif"
    },
    {
        "title": "Sakamoto Days",
        "genre": "Action, Comedy",
        "summary": "A legendary hitman retires to run a convenience store, but teams up with a boy and girl when danger drags him back into action.",
        "status": "Ongoing",
        "author": "Yuto Suzuki",
        "image_path": r"image/sakamoto.webp"
    },
    {
        "title": "Jujutsu Kaisen",
        "genre": "Action, Supernatural, Dark Fantasy",
        "summary": "Gojo faces off against Sukuna in a fierce clash to determine who's the strongest sorcerer of their era.",
        "status": "Ongoing",
        "author": "Gege Akutami",
        "image_path": r"image/jujutsu.webp"
    },
    {
        "title": "My Hero Academia",
        "genre": "Action, Superhero, Fantasy",
        "summary": "In a world where most people have powers, a powerless boy dreams of becoming a hero.",
        "status": "Ongoing",
        "author": "Kohei Horikoshi",
        "image_path": r"image/mha.jpg"
    },
]

# ==== Fetch basic manga list ====
def get_mangas():
    return mangas

# ==== Popular manga section ====
def get_popular_manga():
    return [
        {"name": "Fullmetal Alchemist", "chapter": 116, "genre": "Action, Adventure, Fantasy", "status": "Completed", "image": "image/fullmetal.jpg"},
        {"name": "Demon Slayer", "chapter": 205, "genre": "Action, Supernatural", "status": "Completed", "image": "image/demonslayer.jpg"},    
        {"name": "Bleach", "chapter": 686, "genre": "Action, Supernatural", "status": "Completed", "image": "image/bleach.jpg"},
        {"name": "Attack on Titan", "chapter": 139, "genre": "Action, Drama, Fantasy", "status": "Completed", "image": "image/AOT.jfif"},
        {"name": "Solo Leveling", "chapter": 179, "genre": "Action, Fantasy, Adventure", "status": "Completed", "image": "image/solo.jpg"},
        {"name": "Mashle", "chapter": 162, "genre": "Action, Comedy, Fantasy", "status": "Completed", "image": "image/magic.jpg"},
    ]

# ==== Latest manga updates ====
def get_latest_update():
    return [
        {"name": "Kaiju No. 8", "chapter": 110, "genre": "Action, Sci-Fi", "status": "Ongoing", "image": "image/kaiju.jfif"},
        {"name": "Berserk", "chapter": 374, "genre": "Action, Dark Fantasy", "status": "Ongoing", "image": "image/berserk.jpg"},
        {"name": "Spy x Family", "chapter": 94, "genre": "Action, Comedy, Slice of Life", "status": "Ongoing", "image": "image/spyxfamily.webp"},
        {"name": "Blue Lock", "chapter": 268, "genre": "Sports, Drama", "status": "Ongoing", "image": "image/blue.jpg"},
        {"name": "Frieren: Beyond Journey’s End", "chapter": 133, "genre": "Fantasy, Drama, Adventure, Slice of Life", "status": "Ongoing", "image": "image/Frieren.jpg"},
        {"name": "Chainsaw Man", "chapter": 162, "genre": "Action, Supernatural, Horror", "status": "Ongoing", "image": "image/chainsawman.webp"},
        {"name": "Black Clover", "chapter": 370, "genre": "Action, Fantasy", "status": "Ongoing", "image": "image/blackclover.jpg"},
        {"name": "Four Knights of the Apocalypse", "chapter": 154, "genre": "Action, Adventure, Fantasy", "status": "Ongoing", "image": "image/FourKnights.webp"},
        {"name": "Hunter x Hunter", "chapter": 400, "genre": "Action, Adventure, Fantasy", "status": "Hiatus", "image": "image/hunterhunter.jfif"},
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
