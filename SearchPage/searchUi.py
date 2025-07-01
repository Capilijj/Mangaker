# searchUi.py 
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

        # ==== Layout Config ====
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ==== Scrollable Frame ====
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # ==== Frame for search results ====
        self.results_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.results_frame.pack(fill="both", expand=True)

        # ==== Frame for "No Results" message ====
        self.no_results_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")

        self.no_results_label = ctk.CTkLabel(
            self.no_results_frame,
            text="No search results found.",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.no_results_label.pack(pady=50)
        self.no_results_frame.pack_forget()

        # ==== Internal State ====
        self.manga_widgets = []

        # ==== Bookmark Icons ====
        self.bookmark_empty = CTkImage(light_image=Image.open("image/bookempty.png"), size=(24, 24))
        self.bookmark_filled = CTkImage(light_image=Image.open("image/bookfilled.png"), size=(24, 24))

    def display_results(self, mangas, **kwargs):
        # ==== Reset scrollbar position to top ====
        self.scrollable_frame._parent_canvas.yview_moveto(0)

        # ==== Store for potential future redraw ====
        self.last_results = mangas

        # ==== Clear old results ====
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        self.manga_widgets = []

        # ==== Handle no results ====
        if not mangas:
            self.no_results_frame.pack(pady=50)
            self.results_frame.pack_forget()
            return

        # ==== Display results ====
        self.no_results_frame.pack_forget()
        self.results_frame.pack(fill="both", expand=True)

        # ==== Layout configuration ====
        num_columns = 4
        for col in range(num_columns):
            self.results_frame.grid_columnconfigure(col, weight=1)

        # ==== Render manga cards ====
        for index, manga_data in enumerate(mangas):
            row = index // num_columns
            col = index % num_columns

            manga_frame = ctk.CTkFrame(self.results_frame, fg_color="#242424", corner_radius=10)
            manga_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            # ==== Manga Image ====
            image_path = manga_data.get("image_path") or manga_data.get("image")
            if image_path and os.path.exists(image_path):
                img = Image.open(image_path)
                img = img.resize((150, 200), Image.LANCZOS)
                manga_img = CTkImage(light_image=img, size=(150, 200))
                img_label = ctk.CTkLabel(manga_frame, image=manga_img, text="")
                img_label.image = manga_img
                img_label.pack(pady=10)
            else:
                placeholder_label = ctk.CTkLabel(manga_frame, text="No Image", width=150, height=200, fg_color="#333333")
                placeholder_label.pack(pady=10)

            # ==== Manga Info ====
            title = manga_data.get("title") or manga_data.get("name", "N/A")
            genre = manga_data.get("genre", "N/A")
            status = manga_data.get("status", "N/A")

            ctk.CTkLabel(manga_frame, text=title, font=ctk.CTkFont(size=14, weight="bold"), wraplength=140).pack(pady=(0, 5))
            ctk.CTkLabel(manga_frame, text=f"Genre: {genre}", font=ctk.CTkFont(size=12), wraplength=140).pack(pady=(0, 5))
            ctk.CTkLabel(manga_frame, text=f"Status: {status}", font=ctk.CTkFont(size=12), wraplength=140).pack(pady=(0, 5))

            # ==== Bookmark Button ====
            manga_identifier = title
            is_bookmarked = self.is_bookmarked(manga_data)

            bookmark_btn = ctk.CTkButton(
                manga_frame,
                text="BOOKMARK",
                width=120,
                fg_color="#0dfa21",
                hover_color="#167e03",
                text_color="black",
                image=self.bookmark_filled if is_bookmarked else self.bookmark_empty,
                font=ctk.CTkFont(family="Poppins", size=14, weight="bold")
            )
            bookmark_btn.pack(pady=(5, 10))
            bookmark_btn.configure(command=lambda m=manga_data, b=bookmark_btn: self.toggle_bookmark(m, b))

            # ==== Track for bookmark state refresh ====
            self.manga_widgets.append({"manga": manga_data, "button": bookmark_btn})

    def is_bookmarked(self, manga_data):
        # ==== Unified bookmark checker ====
        bookmarked_mangas = get_bookmarked_mangas()
        identifiers = set()
        for bm in bookmarked_mangas:
            identifiers.add((bm.get("title") or bm.get("name") or "").strip().lower())

        manga_identifier = (manga_data.get("title") or manga_data.get("name") or "").strip().lower()
        return manga_identifier in identifiers

    def toggle_bookmark(self, manga_data, button):
        # ==== Toggle bookmark state and icon ====
        manga_identifier = manga_data.get("title") or manga_data.get("name")
        if not manga_identifier:
            print("Error: Manga data missing 'title' or 'name' for bookmarking.")
            return

        if self.is_bookmarked(manga_data):
            remove_bookmark(manga_data)
            print(f"❌ Un-bookmarked: {manga_identifier}")
            button.configure(image=self.bookmark_empty)
        else:
            bookmark_manga(manga_data)
            print(f"✅ Bookmarked: {manga_identifier}")
            button.configure(image=self.bookmark_filled)

        # ==== Notify controller for global refresh ====
        if self.controller and hasattr(self.controller, 'refresh_all_bookmark_related_uis'):
            self.controller.refresh_all_bookmark_related_uis()

    def refresh_bookmark_states(self):
        # ==== Refresh bookmark icons based on latest state ====
        print("Refreshing bookmark icons in SearchPage...")
        for item in self.manga_widgets:
            manga_data = item["manga"]
            button = item["button"]
            if self.is_bookmarked(manga_data):
                button.configure(image=self.bookmark_filled)
            else:
                button.configure(image=self.bookmark_empty)
