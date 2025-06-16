#===================================================================
#                          Comics Page
#===================================================================
import customtkinter as ctk
from PIL import Image, ImageDraw
from customtkinter import CTkImage
from Admin.adminBackend import  get_manga_list 
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

class AdminPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.button_font = ctk.CTkFont(family="Arial", size=16, weight="bold")


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

