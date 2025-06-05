import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
from backend1 import authenticate, register_user
from dashboard import DashboardPage  


# Helper function to make image circular
def make_circle(img: Image.Image) -> Image.Image:
    size = img.size
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)
    img = img.convert("RGBA")
    img.putalpha(mask)
    return img

# ------------------------- LOGIN PAGE -------------------------
class Login(ctk.CTkFrame):
    def __init__(self, parent, switch_to_register, switch_to_forgot_password, login_success):
        super().__init__(parent)
        self.parent = parent
        self.switch_to_register = switch_to_register
        self.switch_to_forgot_password = switch_to_forgot_password
        self.login_success = login_success
        self.pack(fill="both", expand=True)
        try:
            bg_image = Image.open("image/bg.jpg").resize((1200, 680), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(bg_image)
            self.bg_label = ctk.CTkLabel(self, image=self.bg_photo, text="")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print("Background image not found or failed to load:", e)

        self.card = ctk.CTkFrame(self, width=380, height=530, corner_radius=15, fg_color="white", border_width=3)
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)
        self.card.lift()

        try:
            self.logo_img = Image.open(r"image/mangaker.jpg")  # Replace with your logo path
            self.logo_img = self.logo_img.resize((100, 100), Image.Resampling.LANCZOS)
            self.logo_img = make_circle(self.logo_img)
            self.logo_photo = ImageTk.PhotoImage(self.logo_img)
            self.logo_label = ctk.CTkLabel(self.card, image=self.logo_photo, text="")
            self.logo_label.pack(pady=(10, 10))
        except Exception:
            pass  # ignore if image missing

        self.logo_label = ctk.CTkLabel(self.card, text="James Mangaker",
                                       font=ctk.CTkFont(size=24, weight="bold"), text_color="black")
        self.logo_label.pack(pady=(10, 10))

        self.login_text = ctk.CTkLabel(self.card, text="Login to your account",
                                       font=ctk.CTkFont(size=14, weight="bold"), text_color="#666")
        self.login_text.pack(pady=(5, 10))

        self.email_entry = ctk.CTkEntry(self.card, placeholder_text="Email", width=300, height=40)
        self.email_entry.pack(pady=(5, 10))

        # Load open/closed icons for toggle button
        try:
            self.icon_closed_img = Image.open(r"image/closed.png").resize((25, 25), Image.Resampling.LANCZOS)
            self.icon_closed = ImageTk.PhotoImage(self.icon_closed_img)

            self.icon_open_img = Image.open(r"image/open.png").resize((25, 25), Image.Resampling.LANCZOS)
            self.icon_open = ImageTk.PhotoImage(self.icon_open_img)
        except Exception:
            self.icon_closed = None
            self.icon_open = None

        # Password entry with toggle
        self.password_frame = ctk.CTkFrame(self.card, width=300, height=40)
        self.password_frame.pack(pady=(5, 10))
        self.password_frame.pack_propagate(False)

        self.password_entry = ctk.CTkEntry(self.password_frame, placeholder_text="Password", show="*", width=270)
        self.password_entry.pack(side="left", fill="y")

        self.show_password = False

        self.toggle_password_button = ctk.CTkButton(
            self.password_frame, image=self.icon_closed, text="", width=30, height=50,
            fg_color="transparent", hover=False,
            command=self.toggle_password_visibility
        )
        self.toggle_password_button.pack(side="right")

        self.forgot_password = ctk.CTkLabel(self.card, text="Forgot Password?", text_color="#3b82f6",
                                            cursor="hand2", font=ctk.CTkFont(size=12))
        self.forgot_password.pack(anchor="e", padx=20)
        self.forgot_password.bind("<Button-1>", lambda e: self.switch_to_forgot_password())

        self.login_button = ctk.CTkButton(self.card, text="Log In", width=300, height=40, corner_radius=10,
                                          fg_color="#39ff14", hover_color="#28c20e", text_color="black",
                                          command=self.login_success)
        self.login_button.pack(pady=(5, 0))

        self.signup_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.signup_frame.pack(pady=(5, 0))

        self.not_member_label = ctk.CTkLabel(self.signup_frame, text="Not a member?", text_color="#555")
        self.not_member_label.pack(side="left")

        self.create_account = ctk.CTkLabel(self.signup_frame, text="Create New Account", text_color="#3b82f6",
                                           cursor="hand2")
        self.create_account.pack(side="left", padx=(5))
        self.create_account.bind("<Button-1>", lambda e: self.switch_to_register())

        self.divider = ctk.CTkLabel(self.card, text="────────  Or continue with  ────────", text_color="#aaa")
        self.divider.pack(pady=5)

        self.google_button = ctk.CTkButton(self.card, text="Continue with Google", width=300, height=40,
                                           fg_color="#1a1a1a", text_color="white",
                                           hover_color="#2b2c2b", border_width=1, border_color="#ccc",
                                           command=lambda: messagebox.showinfo("Google", "Google login not yet implemented."))
        self.google_button.pack()

    def toggle_password_visibility(self):
        if self.show_password:
            self.password_entry.configure(show="*")
            if self.icon_closed:
                self.toggle_password_button.configure(image=self.icon_closed)
            self.show_password = False
        else:
            self.password_entry.configure(show="")
            if self.icon_open:
                self.toggle_password_button.configure(image=self.icon_open)
            self.show_password = True
    

