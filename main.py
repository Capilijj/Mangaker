# main.py
# ==================== Imports ====================
import customtkinter as ctk
from Login.loginUi import LoginPage
from SignUp.signUpUi import SignUpPage
from Forgot_pass.forgotUi import ForgotPasswordPage
from Homepage.homeUi import DashboardPage
from Profile.profileUi import ProfilePage
from Homepage.homeBackend import get_user_prof
from SearchPage.searchBackend import search_mangas
from Admin.adminUi import AdminPage
from Bookmark.bookmarkUi import BookmarkPage
from SearchPage.searchUi import SearchPage

from PIL import Image, ImageDraw
from customtkinter import CTkImage
import os
import sqlite3

# =========================================================================================
#                          Function to make the image Circle
# =========================================================================================
def make_circle(img):
    size = (min(img.size),) * 2
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    output = Image.new('RGBA', size)
    img = img.resize(size, Image.Resampling.LANCZOS)
    output.paste(img, (0, 0), mask)
    return output

# =========================================================================================
#                           Top Navigation Bar Header
# =========================================================================================
class TopBar(ctk.CTkFrame):
    def __init__(self, parent, on_home, on_bookmark, on_comics, on_profile, on_search=None):
        super().__init__(parent, height=60, fg_color="#39ff14", corner_radius=15)
        self.on_profile = on_profile
        self.on_search_callback = on_search # Store the search callback

        # Right-side container for search and bell Icon
        self.right_container = ctk.CTkFrame(self, fg_color="transparent")
        self.right_container.pack(side="right", padx=10, pady=10)

        # Left-side container for profile icon
        self.left_container = ctk.CTkFrame(self, fg_color="transparent")
        self.left_container.pack(side="left", padx=10, pady=10)

        # Profile Icon, clickable to show profile page
        self.user_icon_label = ctk.CTkLabel(self.left_container, text="")
        self.user_icon_label.pack(side="left", padx=(10, 0))
        self.user_icon_label.bind("<Button-1>", lambda e: self.on_profile())
        self.refresh_profile_icon()

        # Navigation Buttons
        button_style = {
            "fg_color": "#39ff14",
            "hover_color": "#1f8112",
            "text_color": "black",
            "corner_radius": 10,
        }

        # Button widget -Home, Bookmark, Comics, Profile
        self.home_button = ctk.CTkButton(self, text="Home", command=on_home, **button_style)
        self.home_button.pack(side="left", padx=10, pady=10)

        self.bookmark_button = ctk.CTkButton(self, text="Bookmark", command=on_bookmark, **button_style)
        self.bookmark_button.pack(side="left", padx=10, pady=10)

        self.comics_button = ctk.CTkButton(self, text="Comics", command=on_comics, **button_style)
        self.comics_button.pack(side="left", padx=10, pady=10)

        self.profile_button = ctk.CTkButton(self, text="Profile", command=on_profile, **button_style)
        self.profile_button.pack(side="left", padx=10, pady=10)

        # Store buttons for easy access to manage active state
        self.buttons = {
            "home": self.home_button,
            "bookmark": self.bookmark_button,
            "comics": self.comics_button,
            "profile": self.profile_button
        }
        self.active_button = None

        # === Bell Icon (clickable, circle, hoverable) ===
        bell_path = "image/bell.png"
        if os.path.exists(bell_path):
            bell_img = Image.open(bell_path).resize((40, 40), Image.Resampling.LANCZOS)
            circle_bell = make_circle(bell_img) # Apply circular mask to bell image
            self.bell_icon_img = CTkImage(light_image=circle_bell, dark_image=circle_bell, size=(40, 40))
        else:
            self.bell_icon_img = None
            print("Bell image not found!")

        self.bell_label = ctk.CTkLabel(self.right_container, image=self.bell_icon_img, text="")
        self.bell_label.pack(side="left", padx=(5, 10))

        # --- REMOVED: Notification count label ---
        # self.notif_count_label = ctk.CTkLabel(...)
        # self.notif_count_label.place(...)
        # self.update_notification_count(0) # Removed this call

        # Connect bell click to show dialog
        self.bell_label.bind("<Button-1>", lambda e: self.show_notification_dialog())

        # Hover effect (change cursor)
        self.bell_label.bind("<Enter>", lambda e: self.bell_label.configure(cursor="hand2"))
        self.bell_label.bind("<Leave>", lambda e: self.bell_label.configure(cursor="arrow"))

        # Search field
        self.search_frame = ctk.CTkFrame(self.right_container, width=240, height=36)
        self.search_frame.pack(side="left", padx=(0, 10))
        self.search_frame.pack_propagate(False) # Prevent frame from resizing to content

        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Search...")
        self.search_entry.pack(side="left", fill="both", expand=True)

        # search icon image with enable to click the image icon
        search_icon_path = r"image/glass1.gif"
        if os.path.exists(search_icon_path):
            main_icon_img = Image.open(search_icon_path).resize((25, 25), Image.Resampling.LANCZOS)
            self.search_icon = CTkImage(light_image=main_icon_img, dark_image=main_icon_img, size=(25, 25))
        else:
            self.search_icon = None
            print(f"Image not found: {search_icon_path}")

        self.search_icon_button = ctk.CTkButton(
            self.search_frame,
            image=self.search_icon,
            width=36,
            height=36,
            fg_color="#FFFFFF",
            corner_radius=0,
            text="",
            command=self.trigger_search_from_topbar # Call a local method that uses the callback
        )
        self.search_icon_button.pack(side="left")

    # =========================================================================================
    #                            Top Bar Methods
    # =========================================================================================

    def refresh_profile_icon(self):
        user_info = get_user_prof()
        image_path = user_info.get("profile_image")

        if image_path and os.path.exists(image_path):
            try:
                user_img = Image.open(image_path).resize((32, 32), Image.Resampling.LANCZOS)
                user_img = make_circle(user_img)
                self.user_icon = CTkImage(light_image=user_img, dark_image=user_img, size=(32, 32))
                self.user_icon_label.configure(image=self.user_icon, text="")
                self.user_icon_label.image = self.user_icon
            except Exception as e:
                print(f"❌ Failed to load profile image '{image_path}': {e}")
                self.user_icon_label.configure(image=None, text="")  # No image fallback
                self.user_icon_label.image = None
        else:
            # No image found or file missing – clear the image
            self.user_icon_label.configure(image=None, text="")
            self.user_icon_label.image = None

    def set_active_button(self, key):
        # key: "home", "bookmark", etc.
        # Reset borders for all buttons
        for name, btn in self.buttons.items():
            btn.configure(border_color="black", border_width=0)
        # Set border for the active button
        if key in self.buttons:
            self.buttons[key].configure(border_color="black", border_width=2)
            self.active_button = self.buttons[key]

    # --- REMOVED: update_notification_count method ---
    # def update_notification_count(self, count):
    #     """Updates the notification count displayed on the bell icon."""
    #     if count > 0:
    #         self.notif_count_label.configure(text=str(count), fg_color="red")
    #         self.notif_count_label.place(relx=0.8, rely=0.1, anchor="ne") # Show it
    #     else:
    #         self.notif_count_label.configure(text="")
    #         self.notif_count_label.place_forget() # Hide it if count is 0

    def trigger_search_from_topbar(self):
        """Called when the top bar search button is clicked."""
        query = self.search_entry.get().strip()
        if self.on_search_callback:
            self.on_search_callback(query=query)
            self.search_entry.delete(0, ctk.END) # Clear the search bar after triggering search

    # ====================================================================================
    #                         Notification Dialog Logic
    # ====================================================================================
    def show_notification_dialog(self):
        # Close existing dialog if open
        if hasattr(self, "notif_dialog") and self.notif_dialog.winfo_exists():
            self.notif_dialog.destroy()
            return

        # Create Toplevel window for notification
        self.notif_dialog = ctk.CTkToplevel(self)
        self.notif_dialog.overrideredirect(True)
        self.notif_dialog.attributes("-topmost", True)
        self.notif_dialog.configure(fg_color="#222222")
        self.notif_dialog.geometry("300x120")  # Width x Height

        # Get bell position to place the dialog
        x = self.bell_label.winfo_rootx()
        y = self.bell_label.winfo_rooty() + self.bell_label.winfo_height()

        # Make sure it doesn't go beyond screen bottom
        screen_height = self.winfo_screenheight()
        height = 120

        y = min(y, screen_height - height - 10)

        self.notif_dialog.geometry(f"300x{height}+{x}+{y}")

        # --- MODIFIED: Notification text (no count) ---
        notification_text = "🔔 You have no new notifications."
        # Removed logic that checks current_count and adds to text

        label = ctk.CTkLabel(self.notif_dialog, text=notification_text, text_color="white")
        label.pack(padx=10, pady=10)

        # Optional: Close when focus is lost
        self.notif_dialog.bind("<FocusOut>", lambda e: self.notif_dialog.destroy())

