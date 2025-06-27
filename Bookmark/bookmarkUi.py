import customtkinter as ctk
from PIL import Image
from customtkinter import CTkImage
from Homepage.homeBackend import get_bookmarked_mangas # Import the function
from Homepage.homeBackend import remove_bookmark 
import os

class BookmarkPage(ctk.CTkFrame):
    def __init__(self, parent, on_bookmark_change=None): # bookmark_change parameter
        super().__init__(parent)
        self.on_bookmark_change = on_bookmark_change # Store the callback

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

        self.display_bookmarks() # Call to display bookmarks initially

    def display_bookmarks(self):
        """Clears current displayed bookmarks and re-populates them."""
        # Clear existing widgets in the display frame
        for widget in self.bookmark_display_frame.winfo_children():
            widget.destroy()

        bookmarked_mangas = get_bookmarked_mangas()

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
        # Configure columns in bookmark_display_frame to expand equally, helping center content
        for i in range(num_columns):
            self.bookmark_display_frame.grid_columnconfigure(i, weight=1)

        for idx, manga in enumerate(bookmarked_mangas):
            row = idx // num_columns
            col = idx % num_columns
            self.create_bookmark_item_card(self.bookmark_display_frame, manga, row, col)

    def create_bookmark_item_card(self, parent_frame, manga, row, column):
        container = ctk.CTkFrame(parent_frame, width=360, height=180, corner_radius=8, fg_color="#222222")
        container.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")

        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure((0, 1, 2, 3), weight=1)

        # Determine image path and manga title/name
        image_path = manga.get("image_path") or manga.get("image")
        manga_name = manga.get("title") or manga.get("name")
        manga_genre = manga.get("genre")
        manga_status = manga.get("status")

        try:
            img = Image.open(image_path).resize((120, 130))
            photo = CTkImage(light_image=img, size=(120, 130))
        except Exception as e:
            print(f"Error loading image for {manga_name}: {e}")
            photo = None

        img_label = ctk.CTkLabel(container, image=photo, text="")
        img_label.image = photo
        img_label.grid(row=0, column=0, rowspan=4, padx=10, pady=10, sticky="ns")

        name_label = ctk.CTkLabel(container, text=manga_name, font=ctk.CTkFont(size=16, weight="bold"))
        name_label.grid(row=0, column=1, sticky="sw", pady=(10, 0), padx=10)

    
        if "chapter" in manga:
            chapter_label = ctk.CTkLabel(container, text=f"Chapter {manga['chapter']}", font=ctk.CTkFont(size=14))
            chapter_label.grid(row=1, column=1, sticky="nw", padx=10)
        else:
             # Add an empty label to maintain grid structure if chapter is absent
            ctk.CTkLabel(container, text="", font=ctk.CTkFont(size=14)).grid(row=1, column=1, sticky="nw", padx=10)


        genre_label = ctk.CTkLabel(container, text=f"Genre: {manga_genre}", font=ctk.CTkFont(size=12))
        genre_label.grid(row=2, column=1, sticky="nw", padx=10)

        status_label = ctk.CTkLabel(container, text=f"Status: {manga_status}", font=ctk.CTkFont(size=12))
        status_label.grid(row=3, column=1, sticky="nw", padx=10)

        # Remove Bookmark Button
        remove_bookmark_btn = ctk.CTkButton(
            container,
            text="REMOVE",
            width=120,
            fg_color="#0dfa21", 
            hover_color="#167e03", 
            text_color="black", 
            font=ctk.CTkFont(family="Poppins", size=14, weight="bold"),
            command=lambda m=manga: self.remove_bookmark_action(m)
        )
        remove_bookmark_btn.grid(row=4, column=0, padx=10, pady=(0, 10), sticky="w")

    def remove_bookmark_action(self, manga_to_remove):
        remove_bookmark(manga_to_remove)
        print(f"Removed bookmark: {manga_to_remove.get('title') or manga_to_remove.get('name')}")
        self.display_bookmarks() # Refresh the display on bookmarkUi.py
        if self.on_bookmark_change: # Notify the main app to refresh homepage icons
            self.on_bookmark_change()