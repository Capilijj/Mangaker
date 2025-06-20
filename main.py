#=========================================================
#open mo muna yung todo.py nandun ung sasabihin ko rin pre=
#=========================================================
#==================== Imports ====================
import customtkinter as ctk
from Login.loginUi import LoginPage
from SignUp.signUpUi import SignUpPage
from Forgot_pass.forgotUi import ForgotPasswordPage
from Homepage.homeUi import DashboardPage 
from Profile.profileUi import ProfilePage
from Homepage.homeBackend import get_user_prof # parameter in homebackend function //alam mo nato 
from SearchPage.searchBackend import search_mangas 
from Admin.adminUi import AdminPage
from Bookmark.bookmarkUi import BookmarkPage
from SearchPage.searchUi import SearchPage

from PIL import Image, ImageDraw
from customtkinter import CTkImage
import os # checking file existence or managing paths.

#=========================================================================================
#                                 Function to make the image Circle                      =
#=========================================================================================
def make_circle(img):
    size = (min(img.size),) * 2
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    output = Image.new('RGBA', size)
    img = img.resize(size, Image.Resampling.LANCZOS)
    output.paste(img, (0, 0), mask)
    return output

#=========================================================================================
#                                 Top Navigation Bar Header                              =
#=========================================================================================
class TopBar(ctk.CTkFrame):
    def __init__(self, parent, on_home, on_bookmark, on_comics, on_profile, on_search=None):
        super().__init__(parent, height=60, fg_color="#39ff14", corner_radius=15)
        self.on_profile = on_profile

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

        #Button widget -Home, Bookmark, Comics, Profile
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


#==================================================================================
#                 ito yung TO Do mo ken nasa baba lang yung function logic nito 
#====================================================================================

    # === Bell Icon (clickable, circle, hoverable) ===
        bell_path = "image/bell.png"
        if os.path.exists(bell_path):
            bell_img = Image.open(bell_path).resize((40, 40), Image.Resampling.LANCZOS)
            circle_bell = make_circle(bell_img) # ---- Apply circular mask to bell image ----
            self.bell_icon = CTkImage(light_image=circle_bell, dark_image=circle_bell, size=(40, 40))
        else:
            self.bell_icon = None
            print("Bell image not found!")

        self.bell_label = ctk.CTkLabel(self.right_container, image=self.bell_icon, text="")
        self.bell_label.pack(side="left", padx=(5, 10))

        # Connect bell click to show dialog
        self.bell_label.bind("<Button-1>", lambda e: self.show_notification_dialog())

        # Hover effect (change cursor)
        self.bell_label.bind("<Enter>", lambda e: self.bell_label.configure(cursor="hand2"))
        self.bell_label.bind("<Leave>", lambda e: self.bell_label.configure(cursor="arrow"))
#=====================================================================================================

    # Search field
        self.search_frame = ctk.CTkFrame(self.right_container, width=240, height=36)
        self.search_frame.pack(side="left", padx=(0, 10))
        self.search_frame.pack_propagate(False) # ---- Prevent frame from resizing to content ----

        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Search...")
        self.search_entry.pack(side="left", fill="both", expand=True)

        #search icon image with enable to click the image icon
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
            command=on_search if on_search else lambda: print("Search clicked")
        )
        self.search_icon_button.pack(side="left")

#=========================================================================================
#                                 Top Bar Methods                                       =
#=========================================================================================

    def refresh_profile_icon(self):
        user_info = get_user_prof() # ---- Get user profile information from backend ----
        image_path = user_info.get("profile_image")

        if image_path and os.path.exists(image_path):
            try:
                user_img = Image.open(image_path).resize((32, 32), Image.Resampling.LANCZOS)
                user_img = make_circle(user_img) # ---- Make the profile image circular ----
                self.user_icon = CTkImage(light_image=user_img, dark_image=user_img, size=(32, 32))
                self.user_icon_label.configure(image=self.user_icon, text="")
                self.user_icon_label.image = self.user_icon # ---- Keep a reference to prevent garbage collection ----
            except Exception as e:
                print("Failed to load profile icon:", e)
                self.user_icon_label.configure(image=None, text="") # Fallback if image fails
        else:
            self.user_icon_label.configure(image=None, text="")   # fallback emoji

    def set_active_button(self, key):
        # key: "home", "bookmark", etc.
        # ---- Reset borders for all buttons ----
        for name, btn in self.buttons.items():
            btn.configure(border_color="black", border_width=0)
        # ---- Set border for the active button ----
        if key in self.buttons:
            self.buttons[key].configure(border_color="black", border_width=2)
            self.active_button = self.buttons[key]