# =========================================================================================
#                                     Main App
# =========================================================================================
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1200x700")
        self.title("Login")
        self.resizable(True, False)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- REMOVED: Notification Count Management and Simulation ---
        # self._notification_count = 0
        # self.after(2000, self.simulate_notifications)

        # Initialize TopBar with navigation commands
        self.topbar = TopBar(
            self,
            on_home=self.show_dashboard,
            on_bookmark=self.show_bookmark,
            on_comics=self.show_admin,
            on_profile=self.show_profile,
            on_search=self.initiate_search_display
        )
        self.topbar.grid(row=0, column=0, sticky="ew")

        # Container for different pages
        self.container = ctk.CTkFrame(self)
        self.container.grid(row=1, column=0, sticky="nsew")

        # Initialize all pages
        self.login_page = LoginPage(self.container, self.show_signup, self.show_forgot_password, self.show_dashboard)
        self.signup_page = SignUpPage(self.container, self.show_login)
        self.forgot_password_page = ForgotPasswordPage(self.container, self.show_login)
        self.dashboard_page = DashboardPage(self.container, controller=self)
        self.profile_page = ProfilePage(self.container, on_logout=self.show_login, topbar=self.topbar)
        self.bookmark_page = BookmarkPage(self.container, on_bookmark_change=self.refresh_all_bookmark_related_uis)
        self.admin_page = AdminPage(self.container, controller=self)
        self.search_results_page = SearchPage(self.container, controller=self)

        # Place all pages in the same grid position within the container
        for page in [
            self.login_page, self.signup_page, self.forgot_password_page,
            self.dashboard_page, self.profile_page, self.bookmark_page, self.admin_page,
            self.search_results_page
        ]:
            page.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.show_login()

    # =========================================================================================
    #                                  REMOVED: Notification Handling methods
    # =========================================================================================
    # def get_notification_count(self):
    #     return self._notification_count
    #
    # def set_notification_count(self, count):
    #     self._notification_count = count
    #     self.topbar.update_notification_count(self._notification_count)
    #
    # def add_notification(self, count=1):
    #     self.set_notification_count(self._notification_count + count)
    #
    # def clear_notifications(self):
    #     self.set_notification_count(0)
    #
    # def simulate_notifications(self):
    #     self.add_notification(1)
    #     print(f"Simulated new notification. Total: {self._notification_count}")
    #     self.after(10000, self.simulate_notifications)

    # =========================================================================================
    #                                  Navigation Methods
    # =========================================================================================

    def show_topbar(self):
        self.topbar.grid(row=0, column=0, sticky="ew")

    # LOG IN METHOD
    def show_login(self):
        self.title("Login")
        self.topbar.grid_forget()
        self.login_page.clear_fields()
        self.login_page.tkraise()
        # --- REMOVED: Clear notifications here ---
        # self.clear_notifications()

    # Sign Up METHOD
    def show_signup(self):
        self.title("Sign Up")
        self.topbar.grid_forget()
        self.signup_page.clear_fields()
        self.signup_page.tkraise()

    # Forgot pass METHOD
    def show_forgot_password(self):
        self.title("Forgot Password")
        self.topbar.grid_forget()
        self.forgot_password_page.clear_fields()
        self.forgot_password_page.tkraise()

    # Dashboard/Home METHOD
    def show_dashboard(self):
        self.title("Dashboard")
        self.show_topbar()
        self.topbar.set_active_button("home")
        self.topbar.refresh_profile_icon()
        self.dashboard_page.tkraise()

    # Profile METHOD
    def show_profile(self):
        self.title("Profile")
        self.show_topbar()
        self.topbar.set_active_button("profile")
        self.profile_page.refresh_profile_info()
        self.profile_page.tkraise()
        self.topbar.refresh_profile_icon()

    # Bookmark METHOD
    def show_bookmark(self):
        self.title("Bookmark")
        self.show_topbar()
        self.topbar.set_active_button("bookmark")
        self.bookmark_page.display_bookmarks()
        self.bookmark_page.tkraise()

    # Comics/Admin METHOD (as per your mapping)
    def show_admin(self):
        self.title("Comics (Admin)")
        self.show_topbar()
        self.topbar.set_active_button("comics")
        self.admin_page.refresh_admin_bookmark_states()
        self.admin_page.tkraise()

    # Search_clicked METHOD (called by top bar search button)
    def initiate_search_display(self, query=None, genre_filter=None, status_filter=None, order_filter=None):
        """
        Initiates a search with the given criteria and displays results on SearchPage.
        Called by top bar search or dashboard filters.
        """
        self.title("Search Results")

        if not query and not genre_filter and not status_filter and not order_filter:
            print("No search criteria provided. Displaying empty/previous search results page.")
            self.show_search_results(results=[], query="", genre_filter="", status_filter="", order_filter="")
            return

        results = search_mangas(
            query=query,
            genre_filter=genre_filter,
            status_filter=status_filter,
            order_filter=order_filter
        )

        print(f"DEBUG: initiate_search_display - Query: '{query}', Genre: '{genre_filter}', Status: '{status_filter}', Order: '{order_filter}'")
        print(f"DEBUG: Search Results from search_mangas: {len(results)} found")

        self.show_search_results(results, query, genre_filter, status_filter, order_filter)

    def show_search_results(self, results, query=None, genre_filter=None, status_filter=None, order_filter=None):
        self.show_topbar()
        self.topbar.set_active_button(None)
        self.search_results_page.display_results(
            results,
            query=query,
            genre_filter=genre_filter,
            status_filter=status_filter,
            order_filter=order_filter
        )
        self.search_results_page.tkraise()
        self.search_results_page.refresh_bookmark_states()
        
    def refresh_all_bookmark_related_uis(self):
        print("Refreshing all bookmark-related UIs...")
        if hasattr(self.dashboard_page, 'refresh_all_bookmark_states'):
            self.dashboard_page.refresh_all_bookmark_states()
        if hasattr(self.admin_page, 'refresh_admin_bookmark_states'):
            self.admin_page.refresh_admin_bookmark_states()
        if hasattr(self.bookmark_page, 'display_bookmarks'):
            self.bookmark_page.display_bookmarks()
        if hasattr(self.search_results_page, 'refresh_bookmark_states'):
            self.search_results_page.refresh_bookmark_states()

