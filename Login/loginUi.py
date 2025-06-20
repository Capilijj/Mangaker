#======== import modules ========
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageDraw
from Login.loginBackend import authenticate

#======== function to crop image into circle ========
def make_circle(img: Image.Image) -> Image.Image:
    size = img.size
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)
    img = img.convert("RGBA")
    img.putalpha(mask)
    return img

#======== log in page class ========
class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, switch_to_register, switch_to_forgot_password=None, on_login_success=None):
        super().__init__(parent)
        self.switch_to_register = switch_to_register
        self.switch_to_forgot_password = switch_to_forgot_password
        self.on_login_success = on_login_success
        #======== background image ========
        try:
            bg_image = Image.open("image/bg.jpg").resize((1500, 710), Image.Resampling.LANCZOS)
            self.bg_photo = ctk.CTkImage(light_image=bg_image, size=bg_image.size)
            self.bg_label = ctk.CTkLabel(self, image=self.bg_photo, text="")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print("Background image not found or failed to load:", e)

        #======== login card frame ========
        self.card = ctk.CTkFrame(self, width=380, height=500, corner_radius=15, fg_color="white", border_width=3)
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)
        self.card.lift()

        #======== logo image ========
        try:
            logo_img = Image.open(r"image/mangaker.jpg").resize((100, 100), Image.Resampling.LANCZOS)
            logo_img = make_circle(logo_img)
            logo_photo = ctk.CTkImage(light_image=logo_img, size=(100, 100))
            logo_label = ctk.CTkLabel(self.card, image=logo_photo, text="")
            logo_label.pack(pady=(10, 10))
        except Exception:
            pass

        #======== logo text ========
        logo_text_label = ctk.CTkLabel(self.card, text="James Mangaker",
                                       font=ctk.CTkFont(size=24, weight="bold"), text_color="black")
        logo_text_label.pack(pady=(10, 10))

        #======== email input ========
        self.email_entry = ctk.CTkEntry(self.card, placeholder_text="Email", width=300, height=40)
        self.email_entry.pack(pady=(5, 5))

        #======== password input with toggle ========
        password_frame = ctk.CTkFrame(self.card, width=300, height=40)
        password_frame.pack(pady=(5, 5))
        password_frame.pack_propagate(False)

        self.password_entry = ctk.CTkEntry(password_frame, placeholder_text="Password", show="*", width=270, height=40)
        self.password_entry.pack(side="left", fill="y")

        #======== load eye icons ========
        try:
            icon_closed_img = Image.open(r"image/closed.png").resize((25, 25), Image.Resampling.LANCZOS)
            icon_open_img = Image.open(r"image/open.png").resize((25, 25), Image.Resampling.LANCZOS)
            self.icon_closed = ctk.CTkImage(light_image=icon_closed_img, size=(25, 25))
            self.icon_open = ctk.CTkImage(light_image=icon_open_img, size=(25, 25))
        except Exception:
            self.icon_closed = None
            self.icon_open = None

        self.show_password = False

        self.toggle_password_button = ctk.CTkButton(
            password_frame, image=self.icon_closed, text="", width=30, height=40,
            fg_color="transparent", hover=False, command=self.toggle_password_visibility
        )
        self.toggle_password_button.pack(side="right")

        #======== forgot password label ========
        self.forgot_password = ctk.CTkLabel(self.card, text="Forgot Password?", text_color="#3b82f6",
                                            cursor="hand2", font=ctk.CTkFont(size=12))
        self.forgot_password.pack(anchor="e", padx=20)
        if self.switch_to_forgot_password:
            self.forgot_password.bind("<Button-1>", lambda e: self.switch_to_forgot_password())

        #======== login button ========
        self.login_button = ctk.CTkButton(self.card, text="Log In", width=300, height=40, corner_radius=10,
                                          fg_color="#39ff14", hover_color="#28c20e", text_color="black",
                                          command=self.login)
        self.login_button.pack(pady=(5, 0))

        #======== signup link section ========
        signup_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        signup_frame.pack(pady=(5, 0))

        not_member_label = ctk.CTkLabel(signup_frame, text="Not a member?", text_color="#555")
        not_member_label.pack(side="left")

        create_account = ctk.CTkLabel(signup_frame, text="Create New Account", text_color="#3b82f6",
                                      cursor="hand2")
        create_account.pack(side="left", padx=(5))
        create_account.bind("<Button-1>", lambda e: self.switch_to_register())

        #======== divider ========
        divider = ctk.CTkLabel(self.card, text="────────  Or continue with  ────────", text_color="#aaa")
        divider.pack(pady=5)

        #======== google login button ========
        google_button = ctk.CTkButton(self.card, text="Continue with Google", width=300, height=40,
                                      fg_color="#1a1a1a", text_color="white",
                                      hover_color="#2b2c2b", border_width=1, border_color="#ccc",
                                      command=lambda: messagebox.showinfo("Google", "Google login not yet implemented."))
        google_button.pack()

    #======== function to toggle password visibility ========
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

    #======== login logic ========
    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        success, msg = authenticate(email, password)
        if success:
            messagebox.showinfo("Login", msg)
            self.clear_fields()
            if self.on_login_success:
                self.on_login_success()
        else:
            messagebox.showerror("Login Failed", msg)

    #======== clear entries and reset placeholders ========
    def clear_fields(self):
        self.email_entry.delete(0, 'end')  # clear email field
        self.email_entry.configure(placeholder_text="Email")  # restore placeholder

        self.password_entry.delete(0, 'end')  # clear password field
        self.password_entry.configure(placeholder_text="Password")  # restore placeholder

        self.password_entry.configure(show="*")  # reset password to hidden
        if self.icon_closed:
            self.toggle_password_button.configure(image=self.icon_closed)  # reset eye icon
        self.show_password = False  # reset password toggle state
