# ComicsUi.py
import customtkinter as ctk
from PIL import Image, ImageDraw
from customtkinter import CTkImage
import os
from datetime import datetime

# === Importing backend functions for manga operations ===
from Comics.ComicsBackend import (
    get_manga_list,
    bookmark_manga_admin,
    remove_bookmark_admin,
    get_new_manga_list # Import this for specific "Added" filter checks if needed by UI
)
from user_model import get_bookmarks_by_email
from users_db import current_session
# Ensure these imports are correct and available
from Homepage.homeBackend import get_genres, get_status_options, get_order_options

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

# === Comics Page UI Class ===
class ComicsPage(ctk.CTkFrame):
    def __init__(self, parent, controller, on_bookmark_change=None):
        super().__init__(parent)
        self.controller = controller
        self.on_bookmark_change = on_bookmark_change

        # === Bookmark icons for toggle ===
        self.bookmark_empty = CTkImage(Image.open("image/bookempty.png").resize((24, 24)))
        self.bookmark_filled = CTkImage(Image.open("image/bookfilled.png").resize((24, 24)))

        # === FILTER ROW CONTAINER ===
        self.filter_row_container = ctk.CTkFrame(self, fg_color="#232323", height=60, corner_radius=10)
        self.filter_row_container.pack(side="top", fill="x", padx=15, pady=(10, 5))
        self.filter_row_container.pack_propagate(False)

        self.filter_row_container.grid_rowconfigure(0, weight=1)
        self.filter_row_container.grid_columnconfigure(0, weight=1)
        self.filter_row_container.grid_columnconfigure(1, weight=0) # For Apply Filters button
        self.filter_row_container.grid_columnconfigure(2, weight=0) # For Remove Filters button
        self.filter_row_container.grid_columnconfigure(3, weight=0) # For Genre dropdown
        self.filter_row_container.grid_columnconfigure(4, weight=0) # For Status dropdown
        self.filter_row_container.grid_columnconfigure(5, weight=0) # For Order dropdown
        self.filter_row_container.grid_columnconfigure(6, weight=1) # Filler space

        filter_search_icon_path = r"image/glass2.png"
        if os.path.exists(filter_search_icon_path):
            filter_icon_img = Image.open(filter_search_icon_path).resize((25, 25), Image.Resampling.LANCZOS)
            self.filter_search_icon = CTkImage(light_image=filter_icon_img, dark_image=filter_icon_img, size=(25, 25))
        else:
            self.filter_search_icon = None

        # --- Apply Filters Button ---
        self.filter_search_button = ctk.CTkButton(
            self.filter_row_container,
            text="Apply Filters",
            command=self.filter_search_action,
            fg_color="#39ff14",
            hover_color="#1f8112",
            text_color="black",
            corner_radius=10,
            image=self.filter_search_icon,
            compound="left"
        )
        self.filter_search_button.grid(row=0, column=1, padx=(5, 10), pady=5, sticky="nsew")

        # --- Remove Filters Button ---
        self.remove_filters_button = ctk.CTkButton(
            self.filter_row_container,
            text="Remove Filters",
            command=self.remove_filters_action,
            fg_color="#ff3914", # A distinct color for remove
            hover_color="#b3270e",
            text_color="white",
            corner_radius=10,
        )
        self.remove_filters_button.grid(row=0, column=2, padx=(0, 15), pady=5, sticky="nsew")

        # --- Genre Option Menu ---
        genres_options = get_genres()
        # Remove any existing 'All' to ensure we add it only once at the beginning
        genres_options = [g for g in genres_options if g.lower() != "all"]
        final_genre_options = ["All"] + sorted(genres_options) # Add "All" first, then sort remaining
        self.genre_option_menu = ctk.CTkOptionMenu(
            self.filter_row_container,
            values=final_genre_options,
            button_color="#26c50a",
            button_hover_color="#1f8112"
        )
        self.genre_option_menu.set("Genre") # Set default display text to "Genre"
        self.genre_option_menu.grid(row=0, column=3, padx=15, pady=5, sticky="nsew")

        # --- Status Option Menu ---
        status_options = get_status_options()
        # Remove any existing 'All' to ensure we add it only once at the beginning
        status_options = [s for s in status_options if s.lower() != "all"]
        final_status_options = ["All"] + sorted(status_options) # Add "All" first, then sort remaining
        self.status_option = ctk.CTkOptionMenu(
            self.filter_row_container,
            values=final_status_options,
            button_color="#26c50a",
            button_hover_color="#1f8112"
        )
        self.status_option.set("Status") # Set default display text to "Status"
        self.status_option.grid(row=0, column=4, padx=15, pady=5, sticky="nsew")

        # --- Order Option Menu ---
        order_options = get_order_options()
        # Define standard orders *without* "Order by" as a selectable option
        standard_orders = ["Default", "Added", "Unupdate", "Update", "Popular", "A-Z", "Z-A"]
        
        final_order_options = []
        for opt in standard_orders:
            if opt not in final_order_options and opt in order_options: # Only add if it's in actual options
                final_order_options.append(opt)
        for opt in order_options: # Add any other custom options that aren't standard
            if opt not in final_order_options:
                final_order_options.append(opt)
        
        self.order_option = ctk.CTkOptionMenu(
            self.filter_row_container,
            values=final_order_options,
            button_color="#26c50a",
            button_hover_color="#1f8112"
        )
        # Set default display text to "Order by" (even if not in selectable values)
        self.order_option.set("Order by") 
        self.order_option.grid(row=0, column=5, padx=15, pady=5, sticky="nsew")

        grey_bg = "#4b4848"
        self.genre_option_menu.configure(fg_color=grey_bg)
        self.status_option.configure(fg_color=grey_bg)
        self.order_option.configure(fg_color=grey_bg)

        # === Scrollable container for all content ===
        self.content_scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.content_scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # === Main Section Title ===
        # Initial text is just "ALL MANGAS"
        self.title_label = ctk.CTkLabel(
            self.content_scrollable_frame, text="ALL MANGAS",
            font=ctk.CTkFont(size=24, weight="bold"), anchor="w"
        )
        self.title_label.pack(pady=(0, 10), anchor="w", fill="x")

        # === Container for Manga Grid ===
        self.main_manga_grid_container = ctk.CTkFrame(self.content_scrollable_frame, fg_color="transparent")
        self.main_manga_grid_container.pack(fill="x", expand=True, pady=(0, 20))

        # === INITIAL LOAD: Load all mangas by default ===
        # This populates the grid, but the title initially won't have a count
        self.manga_data = get_manga_list(is_new_added_filter=False)
        self.create_manga_grid(self.main_manga_grid_container, self.manga_data)
        # No count added to title here, as per your request.
        
    # === Get the current user's bookmarks ===
    def get_user_bookmarks(self):
        email = current_session.get("email")
        if not email:
            return []
        return get_bookmarks_by_email(email)

    # === Create grid display for manga list ===
    def create_manga_grid(self, parent_frame, data_to_display):
        for widget in parent_frame.winfo_children():
            widget.destroy()

        num_columns = 5
        for col in range(num_columns):
            parent_frame.grid_columnconfigure(col, weight=1)

        if not data_to_display:
            # Display a general message in the grid area if no data
            # The title label will handle specific "no mangas found with filters" message
            ctk.CTkLabel(parent_frame, text="No mangas to display in this view.",
                         font=ctk.CTkFont(size=16, slant="italic"),
                         text_color="#888").grid(row=0, column=0, columnspan=num_columns, pady=20)
            return

        for idx, manga in enumerate(data_to_display):
            self.create_manga_container(parent_frame, manga, idx // num_columns, idx % num_columns)

    # === Create individual manga item container ===
    def create_manga_container(self, parent, manga, row, column):
        container = ctk.CTkFrame(parent, width=180, height=380, corner_radius=8, fg_color="#222222")
        container.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
        container.grid_propagate(False)

        # === Manga Image Display ===
        image_path = manga.get("image", "")
        try:
            img = Image.open(image_path).resize((150, 200), Image.Resampling.LANCZOS)
            photo = CTkImage(light_image=img, size=(150, 200))
        except FileNotFoundError:
            print(f"Warning: Image file not found for {manga.get('name')}: {image_path}. Using placeholder.")
            placeholder_path = "image/placeholder.png"
            if os.path.exists(placeholder_path):
                img_placeholder = Image.open(placeholder_path).resize((150, 200), Image.Resampling.LANCZOS)
                photo = CTkImage(light_image=img_placeholder, size=(150, 200))
            else:
                photo = None
        except Exception as e:
            print(f"Error loading image for {manga.get('name')}: {e}")
            photo = None

        ctk.CTkLabel(container, image=photo, text="").pack(pady=(10, 5))
        ctk.CTkLabel(container, text=manga["name"], font=ctk.CTkFont(size=14, weight="bold"), wraplength=160, justify="center").pack(pady=(0, 2))
        ctk.CTkLabel(container, text=f"Chapter {manga['chapter']}", font=ctk.CTkFont(size=12)).pack()

        ctk.CTkLabel(container, text=f"Desc: {manga.get('description', 'N/A')}",
                                     font=ctk.CTkFont(size=10), wraplength=160, justify="center").pack(pady=(2,0))
        ctk.CTkLabel(container, text=f"Author: {manga.get('author', 'N/A')}",
                                     font=ctk.CTkFont(size=10)).pack(pady=(2,0))

        ctk.CTkLabel(container, text=f"Genre: {manga['genre']}", font=ctk.CTkFont(size=10)).pack()
        ctk.CTkLabel(container, text=f"Status: {manga['status']}", font=ctk.CTkFont(size=10)).pack()

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
        bm_btn.configure(command=lambda m=manga: self.toggle_bookmark_admin(bm_btn, m))

    # --- Action to apply filters ---
    def filter_search_action(self):
        genre = self.genre_option_menu.get()
        status = self.status_option.get()
        order = self.order_option.get()

        # Determine actual filters to send to backend
        genre_filter_param = None if genre == "All" or genre == "Genre" else genre
        status_filter_param = None if status == "All" or status == "Status" else status 
        order_filter_param = None if order == "Default" or order == "Order by" else order 
        
        # Check if any filter is actually active
        filters_active = any([
            genre_filter_param is not None,
            status_filter_param is not None,
            order_filter_param is not None and order_filter_param != "Default"
        ])


        # === ========== UI LOGIC PARA SA "ADDED" FILTER PARAMETER AT SPECIFIC STATUS OVERRIDES ========== ===
        is_new_added_filter_param = False # Default to false

        if order_filter_param == "Added":
            is_new_added_filter_param = True 
            status_filter_param = None 
            genre_filter_param = None 
        elif order_filter_param == "Popular":
            status_filter_param = "completed" # UI sets status filter for Popular
        elif order_filter_param == "Update":
            status_filter_param = "ongoing" # UI sets status filter for Update
        elif order_filter_param == "Unupdate":
            status_filter_param = ["hiatus", "completed"] # UI sets specific statuses for Unupdate
        # === ========== END UI LOGIC ========== ===

        print(f"Applying filters: Genre={genre_filter_param}, Status={status_filter_param}, Order={order_filter_param}, IsNewAdded={is_new_added_filter_param}")

        filtered_mangas = get_manga_list(
            genre_filter=genre_filter_param,
            status_filter=status_filter_param, # Status filter is now set by UI for these specific orders
            order_filter=order_filter_param,
            is_new_added_filter=is_new_added_filter_param 
        )

        self.manga_data = filtered_mangas
        self.create_manga_grid(self.main_manga_grid_container, self.manga_data)

        # === ========== TITLE LABEL UPDATE LOGIC ========== ===
        if not filters_active and not is_new_added_filter_param:
            # If no filters were actually chosen (all dropdowns are default), just show "ALL MANGAS"
            self.title_label.configure(text="ALL MANGAS")
        elif not filtered_mangas:
            if order_filter_param == "Added":
                self.title_label.configure(text="NO NEWLY ADDED MANGAS YET")
            else:
                self.title_label.configure(text="NO MANGAS FOUND WITH APPLIED FILTERS")
        else:
            # When filters are applied and results exist, show "ALL MANGAS (X results)"
            self.title_label.configure(text=f"ALL MANGAS ({len(filtered_mangas)} results)")
        # === ========== END TITLE LABEL UPDATE LOGIC ========== ===


    # --- Action to remove/reset filters ---
    def remove_filters_action(self):
        # Reset dropdowns to default values
        self.genre_option_menu.set("Genre")
        self.status_option.set("Status")
        self.order_option.set("Order by") 
        
        print("Removing all filters and refreshing manga list.")
        # Call the backend function without any filters (all None), but with is_new_added_filter=False
        # This will load all mangas from DB.
        self.manga_data = get_manga_list(is_new_added_filter=False)
        self.create_manga_grid(self.main_manga_grid_container, self.manga_data)

        # When filters are removed, display "ALL MANGAS" without the count
        self.title_label.configure(text="ALL MANGAS")


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

    # === Refresh the entire manga list (now from DB) and update bookmark states ===
    def refresh_Comics_bookmark_states(self):
        # Re-apply current filters after a bookmark change
        current_genre = self.genre_option_menu.get()
        current_status = self.status_option.get()
        current_order = self.order_option.get()

        genre_filter_param = None if current_genre == "All" or current_genre == "Genre" else current_genre
        status_filter_param = None if current_status == "All" or current_status == "Status" else current_status
        order_filter_param = None if current_order == "Default" or current_order == "Order by" else current_order 

        # Check if any filter is actually active for the refresh logic
        filters_active = any([
            genre_filter_param is not None,
            status_filter_param is not None,
            order_filter_param is not None and order_filter_param != "Default"
        ])

        # === ========== UI LOGIC PARA SA "ADDED" FILTER PARAMETER AT SPECIFIC STATUS OVERRIDES SA REFRESH ========== ===
        is_new_added_filter_param = False 

        if order_filter_param == "Added":
            is_new_added_filter_param = True 
            status_filter_param = None 
            genre_filter_param = None 
        elif order_filter_param == "Popular":
            status_filter_param = "completed" 
        elif order_filter_param == "Update":
            status_filter_param = "ongoing" 
        elif order_filter_param == "Unupdate":
            status_filter_param = ["hiatus", "completed"] 
        # === ========== END UI LOGIC ========== ===

        self.manga_data = get_manga_list(
            genre_filter=genre_filter_param,
            status_filter=status_filter_param, # Status filter is now set by UI for these specific orders
            order_filter=order_filter_param,
            is_new_added_filter=is_new_added_filter_param 
        )
        self.create_manga_grid(self.main_manga_grid_container, self.manga_data)

        # === ========== TITLE LABEL UPDATE LOGIC SA REFRESH ========== ===
        if not filters_active and not is_new_added_filter_param:
            # If no filters were actually chosen, just show "ALL MANGAS"
            self.title_label.configure(text="ALL MANGAS")
        elif not self.manga_data:
            if order_filter_param == "Added":
                self.title_label.configure(text="NO NEWLY ADDED MANGAS YET")
            else:
                self.title_label.configure(text="NO MANGAS FOUND WITH APPLIED FILTERS")
        else:
            # When filters are applied and results exist, show "ALL MANGAS (X results)"
            self.title_label.configure(text=f"ALL MANGAS ({len(self.manga_data)} results)")
        # === ========== END TITLE LABEL UPDATE LOGIC SA REFRESH ========== ===