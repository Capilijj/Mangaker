import customtkinter as ctk
from PIL import Image
from customtkinter import CTkImage
from user_model import get_bookmarks_by_email
from users_db import current_session
from user_model import remove_bookmark_db
from Homepage.homeBackend import get_bookmarked_mangas, get_mangas, get_popular_manga, get_latest_update # Import these for comprehensive manga data
from Comics.ComicsBackend import get_all_manga

class BookmarkPage(ctk.CTkFrame):
    def __init__(self, parent, on_bookmark_change=None):
        super().__init__(parent)
        self.on_bookmark_change = on_bookmark_change

        # ===== Scrollable frame setup =====
        self.scrollable_frame = ctk.CTkScrollableFrame(self, height=700)
        self.scrollable_frame.pack(fill="both", expand=True, padx=5)

        # ===== Header Container (Black Box) =====
        self.header_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="black", corner_radius=0)
        self.header_frame.pack(pady=40, anchor="center")

        # ===== Header Text =====
        instruction_text = (
            "You can save a list of manga titles here up to 50.\n"
            "The list approves based on the latest update date."
            "The list of manga is stored in a browser that you can use right now."
        )

        self.instruction_label = ctk.CTkLabel(
            self.header_frame,
            text=instruction_text,
            font=ctk.CTkFont(size=16, weight="bold"),
            wraplength=500,
            justify="center",
            text_color="#39ff14"
        )
        self.instruction_label.pack(padx=20, pady=20)
        
        # Frame to hold bookmarked manga
        self.bookmark_display_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.bookmark_display_frame.pack(padx=20, pady=20, anchor="center") 

        self.display_bookmarks()

    def display_bookmarks(self):
        """Clears current displayed bookmarks and re-populates them sorted A-Z."""
        for widget in self.bookmark_display_frame.winfo_children():
            widget.destroy()

        email = current_session.get("email")
        if not email:
            bookmarked_titles = []
        else:
            bookmarked_titles = get_bookmarks_by_email(email)

        # ==== Combine and deduplicate all manga sources for a comprehensive list ====
        all_manga_sources = []
        all_manga_sources.extend(get_mangas()) # From local static list
        all_manga_sources.extend(get_popular_manga()) # From popular manga list
        all_manga_sources.extend(get_latest_update()) # From latest update list
        all_manga_sources.extend(get_all_manga()) # From Admin backend
        all_manga_sources.extend(get_bookmarked_mangas()) # Ensure bookmarked mangas are also included if they are a separate source

        unique_manga_map = {}
        for m in all_manga_sources:
            identifier = (m.get("title") or m.get("name") or "").strip()
            if identifier and identifier not in unique_manga_map:
                unique_manga_map[identifier] = m

        # ==== Filter bookmarks only from titles that exist in the master list ====
        bookmarked_mangas = [
            unique_manga_map[title]
            for title in bookmarked_titles
            if title in unique_manga_map
        ]

        # ==== Sort A to Z by title or name ====
        bookmarked_mangas.sort(key=lambda m: (m.get("title") or m.get("name") or "").lower())

        if not bookmarked_mangas:
            no_bookmark_label = ctk.CTkLabel(
                self.bookmark_display_frame,
                text="No bookmarks yet. Start adding your favorite manga!",
                font=ctk.CTkFont(size=18),
                text_color="gray"
            )
            no_bookmark_label.pack(pady=50)
            return

        # Arrange in a grid, 3 columns
        num_columns = 3
        for i in range(num_columns):
            self.bookmark_display_frame.grid_columnconfigure(i, weight=1)

        for idx, manga in enumerate(bookmarked_mangas):
            row = idx // num_columns
            col = idx % num_columns
            self.create_bookmark_item_card(self.bookmark_display_frame, manga, row, col)

    def create_bookmark_item_card(self, parent_frame, manga, row, column):
        container = ctk.CTkFrame(parent_frame, width=360, height=260, corner_radius=8, fg_color="#222222") 
        container.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")

        container.grid_columnconfigure(1, weight=1)
        # Adjusted row configuration to accommodate description and button placement
        container.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=0) 
        container.grid_rowconfigure(6, weight=1) # Give the last row some weight for the button

        image_path = manga.get("image_path") or manga.get("image")
        manga_name = manga.get("title") or manga.get("name")
        manga_genre = manga.get("genre")
        manga_status = manga.get("status")
        # Get description robustly from 'summary', 'desc', or 'description'
        manga_description = manga.get("summary") or manga.get("desc") or manga.get("description", "N/A") 
        manga_author = manga.get("author", "N/A") 

        try:
            img = Image.open(image_path).resize((120, 130))
            photo = CTkImage(light_image=img, size=(120, 130))
        except Exception as e:
            print(f"Error loading image for {manga_name}: {e}")
            photo = None

        img_label = ctk.CTkLabel(container, image=photo, text="")
        img_label.image = photo
        img_label.grid(row=0, column=0, rowspan=7, padx=10, pady=10, sticky="ns") 

        name_label = ctk.CTkLabel(container, text=manga_name, font=ctk.CTkFont(size=16, weight="bold"))
        name_label.grid(row=0, column=1, sticky="sw", pady=(10, 0), padx=10)

        if "chapter" in manga:
            chapter_label = ctk.CTkLabel(container, text=f"Chapter {manga['chapter']}", font=ctk.CTkFont(size=14))
            chapter_label.grid(row=1, column=1, sticky="nw", padx=10)
        else:
            ctk.CTkLabel(container, text="", font=ctk.CTkFont(size=14)).grid(row=1, column=1, sticky="nw", padx=10)

        # Description Label
        description_label = ctk.CTkLabel(container, text=f"Desc: {manga_description}", font=ctk.CTkFont(size=12), wraplength=200, justify="left")
        description_label.grid(row=2, column=1, sticky="nw", padx=10)

        # Author Label
        author_label = ctk.CTkLabel(container, text=f"Author: {manga_author}", font=ctk.CTkFont(size=12))
        author_label.grid(row=3, column=1, sticky="nw", padx=10)

        # Genre Label
        genre_label = ctk.CTkLabel(container, text=f"Genre: {manga_genre}", font=ctk.CTkFont(size=12))
        genre_label.grid(row=4, column=1, sticky="nw", padx=10) 

        # Status Label
        status_label = ctk.CTkLabel(container, text=f"Status: {manga_status}", font=ctk.CTkFont(size=12))
        status_label.grid(row=5, column=1, sticky="nw", padx=10) 

        remove_bookmark_btn = ctk.CTkButton(
            container,
            text="REMOVE",
            width=100, 
            fg_color="#0dfa21", 
            hover_color="#167e03", 
            text_color="black", 
            font=ctk.CTkFont(family="Poppins", size=14, weight="bold"),
            command=lambda m=manga: self.remove_bookmark_action(m)
        )
        # Place the button in column 0 (left side), below the image, aligned to the bottom-left
        remove_bookmark_btn.grid(row=6, column=0, padx=10, pady=(0, 10), sticky="sw") 

    def remove_bookmark_action(self, manga_to_remove):
        email = current_session.get("email")
        if not email:
            return

        title = manga_to_remove.get("title") or manga_to_remove.get("name")
        removed = remove_bookmark_db(email, title)
        if removed:
            print(f"Removed bookmark: {title}")
            self.display_bookmarks()
            if self.on_bookmark_change:
                self.on_bookmark_change()