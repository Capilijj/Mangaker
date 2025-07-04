import customtkinter as ctk
from PIL import Image
from customtkinter import CTkImage
import os
from Homepage.homeBackend import bookmark_manga, remove_bookmark, get_bookmarked_mangas
from SearchPage.searchBackend import search_mangas
from users_db import current_session

def _clean_manga_text(text):
    if text is None:
        return ""
    s_text = str(text).strip()
    if s_text.lower() == "n/a":
        return ""
    return s_text

class SearchPage(ctk.CTkFrame):
    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.configure(fg_color="transparent")
        self.controller = controller

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.pack(fill="both", expand=True, padx=5, pady=20)

        self.no_results_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.no_results_label = ctk.CTkLabel(
            self.no_results_frame,
            text="No search results found.",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.no_results_label.pack(pady=50)
        self.no_results_frame.pack_forget()

        self.manga_widgets = []

        try:
            self.bookmark_empty = CTkImage(light_image=Image.open("image/bookempty.png"), size=(24, 24))
            self.bookmark_filled = CTkImage(light_image=Image.open("image/bookfilled.png"), size=(24, 24))
        except FileNotFoundError:
            self.bookmark_empty = None
            self.bookmark_filled = None

    def display_search_results(self, query=None):
        print(f"Initiating search with query='{query}'")
        results = search_mangas(query=query)
        self.display_results(results, query=query)

    def display_results(self, mangas, query=None):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.manga_widgets.clear()

        if not mangas:
            self.no_results_frame.pack(fill="both", expand=True)
            return
        else:
            self.no_results_frame.pack_forget()

        num_columns = 4
        for index, manga_data in enumerate(mangas):
            row = index // num_columns
            col = index % num_columns

            manga_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="#242424", corner_radius=10)
            manga_frame.grid(row=row, column=col, padx=12, pady=18, sticky="nsew")
            manga_frame.grid_columnconfigure(0, weight=1)

            image_path = manga_data.get("image_path") or manga_data.get("image")
            if image_path and os.path.exists(image_path):
                img = Image.open(image_path)
                img = img.resize((150, 200), Image.Resampling.LANCZOS)
                manga_img = CTkImage(light_image=img, size=(150, 200))
                img_label = ctk.CTkLabel(manga_frame, image=manga_img, text="")
                img_label.image = manga_img
                img_label.grid(row=0, column=0, pady=(10, 5))
            else:
                placeholder_label = ctk.CTkLabel(manga_frame, text="No Image", width=150, height=200, fg_color="#333333")
                placeholder_label.grid(row=0, column=0, pady=(10, 5))

            title = _clean_manga_text(manga_data.get("title") or manga_data.get("name", ""))
            chapter = _clean_manga_text(manga_data.get("chapter", ""))
            genre = _clean_manga_text(manga_data.get("genre", ""))
            status = _clean_manga_text(manga_data.get("status", ""))
            author = _clean_manga_text(manga_data.get("author", ""))
            description = _clean_manga_text(manga_data.get("summary") or manga_data.get("desc") or manga_data.get("description", ""))

            row_idx = 1

            if title:
                ctk.CTkLabel(manga_frame, text=title, font=ctk.CTkFont(size=14, weight="bold"), wraplength=140).grid(row=row_idx, column=0, pady=(0, 2), sticky="ew")
            row_idx += 1

            if chapter:
                ctk.CTkLabel(manga_frame, text=f"Chapter: {chapter}", font=ctk.CTkFont(size=12), wraplength=140).grid(row=row_idx, column=0, pady=(0, 2), sticky="ew")
            row_idx += 1

            if description:
                ctk.CTkLabel(manga_frame, text=f"Desc: {description}", font=ctk.CTkFont(size=12), wraplength=140, justify="left").grid(row=row_idx, column=0, pady=(0, 2), sticky="ew")
            row_idx += 1

            if author:
                ctk.CTkLabel(manga_frame, text=f"Author: {author}", font=ctk.CTkFont(size=12), wraplength=140).grid(row=row_idx, column=0, pady=(0, 2), sticky="ew")
            row_idx += 1

            if genre:
                ctk.CTkLabel(manga_frame, text=f"Genre: {genre}", font=ctk.CTkFont(size=12), wraplength=140).grid(row=row_idx, column=0, pady=(0, 2), sticky="ew")
            row_idx += 1

            if status:
                ctk.CTkLabel(manga_frame, text=f"Status: {status}", font=ctk.CTkFont(size=12), wraplength=140).grid(row=row_idx, column=0, pady=(0, 5), sticky="ew")
            row_idx += 1

            manga_frame.grid_rowconfigure(row_idx, weight=1)
            row_idx += 1

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
            bookmark_btn.grid(row=row_idx, column=0, pady=(5, 10), sticky="s")
            bookmark_btn.configure(command=lambda m=manga_data, b=bookmark_btn: self.toggle_bookmark(m, b))

            self.manga_widgets.append({"manga": manga_data, "button": bookmark_btn})

    def is_bookmarked(self, manga_data):
        email = current_session.get("email")
        if not email:
            return False
        bookmarked_manga_list = get_bookmarked_mangas()
        bookmarked_identifiers = set()
        for bm_manga in bookmarked_manga_list:
            bm_identifier = (_clean_manga_text(bm_manga.get("title")) or _clean_manga_text(bm_manga.get("name")) or "").lower()
            if bm_identifier:
                bookmarked_identifiers.add(bm_identifier)
        manga_identifier = (_clean_manga_text(manga_data.get("title")) or _clean_manga_text(manga_data.get("name")) or "").lower()
        return manga_identifier in bookmarked_identifiers

    def toggle_bookmark(self, manga_data, button):
        manga_identifier = _clean_manga_text(manga_data.get("title") or manga_data.get("name"))
        if not manga_identifier:
            print("Error: Manga data missing 'title' or 'name' for bookmarking.")
            return
        email = current_session.get("email")
        if not email:
            print("No user logged in to bookmark.")
            return
        if self.is_bookmarked(manga_data):
            remove_bookmark(manga_data)
            print(f"❌ Un-bookmarked: {manga_identifier}")
            button.configure(image=self.bookmark_empty)
        else:
            bookmark_manga(manga_data)
            print(f"✅ Bookmarked: {manga_identifier}")
            button.configure(image=self.bookmark_filled)
        if self.controller and hasattr(self.controller, 'refresh_all_bookmark_related_uis'):
            self.controller.refresh_all_bookmark_related_uis()

    def refresh_bookmark_states(self):
        print("Refreshing bookmark icons in SearchPage...")
        for item in self.manga_widgets:
            manga_data = item["manga"]
            button = item["button"]
            if self.is_bookmarked(manga_data):
                button.configure(image=self.bookmark_filled)
            else:
                button.configure(image=self.bookmark_empty)