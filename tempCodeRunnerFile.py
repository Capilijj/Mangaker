            "author": "Koyoharu Gotouge",
            "chapter": 205,
            "genre": "Action, Supernatural",
            "status": "Completed",
            "image": "image/demonslayer.jpg",
            "summary": "A boy joins the Demon Slayer Corps to avenge his family."
        },
        {
            "name": "Bleach",
            "author": "Tite Kubo",
            "chapter": 686,
            "genre": "Action, Supernatural",
            "status": "Completed",
            "image": "image/bleach.jpg",
            "summary": "A teenager becomes a Soul Reaper to battle evil spirits."
        },
        {
            "name": "Attack on Titan",
            "author": "Hajime Isayama",
            "chapter": 139,
            "genre": "Action, Drama, Fantasy",
            "status": "Completed",
            "image": "image/AOT.jfif",
            "summary": "Humans fight for survival against giant man-eating Titans."
        },
        {
            "name": "Solo Leveling",
            "author": "Chugong",
            "chapter": 179,
            "genre": "Action, Fantasy, Adventure",
            "status": "Completed",
            "image": "image/solo.jpg",
            "summary": "A weak hunter rises to the top with mysterious powers."
        },
        {
            "name": "Mashle",
            "author": "Hajime Komoto",
            "chapter": 162,
            "genre": "Action, Comedy, Fantasy",
            "status": "Completed",
            "image": "image/magic.jpg",
            "summary": "A magicless boy muscles through a magical world."
        },
        {
            "name": "Kaiju No. 8",
            "author": "Naoya Matsumoto",
            "chapter": 110,
            "genre": "Action, Sci-Fi",
            "status": "Ongoing",
            "image": "image/kaiju.jfif",
            "summary": "A cleaner turns Kaiju to fight monsters threatening Japan."
        },
        {
            "name": "Berserk",
            "author": "Kentaro Miura",
            "chapter": 374,
            "genre": "Action, Dark Fantasy",
            "status": "Ongoing",
            "image": "image/berserk.jpg",
            "summary": "A lone swordsman battles demons in a dark, brutal world."
        },
        {
            "name": "Spy x Family",
            "author": "Tatsuya Endo",
            "chapter": 94,
            "genre": "Action, Comedy, Slice of Life",
            "status": "Ongoing",
            "image": "image/spyxfamily.webp",
            "summary": "A spy forms a fake family for his secret mission."
        },
        {
            "name": "Blue Lock",
            "author": "Muneyuki Kaneshiro",
            "chapter": 268,
            "genre": "Sports, Drama",
            "status": "Ongoing",
            "image": "image/blue.jpg",
            "summary": "Strikers compete in an intense soccer survival program."
        },
        {
            "name": "Frieren: Beyond Journey’s End",
            "author": "Kanehito Yamada",
            "chapter": 133,
            "genre": "Fantasy, Drama, Adventure, Slice of Life",
            "status": "Ongoing",
            "image": "image/Frieren.jpg",
            "summary": "An elf mage reflects on life after her hero’s journey."
        },
        {
            "name": "Chainsaw Man",
            "author": "Tatsuki Fujimoto",
            "chapter": 162,
            "genre": "Action, Supernatural, Horror",
            "status": "Ongoing",
            "image": "image/chainsawman.webp",
            "summary": "A devil hunter gains powers by fusing with his pet devil."
        },
        {
            "name": "Black Clover",
            "author": "Yūki Tabata",
            "chapter": 370,
            "genre": "Action, Fantasy",
            "status": "Ongoing",
            "image": "image/blackclover.jpg",
            "summary": "A magicless boy dreams of becoming the Wizard King."
        },
        {
            "name": "Four Knights of the Apocalypse",
            "author": "Nakaba Suzuki",
            "chapter": 154,
            "genre": "Action, Adventure, Fantasy",
            "status": "Ongoing",
            "image": "image/FourKnights.webp",
            "summary": "A sequel to Seven Deadly Sins with new legendary knights."
        },
        {
            "name": "Hunter x Hunter",
            "author": "Yoshihiro Togashi",
            "chapter": 400,
            "genre": "Action, Adventure, Fantasy",
            "status": "Hiatus",
            "image": "image/hunterhunter.jfif",
            "summary": "A boy embarks on a journey to find his hunter father."
        },
    ]

    connection = sqlite3.connect('user.db')
    cursor = connection.cursor()

    for m in mangas:
        cursor.execute("""
            INSERT INTO Manga (title, author, latest, status, img_path, description)
            VALUES (?, ?, ?, ?,