# =========================================================================================
#                                     Run Application
# =========================================================================================

if __name__ == "__main__":
    from user_model import init_user_db
    init_user_db()

    mangas = [
        {
            "name": "Dragon Ball",
            "author": "Akira Toriyama",
            "chapter": 519,
            "genre": "Action, Adventure, Martial Arts, Fantasy",
            "status": "Completed",
            "image": r"image/dragonball.jfif",
            "summary": "Son Goku, a young martial artist with a monkey tail, embarks on a quest to find the seven Dragon Balls"
        },
        {
            "name": "One Piece",
            "author": "Eiichiro Oda",
            "chapter": 1090,
            "genre": "Adventure, Fantasy, Action",
            "status": "Ongoing",
            "image": r"image/onepiece.webp",
            "summary": "Monkey D. Luffy, a rubber-powered pirate, sails the seas in search of the legendary One Piece."
        },
        {
            "name": "Naruto",
            "author": "Masashi Kishimoto",
            "chapter": 700,
            "genre": "Adventure, Martial Arts, Fantasy",
            "status": "Completed",
            "image": r"image/naruto.jfif",
            "summary": "Naruto Uzumaki, a young ninja from the Hidden Leaf Village who dreams of becoming the Hokage."
        },
        {
            "name": "Dandadan",
            "author": "Yukinobu Tatsu",
            "chapter": 150,
            "genre": "Action, Supernatural, Sci-Fi, Comedy",
            "status": "Ongoing",
            "image": r"image/dandadan.jfif",
            "summary": "A high school girl and a nerdy boy team up to battle supernatural threats. When strange dreams turn to real."
        },
        {
            "name": "Sakamoto Days",
            "author": "Yuto Suzuki",
            "chapter": 150,
            "genre": "Action, Comedy",
            "status": "Ongoing",
            "image": r"image/sakamoto.webp",
            "summary": "A legendary hitman retires to run a convenience store, but teams up with a boy and girl when danger drags him back into action."
        },
        {
            "name": "Jujutsu Kaisen",
            "author": "Gege Akutami",
            "chapter": 236,
            "genre": "Action, Supernatural, Dark Fantasy",
            "status": "Ongoing",
            "image": r"image/jujutsu.webp",
            "summary": "Gojo faces off against Sukuna in a fierce clash to determine who's the strongest sorcerer of their era."
        },
        {
            "name": "My Hero Academia",
            "author": "Kohei Horikoshi",
            "chapter": 400,
            "genre": "Action, Superhero, Fantasy",
            "status": "Ongoing",
            "image": r"image/mha.jpg",
            "summary": "In a world where most people have powers, a powerless boy dreams of becoming a hero."
        },
        {
            "name": "Fullmetal Alchemist",
            "author": "Hiromu Arakawa",
            "chapter": 116,
            "genre": "Action, Adventure, Fantasy",
            "status": "Completed",
            "image": "image/fullmetal.jpg",
            "summary": "Two brothers seek the Philosopher's Stone after a failed alchemy experiment."
        },
        {
            "name": "Demon Slayer",
            "author": "Koyoharu Gotouge",
            "chapter": 205,
            "genre": "Action, Supernatural",
            "status": "Completed",
            "image": "image/demonslayer.jpg",
            "summary": "A boy joins the Demon Slayer Corps to avenge his family."
        },
        {
            "name": "Bleach",
            "author": "Tite Kubo",
            "chapter": 686,
            "genre": "Action, Supernatural",
            "status": "Completed",
            "image": "image/bleach.jpg",
            "summary": "A teenager becomes a Soul Reaper to battle evil spirits."
        },
        {
            "name": "Attack on Titan",
            "author": "Hajime Isayama",
            "chapter": 139,
            "genre": "Action, Drama, Fantasy",
            "status": "Completed",
            "image": "image/AOT.jfif",
            "summary": "Humans fight for survival against giant man-eating Titans."
        },
        {
            "name": "Solo Leveling",
            "author": "Chugong",
            "chapter": 179,
            "genre": "Action, Fantasy, Adventure",
            "status": "Completed",
            "image": "image/solo.jpg",
            "summary": "A weak hunter rises to the top with mysterious powers."
        },
        {
            "name": "Mashle",
            "author": "Hajime Komoto",
            "chapter": 162,
            "genre": "Action, Comedy, Fantasy",
            "status": "Completed",
            "image": "image/magic.jpg",
            "summary": "A magicless boy muscles through a magical world."
        },
        {
            "name": "Kaiju No. 8",
            "author": "Naoya Matsumoto",
            "chapter": 110,
            "genre": "Action, Sci-Fi",
            "status": "Ongoing",
            "image": "image/kaiju.jfif",
            "summary": "A cleaner turns Kaiju to fight monsters threatening Japan."
        },
        {
            "name": "Berserk",
            "author": "Kentaro Miura",
            "chapter": 374,
            "genre": "Action, Dark Fantasy",
            "status": "Ongoing",
            "image": "image/berserk.jpg",
            "summary": "A lone swordsman battles demons in a dark, brutal world."
        },
        {
            "name": "Spy x Family",
            "author": "Tatsuya Endo",
            "chapter": 94,
            "genre": "Action, Comedy, Slice of Life",
            "status": "Ongoing",
            "image": "image/spyxfamily.webp",
            "summary": "A spy forms a fake family for his secret mission."
        },
        {
            "name": "Blue Lock",
            "author": "Muneyuki Kaneshiro",
            "chapter": 268,
            "genre": "Sports, Drama",
            "status": "Ongoing",
            "image": "image/blue.jpg",
            "summary": "Strikers compete in an intense soccer survival program."
        },
        {
            "name": "Frieren: Beyond Journey’s End",
            "author": "Kanehito Yamada",
            "chapter": 133,
            "genre": "Fantasy, Drama, Adventure, Slice of Life",
            "status": "Ongoing",
            "image": "image/Frieren.jpg",
            "summary": "An elf mage reflects on life after her hero’s journey."
        },
        {
            "name": "Chainsaw Man",
            "author": "Tatsuki Fujimoto",
            "chapter": 162,
            "genre": "Action, Supernatural, Horror",
            "status": "Ongoing",
            "image": "image/chainsawman.webp",
            "summary": "A devil hunter gains powers by fusing with his pet devil."
        },
        {
            "name": "Black Clover",
            "author": "Yūki Tabata",
            "chapter": 370,
            "genre": "Action, Fantasy",
            "status": "Ongoing",
            "image": "image/blackclover.jpg",
            "summary": "A magicless boy dreams of becoming the Wizard King."
        },
        {
            "name": "Four Knights of the Apocalypse",
            "author": "Nakaba Suzuki",
            "chapter": 154,
            "genre": "Action, Adventure, Fantasy",
            "status": "Ongoing",
            "image": "image/FourKnights.webp",
            "summary": "A sequel to Seven Deadly Sins with new legendary knights."
        },
        {
            "name": "Hunter x Hunter",
            "author": "Yoshihiro Togashi",
            "chapter": 400,
            "genre": "Action, Adventure, Fantasy",
            "status": "Hiatus",
            "image": "image/hunterhunter.jfif",
            "summary": "A boy embarks on a journey to find his hunter father."
        },
    ]

    connection = sqlite3.connect('user.db')
    cursor = connection.cursor()

    for m in mangas:
        cursor.execute("""
            INSERT INTO Manga (title, author, status, image_path, description)
            VALUES (?, ?, ?, ?, ?, ?) 
        """, (
        m["name"],
        m["author"],
        m["chapter"],
        m["status"],
        m["image"],
        m["summary"]
        ))

    manga_id = cursor.lastrowid # stores the id of the inserted manga

    # paghihiwalay ng genres para mainsert sa Genre table
    genres = [g.strip() for g in m["genre"].split(",")] 
    for genre in genres: # loop para maistore yung mga genre ng inserted manga sa genre table
        cursor.execute("""
            INSERT INTO Genre (mangaId, genre)
            VALUES (?, ?)
        """, (manga_id, genre))

    connection.commit()
    connection.close()

    app = App()
    app.mainloop()