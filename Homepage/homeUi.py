#================================================
#  Note: sa main.py ni rurun ang buong program
#================================================
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageEnhance
from customtkinter import CTkImage
from Homepage.homeBackend import (
    get_mangas, get_completed_manga, get_latest_update,
    bookmark_manga, remove_bookmark, get_bookmarked_mangas,
    get_display_manga
)

import os

def make_circle(img):
    size = (min(img.size),) * 2
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    output = Image.new('RGBA', size)
    img = img.resize(size, Image.Resampling.LANCZOS)
    output.paste(img, (0, 0), mask)
    return output

# ===============================================================
#                        Manga Viewer
#=================================================================
class MangaViewer(ctk.CTkFrame):
    def __init__(self, parent, controller=None): # Added controller parameter
        super().__init__(parent)
        self.controller = controller # Store controller
        self.current_index = 0
        self.auto_switch_delay = 2000

        self.mangas = get_display_manga()

        self.container = ctk.CTkFrame(self, corner_radius=15, fg_color="#111010")
        self.container.pack(side="top", fill="x", padx=50, pady=20)
        self.container.update_idletasks()

        self.bg_label = ctk.CTkLabel(self.container, text="")
        self.bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.image_label = ctk.CTkLabel(self.container, text="No Image", corner_radius=15, width=250, height=320)
        self.image_label.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="n")
        self.image_label.bind("<Button-1>", self.next_manga)

        self.text_container = ctk.CTkFrame(self.container, fg_color="transparent", corner_radius=0)
        self.text_container.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        self.container.grid_columnconfigure(1, weight=1)

        # Configure column for text_container to ensure content can expand
        self.text_container.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(self.text_container, text="", font=ctk.CTkFont(size=30, weight="bold"), anchor="w")
        self.title_label.grid(row=0, column=0, sticky="nw", pady=(20, 10), padx=15)

        # Only show chapter and summary if they exist in the manga dictionary
        self.chapter_label = ctk.CTkLabel(self.text_container, text="", font=ctk.CTkFont(size=20), anchor="w")
        self.chapter_label.grid(row=1, column=0, sticky="nw", pady=(0,10), padx=15)
        self.chapter_label.grid_forget() # Initially hidden

        self.summary_label = ctk.CTkLabel(self.text_container, text="", font=ctk.CTkFont(size=20), wraplength=450, justify="left", anchor="w")
        self.summary_label.grid(row=2, column=0, sticky="nw", pady=(0,15), padx=15)
        self.summary_label.grid_forget() # Initially hidden

        self.author_label = ctk.CTkLabel(self.text_container, text="", font=ctk.CTkFont(size=20), anchor="w")
        self.author_label.grid(row=3, column=0, sticky="nw", pady=(0,10), padx=15)

        self.genre_label = ctk.CTkLabel(self.text_container, text="", font=ctk.CTkFont(size=20), anchor="w")
        self.genre_label.grid(row=4, column=0, sticky="nw", pady=(0,10), padx=15)

        self.status_label = ctk.CTkLabel(self.text_container, text="", font=ctk.CTkFont(size=20), anchor="w")
        self.status_label.grid(row=5, column=0, sticky="nw", pady=(0,10), padx=15)

        self.bookmark_empty = CTkImage(light_image=Image.open("image/bookempty.png"), size=(30, 30))
        self.bookmark_filled = CTkImage(light_image=Image.open("image/bookfilled.png"), size=(30, 30))
        self.manga_font = ctk.CTkFont(family="Poppins", size=16, weight="bold")

        self.bm_button = ctk.CTkButton(
            self.text_container,
            text="BOOKMARK",
            font=self.manga_font,
            text_color="black",
            image=self.bookmark_empty,
            width=150,
            height=50,
            fg_color="#0dfa21",
            hover_color="#167e03",
            corner_radius=8,
            command=self.toggle_bookmark
        )
        self.bm_button.grid(row=6, column=0, sticky="nw", padx=15, pady=(0, 20)) # Placed in grid

        self.circles_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.circles_frame.grid(row=1, column=0, columnspan=2, pady=(0,20))

        self.circle_buttons = []
        for i in range(len(self.mangas)):
            btn = ctk.CTkButton(
                self.circles_frame,
                text="",
                width=15,
                height=15,
                corner_radius=20,
                fg_color="#555",
                hover_color="#0dfa21",
                command=lambda idx=i: self.change_manga(idx)
            )
            btn.grid(row=0, column=i, padx=10)
            self.circle_buttons.append(btn)

        self.container.bind("<Configure>", self.on_container_resize)
        self.load_manga(self.current_index)
        self.auto_switch() # This line now calls the defined method

    def load_manga(self, index):
        manga = self.mangas[index]
        try:
            img = Image.open(manga["image"]).resize((250, 320), Image.Resampling.LANCZOS)
            ctk_img = CTkImage(light_image=img, dark_image=img, size=(250, 320))
            self.image_label.configure(image=ctk_img, text="")
            self.image_label.image = ctk_img

            enhancer = ImageEnhance.Brightness(img)
            dark_img = enhancer.enhance(0.2)
            container_width = self.container.winfo_width()
            container_height = self.container.winfo_height()

            if container_width < 1 or container_height < 1:
                return

            dark_img_resized = dark_img.resize((container_width, container_height), Image.Resampling.LANCZOS)
            ctk_dark_img = CTkImage(light_image=dark_img_resized, dark_image=dark_img_resized, size=(container_width, container_height))
            self.bg_label.configure(image=ctk_dark_img)
            self.bg_label.image = ctk_dark_img

        except Exception as e:
            print(f"Failed to load image: {e}")
            self.image_label.configure(text="No Image", image=None)
            self.bg_label.configure(image=None)

        self.title_label.configure(text=manga.get("title", "N/A"))

        # Only show chapter and summary if they exist in the manga dictionary
        if "chapter" in manga and manga["chapter"] is not None:
            self.chapter_label.configure(text=f"Chapter: {manga['chapter']}")
            self.chapter_label.grid(row=1, column=0, sticky="nw", pady=(0,10), padx=15) # Use grid
        else:
            self.chapter_label.grid_forget() # Use grid_forget

        if "summary" in manga and manga["summary"] is not None:
            # Changed "Summary" to "Description"
            self.summary_label.configure(text=f"Description: {manga['summary']}")
            self.summary_label.grid(row=2, column=0, sticky="nw", pady=(0,15), padx=15) # Use grid
        else:
            self.summary_label.grid_forget() # Use grid_forget

        self.author_label.configure(text=f"Author: {manga.get('author', 'N/A')}")
        self.genre_label.configure(text=f"Genre: {manga.get('genre', 'N/A')}")
        self.status_label.configure(text=f"Status: {manga.get('status', 'Unknown')}")

        # Update bookmark button based on current manga's bookmark status
        bookmarked_mangas = get_bookmarked_mangas()
        self.is_bookmarked = any(bm.get("title") == manga.get("title") for bm in bookmarked_mangas)
        self.bm_button.configure(image=self.bookmark_filled if self.is_bookmarked else self.bookmark_empty)

        for i, btn in enumerate(self.circle_buttons):
            btn.configure(fg_color="#1f6aa5" if i == index else "#555")

    def on_container_resize(self, event):
        self.load_manga(self.current_index)

    def change_manga(self, idx):
        self.current_index = idx
        self.load_manga(idx)

    def next_manga(self, event=None):
        self.current_index = (self.current_index + 1) % len(self.mangas)
        self.load_manga(self.current_index)

    def read_manga(self):
        print(f"Opening manga: {self.mangas[self.current_index].get('title', 'N/A')}")

    def toggle_bookmark(self):
        current_manga = self.mangas[self.current_index]
        if self.is_bookmarked:
            remove_bookmark(current_manga)
            self.is_bookmarked = False
            print(f"❌ Un-bookmarked: {current_manga.get('title', 'N/A')}")
        else:
            bookmark_manga(current_manga)
            self.is_bookmarked = True
            print(f"✅ Bookmarked: {current_manga.get('title', 'N/A')}")
        new_icon = self.bookmark_filled if self.is_bookmarked else self.bookmark_empty
        self.bm_button.configure(image=new_icon)

    # Add this new method to the MangaViewer class
    def auto_switch(self):
        self.next_manga()
        self.after(self.auto_switch_delay, self.auto_switch)

