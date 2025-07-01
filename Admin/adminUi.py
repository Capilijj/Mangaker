# === Admin Manga Management UI Module ===
import customtkinter as ctk
from PIL import Image, ImageDraw
from customtkinter import CTkImage
import os

# === Importing backend functions for manga operations ===
from Admin.adminBackend import (
    get_manga_list,
    bookmark_manga_admin,
    remove_bookmark_admin,
    get_new_releases_backend,
)
from user_model import get_bookmarks_by_email
from users_db import current_session

# === Helper Function to make profile or icons circular ===
def make_circle(img):
    size = (min(img.size),) * 2
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    output = Image.new('RGBA', size)
    img = img.resize(size, Image.Resampling.LANCZOS)
    output.paste(img, (0, 0), mask)
    return output

# === Admin Page UI Class ===
class AdminPage(ctk.CTkFrame):
    def __init__(self, parent, controller, on_bookmark_change=None):
        super().__init__(parent)
        self.controller = controller
        self.on_bookmark_change = on_bookmark_change

        # === Bookmark icons for toggle ===
        self.bookmark_empty = CTkImage(Image.open("image/bookempty.png").resize((24, 24)))
        self.bookmark_filled = CTkImage(Image.open("image/bookfilled.png").resize((24, 24)))

        # === Scrollable container for all content ===
        self.content_scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.content_scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # === Main Section Title ===
        self.title_label = ctk.CTkLabel(
            self.content_scrollable_frame, text="Ready for the next chapter",
            font=ctk.CTkFont(size=24, weight="bold"), anchor="w"
        )
        self.title_label.pack(pady=(0, 10), anchor="w", fill="x")

        # === Container for Manga Grid ===
        self.main_manga_grid_container = ctk.CTkFrame(self.content_scrollable_frame, fg_color="transparent")
        self.main_manga_grid_container.pack(fill="x", expand=True, pady=(0, 20))

        # === Section Header for New Releases ===
        self.new_release_title = ctk.CTkLabel(
            self.content_scrollable_frame, text="NEW RELEASES",
            font=ctk.CTkFont(size=24, weight="bold"), anchor="w"
        )
        self.new_release_title.pack(pady=(20, 10), anchor="w", fill="x")

        # === Container for New Releases ===
        self.new_release_items_container = ctk.CTkFrame(self.content_scrollable_frame, fg_color="transparent")
        self.new_release_items_container.pack(fill="x", expand=True, pady=(0, 20))

        # === Load data for display ===
        self.manga_data = get_manga_list()
        self.new_release_data = self.get_new_releases()

        # === Populate the UI with data ===
        self.create_manga_grid(self.main_manga_grid_container)
        self.create_new_release_grid(self.new_release_items_container)

    # === Get the current user's bookmarks ===
    def get_user_bookmarks(self):
        email = current_session.get("email")
        if not email:
            return []
        return get_bookmarks_by_email(email)

    # === Create grid display for manga list ===
    def create_manga_grid(self, parent_frame):
        for widget in parent_frame.winfo_children():
            widget.destroy()

        num_columns = 4
        for col in range(num_columns):
            parent_frame.grid_columnconfigure(col, weight=1)

        if not self.manga_data:
            ctk.CTkLabel(parent_frame, text="No mangas available.",
                         font=ctk.CTkFont(size=16, slant="italic"),
                         text_color="#888").grid(row=0, column=0, columnspan=num_columns, pady=20)
            return

        for idx, manga in enumerate(self.manga_data):
            self.create_manga_container(parent_frame, manga, idx // num_columns, idx % num_columns)

    # === Create individual manga item container ===
    def create_manga_container(self, parent, manga, row, column):
        container = ctk.CTkFrame(parent, width=220, height=450, corner_radius=8, fg_color="#222222")
        container.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
        container.grid_propagate(False)

        # === Manga Image Display ===
        image_path = manga.get("image", "")
        try:
            img = Image.open(image_path).resize((180, 250), Image.Resampling.LANCZOS)
            photo = CTkImage(light_image=img, size=(180, 250))
        except:
            photo = None

        ctk.CTkLabel(container, image=photo, text="").pack(pady=(10, 5))
        ctk.CTkLabel(container, text=manga["name"], font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0, 2))
        ctk.CTkLabel(container, text=f"Chapter {manga['chapter']}", font=ctk.CTkFont(size=14)).pack()

        # Add Description and Author here - Font size increased to 12
        ctk.CTkLabel(container, text=f"Desc: {manga.get('description', 'N/A')}",
                     font=ctk.CTkFont(size=12), wraplength=180, justify="center").pack(pady=(2,0))
        ctk.CTkLabel(container, text=f"Author: {manga.get('author', 'N/A')}",
                     font=ctk.CTkFont(size=12)).pack(pady=(2,0))

        ctk.CTkLabel(container, text=f"Genre: {manga['genre']}", font=ctk.CTkFont(size=12)).pack()
        ctk.CTkLabel(container, text=f"Status: {manga['status']}", font=ctk.CTkFont(size=12)).pack()

        # === Optional: Display Release Date ===
        if manga.get("release_date"):
            date_str = manga["release_date"].strftime("%Y-%m-%d")
            ctk.CTkLabel(container, text=f"Released: {date_str}", font=ctk.CTkFont(size=10, slant="italic")).pack()

        # === Bookmark Button Setup ===
        user_bookmarks = self.get_user_bookmarks()
        is_bookmarked = manga["name"] in user_bookmarks

        bm_btn = ctk.CTkButton(
            container,
            text="BOOKMARK",
            width=120,
            fg_color="#0dfa21",
            hover_color="#167e03",
            text_color="black",
            image=self.bookmark_filled if is_bookmarked else self.bookmark_empty,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        bm_btn.pack(side="bottom", pady=(5, 10))

        # IMPORTANT: Set the command AFTER bm_btn is fully created to avoid UnboundLocalError
        bm_btn.configure(command=lambda m=manga: self.toggle_bookmark_admin(bm_btn, m))


    # === Handle bookmark/unbookmark toggle action ===
    def toggle_bookmark_admin(self, btn, manga):
        user_bookmarks = self.get_user_bookmarks()
        title = manga["name"]

        if title in user_bookmarks:
            response = remove_bookmark_admin(manga)
            if "successfully" in response:
                btn.configure(image=self.bookmark_empty)
        else:
            response = bookmark_manga_admin(manga)
            if "successfully" in response:
                btn.configure(image=self.bookmark_filled)

        # === Trigger callback to update other pages if needed ===
        if self.on_bookmark_change:
            self.on_bookmark_change()

    # === Refresh the entire admin manga list and new releases ===
    def refresh_admin_bookmark_states(self):
        self.manga_data = get_manga_list()
        self.new_release_data = self.get_new_releases()
        self.create_manga_grid(self.main_manga_grid_container)
        self.create_new_release_grid(self.new_release_items_container)

    # === Get new releases data ===
    def get_new_releases(self):
        return get_new_releases_backend()

    # === Create the grid for new manga releases ===
    def create_new_release_grid(self, parent_frame):
        for widget in parent_frame.winfo_children():
            widget.destroy()

        num_columns = 4
        for col in range(num_columns):
            parent_frame.grid_columnconfigure(col, weight=1)

        if not self.new_release_data:
            ctk.CTkLabel(parent_frame, text="No new releases yet.",
                         font=ctk.CTkFont(size=16, slant="italic"),
                         text_color="#888").grid(row=0, column=0, columnspan=num_columns, pady=20)
            return

        for idx, manga in enumerate(self.new_release_data[:4]):
            self.create_manga_container(parent_frame, manga, 0, idx)