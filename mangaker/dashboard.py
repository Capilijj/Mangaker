import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw, ImageEnhance
from backend2 import get_mangas
import os
from bookmark import BookmarkPage
from profile import ProfilePage

# Helper to crop image in a circular shape
def make_circle(img):
    size = (min(img.size),) * 2
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    output = Image.new('RGBA', size)
    img = img.resize(size, Image.Resampling.LANCZOS)
    output.paste(img, (0, 0), mask)
    return output

class MangaViewer(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.current_index = 0
        self.auto_switch_delay = 6000

        self.mangas = get_mangas()  # Call the function to get the list

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
        self.after(self.auto_switch_delay, self.auto_switch)

    def load_manga(self, index):
        manga = self.mangas[index]
        try:
            img = Image.open(manga["image_path"]).resize((250, 320), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.image_label.configure(image=photo, text="")
            self.image_label.image = photo

            enhancer = ImageEnhance.Brightness(img)
            dark_img = enhancer.enhance(0.2)
            container_width = self.container.winfo_width()
            container_height = self.container.winfo_height()

            if container_width < 1 or container_height < 1:
                return

            dark_img_resized = dark_img.resize((container_width, container_height), Image.Resampling.LANCZOS)
            dark_photo = ImageTk.PhotoImage(dark_img_resized)
            self.bg_label.configure(image=dark_photo)
            self.bg_label.image = dark_photo
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


class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.active_button = None

        # Top container
        self.top_container = ctk.CTkFrame(self, height=60, fg_color="#39ff14", corner_radius=15)
        self.top_container.pack(side="top", fill="x", pady=10, padx=10)

        # Circle logo with no background frame
        try:
            self.logo_img = Image.open(r"image/mangaker.jpg")
            self.logo_img = self.logo_img.resize((40, 40), Image.Resampling.LANCZOS)
            self.logo_img = make_circle(self.logo_img)
            self.logo_photo = ImageTk.PhotoImage(self.logo_img)
            self.logo = ctk.CTkLabel(self.top_container, image=self.logo_photo, text="")
            self.logo.pack(side="left", padx=15, pady=10)
        except Exception as e:
            print("Logo loading failed:", e)

        # Common style for buttons
        button_style = {
            "fg_color": "#39ff14",
            "hover_color": "#1f8112",
            "text_color": "black",
            "corner_radius": 10,
        }

        # Navigation buttons
        self.home_button = ctk.CTkButton(self.top_container, text="Home", command=self.home_action, **button_style)
        self.home_button.pack(side="left", padx=10, pady=10)

        self.bookmark_button = ctk.CTkButton(self.top_container, text="Bookmark", command=self.bookmark_action, **button_style)
        self.bookmark_button.pack(side="left", padx=10, pady=10)

        self.profile_button = ctk.CTkButton(self.top_container, text="Profile", command=self.profile_action, **button_style)
        self.profile_button.pack(side="left", padx=10, pady=10)

        # Search bar setup
        self.search_frame = ctk.CTkFrame(self.top_container, width=240, height=36)
        self.search_frame.pack(side="right", pady=10, padx=10)
        self.search_frame.pack_propagate(False)

        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Search...")
        self.search_entry.pack(side="left", fill="both", expand=True)
        self.search_entry.bind("<Return>", self.on_enter_pressed)

        # Search icon for main search (glass1.gif)
        main_search_icon_path = r"image/glass1.gif"
        if os.path.exists(main_search_icon_path):
            main_icon_img = Image.open(main_search_icon_path).resize((25, 25), Image.Resampling.LANCZOS)
            self.search_icon = ImageTk.PhotoImage(main_icon_img)
        else:
            self.search_icon = None
            print(f"Image not found: {main_search_icon_path}")

        self.search_icon_button = ctk.CTkButton(
            self.search_frame,
            image=self.search_icon,
            width=36,
            height=36,
            fg_color="#FFFFFF",
            corner_radius=0,
            text="",
        )
        self.search_icon_button.pack(side="right")

        # --- Filter row frame below top_container ---
        self.filter_row_frame = ctk.CTkFrame(self, fg_color="transparent", height=50)
        self.filter_row_frame.pack(side="top", fill="x", pady=(0, 10))
        self.filter_row_frame.pack_propagate(False)  # fix height so it doesn't shrink

        # Inner frame to hold filter widgets centered horizontally
        self.filter_inner_frame = ctk.CTkFrame(self.filter_row_frame, fg_color="transparent")
        self.filter_inner_frame.place(relx=0.5, rely=0, anchor="n")

        # Filter search BUTTON (with separate image glass2.png)
        filter_search_icon_path = r"image/glass2.png"
        if os.path.exists(filter_search_icon_path):
            filter_icon_img = Image.open(filter_search_icon_path).resize((25, 25), Image.Resampling.LANCZOS)
            self.filter_search_icon = ImageTk.PhotoImage(filter_icon_img)
        else:
            self.filter_search_icon = None
            print(f"Image not found: {filter_search_icon_path}")

        if self.filter_search_icon is not None:
            self.filter_search_button = ctk.CTkButton(
                self.filter_inner_frame,
                text="Search by title",
                image=self.filter_search_icon,
                compound="left",
                fg_color="#39ff14",
                hover_color="#1f8112",
                text_color="black",
                corner_radius=10,
            )
        else:
            self.filter_search_button = ctk.CTkButton(
                self.filter_inner_frame,
                text="Search by title",
                command=self.filter_search_action,
                fg_color="#39ff14",
                hover_color="#1f8112",
                text_color="black",
                corner_radius=10,
            )
        # Use grid for filter widgets now
        self.filter_search_button.grid(row=0, column=0, padx=5, pady=5)

        # Expanded list of manga genres for dropdown
        self.genres = [
            "Action", "Adventure", "Comedy", "Drama", "Fantasy", "Romance",
            "Shounen", "Shoujo", "Seinen", "Josei", "Sci-Fi", "Horror",
            "Sports", "Slice of Life", "Mystery", "Mecha", "Supernatural",
            "Historical", "Ecchi", "Isekai"
        ]

        # Genre single-select dropdown
        self.genre_option_menu = ctk.CTkOptionMenu(self.filter_inner_frame, values=self.genres)
        self.genre_option_menu.set("Genre")
        self.genre_option_menu.grid(row=0, column=1, padx=5, pady=5)

        # Status dropdown (single select)
        self.status_option = ctk.CTkOptionMenu(self.filter_inner_frame, values=["All", "Ongoing", "Completed", "Hiatus"])
        self.status_option.set("Status")
        self.status_option.grid(row=0, column=2, padx=5, pady=5)

        # Order by dropdown (single select)
        self.order_option = ctk.CTkOptionMenu(self.filter_inner_frame, values=["Popular", "A-Z" , "Z-A", "Update", "Added"])
        self.order_option.set("Order By Default")
        self.order_option.grid(row=0, column=3, padx=5, pady=5)

        # Change dropdown backgrounds to grey (#4b4848)
        grey_bg = "#4b4848"
        self.genre_option_menu.configure(fg_color=grey_bg)
        self.status_option.configure(fg_color=grey_bg)
        self.order_option.configure(fg_color=grey_bg)

        self.content_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.content_container.pack(fill="both", expand=True)
        
        self.manga_viewer = MangaViewer(self.content_container)
        self.manga_viewer.pack(fill="both", expand=True)
        
        # Bookmark and Profile containers (start hidden)
        self.bookmark_container = ctk.CTkFrame(self)
        self.profile_container = ctk.CTkFrame(self)
        # Add more content below the manga viewer inside the scrollable container
        self.extra_label = ctk.CTkLabel(self.content_container, text="More Content Below Manga Viewer", font=ctk.CTkFont(size=20))
        self.extra_label.pack(pady=20)

        # Example: add a button below that
        self.extra_button = ctk.CTkButton(self.content_container, text="Extra Button", command=lambda: print("Extra Button Clicked"))
        self.extra_button.pack(pady=10)

        # Initialize pages inside containers
        self.bookmark_page = BookmarkPage(self.bookmark_container)
        self.bookmark_page.pack(fill="both", expand=True)

        self.profile_page = ProfilePage(self.profile_container)
        self.profile_page.pack(fill="both", expand=True)

        # Set Home button active by default
        self.home_action()

    def set_active_button(self, active_btn):
        for btn in [self.home_button, self.bookmark_button, self.profile_button]:
            btn.configure(border_color="black", border_width=0)
        active_btn.configure(border_color="black", border_width=2)
        self.active_button = active_btn

    def home_action(self):
        self.set_active_button(self.home_button)
        self.bookmark_container.pack_forget()
        self.profile_container.pack_forget()

        # Pack filter row and content container in correct order
        self.filter_row_frame.pack(side="top", fill="x", pady=(0, 10))
        self.content_container.pack(fill="both", expand=True)

        # Reset search and filters
        self.search_entry.delete(0, "end")
        self.genre_option_menu.set("Genre")
        self.status_option.set("Status")
        self.order_option.set("Order By Default")
        self.update_filter_visibility()
        self.controller.title("Home")

    def bookmark_action(self):
        self.set_active_button(self.bookmark_button)
        self.content_container.pack_forget()
        self.profile_container.pack_forget()
        self.filter_row_frame.pack_forget()
        self.bookmark_container.pack(fill="both", expand=True)
        self.update_filter_visibility()
        self.controller.title("Bookmarks")

    def profile_action(self):
        self.set_active_button(self.profile_button)
        self.content_container.pack_forget()
        self.bookmark_container.pack_forget()
        self.filter_row_frame.pack_forget()
        self.profile_container.pack(fill="both", expand=True)
        self.update_filter_visibility()
        self.controller.title("Profile")  
        
    def update_filter_visibility(self):
        if self.active_button == self.home_button:
            # Show filter widgets
            for idx, widget in enumerate(self.filter_inner_frame.winfo_children()):
                widget.grid(row=0, column=idx, padx=5, pady=5)
        else:
            # Hide filter widgets
            for widget in self.filter_inner_frame.winfo_children():
                widget.grid_remove()

    def on_enter_pressed(self, event):
        search_text = self.search_entry.get()
        print(f"Search entered: {search_text}")

    def filter_search_action(self):
        print("Filter search button clicked")

# Run the app
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Dashboard test")
        self.geometry("600x700")

        self.dashboard = DashboardPage(self, controller=self)
        self.dashboard.pack(fill="both", expand=True)
    

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("green")
    app = App()
    app.mainloop()
