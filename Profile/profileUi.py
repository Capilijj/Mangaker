import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageDraw
from customtkinter import CTkImage
from Profile.profileBackend import buffer_manga_request, get_user_prof, save_user_prof
from tkinter import messagebox
import os
import shutil

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

        self.user_info = get_user_prof()
        self.username = self.user_info.get("username", "Unknown User")
        self.email = self.user_info.get("email", "unknown@gmail.com")
        self.profile_img_path = self.user_info.get("profile_image", None)

        # ==== Profile Circle Image ====
        self.profile_img_label = ctk.CTkLabel(self, text="")
        self.profile_img_label.pack(pady=(40, 10))
        self.set_profile_image(self.profile_img_path)

        # ==== Nickname and Email ====
        self.nickname_label = ctk.CTkLabel(self, text=self.username, font=ctk.CTkFont(size=20, weight="bold"), text_color="#39ff14")
        self.nickname_label.pack()

        self.email_label = ctk.CTkLabel(self, text=self.email, font=ctk.CTkFont(size=16), text_color="white")
        self.email_label.pack(pady=(0, 20))

        # ==== Button Group ====
        button_style = {
            "width": 200,
            "height": 40,
            "corner_radius": 10,
            "fg_color": "#39ff14",
            "hover_color": "#167e03",
            "text_color": "black"
        }

        self.update_nick_btn = ctk.CTkButton(self, text="Update Name", command=self.toggle_nickname_entry, **button_style)
        self.update_nick_btn.pack(pady=5)

        self.update_photo_btn = ctk.CTkButton(self, text="Update Photo", command=self.upload_photo, **button_style)
        self.update_photo_btn.pack(pady=5)

        self.request_manga_btn = ctk.CTkButton(self, text="Request Manga", command=self.toggle_request_popup, **button_style)
        self.request_manga_btn.pack(pady=5)

        self.logout_btn = ctk.CTkButton(self, text="Log Out", command=self.logout_action, **button_style)
        self.logout_btn.pack(pady=5)

        # ==== Inline Popups ====
        self.nickname_entry_container = None
        self.request_popup_container = None

    def set_profile_image(self, img_path):
        if img_path and os.path.exists(img_path):
            img = Image.open(img_path)
        else:
            img = Image.new("RGB", (200, 200), "#C9C5C5")
        circ_img = make_circle(img)
        ctk_img = CTkImage(light_image=circ_img, dark_image=circ_img, size=(120, 120))
        self.profile_img_label.configure(image=ctk_img)
        self.profile_img_label.image = ctk_img

    def refresh_profile_info(self):
        self.user_info = get_user_prof()
        self.username = self.user_info.get("username", "Unknown User")
        self.email = self.user_info.get("email", "unknown@gmail.com")
        self.profile_img_path = self.user_info.get("profile_image", None)

        self.nickname_label.configure(text=self.username)
        self.email_label.configure(text=self.email)
        self.set_profile_image(self.profile_img_path)

    def toggle_nickname_entry(self):
        if self.nickname_entry_container:
            self.nickname_entry_container.destroy()
            self.nickname_entry_container = None
            return

        self.nickname_entry_container = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=12)
        self.nickname_entry_container.place(relx=0.5, rely=0.5, anchor="center")
        self.nickname_entry_container.configure(width=300, height=150, border_width=2, border_color="#39ff14")

        # ❌ Close Button
        close_btn = ctk.CTkButton(self.nickname_entry_container, text="❌", width=24, height=24,
                                  font=ctk.CTkFont(size=14), corner_radius=100,
                                  fg_color="transparent", hover_color="#333",
                                  command=lambda: self.nickname_entry_container.destroy())
        close_btn.place(relx=1, rely=0, anchor="ne", x=-5, y=5)

        # Entry Field
        entry = ctk.CTkEntry(self.nickname_entry_container, placeholder_text="New Nickname", width=200)
        entry.place(relx=0.5, rely=0.5, anchor="center", y=-10)

        # Save Button
        def save_nickname():
            new_name = entry.get().strip()
            if new_name:
                success, msg = save_user_prof({"username": new_name})
                print("✅" if success else "❌", msg)
                if success:
                    self.refresh_profile_info()
                    if self.topbar:
                        self.topbar.refresh_profile_icon()
                self.nickname_entry_container.destroy()
                self.nickname_entry_container = None

        save_btn = ctk.CTkButton(self.nickname_entry_container, text="Save", command=save_nickname,
                                 width=100, height=35, fg_color="#28c20e", hover_color="#167e03", text_color="black")
        save_btn.place(relx=0.5, rely=0.5, anchor="center", y=35)

    def toggle_request_popup(self):
        if self.request_popup_container:
            self.request_popup_container.destroy()
            self.request_popup_container = None
            return

        self.request_popup_container = ctk.CTkFrame(self, fg_color="#1f1f1f", corner_radius=12)
        self.request_popup_container.place(relx=0.5, rely=0.5, anchor="center")
        self.request_popup_container.configure(width=330, height=180, border_width=2, border_color="#39ff14")

        close_btn = ctk.CTkButton(self.request_popup_container, text="❌", width=24, height=24,
                                  font=ctk.CTkFont(size=14), corner_radius=100,
                                  fg_color="transparent", hover_color="#333",
                                  command=lambda: self.request_popup_container.destroy())
        close_btn.place(relx=1, rely=0, anchor="ne", x=-5, y=5)

        label = ctk.CTkLabel(self.request_popup_container, text="Request Your Manga", text_color="white")
        label.place(relx=0.5, rely=0.2, anchor="center")

        entry = ctk.CTkEntry(self.request_popup_container, width=220)
        entry.place(relx=0.5, rely=0.5, anchor="center")

        def submit_request():
            value = entry.get().strip()
            if not value:
                print("⚠️ Empty request.")
            elif len(value) > 15:
                print("⚠️ Max 15 characters.")
            else:
                success, msg = buffer_manga_request(value, self.email)
            if success:
                messagebox.showinfo("Request Submitted", 
                    "✅ Your request has been submitted successfully!\n\nPlease wait while our admin reviews it. Thank you for your suggestion!")
                self.request_popup_container.destroy()
                self.request_popup_container = None
            else:
                messagebox.showerror("Request Failed", msg)


        submit_btn = ctk.CTkButton(self.request_popup_container, text="Submit", command=submit_request,
                                   fg_color="#39ff14", hover_color="#167e03", text_color="black")
        submit_btn.place(relx=0.5, rely=0.75, anchor="center")

    def upload_photo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
        if file_path:
            save_dir = "images"
            os.makedirs(save_dir, exist_ok=True)
            name, ext = os.path.splitext(os.path.basename(file_path))
            filename = f"{name}{ext}"
            relative_path = os.path.join(save_dir, filename)
            shutil.copy(file_path, relative_path)
            self.user_info["profile_image"] = relative_path

            try:
                save_user_prof(self.user_info)
                print("✅ Profile image updated:", relative_path)
            except Exception as e:
                print("❌ Failed to save profile:", str(e))

            self.set_profile_image(relative_path)
            if self.topbar:
                self.topbar.refresh_profile_icon()

    def logout_action(self):
        print("[Logging out...]")
        if self.on_logout:
            self.on_logout()
        else:
            print("No logout callback provided.")
