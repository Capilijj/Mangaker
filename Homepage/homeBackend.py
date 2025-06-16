from users_db import users_db, current_session
# <<<BACK END TO NG DASHBOARD PAGE PLACE HOLDER LANG TO PRE KAW NA BAHALA KUNG SA DATBASE MO LALAGAY>>>
mangas = [
    {
        "title": "One Piece",
        "genre": "Adventure, Fantasy, Action",
        "summary": "Monkey D. Luffy and his crew search for the ultimate treasure known as the One Piece.",
        "status": "Ongoing",
        "author": "Eiichiro Oda",
        "image_path": r"image/onepiece.jpg"
    },
    {
        "title": "Naruto",
        "genre": "Adventure, Martial Arts, Fantasy",
        "summary": "Naruto Uzumaki strives to become the strongest ninja and lead his village.",
        "status": "Completed",
        "author": "Masashi Kishimoto",
        "image_path": r"image/naruto.jfif"
    },
    {
        "title": "Attack on Titan",
        "genre": "Action, Drama, Fantasy",
        "summary": "In a world besieged by Titans, humanity fights for survival behind giant walls.",
        "status": "Completed",
        "author": "Hajime Isayama",
        "image_path": r"image/AOT.jfif"
    },
    {
    "title": "Mashle: Magic and Muscles",
    "genre": "Action, Comedy, Fantasy",
    "summary": "In a magical world where strength is everything, a powerless boy uses brute strength to survive in a magic academy.",
    "status": "Completed",
    "author": "Hajime Komoto",
    "image_path": r"image/magic.jpg"
},
{
    "title": "Dandadan",
    "genre": "Action, Supernatural, Sci-Fi, Comedy",
    "summary": "A high school girl and a nerdy boy team up to battle supernatural threats after discovering psychic powers and alien forces.",
    "status": "Ongoing",
    "author": "Yukinobu Tatsu",
    "image_path": r"image/dandadan.jfif"
},
{
    "title": "Sakamoto Days",
    "genre": "Action, Comedy",
    "summary": "A legendary hitman retires to run a convenience store but finds himself dragged back into the assassin world.",
    "status": "Ongoing",
    "author": "Yuto Suzuki",
    "image_path": r"image/sakamoto.webp"
}
]

def get_mangas():
    return mangas

def get_popular_manga():
    return [
        {"name": "One Piece", "chapter": 1117, "image": "image/onepiece.jpg"},
        {"name": "Naruto", "chapter": 700, "image": "image/naruto.jfif"},
        {"name": "Bleach", "chapter": 686, "image": "image/bleach.jpg"},
        {"name": "Dragon Ball", "chapter": 519, "image": "image/dragonball.jfif"},
        {"name": "Spy x Family", "chapter": 94, "image": "image/spyxfamily.webp"},
        {"name": "Kaiju No. 8", "chapter": 110, "image": "image/kaiju.jfif"},
    ]



def get_latest_update():
    return [
        {"name": "Demon Slayer", "chapter": 205, "image": "image/demonslayer.jpg"},
        {"name": "Attack on Titan", "chapter": 139, "image": "image/AOT.jfif"},
        {"name": "Jujutsu Kaisen", "chapter": 262, "image": "image/jujutsu_kaisen.jpg"},
        {"name": "Blue Lock", "chapter": 268, "image": "image/blue.jpg"},
        {"name": "Tokyo Revengers", "chapter": 278, "image": "image/TokyoRever.jpg"},
        {"name": "Chainsaw Man", "chapter": 162, "image": "image/chainsawman.webp"},
        {"name": "Black Clover", "chapter": 370, "image": "image/blackclover.jpg"},
        {"name": "Fairy Tail", "chapter": 545, "image": "image/fairy tale.jfif"},
        {"name": "Hunter x Hunter", "chapter": 400, "image": "image/hunterhunter.jfif"},
    ]

    #example lang to placeholder
def get_user_prof():
    return {
        "profile_image": ""  
    }

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

def get_user_prof():
    email = current_session.get("email")
    if email in users_db:
        return {
            "username": users_db[email].get("username", "Unknown User"),
            "email": email,
            "profile_image": users_db[email].get("profile_image", None)  
        }
    return {
        "username": "Unknown User",
        "email": "unknown@gmail.com",
        "profile_image": None
    }