#========================================================================================
#         ito yung dialog box na lilitaw pag ka click add ka dito ng count number sa taas
#========================================================================================
    def show_notification_dialog(self):
        # ---- Close existing dialog if open ----
        if hasattr(self, "notif_dialog") and self.notif_dialog.winfo_exists():
            self.notif_dialog.destroy()
            return

        # Create Toplevel window for notification
        self.notif_dialog = ctk.CTkToplevel(self)
        self.notif_dialog.overrideredirect(True)   
        self.notif_dialog.attributes("-topmost", True) 
        self.notif_dialog.configure(fg_color="#222222")
        self.notif_dialog.geometry("300x120")   # Width x Height

        # Get bell position to place the dialog
        x = self.bell_label.winfo_rootx()
        y = self.bell_label.winfo_rooty() + self.bell_label.winfo_height()

        # Make sure it doesn't go beyond screen bottom
        screen_height = self.winfo_screenheight()
        height = 120

        y = min(y, screen_height - height - 10) 

        self.notif_dialog.geometry(f"300x{height}+{x}+{y}")

        # Example content for the notification dialog
        label = ctk.CTkLabel(self.notif_dialog, text="🔔 You have no new notifications.", text_color="white")
        label.pack(padx=10, pady=10)

        # Optional: Close when focus is lost
        self.notif_dialog.bind("<FocusOut>", lambda e: self.notif_dialog.destroy())


