import customtkinter as ctk
from PIL import Image, ImageDraw, ImageEnhance
from customtkinter import CTkImage
from Homepage.homeBackend import (
    get_mangas, get_popular_manga, get_latest_update, get_user_prof,
    get_genres, get_status_options, get_order_options
)
import os

def make_circle(img):
    size = (min(img.size),) * 2
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    output = Image.new('RGBA', size)
    img = img.resize(size, Image.Resampling.LANCZOS)
    output.paste(img, (0, 0), mask)
    return output


# ===============================================================
#                        Manga Viewer                           
#================================================================
class MangaViewer(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.current_index = 0
        self.auto_switch_delay = 4000

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

        self.read_button = ctk.CTkButton(self.text_container, text="READ", command=self.read_manga,
                                        fg_color="#39ff14", text_color="black", hover_color="#167e03",
                                        font=ctk.CTkFont(size=20,))
        self.read_button.pack(anchor="nw", padx=15, pady=(0,20))

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

        self.title_label.configure(text=manga["title"])
        self.genre_label.configure(text=f"Genre: {manga['genre']}")
        self.summary_label.configure(text=f"Summary: {manga['summary']}")
        self.status_label.configure(text=f"Status: {manga['status']}")
        self.author_label.configure(text=f"Author: {manga['author']}")

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
        print(f"Opening manga: {self.mangas[self.current_index]['title']}")

#=========================================================================================
#            MangaListSection class to display popular and latest manga                  
#=========================================================================================
class MangaListSection(ctk.CTkFrame):
    def __init__(self, parent, show_manga_list_callback):
        super().__init__(parent)
        self.configure(fg_color="transparent")
        self.popular_manga = get_popular_manga()
        self.latest_update = get_latest_update()
        self.show_manga_list_callback = show_manga_list_callback
        self.create_popular_section()
        self.create_latest_update_section()

    def create_popular_section(self):
        label = ctk.CTkLabel(self, text="POPULAR TODAY", font=ctk.CTkFont(size=20, weight="bold"))
        label.grid(row=0, column=0, pady=(0, 15), sticky="w")

        popular_frame = ctk.CTkFrame(self)
        popular_frame.grid(row=1, column=0, pady=(0, 30), sticky="ew")
        popular_frame.grid_columnconfigure(tuple(range(6)), weight=1)

        for idx, manga in enumerate(self.popular_manga):
            container = ctk.CTkFrame(popular_frame, width=155, height=320, corner_radius=8)
            container.grid(row=0, column=idx, padx=5, sticky="nsew")

            try:
                img = Image.open(manga["image"]).resize((140, 190))
                photo = CTkImage(light_image=img, size=(90, 100))
            except Exception:
                photo = None

            img_label = ctk.CTkLabel(container, image=photo, text="")
            img_label.image = photo
            img_label.pack(pady=10)

            name_label = ctk.CTkLabel(container, text=manga["name"], font=ctk.CTkFont(size=16, weight="bold"))
            name_label.pack(pady=(0, 3))
            chapter_label = ctk.CTkLabel(container, text=f"Chapter {manga['chapter']}", font=ctk.CTkFont(size=13))
            chapter_label.pack()

            btn = ctk.CTkButton(container, text="Read Now", width=130, fg_color="#0dfa21", hover_color="#167e03", text_color="black")
            btn.pack(pady=10)

    def create_latest_update_section(self):
        header_frame = ctk.CTkFrame(self)
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

        latest_frame = ctk.CTkFrame(self)
        latest_frame.grid(row=3, column=0, sticky="ew")

        for idx, manga in enumerate(self.latest_update):
            r = idx // 3
            c = idx % 3
            self.create_latest_manga_container(latest_frame, manga, row=r, column=c)

    def create_latest_manga_container(self, parent, manga, row, column):
        container = ctk.CTkFrame(parent, width=280, height=120, corner_radius=8, fg_color="#222222")
        container.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")

        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure((0, 1, 2), weight=1)
        parent.grid_columnconfigure(column, weight=1)

        try:
            img = Image.open(manga["image"]).resize((90, 100))
            photo = CTkImage(light_image=img, size=(90, 100))
        except Exception:
            photo = None

        img_label = ctk.CTkLabel(container, image=photo, text="")
        img_label.image = photo
        img_label.grid(row=0, column=0, rowspan=3, padx=10, pady=10, sticky="ns")

        name_label = ctk.CTkLabel(container, text=manga["name"], font=ctk.CTkFont(size=16, weight="bold"))
        name_label.grid(row=0, column=1, sticky="sw", pady=(15, 0), padx=10)

        chapter_label = ctk.CTkLabel(container, text=f"Chapter {manga['chapter']}", font=ctk.CTkFont(size=14))
        chapter_label.grid(row=1, column=1, sticky="nw", padx=10)

        btn = ctk.CTkButton(container, text="READ", width=80, fg_color="#0dfa21", hover_color="#167e03", text_color="black")
        btn.grid(row=0, column=2, rowspan=3, padx=15, pady=10, sticky="ns")

#==========================================================================================
#                        DashboardPage class to manage the main dashboard UI              
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

        self.genre_option_menu = ctk.CTkOptionMenu(self.filter_inner_frame, values=get_genres())
        self.genre_option_menu.set("Genre")
        self.genre_option_menu.grid(row=0, column=1, padx=5, pady=5)

        self.status_option = ctk.CTkOptionMenu(self.filter_inner_frame, values=get_status_options())
        self.status_option.set("Status")
        self.status_option.grid(row=0, column=2, padx=5, pady=5)

        self.order_option = ctk.CTkOptionMenu(self.filter_inner_frame, values=get_order_options())
        self.order_option.set("Order By Default")
        self.order_option.grid(row=0, column=3, padx=5, pady=5)

        grey_bg = "#4b4848"
        self.genre_option_menu.configure(fg_color=grey_bg)
        self.status_option.configure(fg_color=grey_bg)
        self.order_option.configure(fg_color=grey_bg)

        # ========== MAIN CONTENT AREA ============
        self.content_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.content_container.pack(fill="both", expand=True)

        self.manga_viewer = MangaViewer(self.content_container)
        self.manga_viewer.pack(fill="both", expand=True)

        self.mangalist_section = MangaListSection(self.content_container, show_manga_list_callback=self.show_manga_list)
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

    def show_manga_list(self):
        if hasattr(self.controller, "show_manga_list"):
            self.controller.show_manga_list()