from user_model import get_user_by_email, add_bookmark, remove_bookmark_db, get_bookmarks_by_email, clear_bookmarks
from users_db import users_db, current_session  # assuming you moved current_session here from users_db

# Manga list (placeholder data)
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

# --- Manga Fetching ---
def get_mangas():
    return mangas

def get_popular_manga():
    return [
        {"name": "Fullmetal Alchemist", "chapter": 116, "genre": "Action, Adventure, Fantasy", "status": "Completed", "image": "image/fullmetal.jpg"},
        {"name": "Berserk", "chapter": 374, "genre": "Action, Dark Fantasy", "status": "Ongoing", "image": "image/berserk.jpg"},
        {"name": "Bleach", "chapter": 686, "genre": "Action, Supernatural", "status": "Completed", "image": "image/bleach.jpg"},
        {"name": "Attack on Titan", "chapter": 139, "genre": "Action, Drama, Fantasy", "status": "Completed", "image": "image/AOT.jfif"},
        {"name": "Spy x Family", "chapter": 94, "genre": "Action, Comedy, Slice of Life", "status": "Ongoing", "image": "image/spyxfamily.webp"},
        {"name": "Kaiju No. 8", "chapter": 110, "genre": "Action, Sci-Fi", "status": "Ongoing", "image": "image/kaiju.jfif"},
    ]

def get_latest_update():
    return [
        {"name": "Demon Slayer", "chapter": 205, "genre": "Action, Supernatural", "status": "Completed", "image": "image/demonslayer.jpg"},
        {"name": "Mashle: Magic and Muscles", "chapter": 162, "genre": "Action, Comedy, Fantasy", "status": "Completed", "image": "image/magic.jpg"},
        {"name": "Dr. Stone", "chapter": 232, "genre": "Sci-Fi, Adventure", "status": "Completed", "image": "image/drstone.jpg"},
        {"name": "Blue Lock", "chapter": 268, "genre": "Sports, Drama", "status": "Ongoing", "image": "image/blue.jpg"},
        {"name": "Tokyo Revengers", "chapter": 278, "genre": "Action, Supernatural", "status": "Completed", "image": "image/TokyoRever.jpg"},
        {"name": "Chainsaw Man", "chapter": 162, "genre": "Action, Supernatural, Horror", "status": "Ongoing", "image": "image/chainsawman.webp"},
        {"name": "Black Clover", "chapter": 370, "genre": "Action, Fantasy", "status": "Ongoing", "image": "image/blackclover.jpg"},
        {"name": "Fairy Tail", "chapter": 545, "genre": "Action, Adventure, Fantasy", "status": "Completed", "image": "image/fairy tale.jfif"},
        {"name": "Hunter x Hunter", "chapter": 400, "genre": "Action, Adventure, Fantasy", "status": "Hiatus", "image": "image/hunterhunter.jfif"},
    ]

# --- User Profile ---
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

# --- Filters ---
def get_genres():
    return [
        "Action", "Adventure", "Comedy", "Drama", "Fantasy", "Romance",
        "Shounen", "Shoujo", "Seinen", "Josei", "Sci-Fi", "Horror",
        "Sports", "Slice of Life", "Mystery", "Mecha", "Supernatural",
        "Historical", "Ecchi", "Isekai"
    ]

def get_status_options():
    return ["All", "Ongoing", "Completed", "Hiatus"]

def get_order_options():
    return ["Popular", "A-Z", "Z-A", "Update", "Added"]

# --- Bookmarks ---
def bookmark_manga(manga):
    email = current_session.get("email")
    if not email:
        return "No user logged in."
    return add_bookmark(email, manga)

def remove_bookmark(manga):
    email = current_session.get("email")
    if not email:
        return "No user logged in."
    return remove_bookmark_db(email, manga)

def get_bookmarked_mangas():
    email = current_session.get("email")
    if not email:
        return []
    return get_bookmarks_by_email(email)

def remove_all_bookmarks():
    email = current_session.get("email")
    if not email:
        return False, "No user logged in."
    return clear_bookmarks(email)
