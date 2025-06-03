import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw


# In-memory user "database"
users = {}

# Set appearance
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green")  # Using your green theme here

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
class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, switch_to_register, switch_to_forgot_password, login_success):
        super().__init__(parent)
        self.parent = parent
        self.switch_to_register = switch_to_register
        self.switch_to_forgot_password = switch_to_forgot_password
        self.login_success = login_success
        self.pack(fill="both", expand=True)

        self.card = ctk.CTkFrame(self, width=360, height=530, corner_radius=15, fg_color="white", border_width=3)
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)

       
        try:
            self.logo_img = Image.open(r"C:/Users/Admin/OneDrive/Desktop/python_project/logo.jfif")
            self.logo_img = self.logo_img.resize((100, 100), Image.Resampling.LANCZOS)
            self.logo_img = make_circle(self.logo_img)
            self.logo_photo = ImageTk.PhotoImage(self.logo_img)
            self.logo_label = ctk.CTkLabel(self.card, image=self.logo_photo, text="")
            self.logo_label.pack(pady=(10, 10))
        except Exception:
            pass  # ignore if image missing

        self.logo_label = ctk.CTkLabel(self.card, text="James Mangaker",
                                       font=ctk.CTkFont(size=24, weight="bold"), text_color="#333")
        self.logo_label.pack(pady=(10, 10))

        self.login_text = ctk.CTkLabel(self.card, text="Login to your account",
                                       font=ctk.CTkFont(size=14, weight="bold"), text_color="#666")
        self.login_text.pack(pady=(5, 10))

        self.email_entry = ctk.CTkEntry(self.card, placeholder_text="Email", width=300, height=40)
        self.email_entry.pack(pady=(5, 10))

        # Load open/closed icons for toggle button
        self.icon_closed_img = Image.open(r"C:/Users/Admin/OneDrive/Desktop/python_project/closed.png").resize((25, 25), Image.Resampling.LANCZOS)
        self.icon_closed = ImageTk.PhotoImage(self.icon_closed_img)

        self.icon_open_img = Image.open(r"C:/Users/Admin/OneDrive/Desktop/python_project/open.png").resize((25, 25), Image.Resampling.LANCZOS)
        self.icon_open = ImageTk.PhotoImage(self.icon_open_img)

        # Password entry with toggle
        self.password_frame = ctk.CTkFrame(self.card, width=300, height=40)
        self.password_frame.pack(pady=(5, 10))
        self.password_frame.pack_propagate(False)

        self.password_entry = ctk.CTkEntry(self.password_frame, placeholder_text="Password", show="*", width=270 )
        self.password_entry.pack(side="left", fill="y")

        self.show_password = False

        self.toggle_password_button = ctk.CTkButton(
            self.password_frame, image=self.icon_closed, text="", width=30, height=50,
            fg_color="#302e2e", hover=False,
            command=self.toggle_password_visibility
        )
        self.toggle_password_button.pack(side="right")

        self.forgot_password = ctk.CTkLabel(self.card, text="Forgot Password?", text_color="#3b82f6",
                                            cursor="hand2", font=ctk.CTkFont(size=12))
        self.forgot_password.pack(anchor="e", padx=20)
        self.forgot_password.bind("<Button-1>", lambda e: self.switch_to_forgot_password())

        self.login_button = ctk.CTkButton(self.card, text="Log In", width=300, height=40, corner_radius=10,
                                          fg_color="#39ff14", hover_color="#28c20e", text_color="black",
                                          command=self.login_action)
        self.login_button.pack(pady=(5, 0))

        self.signup_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.signup_frame.pack(pady=(5, 0))

        self.not_member_label = ctk.CTkLabel(self.signup_frame, text="Not a member?", text_color="#555")
        self.not_member_label.pack(side="left")

        self.create_account = ctk.CTkLabel(self.signup_frame, text="Create New Account", text_color="#3b82f6",
                                           cursor="hand2")
        self.create_account.pack(side="left", padx=(3, 10))
        self.create_account.bind("<Button-1>", lambda e: self.switch_to_register())

        self.divider = ctk.CTkLabel(self.card, text="────────  Or continue with  ────────", text_color="#aaa")
        self.divider.pack(pady=5)

        self.google_button = ctk.CTkButton(self.card, text="Continue with Google", width=300, height=40,
                                           fg_color="white", text_color="black",
                                           hover_color="#e5e7eb", border_width=1, border_color="#ccc",
                                           command=self.google_action)
        self.google_button.pack()

    def toggle_password_visibility(self):
        if self.show_password:
            self.password_entry.configure(show="*")
            self.toggle_password_button.configure(image=self.icon_closed)
            self.show_password = False
        else:
            self.password_entry.configure(show="")
            self.toggle_password_button.configure(image=self.icon_open)
            self.show_password = True

    def login_action(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if email not in users:
            messagebox.showerror("Login Failed", "No account found with that email.")
        elif users[email]["password"] != password:
            messagebox.showerror("Login Failed", "Incorrect password.")
        else:
            messagebox.showinfo("Login Success", f"Welcome back, {users[email]['username']}!")
            self.login_success()  # Notify app that login succeeded

    def google_action(self):
        messagebox.showinfo("Google", "Google login not yet implemented.")


# ------------------------- REGISTER PAGE -------------------------
class RegisterPage(ctk.CTkFrame):
    def __init__(self, parent, switch_to_login):
        super().__init__(parent)
        self.parent = parent
        self.switch_to_login = switch_to_login
        self.pack(fill="both", expand=True)

        self.card = ctk.CTkFrame(self, width=360, height=400, corner_radius=15, fg_color="white", border_width=3)
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)

        try:
            self.logo_img = Image.open(r"C:/Users/Admin/OneDrive/Desktop/python_project/logo.jpg")
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
        self.username_entry.pack(pady=10)

        self.email_entry = ctk.CTkEntry(self.card, placeholder_text="Email", width=300, height=40)
        self.email_entry.pack(pady=10)

        # Load open/closed icons for toggle buttons
        self.icon_closed_img = Image.open(r"C:/Users/Admin/OneDrive/Desktop/python_project/closed.png").resize((25, 25), Image.Resampling.LANCZOS)
        self.icon_closed = ImageTk.PhotoImage(self.icon_closed_img)

        self.icon_open_img = Image.open(r"C:/Users/Admin/OneDrive/Desktop/python_project/open.png").resize((25, 25), Image.Resampling.LANCZOS)
        self.icon_open = ImageTk.PhotoImage(self.icon_open_img)

        # Password frame
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

        # Confirm password frame
        self.confirm_password_frame = ctk.CTkFrame(self.card, width=300, height=40)
        self.confirm_password_frame.pack(pady=5)
        self.confirm_password_frame.pack_propagate(False)

        self.confirm_password_entry = ctk.CTkEntry(self.confirm_password_frame, placeholder_text="Confirm Password", show="*", width=270)
        self.confirm_password_entry.pack(side="left", fill="y")

        self.show_confirm_password = False

        self.toggle_confirm_password_button = ctk.CTkButton(
             self.confirm_password_frame, image=self.icon_closed, text="",
             width=30, height=40,
            fg_color="#302e2e",
            command=self.toggle_confirm_password_visibility
        )
        self.toggle_confirm_password_button.pack(side="right")

        self.register_button = ctk.CTkButton(self.card, text="Create Account", width=300, height=40,
                                             fg_color="#39ff14", hover_color="#28c20e", text_color="black",
                                             corner_radius=10, command=self.register_action)
        self.register_button.pack(pady=15)

        self.login_label_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.login_label_frame.pack()

        self.already_member_label = ctk.CTkLabel(self.login_label_frame, text="Already a member?", text_color="#555")
        self.already_member_label.pack(side="left")

        self.login_here = ctk.CTkLabel(self.login_label_frame, text="Login Here", text_color="#3b82f6",
                                       cursor="hand2")
        self.login_here.pack(side="left", padx=(5, 10))
        self.login_here.bind("<Button-1>", lambda e: self.switch_to_login())

    def toggle_password_visibility(self):
        if self.show_password:
            self.password_entry.configure(show="*")
            self.toggle_password_button.configure(image=self.icon_closed)
            self.show_password = False
        else:
            self.password_entry.configure(show="")
            self.toggle_password_button.configure(image=self.icon_open)
            self.show_password = True

    def toggle_confirm_password_visibility(self):
        if self.show_confirm_password:
            self.confirm_password_entry.configure(show="*")
            self.toggle_confirm_password_button.configure(image=self.icon_closed)
            self.show_confirm_password = False
        else:
            self.confirm_password_entry.configure(show="")
            self.toggle_confirm_password_button.configure(image=self.icon_open)
            self.show_confirm_password = True

    def register_action(self):
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()

        if not username or not email or not password or not confirm_password:
            messagebox.showerror("Error", "All fields are required.")
            return
        
        if not email.endswith("@gmail.com"):
            messagebox.showerror("Error", "Email must be a Gmail address (ending with @gmail.com).")
            return

        if email in users:
            messagebox.showerror("Error", "An account with this email already exists.")
            return

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        users[email] = {
            "username": username,
            "password": password
        }
        messagebox.showinfo("Success", "Account created successfully! Please login.")
        self.switch_to_login()


