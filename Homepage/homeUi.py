#================================================
#  Note: sa main.py ni rurun ang buong program
#================================================
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageEnhance
from customtkinter import CTkImage
from Homepage.homeBackend import (
    get_mangas, get_popular_manga, get_latest_update,
    get_genres, get_status_options, get_order_options,
    bookmark_manga, remove_bookmark, get_bookmarked_mangas 
)
from SearchPage.searchBackend import search_mangas 
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

        self.mangas = get_mangas()

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

        self.title_label = ctk.CTkLabel(self.text_container, text="", font=ctk.CTkFont(size=30, weight="bold"), anchor="w")
        self.title_label.pack(anchor="nw", pady=(20, 10), padx=15)

        self.genre_label = ctk.CTkLabel(self.text_container, text="", font=ctk.CTkFont(size=20), anchor="w")
        self.genre_label.pack(anchor="nw", pady=(0,10), padx=15)

        self.summary_label = ctk.CTkLabel(self.text_container, text="", font=ctk.CTkFont(size=20), wraplength=450, justify="left", anchor="w")
        self.summary_label.pack(anchor="nw", pady=(0,15), padx=15)

        self.status_label = ctk.CTkLabel(self.text_container, text="", font=ctk.CTkFont(size=20), anchor="w")
        self.status_label.pack(anchor="nw", pady=(0,10), padx=15)

        self.author_label = ctk.CTkLabel(self.text_container, text="", font=ctk.CTkFont(size=20), anchor="w")
        self.author_label.pack(anchor="nw", pady=(0,10), padx=15)

        # self.is_bookmarked = False # This will be set dynamically 
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
        self.bm_button.pack(anchor="nw", padx=15, pady=(0, 20))

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
        self.auto_switch()

    def load_manga(self, index):
        manga = self.mangas[index]
        try:
            img = Image.open(manga["image_path"]).resize((250, 320), Image.Resampling.LANCZOS)
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
        self.genre_label.configure(text=f"Genre: {manga.get('genre', 'N/A')}") 
        self.summary_label.configure(text=f"Summary: {manga.get('summary', 'N/A')}") 
        self.status_label.configure(text=f"Status: {manga.get('status', 'Unknown')}")
        self.author_label.configure(text=f"Author: {manga.get('author', 'N/A')}") 

        # Update bookmark button based on current manga's bookmark status
        bookmarked_mangas = get_bookmarked_mangas()
        self.is_bookmarked = any(bm.get("title") == manga.get("title") for bm in bookmarked_mangas) # Use .get() for consistency
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

    def auto_switch(self):
        self.next_manga()
        self.after(self.auto_switch_delay, self.auto_switch)

    def read_manga(self):
        print(f"Opening manga: {self.mangas[self.current_index].get('title', 'N/A')}") # Use .get()

    def toggle_bookmark(self):
        current_manga = self.mangas[self.current_index]
        if self.is_bookmarked:
            remove_bookmark(current_manga)
            self.is_bookmarked = False
            print(f"❌ Un-bookmarked: {current_manga.get('title', 'N/A')}") # Use .get()
        else:
            bookmark_manga(current_manga)
            self.is_bookmarked = True
            print(f"✅ Bookmarked: {current_manga.get('title', 'N/A')}") # Use .get()
        new_icon = self.bookmark_filled if self.is_bookmarked else self.bookmark_empty
        self.bm_button.configure(image=new_icon)

