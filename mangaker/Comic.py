import customtkinter as ctk
from PIL import Image, ImageTk

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class MangaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Manga Viewer")
        self.geometry("1300x950")  # wider for 5 columns

        self.button_font = ctk.CTkFont(family="Arial", size=16, weight="bold")

        self.main_frame = ctk.CTkFrame(self, width=1280, height=900)
        self.main_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.manga_list = [
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

        self.create_comic_section()

    def create_comic_section(self):
        # Top container frame for back button and title label
        top_container = ctk.CTkFrame(self.main_frame)
        top_container.pack(fill="x", pady=(0, 10), padx=5)

        # Back button on the left
        back_button = ctk.CTkButton(
            top_container,
            text="Back",
            width=80,
            fg_color="#0dfa21", text_color="black",hover_color="#167e03",
            command=self.back_action,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        back_button.pack(side="right")

        # Title label next to back button
        title_label = ctk.CTkLabel(
            top_container,
            text="Ready for the next chapter",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left", padx=20)

        # Scrollable frame for manga items
        scrollable_frame = ctk.CTkScrollableFrame(self.main_frame, width=1280, height=850)
        scrollable_frame.pack(fill="both", expand=True)

        scrollable_frame.grid_columnconfigure(tuple(range(5)), weight=1)

        # Manga items in grid
        for i, manga in enumerate(self.manga_list):
            row = i // 5
            col = i % 5
            self.create_comic_item(scrollable_frame, row, col, manga["name"], manga["chapter"])

    def create_comic_item(self, parent, row, column, name, chapter):
        container = ctk.CTkFrame(parent, width=240, height=280, corner_radius=8, fg_color="#222222")
        container.grid(row=row, column=column, padx=12, pady=12, sticky="nsew")

        parent.grid_columnconfigure(column, weight=1)

        try:
            img = Image.open("image/onepiece.jpg").resize((120, 160))
            photo = ImageTk.PhotoImage(img)
        except Exception:
            photo = None

        img_label = ctk.CTkLabel(container, image=photo, text="")
        img_label.image = photo
        img_label.pack(pady=12)

        name_label = ctk.CTkLabel(container, text=name, font=ctk.CTkFont(size=16, weight="bold"))
        name_label.pack(pady=(0, 4))

        chapter_label = ctk.CTkLabel(container, text=f"Chapter {chapter}", font=ctk.CTkFont(size=14))
        chapter_label.pack()

        btn = ctk.CTkButton(container, text="Read", width=110,
                            fg_color="#0dfa21", hover_color="#167e03", text_color="black", font=self.button_font)
        btn.pack(pady=10)

    def back_action(self):
        print("Back button clicked")
        # Implement what you want to do when back button is clicked


if __name__ == "__main__":
    app = MangaApp()
    app.mainloop()
