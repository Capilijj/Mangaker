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
    }
]

def get_mangas():
    return mangas

def get_popular_manga():
    return [
        {"name": "One Piece", "chapter": 1050, "image": "image/onepiece.jpg"},
        {"name": "Naruto", "chapter": 700, "image": "image/onepiece.jpg"},
        {"name": "Bleach", "chapter": 686, "image": "image/onepiece.jpg"},
        {"name": "My Hero Academia", "chapter": 330, "image": "image/onepiece.jpg"},
        {"name": "Black Clover", "chapter": 320, "image": "image/onepiece.jpg"},
        {"name": "Dragon Ball", "chapter": 519, "image": "image/onepiece.jpg"},
    ]

def get_latest_update():
    return [
        {"name": "Demon Slayer", "chapter": 205, "image": "image/onepiece.jpg"},
        {"name": "Attack on Titan", "chapter": 139, "image": "image/onepiece.jpg"},
        {"name": "Jujutsu Kaisen", "chapter": 200, "image": "image/onepiece.jpg"},
        {"name": "Blue Lock", "chapter": 262, "image": "image/onepiece.jpg"},
        {"name": "Tokyo Revengers", "chapter": 220, "image": "image/onepiece.jpg"},
        {"name": "Chainsaw Man", "chapter": 97, "image": "image/onepiece.jpg"},
        {"name": "Black Clover", "chapter": 320, "image": "image/onepiece.jpg"},
        {"name": "Fairy Tail", "chapter": 545, "image": "image/onepiece.jpg"},
        {"name": "Hunter x Hunter", "chapter": 390, "image": "image/onepiece.jpg"},
    ]

#<<BACKEND NG COMICS PAGE>>>>>>

#example lang to placeholder
def get_user_prof():
    return {
        "profile_image": "image/user.jpg"  
    }

manga_list = [
    {"name": "Oshi no Ko", "chapter": 75},
    {"name": "Jujutsu Kaisen", "chapter": 200},
    {"name": "Chainsaw Man", "chapter": 97},
    {"name": "Blue Lock", "chapter": 262},
    {"name": "Tokyo Revengers", "chapter": 220},
    {"name": "Made in Abyss", "chapter": 60},
    {"name": "Vinland Saga", "chapter": 190},
    {"name": "Mob Psycho 100", "chapter": 150},
    {"name": "The Promised Neverland", "chapter": 181},
    {"name": "Dr. Stone", "chapter": 235},
    {"name": "Spy x Family", "chapter": 65},
    {"name": "Berserk", "chapter": 364},
    {"name": "Fairy Tail", "chapter": 545},
    {"name": "Hunter x Hunter", "chapter": 390},
    {"name": "My Dress-Up Darling", "chapter": 105},
]

def get_manga_list():
    return manga_list