#=========================================================================================
#           MangaListSection class to display completed and latest manga                  =
#=========================================================================================
class MangaListSection(ctk.CTkFrame):
    def __init__(self, parent, show_manga_list_callback):
        super().__init__(parent)
        self.configure(fg_color="transparent")
        self.controller = None # Will be set by DashboardPage

        # Container with matching padding
        self.main_container = ctk.CTkFrame(self, corner_radius=15, fg_color="transparent")
        self.main_container.pack(fill="x", padx=70, pady=20)

        self.completed_manga = get_completed_manga()
        self.latest_update = get_latest_update()
        self.show_manga_list_callback = show_manga_list_callback

        self.refresh_bookmark_buttons() # Initial call to create sections and set buttons
        
    #=========================================
    #           Completed manga
    #========================================
    def create_completed_section(self):
        label = ctk.CTkLabel(self.main_container, text="COMPLETED SERIES", font=ctk.CTkFont(size=20, weight="bold"))
        label.grid(row=0, column=0, pady=(0, 15), sticky="w")

        # Replaced CTkScrollableFrame with a regular CTkFrame for completed manga
        completed_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        completed_frame.grid(row=1, column=0, pady=(10, 30), sticky="ew")

        # Configure columns in completed_frame to expand equally
        for i in range(len(self.completed_manga)):
            completed_frame.grid_columnconfigure(i, weight=1)

        ITEM_WIDTH = 200
        ITEM_HEIGHT = 400

        for idx, manga in enumerate(self.completed_manga):
            container = ctk.CTkFrame(completed_frame, corner_radius=8, fg_color="#222222", width=ITEM_WIDTH, height=ITEM_HEIGHT)
            container.grid(row=0, column=idx, padx=10, sticky="ns")
            container.pack_propagate(False)

            container.grid_columnconfigure(0, weight=1)
            container.grid_rowconfigure(6, weight=1)

            try:
                img = Image.open(manga.get("image", "")).resize((120, 180))
                photo = CTkImage(light_image=img, size=(120, 180))
            except Exception:
                photo = None

            img_label = ctk.CTkLabel(container, image=photo, text="")
            img_label.image = photo
            img_label.grid(row=0, column=0, pady=(10, 5))

            name_label = ctk.CTkLabel(container, text=manga.get("title", "N/A"), font=ctk.CTkFont(size=16, weight="bold"), wraplength=ITEM_WIDTH-20, justify="center")
            name_label.grid(row=1, column=0, pady=(0, 2))

            chapter_label = ctk.CTkLabel(container, text=f"Chapter {manga.get('chapter', 'N/A')}", font=ctk.CTkFont(size=14))
            chapter_label.grid(row=2, column=0)

            desc_label = ctk.CTkLabel(container, text=f"Desc: {manga.get('summary', 'N/A')}", font=ctk.CTkFont(size=12), wraplength=ITEM_WIDTH-20, justify="left")
            desc_label.grid(row=3, column=0, pady=(2, 0))

            author_label = ctk.CTkLabel(container, text=f"Author: {manga.get('author', 'N/A')}", font=ctk.CTkFont(size=12))
            author_label.grid(row=4, column=0, pady=(2, 0))

            genre_label = ctk.CTkLabel(container, text=f"Genre: {manga.get('genre', 'N/A')}", font=ctk.CTkFont(size=12), wraplength=ITEM_WIDTH-20, justify="center")
            genre_label.grid(row=5, column=0, pady=(2, 0))

            status_label = ctk.CTkLabel(container, text=f"Status: {manga.get('status', 'Unknown')}", font=ctk.CTkFont(size=12))
            status_label.grid(row=6, column=0, pady=(0, 5))

            bookmark_empty = CTkImage(light_image=Image.open("image/bookempty.png"), size=(24, 24))
            bookmark_filled = CTkImage(light_image=Image.open("image/bookfilled.png"), size=(24, 24))

            bookmarked_mangas = get_bookmarked_mangas()
            is_bookmarked = any(bm.get("title") == manga.get("title") for bm in bookmarked_mangas)

            bm_btn = ctk.CTkButton(container, text="BOOKMARK", width=120,
                                   image=bookmark_filled if is_bookmarked else bookmark_empty,
                                   text_color="black", font=ctk.CTkFont(size=14, weight="bold"),
                                   fg_color="#0dfa21", hover_color="#167e03")
            bm_btn.configure(command=lambda btn=bm_btn, m=manga: self.toggle_bookmark_list_item(btn, m))
            bm_btn.grid(row=7, column=0, pady=(5, 10))

    def toggle_bookmark_list_item(self, btn, manga):
        bookmarked_mangas = get_bookmarked_mangas()
        is_bookmarked = any(bm.get("title") == manga.get("title") for bm in bookmarked_mangas)

        bookmark_empty = CTkImage(light_image=Image.open("image/bookempty.png"), size=(24, 24))
        bookmark_filled = CTkImage(light_image=Image.open("image/bookfilled.png"), size=(24, 24))

        if is_bookmarked:
            remove_bookmark(manga)
            btn.configure(image=bookmark_empty)
        else:
            bookmark_manga(manga)
            btn.configure(image=bookmark_filled)

    #=========================================
    #           Latest update manga
    #=========================================
    def create_latest_update_section(self):
        self.main_container.grid_columnconfigure(0, weight=1)
        header_frame = ctk.CTkFrame(self.main_container)
        header_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=0)
        header_frame.grid_columnconfigure(2, weight=0)  # For refresh button

        label = ctk.CTkLabel(header_frame, text="LATEST UPDATE", font=ctk.CTkFont(size=20, weight="bold"))
        label.grid(row=0, column=0, sticky="w")

        refresh_btn = ctk.CTkButton(
            header_frame,
            text="Refresh",
            width=80,
            fg_color="#0dfa21",
            hover_color="#167e03",
            text_color="black",
            command=self.refresh_sections
        )
        refresh_btn.grid(row=0, column=1, sticky="e", padx=(10, 5))

        view_all_btn = ctk.CTkButton(
            header_frame,
            text="View All",
            width=80,
            fg_color="#0dfa21",
            hover_color="#167e03",
            text_color="black",
            command=self.show_manga_list_callback
        )
        view_all_btn.grid(row=0, column=2, sticky="e")


        # ------------------------------

        latest_frame = ctk.CTkFrame(self.main_container)
        latest_frame.grid(row=3, column=0, sticky="ew")

        for i in range(3):
            latest_frame.grid_columnconfigure(i, weight=1)

        for idx, manga in enumerate(self.latest_update):
            r = idx // 3
            c = idx % 3
            self.create_latest_manga_container(latest_frame, manga, row=r, column=c)

    def create_latest_manga_container(self, parent, manga, row, column):
        container = ctk.CTkFrame(parent, height=200, corner_radius=8, fg_color="#222222")
        container.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")

        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=0)
        container.grid_rowconfigure(5, weight=1)

        try:
            img = Image.open(manga.get("image", "")).resize((100, 150))
            photo = CTkImage(light_image=img, size=(100, 150))
        except Exception:
            photo = None

        img_label = ctk.CTkLabel(container, image=photo, text="")
        img_label.image = photo
        img_label.grid(row=0, column=0, rowspan=7, padx=10, pady=10, sticky="ns")

        name_label = ctk.CTkLabel(container, text=manga.get("title", "N/A"), font=ctk.CTkFont(size=16, weight="bold"), anchor="w")
        name_label.grid(row=0, column=1, sticky="sw", pady=(10, 0), padx=5)

        chapter_label = ctk.CTkLabel(container, text=f"Chapter {manga.get('chapter', 'N/A')}", font=ctk.CTkFont(size=14), anchor="w")
        chapter_label.grid(row=1, column=1, sticky="nw", padx=5)

        desc_label = ctk.CTkLabel(container, text=f"Desc: {manga.get('summary', 'N/A')}", font=ctk.CTkFont(size=12), wraplength=200, justify="left", anchor="w")
        desc_label.grid(row=2, column=1, sticky="nw", padx=5)

        author_label = ctk.CTkLabel(container, text=f"Author: {manga.get('author', 'N/A')}", font=ctk.CTkFont(size=12), anchor="w")
        author_label.grid(row=3, column=1, sticky="nw", padx=5)

        genre_label = ctk.CTkLabel(container, text=f"Genre: {manga.get('genre', 'N/A')}", font=ctk.CTkFont(size=12), wraplength=200, justify="left", anchor="w")
        genre_label.grid(row=4, column=1, sticky="nw", padx=5)

        status_label = ctk.CTkLabel(container, text=f"Status: {manga.get('status', 'Unknown')}", font=ctk.CTkFont(size=12), anchor="w")
        status_label.grid(row=5, column=1, sticky="nw", padx=5)

        bookmark_empty = CTkImage(light_image=Image.open("image/bookempty.png"), size=(24, 24))
        bookmark_filled = CTkImage(light_image=Image.open("image/bookfilled.png"), size=(24, 24))

        bookmarked_mangas = get_bookmarked_mangas()
        is_bookmarked = any(bm.get("title") == manga.get("title") for bm in bookmarked_mangas)

        bookmark_btn = ctk.CTkButton(
            container,
            text="BOOKMARK",
            width=120,
            fg_color="#0dfa21",
            hover_color="#167e03",
            text_color="black",
            image=bookmark_filled if is_bookmarked else bookmark_empty,
            font=ctk.CTkFont(family="Poppins", size=14, weight="bold")
        )
        bookmark_btn.grid(row=6, column=1, padx=5, pady=(5, 10), sticky="nw")
        bookmark_btn.configure(command=lambda b=bookmark_btn, m=manga: self.toggle_bookmark_list_item(b, m))

    # New method to refresh the bookmark buttons on the completed and latest sections
    def refresh_bookmark_buttons(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()
        self.create_completed_section()
        self.create_latest_update_section()

    def refresh_sections(self):
        self.completed_manga = get_completed_manga()
        self.latest_update = get_latest_update()
        self.refresh_bookmark_buttons()

#==========================================================================================
#           DashboardPage class to manage the main dashboard UI
#==========================================================================================
class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.content_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.content_container.pack(fill="both", expand=True)

        self.manga_viewer = MangaViewer(self.content_container, controller=self.controller)
        self.manga_viewer.pack(fill="both", expand=True)

        self.mangalist_section = MangaListSection(self.content_container, show_manga_list_callback=self.controller.show_Comics)
        self.mangalist_section.controller = self.controller
        self.mangalist_section.pack(fill="x", expand=False, pady=10)

        self.home_action()

    def home_action(self):
        self.content_container.pack(fill="both", expand=True)
        self.controller.title("Dashboard")

    def refresh_all_bookmark_states(self):
        self.manga_viewer.load_manga(self.manga_viewer.current_index)
        self.mangalist_section.refresh_bookmark_buttons()