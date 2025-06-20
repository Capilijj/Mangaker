import customtkinter as ctk
from PIL import Image, ImageDraw, ImageOps
from customtkinter import CTkImage
# Import the new bookmarking functions and get_new_releases_backend from adminBackend
from Admin.adminBackend import get_manga_list, bookmark_manga_admin, remove_bookmark_admin, get_new_releases_backend
from Homepage.homeBackend import get_bookmarked_mangas # To check existing bookmarks (which are in 'title' format)
import os

#======== helper function to make circular image ========
def make_circle(img):
    size = (min(img.size),) * 2
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    output = Image.new('RGBA', size)
    img = img.resize(size, Image.Resampling.LANCZOS)
    output.paste(img, (0, 0), mask)
    return output

#==========================================================================================
#                            AdminPage class to manage admin functionalities
#==========================================================================================
class AdminPage(ctk.CTkFrame):
    def __init__(self, parent, controller, on_bookmark_change=None):
        super().__init__(parent)
        self.controller = controller
        self.on_bookmark_change = on_bookmark_change
        self.button_font = ctk.CTkFont(family="Arial", size=16, weight="bold")

        self.bookmark_empty = CTkImage(light_image=Image.open("image/bookempty.png"), size=(24, 24))
        self.bookmark_filled = CTkImage(light_image=Image.open("image/bookfilled.png"), size=(24, 24))

        self.content_scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.content_scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # ---- TITLE LABEL (for existing mangas, within the scrollable frame) ----
        self.title_label = ctk.CTkLabel(self.content_scrollable_frame, text="Ready for the next chapter", font=ctk.CTkFont(size=24, weight="bold"), anchor="w")
        self.title_label.pack(side="top", pady=(0, 10), anchor="w", fill="x", padx=0)

        # ---- Frame for the main manga grid (within the scrollable frame) ----
        self.main_manga_grid_container = ctk.CTkFrame(self.content_scrollable_frame, fg_color="transparent")
        self.main_manga_grid_container.pack(fill="x", expand=True, pady=(0, 20))

        # ---- New Release Section ----
        self.new_release_title = ctk.CTkLabel(self.content_scrollable_frame, text="NEW RELEASES", font=ctk.CTkFont(size=24, weight="bold"), anchor="w")
        self.new_release_title.pack(side="top", pady=(20, 10), anchor="w", fill="x", padx=0)

        # ---- Frame for new release items (within the same scrollable frame) ----
        self.new_release_items_container = ctk.CTkFrame(self.content_scrollable_frame, fg_color="transparent")
        self.new_release_items_container.pack(fill="x", expand=True, pady=(0, 20))

        # --- Initialize data for both sections ---
        self.manga_data = get_manga_list() # Get default mangas
        self.new_release_data = self.get_new_releases() # Get new release mangas

        # --- Create grids ---
        self.create_manga_grid(self.main_manga_grid_container)
        self.create_new_release_grid(self.new_release_items_container)


    def create_manga_grid(self, parent_frame):
        """
        Creates and populates the grid for general manga display.
        This now only displays mangas from the default manga_list (not new releases).
        """
        for widget in parent_frame.winfo_children():
            widget.destroy()

        num_columns = 4

        for col in range(num_columns):
            parent_frame.grid_columnconfigure(col, weight=1)

        if not self.manga_data:
            no_manga_label = ctk.CTkLabel(parent_frame, text="No other mangas available at the moment.",
                                          font=ctk.CTkFont(size=16, slant="italic"), text_color="#888")
            no_manga_label.grid(row=0, column=0, columnspan=num_columns, pady=20, sticky="nsew")
            parent_frame.grid_rowconfigure(0, weight=1)
            parent_frame.grid_columnconfigure(0, weight=1)
            return

        for idx, manga in enumerate(self.manga_data):
            row = idx // num_columns
            col = idx % num_columns
            self.create_manga_container(parent_frame, manga, row, col)

    def create_manga_container(self, parent, manga, row, column):
        container = ctk.CTkFrame(parent, width=220, height=380, corner_radius=8, fg_color="#222222")
        container.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
        container.grid_propagate(False)

        image_path = manga.get("image", "")
        if os.path.exists(image_path):
            try:
                img = Image.open(image_path).resize((180, 250), Image.Resampling.LANCZOS)
                photo = CTkImage(light_image=img, dark_image=img, size=(180, 250))
            except Exception as e:
                print(f"Error loading image {image_path}: {e}")
                photo = None
        else:
            photo = None

        img_label = ctk.CTkLabel(container, image=photo, text="")
        img_label.image = photo
        img_label.pack(pady=(10, 5))

        name_label = ctk.CTkLabel(container, text=manga["name"], font=ctk.CTkFont(size=16, weight="bold"))
        name_label.pack(pady=(0, 2))

        chapter_label = ctk.CTkLabel(container, text=f"Chapter {manga['chapter']}", font=ctk.CTkFont(size=14))
        chapter_label.pack()

        genre_label = ctk.CTkLabel(container, text=f"Genre: {manga['genre']}", font=ctk.CTkFont(size=12))
        genre_label.pack()

        status_label = ctk.CTkLabel(container, text=f"Status: {manga['status']}", font=ctk.CTkFont(size=12))
        status_label.pack()

        # ---- Display Release Date ----
        release_date = manga.get("release_date")
        if release_date:
            formatted_date = release_date.strftime("%Y-%m-%d")
            release_date_label = ctk.CTkLabel(container, text=f"Released: {formatted_date}", font=ctk.CTkFont(size=10, slant="italic"))
            release_date_label.pack(pady=(2, 0))

        bookmarked_mangas = get_bookmarked_mangas()
        is_bookmarked = any(bm.get("title") == manga.get("name") for bm in bookmarked_mangas)

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
        bm_btn.pack(pady=10)
        bm_btn.configure(command=lambda btn=bm_btn, m=manga: self.toggle_bookmark_admin(btn, m))

    def toggle_bookmark_admin(self, btn, manga):
        bookmarked_mangas = get_bookmarked_mangas()
        is_bookmarked = any(bm.get("title") == manga.get("name") for bm in bookmarked_mangas)

        if is_bookmarked:
            response = remove_bookmark_admin(manga)
            if "successfully" in response:
                btn.configure(image=self.bookmark_empty)
                print(f"❌ Un-bookmarked: {manga.get('name', 'N/A')}")
            else:
                print(f"Error un-bookmarking: {response}")
        else:
            response = bookmark_manga_admin(manga)
            if "successfully" in response:
                btn.configure(image=self.bookmark_filled)
                print(f"✅ Bookmarked: {manga.get('name', 'N/A')}")
            else:
                print(f"Error bookmarking: {response}")

        if self.on_bookmark_change:
            self.on_bookmark_change()

    def refresh_admin_bookmark_states(self):
        """Refreshes the bookmark states for both default mangas and new releases."""
        self.manga_data = get_manga_list() # Re-fetch default mangas
        self.new_release_data = self.get_new_releases() # Re-fetch new release mangas

        self.create_manga_grid(self.main_manga_grid_container) # Re-create default manga grid
        self.create_new_release_grid(self.new_release_items_container) # Re-create new release grid

    def get_new_releases(self):
        """Fetches new release manga data from the backend."""
        return get_new_releases_backend() # Walang limit parameter  # Still limiting to 1 for the "NEW RELEASES" section

    def create_new_release_grid(self, parent_frame):
        """
        Creates and populates the grid for new release mangas.
        This now only displays mangas from the new_manga_list.
        """
        for widget in parent_frame.winfo_children():
            widget.destroy()

        num_columns = 4

        for col in range(num_columns):
            parent_frame.grid_columnconfigure(col, weight=1)

        if not self.new_release_data:
            no_release_label = ctk.CTkLabel(parent_frame, text="No new releases yet.",
                                            font=ctk.CTkFont(size=16, slant="italic"), text_color="#888")
            no_release_label.grid(row=0, column=0, columnspan=num_columns, pady=20, sticky="nsew")
            parent_frame.grid_rowconfigure(0, weight=1)
            parent_frame.grid_columnconfigure(0, weight=1)
            return

        for idx, manga in enumerate(self.new_release_data):
            if idx >= 4:
                break
            row = 0
            col = idx % num_columns
            self.create_manga_container(parent_frame, manga, row, col)