#=========================================================================================
#           MangaListSection class to display popular and latest manga                  =
#=========================================================================================
class MangaListSection(ctk.CTkFrame):
    def __init__(self, parent, show_manga_list_callback):
        super().__init__(parent)
        self.configure(fg_color="transparent")
        self.controller = None # Will be set by DashboardPage

        # Container with matching padding
        self.main_container = ctk.CTkFrame(self, corner_radius=15, fg_color="transparent")
        self.main_container.pack(fill="x", padx=70, pady=20)

        self.popular_manga = get_popular_manga()
        self.latest_update = get_latest_update()
        self.show_manga_list_callback = show_manga_list_callback

        self.refresh_bookmark_buttons() # Initial call to create sections and set buttons
    #=========================================
    #            Popular manga
    #========================================
    def create_popular_section(self):
        label = ctk.CTkLabel(self.main_container, text="POPULAR TODAY", font=ctk.CTkFont(size=20, weight="bold"))
        label.grid(row=0, column=0, pady=(0, 15), sticky="w")

        popular_frame = ctk.CTkFrame(self.main_container)
        popular_frame.grid(row=1, column=0, pady=(10, 30), sticky="ew")

        for col in range(4):
            popular_frame.grid_columnconfigure(col, weight=0)

        for idx, manga in enumerate(self.popular_manga):
            container = ctk.CTkFrame(popular_frame, corner_radius=8, fg_color="#222222")
            container.grid(row=0, column=idx, padx=20, sticky="n")

            try:
                img = Image.open(manga.get("image", "")).resize((120, 180)) # Use .get() for image path
                photo = CTkImage(light_image=img, size=(120, 180))
            except Exception:
                photo = None

            img_label = ctk.CTkLabel(container, image=photo, text="")
            img_label.image = photo
            img_label.pack(pady=(10, 5))

            name_label = ctk.CTkLabel(container, text=manga.get("name", "N/A"), font=ctk.CTkFont(size=16, weight="bold"))
            name_label.pack(pady=(0, 2))

            chapter_label = ctk.CTkLabel(container, text=f"Chapter {manga.get('chapter', 'N/A')}", font=ctk.CTkFont(size=14))
            chapter_label.pack()

            genre_label = ctk.CTkLabel(container, text=f"Genre: {manga.get('genre', 'N/A')}", font=ctk.CTkFont(size=12))
            genre_label.pack(pady=(2, 0))

            status_label = ctk.CTkLabel(container, text=f"Status: {manga.get('status', 'Unknown')}", font=ctk.CTkFont(size=12)) # Use .get()
            status_label.pack(pady=(0, 5))

            bookmark_empty = CTkImage(light_image=Image.open("image/bookempty.png"), size=(24, 24))
            bookmark_filled = CTkImage(light_image=Image.open("image/bookfilled.png"), size=(24, 24))

            # Check initial bookmark status for each manga
            bookmarked_mangas = get_bookmarked_mangas()
            is_bookmarked = any(bm.get("name") == manga.get("name") for bm in bookmarked_mangas) # Use .get()

            bm_btn = ctk.CTkButton(container, text="BOOKMARK", width=120,
                                 image=bookmark_filled if is_bookmarked else bookmark_empty, # Set initial image
                                 text_color="black", font=ctk.CTkFont(size=14, weight="bold"),
                                 fg_color="#0dfa21", hover_color="#167e03")
            bm_btn.configure(command=lambda btn=bm_btn, m=manga: self.toggle_bookmark_list_item(btn, m))
            bm_btn.pack(pady=(5, 10))

    def toggle_bookmark_list_item(self, btn, manga):
        bookmarked_mangas = get_bookmarked_mangas()
        is_bookmarked = any(bm.get("name") == manga.get("name") for bm in bookmarked_mangas) # Use .get()

        bookmark_empty = CTkImage(light_image=Image.open("image/bookempty.png"), size=(24, 24))
        bookmark_filled = CTkImage(light_image=Image.open("image/bookfilled.png"), size=(24, 24))

        if is_bookmarked:
            remove_bookmark(manga)
            btn.configure(image=bookmark_empty)
            print(f"❌ Un-bookmarked: {manga.get('name', 'N/A')}") # Use .get()
        else:
            bookmark_manga(manga)
            btn.configure(image=bookmark_filled)
            print(f"✅ Bookmarked: {manga.get('name', 'N/A')}") # Use .get()

    #=========================================
    #            Latest update manga
    #=========================================
    def create_latest_update_section(self):
        self.main_container.grid_columnconfigure(0, weight=1)
        header_frame = ctk.CTkFrame(self.main_container)
        header_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=0)

        label = ctk.CTkLabel(header_frame, text="LATEST UPDATE", font=ctk.CTkFont(size=20, weight="bold"))
        label.grid(row=0, column=0, sticky="w")

        view_all_btn = ctk.CTkButton(
            header_frame,
            text="View All",
            width=80,
            fg_color="#0dfa21",
            hover_color="#167e03",
            text_color="black",
            command=self.show_manga_list_callback
        )
        view_all_btn.grid(row=0, column=1, sticky="e")

        latest_frame = ctk.CTkFrame(self.main_container)
        latest_frame.grid(row=3, column=0, sticky="ew")

        for idx, manga in enumerate(self.latest_update):
            r = idx // 3
            c = idx % 3
            self.create_latest_manga_container(latest_frame, manga, row=r, column=c)


    def create_latest_manga_container(self, parent, manga, row, column):
        container = ctk.CTkFrame(parent, width=360, height=180, corner_radius=8, fg_color="#222222")
        container.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")

        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure((0, 1, 2), weight=1)
        parent.grid_columnconfigure(column, weight=1)

        try:
            img = Image.open(manga.get("image", "")).resize((120, 130)) # Use .get()
            photo = CTkImage(light_image=img, size=(120, 130))
        except Exception:
            photo = None

        img_label = ctk.CTkLabel(container, image=photo, text="")
        img_label.image = photo
        img_label.grid(row=0, column=0, rowspan=4, padx=10, pady=10, sticky="ns")

        name_label = ctk.CTkLabel(container, text=manga.get("name", "N/A"), font=ctk.CTkFont(size=16, weight="bold"))
        name_label.grid(row=0, column=1, sticky="sw", pady=(10, 0), padx=10)

        chapter_label = ctk.CTkLabel(container, text=f"Chapter {manga.get('chapter', 'N/A')}", font=ctk.CTkFont(size=14))
        chapter_label.grid(row=1, column=1, sticky="nw", padx=10)

        genre_label = ctk.CTkLabel(container, text=f"Genre: {manga.get('genre', 'N/A')}", font=ctk.CTkFont(size=12))
        genre_label.grid(row=2, column=1, sticky="nw", padx=10)

        status_label = ctk.CTkLabel(container, text=f"Status: {manga.get('status', 'Unknown')}", font=ctk.CTkFont(size=12)) # Use .get()
        status_label.grid(row=3, column=1, sticky="nw", padx=10)

        bookmark_empty = CTkImage(light_image=Image.open("image/bookempty.png"), size=(24, 24))
        bookmark_filled = CTkImage(light_image=Image.open("image/bookfilled.png"), size=(24, 24))

        # Check initial bookmark status for each manga
        bookmarked_mangas = get_bookmarked_mangas()
        is_bookmarked = any(bm.get("name") == manga.get("name") for bm in bookmarked_mangas) # Use .get()

        bookmark_btn = ctk.CTkButton(
            container,
            text="BOOKMARK",
            width=120,
            fg_color="#0dfa21",
            hover_color="#167e03",
            text_color="black",
            image=bookmark_filled if is_bookmarked else bookmark_empty, # Set initial image
            font=ctk.CTkFont(family="Poppins", size=14, weight="bold")
        )
        bookmark_btn.grid(row=4, column=0, padx=10, pady=(0, 10), sticky="w")
        bookmark_btn.configure(command=lambda b=bookmark_btn, m=manga: self.toggle_bookmark_list_item(b, m))

    # New method to refresh the bookmark buttons on the popular and latest sections
    def refresh_bookmark_buttons(self):
        # Clear existing sections
        for widget in self.main_container.winfo_children():
            widget.destroy()
        # Re-create sections to update bookmark states
        self.create_popular_section()
        self.create_latest_update_section()

