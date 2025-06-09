import customtkinter as ctk
from PIL import Image, ImageDraw
from customtkinter import CTkImage
from backend2 import get_user_prof, get_manga_list 
import os

def make_circle(img):
    size = (min(img.size),) * 2
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    output = Image.new('RGBA', size)
    img = img.resize(size, Image.Resampling.LANCZOS)
    output.paste(img, (0, 0), mask)
    return output

class MangaListPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.button_font = ctk.CTkFont(family="Arial", size=16, weight="bold")

        # --- HEADER (Top container) ---
        self.top_container = ctk.CTkFrame(self, height=60, fg_color="#39ff14", corner_radius=15)
        self.top_container.pack(side="top", fill="x", pady=10, padx=10)

        # Circle logo
        try:
            self.logo_img = Image.open(r"image/mangaker.jpg")
            self.logo_img = self.logo_img.resize((40, 40), Image.Resampling.LANCZOS)
            self.logo_img = make_circle(self.logo_img)
            self.logo_photo = CTkImage(light_image=self.logo_img, dark_image=self.logo_img, size=(40, 40))
            self.logo = ctk.CTkLabel(self.top_container, image=self.logo_photo, text="")
            self.logo.pack(side="left", padx=15, pady=10)
        except Exception as e:
            print("Logo loading failed:", e)

        button_style = {
            "fg_color": "#39ff14",
            "hover_color": "#1f8112",
            "text_color": "black",
            "corner_radius": 10,
        }

        self.home_button = ctk.CTkButton(self.top_container, text="Home", command=self.go_home, **button_style)
        self.home_button.pack(side="left", padx=10, pady=10)

        self.bookmark_button = ctk.CTkButton(self.top_container, text="Bookmark", command=self.bookmark_action, **button_style)
        self.bookmark_button.pack(side="left", padx=10, pady=10)

        self.profile_button = ctk.CTkButton(self.top_container, text="Profile", command=self.profile_action, **button_style)
        self.profile_button.pack(side="left", padx=10, pady=10)

         # User profile dapat ito
        user_info = get_user_prof()
        image_path = user_info.get("profile_image")

        if image_path and os.path.exists(image_path):
            user_img = Image.open(image_path).resize((32, 32), Image.Resampling.LANCZOS)
            user_img = make_circle(user_img)
            self.user_icon = CTkImage(light_image=user_img, dark_image=user_img, size=(32, 32))
        else:
            self.user_icon = None
            print(f"Image not found: {image_path}")

        self.user_icon_label = ctk.CTkLabel(
            self.top_container,
            image=self.user_icon,
            text=""
        )
        self.user_icon_label.pack(side="right", padx=(5, 15), pady=0)
        self.user_icon_label.bind("<Button-1>", lambda e: self.profile_action())

        self.search_frame = ctk.CTkFrame(self.top_container, width=240, height=36)
        self.search_frame.pack(side="right", pady=10, padx=10)
        self.search_frame.pack_propagate(False)

        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Search...")
        self.search_entry.pack(side="left", fill="both", expand=True)
        self.search_entry.bind("<Return>", self.on_enter_pressed)

        main_search_icon_path = r"image/glass1.gif"
        if os.path.exists(main_search_icon_path):
            main_icon_img = Image.open(main_search_icon_path).resize((25, 25), Image.Resampling.LANCZOS)
            self.search_icon = CTkImage(light_image=main_icon_img, dark_image=main_icon_img, size=(25, 25))
        else:
            self.search_icon = None
            print(f"Image not found: {main_search_icon_path}")

        self.search_icon_button = ctk.CTkButton(
            self.search_frame,
            image=self.search_icon,
            width=36,
            height=36,
            fg_color="#FFFFFF",
            corner_radius=0,
            text="",
        )
        self.search_icon_button.pack(side="right")

        self.filter_row_frame = ctk.CTkFrame(self, fg_color="transparent", height=50)
        self.filter_row_frame.pack(side="top", fill="x", pady=(10, 10))
        self.filter_row_frame.pack_propagate(False)

        # --- TITLE LABEL (below header, above grid) ---
        self.title_label = ctk.CTkLabel(self, text="Ready for the next chapter", font=ctk.CTkFont(size=24, weight="bold"), anchor="w")
        self.title_label.pack(side="top", pady=(5, 0), anchor="w", fill="x", padx=10)


        # --- MANGA GRID ---
        self.main_frame = ctk.CTkFrame(self, width=1280, height=900)
        self.main_frame.pack(pady=(5, 0), padx=5, fill="both", expand=True)

        self.manga_list = get_manga_list() 
        self.create_comic_section()

    def create_comic_section(self):
        scrollable_frame = ctk.CTkScrollableFrame(self.main_frame, width=1280, height=850)
        scrollable_frame.pack(fill="both", expand=True)
        scrollable_frame.grid_columnconfigure(tuple(range(5)), weight=1)

        for i, manga in enumerate(self.manga_list):
            row = i // 5
            col = i % 5
            self.create_comic_item(scrollable_frame, row, col, manga["name"], manga["chapter"])

    def create_comic_item(self, parent, row, column, name, chapter):
        container = ctk.CTkFrame(parent, width=240, height=280, corner_radius=8, fg_color="#222222")
        container.grid(row=row, column=column, padx=12, pady=12, sticky="nsew")
        parent.grid_columnconfigure(column, weight=1)

        photo = None
        try:
            img = Image.open("image/onepiece.jpg").resize((120, 160))
            photo = CTkImage(light_image=img, size=(120, 160))
        except Exception:
            pass

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

    def go_home(self):
        self.controller.show_dashboard()

    def bookmark_action(self):
        self.controller.show_dashboard()
        self.controller.dashboard.bookmark_action()

    def profile_action(self):
        self.controller.show_dashboard()
        self.controller.dashboard.profile_action()

    def on_enter_pressed(self, event):
        # Placeholder for search action
        pass

