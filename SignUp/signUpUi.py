import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageDraw
from SignUp.signUpBackend import register_user
from tkinter import filedialog
import os
import shutil


#======== helper function to make circular image ========
def make_circle(img: Image.Image) -> Image.Image:
    size = img.size
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)
    img = img.convert("RGBA")
    img.putalpha(mask)
    return img

#======== sign up page class ========
class SignUpPage(ctk.CTkFrame):
    def __init__(self, parent, switch_to_login):
        super().__init__(parent)
        self.switch_to_login = switch_to_login
        self.user_info = {}

        #======== background image ========
        try:
            bg_image = Image.open("image/bg.jpg").resize((1500, 710), Image.Resampling.LANCZOS)
            self.bg_photo = ctk.CTkImage(light_image=bg_image, size=bg_image.size)
            self.bg_label = ctk.CTkLabel(self, image=self.bg_photo, text="")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print("Background image not found or failed to load:", e)

        #======== card container ========
        self.card = ctk.CTkFrame(self, width=360, height=530, corner_radius=15, fg_color="white", border_width=3)
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)

        #======== profile image preview (circle) ========
        self.profile_img_label = ctk.CTkLabel(self.card, text="")
        self.profile_img_label.pack(pady=(15, 5))
        self.set_profile_image(None)

        #======== upload photo button ========
        upload_btn = ctk.CTkButton(self.card, text="Upload Photo", width=120, fg_color="#39ff14",hover_color="#28c20e", text_color="black", command=self.upload_photo)
        upload_btn.pack(pady=(0, 10))

        #======== page title ========
        title = ctk.CTkLabel(self.card, text="Create an Account",
                             font=ctk.CTkFont(size=20, weight="bold"), text_color="#333")
        title.pack(pady=(20, 10))

        #======== input fields: username & email ========
        self.username_entry = ctk.CTkEntry(self.card, placeholder_text="Username", width=300, height=40)
        self.username_entry.pack(pady=5)

        self.email_entry = ctk.CTkEntry(self.card, placeholder_text="Email", width=300, height=40)
        self.email_entry.pack(pady=5)

        #======== prepare password toggle icons ========
        try:
            icon_closed_img = Image.open(r"image/closed.png").resize((25, 25), Image.Resampling.LANCZOS)
            icon_open_img = Image.open(r"image/open.png").resize((25, 25), Image.Resampling.LANCZOS)
            self.icon_closed = ctk.CTkImage(light_image=icon_closed_img, size=(25, 25))
            self.icon_open = ctk.CTkImage(light_image=icon_open_img, size=(25, 25))
        except Exception:
            self.icon_closed = None
            self.icon_open = None

        #======== password entry ========
        self.password_frame = ctk.CTkFrame(self.card, width=300, height=40)
        self.password_frame.pack(pady=5)
        self.password_frame.pack_propagate(False)

        self.password_entry = ctk.CTkEntry(self.password_frame, placeholder_text="Password", show="*", width=270)
        self.password_entry.pack(side="left", fill="y")

        self.show_password = False

        self.toggle_password_button = ctk.CTkButton(
            self.password_frame, image=self.icon_closed, text="", width=30, height=40,
            fg_color="#302e2e", command=self.toggle_password_visibility
        )
        self.toggle_password_button.pack(side="right")

        #======== confirm password entry ========
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

        #======== register button ========
        self.register_button = ctk.CTkButton(self.card, text="Register", width=300, height=40,
                                             fg_color="#39ff14", hover_color="#28c20e",
                                             text_color="black",
                                             command=self.register)
        self.register_button.pack(pady=(10, 0))

        #======== back to login label ========
        self.back_to_login = ctk.CTkLabel(self.card, text="Back to Login", text_color="#3b82f6",
                                          cursor="hand2")
        self.back_to_login.pack(pady=(5, 0))
        self.back_to_login.bind("<Button-1>", lambda e: self.switch_to_login())
   
        #======== circular image setup ========
    def set_profile_image(self, img_path):
        if img_path and os.path.exists(img_path):
            img = Image.open(img_path)
        else:
            img = Image.new("RGB", (200, 200), "#818080")
        circ_img = make_circle(img)
        ctk_img = ctk.CTkImage(light_image=circ_img, dark_image=circ_img, size=(120, 120))
        self.profile_img_label.configure(image=ctk_img)
        self.profile_img_label.image = ctk_img

        #======== upload profile image ========
    def upload_photo(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")]
        )
        if file_path:
            save_dir = "user_images"
            os.makedirs(save_dir, exist_ok=True)
            ext = os.path.splitext(file_path)[1]
            username = self.username_entry.get() or "user"
            save_path = os.path.join(save_dir, f"{username}_profile{ext}")
            shutil.copy(file_path, save_path)

            self.user_info["profile_image"] = save_path
            self.set_profile_image(save_path)

    #======== toggle password visibility ========
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

    #======== toggle confirm password visibility ========
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

    #======== register button logic ========
    def register(self):
        email = self.email_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        image_path = self.user_info.get("profile_image")  
        success, message = register_user(email, username, password, confirm_password, image_path)
      
        if success:
            messagebox.showinfo("Success", message)
            self.switch_to_login()
        else:
            messagebox.showerror("Registration Failed", message)

    #======== clear input fields ========
    def clear_fields(self):
        self.username_entry.delete(0, 'end')
        self.username_entry.configure(placeholder_text="Username")

        self.email_entry.delete(0, 'end')
        self.email_entry.configure(placeholder_text="Email")

        self.password_entry.delete(0, 'end')
        self.password_entry.configure(placeholder_text="Password", show="*")

        self.confirm_password_entry.delete(0, 'end')
        self.confirm_password_entry.configure(placeholder_text="Confirm Password", show="*")

        self.show_password = False
        self.show_confirm_password = False

        if self.icon_closed:
            self.toggle_password_button.configure(image=self.icon_closed)
            self.toggle_confirm_password_button.configure(image=self.icon_closed)

        # Reset profile image preview
        self.user_info["profile_image"] = None
        self.set_profile_image(None)

