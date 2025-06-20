import customtkinter as ctk
from PIL import Image
from customtkinter import CTkImage
import os
from Homepage.homeBackend import bookmark_manga, remove_bookmark, get_bookmarked_mangas

class SearchPage(ctk.CTkFrame):
    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.configure(fg_color="transparent")
        self.controller = controller

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.results_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.results_frame.pack(fill="both", expand=True)

        self.no_results_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")

        self.no_results_label = ctk.CTkLabel(
            self.no_results_frame, 
            text="No search results found.",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.no_results_label.pack(pady=50)
        self.no_results_frame.pack_forget()  # Hide initially


        self.manga_widgets = [] # To keep track of manga widgets for bookmark refresh

    def display_results(self, results, query=None, genre_filter=None, status_filter=None, order_filter=None):
        # Hide both frames first
        self.no_results_frame.pack_forget()
        self.results_frame.pack_forget()

        # Clear old results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        self.manga_widgets = []

        # If walang query or filter
    def display_results(self, results, query=None, genre_filter=None, status_filter=None, order_filter=None):
        # Hide both frames first
        self.no_results_frame.pack_forget()
        self.results_frame.pack_forget()

        # Clear old results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        self.manga_widgets = []

        # --- Condition 1: Nothing selected or typed ---
        if not query and not genre_filter and not status_filter and not order_filter:
            self.no_results_label.configure(text="Please select a filter or enter a search term.")
            self.no_results_frame.pack(pady=50)
            return

        # --- Condition 2: Search bar is empty (explicitly blank) ---
        if query == "":
            self.no_results_label.configure(text="Please enter a search term.")
            self.no_results_frame.pack(pady=50)
            return

        # --- Condition 3: No results found ---
        if not results:
            if query:
                self.no_results_label.configure(text=f"No results found for '{query}'.")
            else:
                self.no_results_label.configure(text="No matching manga found.")
            self.no_results_frame.pack(pady=50)
            return

        # --- ✅ Show results ---
        self.results_frame.pack(fill="both", expand=True)
        num_columns = 4
        for i, manga in enumerate(results):
            row = i // num_columns
            col = i % num_columns
            self.create_manga_card(self.results_frame, manga, row, col)

        for col in range(num_columns):
            self.results_frame.grid_columnconfigure(col, weight=1)



    def create_manga_card(self, parent, manga_data, row, column):
        card_container = ctk.CTkFrame(parent, corner_radius=8, fg_color="#222222")
        card_container.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")

        try:
            # Check if 'image_path' exists and is valid, otherwise use a placeholder
            image_path = manga_data.get("image_path") or manga_data.get("image") # Account for both keys
            if image_path and os.path.exists(image_path):
                img = Image.open(image_path).resize((150, 220))
                photo = CTkImage(light_image=img, size=(150, 220))
            else:   
                # Fallback for missing image or error
                img = Image.new('RGB', (150, 220), color = 'gray')
                photo = CTkImage(light_image=img, size=(150, 220))
                print(f"Warning: Could not load image for {manga_data.get('title', 'N/A')}. Path: {image_path or 'N/A'}")
        except Exception as e:
            img = Image.new('RGB', (150, 220), color = 'gray')
            photo = CTkImage(light_image=img, size=(150, 220))
            print(f"Error loading image for {manga_data.get('title', 'N/A')}: {e}")


        img_label = ctk.CTkLabel(card_container, image=photo, text="")
        img_label.image = photo
        img_label.pack(pady=(10, 5))

        # Use 'title' or 'name' based on manga data structure
        display_title = manga_data.get("title") or manga_data.get("name", "No Title")
        title_label = ctk.CTkLabel(card_container, text=display_title, font=ctk.CTkFont(size=16, weight="bold"), wraplength=140, justify="center")
        title_label.pack(pady=(0, 5))

        # --- MODIFICATION START ---
        # Add Genre Label
        genre = manga_data.get("genre", "N/A")
        genre_label = ctk.CTkLabel(card_container, text=f"Genre: {genre}", font=ctk.CTkFont(size=12), wraplength=140, justify="center")
        genre_label.pack(pady=(2, 0))

        # Add Status Label
        status = manga_data.get("status", "N/A")
        status_label = ctk.CTkLabel(card_container, text=f"Status: {status}", font=ctk.CTkFont(size=12), wraplength=140, justify="center")
        status_label.pack(pady=(0, 5))
        # --- MODIFICATION END ---

        # Bookmark button
        bookmark_empty = CTkImage(light_image=Image.open("image/bookempty.png"), size=(24, 24))
        bookmark_filled = CTkImage(light_image=Image.open("image/bookfilled.png"), size=(24, 24))

        # Check bookmark state based on either 'title' or 'name'
        bookmarked_mangas = get_bookmarked_mangas()
        is_bookmarked = any(
            (bm.get("title") == manga_data.get("title") and manga_data.get("title") is not None) or
            (bm.get("name") == manga_data.get("name") and manga_data.get("name") is not None)
            for bm in bookmarked_mangas
        )

        bm_btn = ctk.CTkButton(card_container, text="BOOKMARK", width=120,
                            image=bookmark_filled if is_bookmarked else bookmark_empty,
                            text_color="black", font=ctk.CTkFont(size=14, weight="bold"),
                            fg_color="#0dfa21", hover_color="#167e03",
                            command=lambda btn=None, m=manga_data: self.toggle_bookmark_search_item(btn, m))
        bm_btn.pack(pady=(5, 10))
        
        # Store the button reference and manga data for later refresh
        self.manga_widgets.append({"manga": manga_data, "button": bm_btn})


    def toggle_bookmark_search_item(self, btn_widget, manga_data):
        bookmarked_mangas = get_bookmarked_mangas()
        
        # Check if the manga is bookmarked using either 'title' or 'name'
        is_bookmarked = any(
            (bm.get("title") == manga_data.get("title") and manga_data.get("title") is not None) or
            (bm.get("name") == manga_data.get("name") and manga_data.get("name") is not None)
            for bm in bookmarked_mangas
        )

        if is_bookmarked:
            remove_bookmark(manga_data)
            print(f"❌ Un-bookmarked: {manga_data.get('title') or manga_data.get('name')}")
        else:
            bookmark_manga(manga_data)
            print(f"✅ Bookmarked: {manga_data.get('title') or manga_data.get('name')}")
        
        # Call the refresh method on the controller to update all relevant UIs
        if self.controller:
            self.controller.refresh_all_bookmark_related_uis()

    def refresh_bookmark_states(self):
        bookmark_empty = CTkImage(light_image=Image.open("image/bookempty.png"), size=(24, 24))
        bookmark_filled = CTkImage(light_image=Image.open("image/bookfilled.png"), size=(24, 24))
        bookmarked_mangas = get_bookmarked_mangas()

        for item in self.manga_widgets:
            manga_data = item["manga"]
            button = item["button"]
            
            # Check bookmark state based on either 'title' or 'name'
            is_bookmarked = any(
                (bm.get("title") == manga_data.get("title") and manga_data.get("title") is not None) or
                (bm.get("name") == manga_data.get("name") and manga_data.get("name") is not None)
                for bm in bookmarked_mangas
            )
            button.configure(image=bookmark_filled if is_bookmarked else bookmark_empty)