# ------------------------- REGISTER PAGE -------------------------
class RegisterPage(ctk.CTkFrame):
    def __init__(self, parent, switch_to_login):
        super().__init__(parent)
        self.parent = parent
        self.switch_to_login = switch_to_login
        self.pack(fill="both", expand=True)
        try:
            bg_image = Image.open("image/bg.jpg").resize((1200, 680), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(bg_image)
            self.bg_label = ctk.CTkLabel(self, image=self.bg_photo, text="")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print("Background image not found or failed to load:", e)


        self.card = ctk.CTkFrame(self, width=360, height=480, corner_radius=15, fg_color="white", border_width=3)
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)

        try:
            self.logo_img = Image.open(r"image/mangaker.jpg")  # Replace with your logo path
            self.logo_img = self.logo_img.resize((100, 100), Image.Resampling.LANCZOS)
            self.logo_img = make_circle(self.logo_img)
            self.logo_photo = ImageTk.PhotoImage(self.logo_img)
            self.logo_label = ctk.CTkLabel(self.card, image=self.logo_photo, text="")
            self.logo_label.pack(pady=(10, 10))
        except Exception:
            pass

        self.title = ctk.CTkLabel(self.card, text="Create an Account",
                                  font=ctk.CTkFont(size=20, weight="bold"), text_color="#333")
        self.title.pack(pady=(20, 10))

        self.username_entry = ctk.CTkEntry(self.card, placeholder_text="Username", width=300, height=40)
        self.username_entry.pack(pady=5)

        self.email_entry = ctk.CTkEntry(self.card, placeholder_text="Email", width=300, height=40)
        self.email_entry.pack(pady=5)

        try:
            self.icon_closed_img = Image.open(r"image/closed.png").resize((25, 25), Image.Resampling.LANCZOS)
            self.icon_closed = ImageTk.PhotoImage(self.icon_closed_img)

            self.icon_open_img = Image.open(r"image/open.png").resize((25, 25), Image.Resampling.LANCZOS)
            self.icon_open = ImageTk.PhotoImage(self.icon_open_img)
        except Exception:
            self.icon_closed = None
            self.icon_open = None

        self.password_frame = ctk.CTkFrame(self.card, width=300, height=40)
        self.password_frame.pack(pady=5)
        self.password_frame.pack_propagate(False)

        self.password_entry = ctk.CTkEntry(self.password_frame, placeholder_text="Password", show="*", width=270)
        self.password_entry.pack(side="left", fill="y")

        self.show_password = False

        self.toggle_password_button = ctk.CTkButton(
            self.password_frame, image=self.icon_closed, text="",
            width=30, height=40,
            fg_color="#302e2e",
            command=self.toggle_password_visibility
        )
        self.toggle_password_button.pack(side="right")

        self.confirm_password_frame = ctk.CTkFrame(self.card, width=300, height=40)
        self.confirm_password_frame.pack(pady=5)
        self.confirm_password_frame.pack_propagate(False)

        self.confirm_password_entry = ctk.CTkEntry(self.confirm_password_frame, placeholder_text="Confirm Password", show="*", width=270)
        self.confirm_password_entry.pack(side="left", fill="y")

        self.show_confirm_password = False

        self.toggle_confirm_password_button = ctk.CTkButton(
            self.confirm_password_frame, image=self.icon_closed, text="",
            width=30, height=40,
            fg_color="transparent",
            command=self.toggle_confirm_password_visibility
        )
        self.toggle_confirm_password_button.pack(side="right")

        self.register_button = ctk.CTkButton(self.card, text="Register", width=300, height=40,
                                             fg_color="#39ff14", hover_color="#28c20e",
                                             text_color="black",
                                             command=self.register)
        self.register_button.pack(pady=(10, 0))

        self.back_to_login = ctk.CTkLabel(self.card, text="Back to Login", text_color="#3b82f6",
                                          cursor="hand2")
        self.back_to_login.pack(pady=(5, 0))
        self.back_to_login.bind("<Button-1>", lambda e: self.switch_to_login())

    def toggle_password_visibility(self):
        if self.show_password:
            self.password_entry.configure(show="*")
            if self.icon_closed:
                self.toggle_password_button.configure(image=self.icon_closed)
            self.show_password = False
        else:
            self.password_entry.configure(show="")
            if self.icon_open:
                self.toggle_password_button.configure(image=self.icon_open)
            self.show_password = True

    def toggle_confirm_password_visibility(self):
        if self.show_confirm_password:
            self.confirm_password_entry.configure(show="*")
            if self.icon_closed:
                self.toggle_confirm_password_button.configure(image=self.icon_closed)
            self.show_confirm_password = False
        else:
            self.confirm_password_entry.configure(show="")
            if self.icon_open:
                self.toggle_confirm_password_button.configure(image=self.icon_open)
            self.show_confirm_password = True
    
    def register(self):
        email = self.email_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        if not email or not username or not password or not confirm_password:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return
        if not email.endswith("@gmail.com"):
            messagebox.showerror("Error", "Email must be a Gmail address (ending with @gmail.com).")
            return

        if password != confirm_password:
            messagebox.showerror("Password Error", "Passwords do not match.")
            return
        
        success, message = register_user(email, username, password)
        if success:
            messagebox.showinfo("Success", message)
            self.switch_to_login()
        else:
            messagebox.showerror("Registration Failed", message)

