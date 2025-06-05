import customtkinter as ctk
from PIL import Image, ImageTk

ctk.set_appearance_mode("System")  # or "Dark", "Light"
ctk.set_default_color_theme("blue")

class MangaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Manga Viewer")
        self.geometry("960x750")
        self.main_frame = ctk.CTkFrame(self, width=940, height=720)
        self.main_frame.pack(pady=10, padx=10)

        # Popular manga: 6 entries total
        self.popular_manga = [
            {"name": "One Piece", "chapter": 1050, "image": "image/onepiece.jpg"},
            {"name": "Naruto", "chapter": 700, "image": "image/onepiece.jpg"},
            {"name": "Bleach", "chapter": 686, "image": "image/onepiece.jpg"},
            {"name": "My Hero Academia", "chapter": 330, "image": "image/onepiece.jpg"},
            {"name": "Black Clover", "chapter": 320, "image": "image/onepiece.jpg"},
            {"name": "Dragon Ball", "chapter": 519, "image": "image/onepiece.jpg"},
        ]

        # Latest update manga (9 entries)
        self.latest_update = [
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

        self.create_popular_section()
        self.create_latest_update_section()

    def create_popular_section(self):
        label = ctk.CTkLabel(self.main_frame, text="POPULAR TODAY", font=ctk.CTkFont(size=20, weight="bold"))
        label.grid(row=0, column=0, pady=(0, 15), sticky="w")

        popular_frame = ctk.CTkFrame(self.main_frame)
        popular_frame.grid(row=1, column=0, pady=(0, 30), sticky="ew")
        popular_frame.grid_columnconfigure(tuple(range(6)), weight=1)

        for idx, manga in enumerate(self.popular_manga):
            container = ctk.CTkFrame(popular_frame, width=155, height=320, corner_radius=8)
            container.grid(row=0, column=idx, padx=5, sticky="nsew")

            try:
                img = Image.open(manga["image"]).resize((140, 190))
                photo = ImageTk.PhotoImage(img)
            except Exception:
                photo = None

            img_label = ctk.CTkLabel(container, image=photo, text="")
            img_label.image = photo
            img_label.pack(pady=10)

            name_label = ctk.CTkLabel(container, text=manga["name"], font=ctk.CTkFont(size=16, weight="bold"))
            name_label.pack(pady=(0, 3))
            chapter_label = ctk.CTkLabel(container, text=f"Chapter {manga['chapter']}", font=ctk.CTkFont(size=13))
            chapter_label.pack()

            btn = ctk.CTkButton(container, text="Read Now", width=130, fg_color="#0dfa21", hover_color="#167e03", text_color="black")
            btn.pack(pady=10)

    def create_latest_update_section(self):
        header_frame = ctk.CTkFrame(self.main_frame)
        header_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=0)

        label = ctk.CTkLabel(header_frame, text="LATEST UPDATE", font=ctk.CTkFont(size=20, weight="bold"))
        label.grid(row=0, column=0, sticky="w")

        view_all_btn = ctk.CTkButton(header_frame, text="View All", width=80, fg_color="#0dfa21",hover_color="#167e03", text_color="black")
        view_all_btn.grid(row=0, column=1, sticky="e")

        latest_frame = ctk.CTkFrame(self.main_frame)
        latest_frame.grid(row=3, column=0, sticky="ew")

        for idx, manga in enumerate(self.latest_update):
            r = idx // 3
            c = idx % 3
            self.create_latest_manga_container(latest_frame, manga, row=r, column=c)

    def create_latest_manga_container(self, parent, manga, row, column):
        container = ctk.CTkFrame(parent, width=280, height=120, corner_radius=8, fg_color="#222222")
        container.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")

        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure((0, 1, 2), weight=1)
        parent.grid_columnconfigure(column, weight=1)

        try:
            img = Image.open(manga["image"]).resize((90, 100))
            photo = ImageTk.PhotoImage(img)
        except Exception:
            photo = None

        img_label = ctk.CTkLabel(container, image=photo, text="")
        img_label.image = photo
        img_label.grid(row=0, column=0, rowspan=3, padx=10, pady=10, sticky="ns")

        name_label = ctk.CTkLabel(container, text=manga["name"], font=ctk.CTkFont(size=16, weight="bold"))
        name_label.grid(row=0, column=1, sticky="sw", pady=(15, 0), padx=10)

        chapter_label = ctk.CTkLabel(container, text=f"Chapter {manga['chapter']}", font=ctk.CTkFont(size=14))
        chapter_label.grid(row=1, column=1, sticky="nw", padx=10)

        # Updated button text to all caps "READ"
        btn = ctk.CTkButton(container, text="READ", width=80, fg_color="#0dfa21", hover_color="#167e03", text_color="black")
        btn.grid(row=0, column=2, rowspan=3, padx=15, pady=10, sticky="ns")

if __name__ == "__main__":
    app = MangaApp()
    app.mainloop()
