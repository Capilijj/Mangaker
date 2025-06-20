import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageDraw
from customtkinter import CTkImage
import os
import shutil

# ==== Import backend ====
try:
    from Profile.profileBackend import get_user_prof, save_user_prof
except ImportError:
    def get_user_prof():
        return {"username": "Unknown User", "email": "unknown@gmail.com", }
    def save_user_prof(profile):
        pass

# ==== Circle Image Utility ====
def make_circle(img):
    size = (min(img.size),) * 2
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    output = Image.new('RGBA', size)
    img = img.resize(size, Image.Resampling.LANCZOS)
    output.paste(img, (0, 0), mask)
    return output

# ==== Profile Page UI ====
class ProfilePage(ctk.CTkFrame):
    def __init__(self, parent, on_logout=None, on_bookmark=None, topbar=None):
        super().__init__(parent)
        self.on_logout = on_logout
        self.on_bookmark = on_bookmark
        self.topbar = topbar

        # ==== Load user info ====
        self.user_info = get_user_prof()
        self.username = self.user_info.get("username", "Unknown User")
        self.email = self.user_info.get("email", "unknown@gmail.com")
        self.profile_img_path = self.user_info.get("profile_image", None)

        # ==== Title ====
        self.title_label = ctk.CTkLabel(self, text="Profile", font=ctk.CTkFont(size=28, weight="bold"), text_color="white")
        self.title_label.pack(pady=(40, 10))

        # ==== Profile Image ====
        self.profile_img_label = ctk.CTkLabel(self, text="")
        self.profile_img_label.pack(pady=(0, 10))

        # ==== Username Display Only (No Editing) ====
        self.username_label = ctk.CTkLabel(self, text=f" {self.username}", font=ctk.CTkFont(size=20, weight="bold"), text_color="#39ff14")
        self.username_label.pack(pady=(0, 5))

        # ==== Email Display ====
        self.email_label = ctk.CTkLabel(self, text=f" {self.email}", font=ctk.CTkFont(size=16), text_color="white")
        self.email_label.pack(pady=(0, 25))


        # ==== Buttons ====
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(pady=(0, 20))

        button_width = 200

        # ==== Upload Button ====
        self.upload_btn = ctk.CTkButton(self.button_frame, text="Update Photo", command=self.upload_photo, width=button_width,height=45, corner_radius=12, fg_color="#39ff14", hover_color="#28c20e", text_color="black", font=ctk.CTkFont(size=16, weight="bold"))
        self.upload_btn.pack(pady=(0, 15))

        # ==== Logout Button ====
        self.logout_btn = ctk.CTkButton(self.button_frame,text="Log Out",command=self.logout_action, width=button_width,height=45,corner_radius=12,fg_color="#39ff14", hover_color="#28c20e", text_color="black",font=ctk.CTkFont(size=16, weight="bold"))
        self.logout_btn.pack()

        # ==== Load Image ====
        self.set_profile_image(self.profile_img_path)

    def set_profile_image(self, img_path):
        if img_path and os.path.exists(img_path):
            img = Image.open(img_path)
        else:
            img = Image.new("RGB", (200, 200), "#C9C5C5")
        circ_img = make_circle(img)
        ctk_img = CTkImage(light_image=circ_img, dark_image=circ_img, size=(120, 120))
        self.profile_img_label.configure(image=ctk_img)
        self.profile_img_label.image = ctk_img

    def upload_photo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
        if file_path:
            save_dir = "user_images"
            os.makedirs(save_dir, exist_ok=True)
            ext = os.path.splitext(file_path)[1]
            username = self.user_info.get("username", "user")
            save_path = os.path.join(save_dir, f"{username}_profile{ext}")
            shutil.copy(file_path, save_path)

            # 🔄 Auto-update backend and UI
            self.user_info["profile_image"] = save_path
            try:
                save_user_prof(self.user_info)
                print("Profile updated automatically.")
            except Exception as e:
                print(" Failed to auto-save profile:", str(e))

            self.set_profile_image(save_path)
            
            if self.topbar:
                self.topbar.refresh_profile_icon()

    def refresh_profile_info(self):
        self.user_info = get_user_prof()
        self.username = self.user_info.get("username", "Unknown User")
        self.email = self.user_info.get("email", "unknown@gmail.com")
        self.profile_img_path = self.user_info.get("profile_image", None)

        self.username_label.configure(text=f" {self.username}")
        self.email_label.configure(text=f" {self.email}")
        self.set_profile_image(self.profile_img_path)

    def logout_action(self):
        print("[Logging out...")
        if self.on_logout:
            self.on_logout()
        else:
            print("No logout callback provided.")

# ==== Standalone Test ====
if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("green")
    app = ctk.CTk()
    app.geometry("400x700")

    def go_to_login():
        from Login.loginUi import LoginPage
        app.title("Login")
        for widget in app.winfo_children():
            widget.destroy()
        LoginPage(app, None, None, lambda: print("Go to dashboard")).pack(fill="both", expand=True)

    profile = ProfilePage(app, on_logout=go_to_login)
    profile.pack(fill="both", expand=True)
    app.mainloop()