# ------------------------- FORGOT PASSWORD PAGE -------------------------
class ForgotPasswordPage(ctk.CTkFrame):
    def __init__(self, parent, switch_to_login):
        super().__init__(parent)
        self.parent = parent
        self.switch_to_login = switch_to_login
        self.pack(fill="both", expand=True)
        
        try:
            bg_image = Image.open("image/bg.jpg").resize((1200, 680), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(bg_image)
            self.bg_label = ctk.CTkLabel(self, image=self.bg_photo, text="")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print("Background image not found or failed to load:", e)
        
        self.card = ctk.CTkFrame(self, width=360, height=230, corner_radius=15, fg_color="white", border_width=3)
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)

        self.title = ctk.CTkLabel(self.card, text="Forgot Password",
                                  font=ctk.CTkFont(size=20, weight="bold"), text_color="#333")
        self.title.pack(pady=(20, 10))

        self.email_entry = ctk.CTkEntry(self.card, placeholder_text="Enter your email", width=300, height=40)
        self.email_entry.pack(pady=10)

        self.send_button = ctk.CTkButton(self.card, text="Send Reset Link", width=300, height=40,
                                         fg_color="#39ff14", hover_color="#28c20e",
                                         text_color="black",
                                         command=lambda: messagebox.showinfo("Forgot Password", "Reset link not implemented."))
        self.send_button.pack(pady=10)

        self.back_to_login = ctk.CTkLabel(self.card, text="Back to Login", text_color="#3b82f6",
                                          cursor="hand2")
        self.back_to_login.pack()
        self.back_to_login.bind("<Button-1>", lambda e: self.switch_to_login())

# ------------------------- APP CLASS -------------------------
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Login with Background")
        self.geometry("1200x680")
        self.resizable(False, False) #palitan nalang to pag trip max ang window to (True , False)

        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)
        self.login_page = Login(self.container, self.show_register, self.show_forgot_password, self.login_success)
        self.register_page = RegisterPage(self.container, self.show_login)
        self.forgot_password_page = ForgotPasswordPage(self.container, self.show_login)
        self.dashboard_page = DashboardPage(self.container, self)

        # Place all pages
        for page in (self.login_page, self.register_page, self.forgot_password_page, self.dashboard_page):
            page.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.show_login()
        
    def show_login(self):
        self.login_page.tkraise()
    
    def show_register(self):
        self.register_page.tkraise()

    def show_forgot_password(self):
        self.forgot_password_page.tkraise()     

    def show_dashboard(self):
        self.dashboard_page.tkraise()

    def login_success(self):
        email = self.login_page.email_entry.get()
        password = self.login_page.password_entry.get()

        if not email or not password:
            messagebox.showwarning("Input Error", "Please enter both email and password.")
            return
        
        success, message = authenticate(email, password)

        if success:
            messagebox.showinfo("Success", message)
            self.show_dashboard()
        else:
            messagebox.showerror("Login Failed", message)


# ------------------------- RUN APP -------------------------
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = App()
    app.mainloop()