#=========================================================================================
#                                     Main App                                          =
#=========================================================================================
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1200x700")
        self.title("Login")
        self.resizable(True, False) # ---- PAG AYAW NIYO NA FUFULL SCREEN PWEDE (False , False) ----

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Initialize TopBar with navigation commands
        self.topbar = TopBar(
            self,
            on_home=self.show_dashboard,
            on_bookmark=self.show_bookmark,
            on_comics=self.show_admin, 
            on_profile=self.show_profile,
            on_search=self.search_clicked 
        )
        self.topbar.grid(row=0, column=0, sticky="ew")

        # Container for different pages
        self.container = ctk.CTkFrame(self)
        self.container.grid(row=1, column=0, sticky="nsew")

        # Initialize all pages
        self.login_page = LoginPage(self.container, self.show_signup, self.show_forgot_password, self.show_dashboard)
        self.signup_page = SignUpPage(self.container, self.show_login)
        self.forgot_password_page = ForgotPasswordPage(self.container, self.show_login)
        # Pass self (the controller) to DashboardPage so it can trigger filtered searches
        self.dashboard_page = DashboardPage(self.container, controller=self)
        self.profile_page = ProfilePage(self.container, on_logout=self.show_login, topbar=self.topbar)

        self.bookmark_page = BookmarkPage(self.container, on_bookmark_change=self.refresh_all_bookmark_related_uis)

        self.admin_page = AdminPage(self.container, controller=self)
        # Initialize SearchPage, pass controller to it
        self.search_results_page = SearchPage(self.container, controller=self)

        # Place all pages in the same grid position within the container
        for page in [
            self.login_page, self.signup_page, self.forgot_password_page,
            self.dashboard_page, self.profile_page, self.bookmark_page, self.admin_page,
            self.search_results_page
        ]:
            page.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.show_login() # ---- Start the application with the login page ----

    #=========================================================================================
    #                                   Navigation Methods                                  =
    #=========================================================================================

    def show_topbar(self):
        self.topbar.grid(row=0, column=0, sticky="ew")
    #LOG IN METHOD
    def show_login(self):
        self.title("Login")
        self.topbar.grid_forget() # ---- Hide top bar for login/signup/forgot password pages ----
        self.login_page.clear_fields()
        self.login_page.tkraise()
    #sign Up METHOD
    def show_signup(self):
        self.title("Sign Up")
        self.topbar.grid_forget()
        self.signup_page.clear_fields()
        self.signup_page.tkraise()
    #Forgot pass METHOD
    def show_forgot_password(self):
        self.title("Forgot Password")
        self.topbar.grid_forget()
        self.forgot_password_page.clear_fields()
        self.forgot_password_page.tkraise()
    #Dashboard/Home METHOD
    def show_dashboard(self):
        self.title("Dashboard")
        self.show_topbar()
        self.topbar.set_active_button("home") # ---- Highlight 'Home' button in top bar ----
        self.topbar.refresh_profile_icon() # ---- Ensure profile icon is up-to-date ----
        self.dashboard_page.tkraise()
    #Profile METHOD
    def show_profile(self):
        self.title("Profile")
        self.show_topbar()
        self.topbar.set_active_button("profile") 
        self.profile_page.refresh_profile_info() 
        self.profile_page.tkraise()
        self.topbar.refresh_profile_icon()
    #Bookmark METHOD
    def show_bookmark(self):
        self.title("Bookmark")
        self.show_topbar()
        self.topbar.set_active_button("bookmark")
        self.bookmark_page.display_bookmarks() 
        self.bookmark_page.tkraise()
    #Comics METHOD
    def show_admin(self):
        self.title("Comics")
        self.show_topbar()
        self.topbar.set_active_button("comics") 
        self.admin_page.refresh_admin_bookmark_states() 
        self.admin_page.tkraise()

    #Search_clicked METHOD
    def search_clicked(self):
        query = self.topbar.search_entry.get().strip() 

        if not query:
            self.show_search_results(results=[], query=query)
            return

        # Proceed with search
        self.initiate_search_display(query=query)
        self.topbar.search_entry.delete(0, ctk.END) # Clear the search bar

    # New method to handle searches from various sources (top bar or filters)
    def initiate_search_display(self, query=None, genre_filter=None, status_filter=None, order_filter=None):
        """
        Initiates a search with the given criteria and displays results on SearchPage.
        Called by top bar search or dashboard filters.
        """
        self.title("Search Results")

        # Call the backend search function with all parameters
        results = search_mangas(
            query=query,
            genre_filter=genre_filter,
            status_filter=status_filter,
            order_filter=order_filter
        )

        print(f"DEBUG: initiate_search_display - Query: '{query}', Genre: '{genre_filter}', Status: '{status_filter}', Order: '{order_filter}'")
        print(f"DEBUG: Search Results from search_mangas: {len(results)} found")

        # Display results on the SearchPage
        self.show_search_results(results, query, genre_filter, status_filter, order_filter)


    def show_search_results(self, results, query=None, genre_filter=None, status_filter=None, order_filter=None):
        """
        Shows the SearchPage and passes the search results and criteria to it.
        """
        self.show_topbar()
        self.topbar.set_active_button(None) # No active button for search results page
        # ---- Pass all relevant search criteria to display_results for conditional display ----
        self.search_results_page.display_results(results, query, genre_filter, status_filter, order_filter)
        self.search_results_page.tkraise()


    # New method to refresh bookmark icons across all relevant UIs
    def refresh_all_bookmark_related_uis(self):
        self.dashboard_page.refresh_all_bookmark_states() # Refreshes dashboard icons
        self.admin_page.refresh_admin_bookmark_states() # Refreshes admin page icons
        self.bookmark_page.display_bookmarks() # Refresh bookmarks in the bookmark page
        self.search_results_page.refresh_bookmark_states() # Refresh search results page icons

#=========================================================================================
#                                       Run Application                                 =
#=========================================================================================
if __name__ == "__main__":
    app = App()
    app.mainloop()