# ------------------------- FORGOT PASSWORD PAGE -------------------------
class ForgotPasswordPage(ctk.CTkFrame):
    def __init__(self, parent, switch_to_login):
        super().__init__(parent)
        self.parent = parent
        self.switch_to_login = switch_to_login
        self.pack(fill="both", expand=True)

        self.card = ctk.CTkFrame(self, width=360, height=250, corner_radius=15, fg_color="white", border_width=3)
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)

        try:
            self.logo_img = Image.open(r"C:/Users/Admin/OneDrive/Desktop/python_project/logo.jpg")
            self.logo_img = self.logo_img.resize((100, 100), Image.Resampling.LANCZOS)
            self.logo_img = make_circle(self.logo_img)
            self.logo_photo = ImageTk.PhotoImage(self.logo_img)
            self.logo_label = ctk.CTkLabel(self.card, image=self.logo_photo, text="")
            self.logo_label.pack(pady=(10, 10))
        except Exception:
            pass

        self.title = ctk.CTkLabel(self.card, text="Forgot Password",
                                  font=ctk.CTkFont(size=20, weight="bold"), text_color="#333")
        self.title.pack(pady=(20, 20))

        self.email_entry = ctk.CTkEntry(self.card, placeholder_text="Enter your email", width=300, height=40)
        self.email_entry.pack(pady=(5, 15))

        self.reset_button = ctk.CTkButton(self.card, text="Reset Password", width=300, height=40,
                                          fg_color="#39ff14", hover_color="#28c20e", text_color="black",
                                          corner_radius=10, command=self.reset_password)
        self.reset_button.pack(pady=(5, 15))

        self.back_to_login = ctk.CTkLabel(self.card, text="Back to Login", text_color="#3b82f6", cursor="hand2")
        self.back_to_login.pack()
        self.back_to_login.bind("<Button-1>", lambda e: self.switch_to_login())

    def reset_password(self):
        email = self.email_entry.get().strip()
        if email not in users:
            messagebox.showerror("Error", "No account found with this email.")
            return
        # In real app, trigger email reset here
        messagebox.showinfo("Reset Password", "Password reset instructions sent to your email.")


# ------------------------- MAIN APPLICATION -------------------------
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Login System")
        self.geometry("600x700")
        self.resizable(True, False)

        self.login_page = None
        self.register_page = None
        self.forgot_password_page = None

        self.show_login()

    def clear_pages(self):
        if self.login_page:
            self.login_page.destroy()
            self.login_page = None
        if self.register_page:
            self.register_page.destroy()
            self.register_page = None
        if self.forgot_password_page:
            self.forgot_password_page.destroy()
            self.forgot_password_page = None

    def show_login(self):
        self.clear_pages()
        self.login_page = LoginPage(self, switch_to_register=self.show_register,
                                    switch_to_forgot_password=self.show_forgot_password,
                                    login_success=self.login_success)

    def show_register(self):
        self.clear_pages()
        self.register_page = RegisterPage(self, switch_to_login=self.show_login)

    def show_forgot_password(self):
        self.clear_pages()
        self.forgot_password_page = ForgotPasswordPage(self, switch_to_login=self.show_login)

    def login_success(self):
        # For now, do nothing after login success
        pass


if __name__ == "__main__":
    app = App()
    app.mainloop()
