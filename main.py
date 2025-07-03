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
from Comics.ComicsUi import ComicsPage
from Bookmark.bookmarkUi import BookmarkPage
from SearchPage.searchUi import SearchPage
from administrator import AdminPage #administrator.py
from PIL import Image, ImageDraw
from customtkinter import CTkImage
import os
from user_model import init_user_db, authenticate_user, get_current_user_role, clear_current_user # Added authenticate_user, get_current_user_role, clear_current_user
from tkinter import messagebox # Added for error messages


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

        notification_text = "🔔 You have no new notifications."

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

        # Initialize TopBar (will be packed/grid later when user is logged in)
        self.topbar = TopBar(
            self,
            on_home=self.show_dashboard,
            on_bookmark=self.show_bookmark,
            on_comics=self.show_Comics,
            on_profile=self.show_profile,
            on_search=self.initiate_search_display
        )
        # self.topbar.grid(row=0, column=0, sticky="ew") # Do not grid initially

        # Container for different pages
        self.container = ctk.CTkFrame(self)
        self.container.grid(row=1, column=0, sticky="nsew")

        # Initialize all pages
        self.login_page = LoginPage(self.container, self.show_signup, self.show_forgot_password, on_login_success_user=self.show_dashboard, on_login_success_admin=self.show_administrator, controller=self)
        self.signup_page = SignUpPage(self.container, self.show_login)
        self.forgot_password_page = ForgotPasswordPage(self.container, self.show_login)
        self.dashboard_page = DashboardPage(self.container, controller=self)
        self.profile_page = ProfilePage(self.container, on_logout=self.show_login, topbar=self.topbar)
        self.bookmark_page = BookmarkPage(self.container, on_bookmark_change=self.refresh_all_bookmark_related_uis)
        self.Comics_page = ComicsPage(self.container, controller=self)
        self.search_results_page = SearchPage(self.container, controller=self)
        self.administrator_page = AdminPage(self.container, controller=self) # Initialize AdminPage

        # Place all pages in the same grid position within the container
        for page in [
            self.login_page, self.signup_page, self.forgot_password_page,
            self.dashboard_page, self.profile_page, self.bookmark_page, self.Comics_page,
            self.search_results_page,
            self.administrator_page
        ]:
            page.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.show_login() # Start with the login page

    # =========================================================================================
    #                                  Navigation Methods
    # =========================================================================================

    def show_topbar(self):
        self.topbar.grid(row=0, column=0, sticky="ew")

    # LOG IN METHOD
    def show_login(self):
        self.title("Login")
        # Ensure topbar is hidden when on login/signup/forgot password pages
        self.topbar.grid_forget()
        self.login_page.clear_fields()
        self.login_page.tkraise()
        # Ensure CURRENT_USER is cleared on logout/back to login
        clear_current_user()


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
    def show_Comics(self):
        self.title("Comics")
        self.show_topbar()
        self.topbar.set_active_button("comics")
        self.Comics_page.refresh_Comics_bookmark_states()
        self.Comics_page.tkraise()

    def show_administrator(self):
        self.title("Administrator")
        self.topbar.grid_forget()  # Hide topbar for admin page

        # Essential: Refresh admin UI elements based on CURRENT_USER
        self.administrator_page.refresh_profile_display()

        # Force display
        self.administrator_page.lift()
        self.administrator_page.tkraise()
        self.administrator_page.update()


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
        if hasattr(self.Comics_page, 'refresh_Comics_bookmark_states'):
            self.Comics_page.refresh_Comics_bookmark_states()
        if hasattr(self.bookmark_page, 'display_bookmarks'):
            self.bookmark_page.display_bookmarks()
        if hasattr(self.search_results_page, 'refresh_bookmark_states'):
            self.search_results_page.refresh_bookmark_states()

# =========================================================================================
#                                     Run Application
# =========================================================================================

if __name__ == "__main__":
    init_user_db() # Ensure the database is initialized and admin user exists

    app = App()
    app.mainloop()