#==========================================================================================
#           DashboardPage class to manage the main dashboard UI
#==========================================================================================
class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # ========== FILTERS BELOW HEADER =========
        self.filter_row_frame = ctk.CTkFrame(self, fg_color="transparent", height=50)
        self.filter_row_frame.pack(side="top", fill="x", pady=(0, 10))
        self.filter_row_frame.pack_propagate(False)

        self.filter_inner_frame = ctk.CTkFrame(self.filter_row_frame, fg_color="transparent")
        self.filter_inner_frame.place(relx=0.5, rely=0, anchor="n")

        filter_search_icon_path = r"image/glass2.png"
        if os.path.exists(filter_search_icon_path):
            filter_icon_img = Image.open(filter_search_icon_path).resize((25, 25), Image.Resampling.LANCZOS)
            self.filter_search_icon = CTkImage(light_image=filter_icon_img, dark_image=filter_icon_img, size=(25, 25))
        else:
            self.filter_search_icon = None

        self.filter_search_button = ctk.CTkButton(
            self.filter_inner_frame,
            text="Search by title",
            command=self.filter_search_action,
            fg_color="#39ff14",
            hover_color="#1f8112",
            text_color="black",
            corner_radius=10,
            image=self.filter_search_icon,
            compound="left"
        )
        self.filter_search_button.grid(row=0, column=0, padx=5, pady=5)

        self.genre_option_menu = ctk.CTkOptionMenu(self.filter_inner_frame, values=get_genres(), button_color="#26c50a" , button_hover_color="#1f8112")
        self.genre_option_menu.set("Genre")
        self.genre_option_menu.grid(row=0, column=1, padx=5, pady=5)

        self.status_option = ctk.CTkOptionMenu(self.filter_inner_frame, values=get_status_options(), button_color="#26c50a", button_hover_color="#1f8112")
        self.status_option.set("Status")
        self.status_option.grid(row=0, column=2, padx=5, pady=5)

        self.order_option = ctk.CTkOptionMenu(self.filter_inner_frame, values=get_order_options(), button_color="#26c50a", button_hover_color="#1f8112")
        self.order_option.set("Order By Default")
        self.order_option.grid(row=0, column=3, padx=5, pady=5)

        grey_bg = "#4b4848"
        self.genre_option_menu.configure(fg_color=grey_bg)
        self.status_option.configure(fg_color=grey_bg)
        self.order_option.configure(fg_color=grey_bg)

        # ========== MAIN CONTENT AREA WITH SCROLLABLE FRAME ============
        self.content_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.content_container.pack(fill="both", expand=True)

        self.manga_viewer = MangaViewer(self.content_container, controller=self.controller) # Pass controller here
        self.manga_viewer.pack(fill="both", expand=True)

        # Updated to call show_admin directly or ensure show_manga_list calls show_admin
        self.mangalist_section = MangaListSection(self.content_container, show_manga_list_callback=self.controller.show_admin)
        self.mangalist_section.controller = self.controller # Pass controller to MangaListSection
        self.mangalist_section.pack(fill="x", expand=False, pady=10)

        self.home_action()

    # =============================================
    # ========== BUTTON ACTION FUNCTIONS ==========
    # =============================================

    def home_action(self):
        self.filter_row_frame.pack(side="top", fill="x", pady=(0, 10))
        self.content_container.pack(fill="both", expand=True)
        self.genre_option_menu.set("Genre")
        self.status_option.set("Status")
        self.order_option.set("Order By Default")
        self.update_filter_visibility()
        self.controller.title("Dashboard")

    def update_filter_visibility(self):
        self.filter_row_frame.pack(side="top", fill="x", pady=(0, 10))

    def filter_search_action(self):
        print("Filter search button clicked")
        genre = self.genre_option_menu.get()
        status = self.status_option.get()
        order = self.order_option.get()

        # Convert "Genre", "Status", "Order By Default" to None for searchBackend
        genre = None if genre == "Genre" else genre
        status = None if status == "Status" else status
        order = None if order == "Order By Default" else order

        # Initiate the search display (this will navigate to the SearchPage)
        if self.controller and hasattr(self.controller, 'initiate_search_display'):
            self.controller.initiate_search_display(query=None, genre_filter=genre, status_filter=status, order_filter=order)

        # Reset the filter options on the DashboardPage AFTER the search is initiated
        self.genre_option_menu.set("Genre")
        self.status_option.set("Status")
        self.order_option.set("Order By Default")
        print("Filter options reset after search initiation.")

    # New method to refresh bookmark states for all relevant sections
    def refresh_all_bookmark_states(self):
        self.manga_viewer.load_manga(self.manga_viewer.current_index) # Refresh current manga viewer state
        self.mangalist_section.refresh_bookmark_buttons() # Refresh all buttons in lists
