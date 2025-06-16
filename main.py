#==================== Imports ====================
import customtkinter as ctk
from Login.loginUi import LoginPage
from SignUp.signUpUi import SignUpPage
from Forgot_pass.forgotUi import ForgotPasswordPage
from Homepage.homeUi import DashboardPage
from Profile.profileUi import ProfilePage
from Homepage.homeBackend import get_user_prof     
from Admin.adminUi import AdminPage
from Bookmark.bookmarkUi import BookmarkPage

from PIL import Image, ImageDraw
from customtkinter import CTkImage
import os

#==================== Helper Function ====================
def make_circle(img):
    size = (min(img.size),) * 2
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    output = Image.new('RGBA', size)
    img = img.resize(size, Image.Resampling.LANCZOS)
    output.paste(img, (0, 0), mask)
    return output

#==================== Top Navigation Bar ====================
class TopBar(ctk.CTkFrame):
    def __init__(self, parent, on_home, on_bookmark, on_comics, on_profile, on_search=None):
        super().__init__(parent, height=60, fg_color="#39ff14", corner_radius=15)
        self.on_profile = on_profile

        # Logo
        try:
            self.logo_img = Image.open(r"image/mangaker.jpg")
            self.logo_img = make_circle(self.logo_img.resize((40, 40), Image.Resampling.LANCZOS))
            self.logo_photo = CTkImage(light_image=self.logo_img, dark_image=self.logo_img, size=(40, 40))
            self.logo = ctk.CTkLabel(self, image=self.logo_photo, text="")
            self.logo.pack(side="left", padx=15, pady=10)
        except Exception as e:
            print("Logo loading failed:", e)

        # Navigation Buttons
        button_style = {
            "fg_color": "#39ff14",
            "hover_color": "#1f8112",
            "text_color": "black",
            "corner_radius": 10,
        }

        self.home_button = ctk.CTkButton(self, text="Home", command=on_home, **button_style)
        self.home_button.pack(side="left", padx=10, pady=10)

        self.bookmark_button = ctk.CTkButton(self, text="Bookmark", command=on_bookmark, **button_style)
        self.bookmark_button.pack(side="left", padx=10, pady=10)

        self.comics_button = ctk.CTkButton(self, text="Comics", command=on_comics, **button_style)
        self.comics_button.pack(side="left", padx=10, pady=10)

        self.profile_button = ctk.CTkButton(self, text="Profile", command=on_profile, **button_style)
        self.profile_button.pack(side="left", padx=10, pady=10)

        self.buttons = {
            "home": self.home_button,
            "bookmark": self.bookmark_button,
            "comics": self.comics_button,
            "profile": self.profile_button
        }
        self.active_button = None

        # Right-side container
        self.right_container = ctk.CTkFrame(self, fg_color="transparent")
        self.right_container.pack(side="right", padx=10, pady=10)

        # Search field
        self.search_frame = ctk.CTkFrame(self.right_container, width=240, height=36)
        self.search_frame.pack(side="left", padx=(0, 10))
        self.search_frame.pack_propagate(False)

        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Search...")
        self.search_entry.pack(side="left", fill="both", expand=True)

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
        self.search_icon_button.pack(side="right")

        # Profile Icon
        self.user_icon_label = ctk.CTkLabel(self.right_container, text="")
        self.user_icon_label.pack(side="left", padx=(10, 0))
        self.user_icon_label.bind("<Button-1>", lambda e: self.on_profile())
        self.refresh_profile_icon()

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
                print("Failed to load profile icon:", e)
                self.user_icon_label.configure(image=None, text="")
        else:
            self.user_icon_label.configure(image=None, text="")  # fallback emoji
    
    def set_active_button(self, key):
        # key: "home", "bookmark", etc.
        for name, btn in self.buttons.items():
            btn.configure(border_color="black", border_width=0)
        if key in self.buttons:
            self.buttons[key].configure(border_color="black", border_width=2)
            self.active_button = self.buttons[key]

#==================== Main App ====================
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1200x680")
        self.title("Login")
        self.resizable(False, False)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.topbar = TopBar(
            self,
            on_home=self.show_dashboard,
            on_bookmark=self.show_bookmark,
            on_comics=self.show_admin,
            on_profile=self.show_profile,
            on_search=self.search_clicked
        )
        self.topbar.grid(row=0, column=0, sticky="ew")

        self.container = ctk.CTkFrame(self)
        self.container.grid(row=1, column=0, sticky="nsew")

        self.login_page = LoginPage(self.container, self.show_signup, self.show_forgot_password, self.show_dashboard)
        self.signup_page = SignUpPage(self.container, self.show_login)
        self.forgot_password_page = ForgotPasswordPage(self.container, self.show_login)
        self.dashboard_page = DashboardPage(self.container, controller=self)
        self.profile_page = ProfilePage(self.container, on_logout=self.show_login, topbar=self.topbar)
        self.bookmark_page = BookmarkPage(self.container)
        self.admin_page = AdminPage(self.container, controller=self)

        for page in [
            self.login_page, self.signup_page, self.forgot_password_page,
            self.dashboard_page, self.profile_page, self.bookmark_page, self.admin_page
        ]:
            page.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.show_login()

    #==================== Navigation ====================

    def show_topbar(self):
        self.topbar.grid(row=0, column=0, sticky="ew")

    def show_login(self):
        self.title("Login")
        self.topbar.grid_forget()
        self.login_page.clear_fields()
        self.login_page.tkraise()

    def show_signup(self):
        self.title("Sign Up")
        self.topbar.grid_forget()
        self.signup_page.clear_fields()
        self.signup_page.tkraise()

    def show_forgot_password(self):
        self.title("Forgot Password")
        self.topbar.grid_forget()
        self.forgot_password_page.clear_fields()
        self.forgot_password_page.tkraise()

    def show_dashboard(self):
        self.title("Dashboard")
        self.show_topbar()
        self.topbar.set_active_button("home")
        self.topbar.refresh_profile_icon()
        self.dashboard_page.tkraise()

    def show_profile(self):
        self.title("Profile")
        self.show_topbar()
        self.topbar.set_active_button("profile")
        self.profile_page.refresh_profile_info()
        self.profile_page.tkraise()
        self.topbar.refresh_profile_icon()

    def show_bookmark(self):
        self.title("Bookmark")
        self.show_topbar()
        self.topbar.set_active_button("bookmark")
        self.bookmark_page.tkraise()

    def show_admin(self):
        self.title("Comics")
        self.show_topbar()
        self.topbar.set_active_button("comics")
        self.admin_page.tkraise()

    def show_manga_list(self):
        self.title("Comics")
        self.show_topbar()
        self.topbar.set_active_button("comics")
        self.admin_page.tkraise()

    def search_clicked(self):
        self.title("Search Results")
        query = self.topbar.search_entry.get()
        print(f"Search for: {query}")

#==================== Run ====================
if __name__ == "__main__":
    app = App()
    app.mainloop()
