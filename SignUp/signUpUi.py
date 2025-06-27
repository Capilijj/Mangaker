import customtkinter as ctk 
from tkinter import messagebox, filedialog
from PIL import Image, ImageDraw
from SignUp.signUpBackend import validate_user_data, finalize_registration, send_otp_email

import os
import shutil
import random
import time
import threading
from functools import partial

# ======== Helper Function to Make Circular Image ========
def make_circle(img: Image.Image) -> Image.Image:
    size = img.size
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)
    img = img.convert("RGBA")
    img.putalpha(mask)
    return img

#=======OTP POPUP AS CONTAINER INSTEAD OF WINDOW=========
class OtpPopup(ctk.CTkFrame):
    def __init__(self, parent, email, on_success):
        # Increased container size, corner radius
        super().__init__(parent, width=550, height=300, corner_radius=20, fg_color="black", border_width=2, border_color="#A0A0A0")
        self.email = email
        self.on_success = on_success
        self.otp = None
        self.expiry = None
        self.otp_entries = []
        self.cancelled = False

        self.build_ui()
        # Do NOT call self.place() or generate_and_send_otp() here

    def generate_and_send_otp_and_show(self):
        self.otp = str(random.randint(100000, 999999))
        self.expiry = time.time() + 300
        success = send_otp_email(self.email, self.otp)

        if success:
            messagebox.showinfo("OTP Sent", "OTP sent to your email.")
            self.place(relx=0.5, rely=0.5, anchor="center") # Place the popup after message
            self.countdown()
        else:
            messagebox.showerror("Error", "Failed to send OTP.")
            self.destroy()

    def build_ui(self):
        ctk.CTkLabel(self, text="Enter the 6-digit OTP", font=("Arial", 20)).pack(pady=20)

        otp_frame = ctk.CTkFrame(self, fg_color="transparent")
        otp_frame.pack(pady=10)

        for i in range(6):
            entry = ctk.CTkEntry(
                otp_frame,
                width=60,   # Wider input
                height=60,  # Taller input
                justify='center',
                font=("Arial", 24),  # Larger font
                corner_radius=12,    # Rounder corners
                fg_color="#272829",
                text_color="black",
                border_width=2,
                border_color="#0F0F0F"
            )
            entry.grid(row=0, column=i, padx=10)  # More spacing
            entry.bind("<KeyRelease>", partial(self.handle_key, index=i))
            self.otp_entries.append(entry)

        self.otp_entries[0].focus()

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=20)

        ctk.CTkButton(button_frame, text="Verify", command=self.verify_otp, text_color="black",
                      fg_color="#39ff14", hover_color="#1f8112", width=120, height=40).pack(side="left", padx=20)
        ctk.CTkButton(button_frame, text="Cancel", command=self.cancel_otp, text_color="black",
                      fg_color="gray", hover_color="red", width=120, height=40).pack(side="left", padx=20)

        self.countdown_label = ctk.CTkLabel(self, text="")
        self.countdown_label.pack(pady=10)

    def handle_key(self, event, index):
        key = event.keysym
        current = self.otp_entries[index]
        if key == "BackSpace":
            if current.get() == "" and index > 0:
                self.otp_entries[index - 1].focus()
                self.otp_entries[index - 1].delete(0, "end")
            else:
                current.delete(0, "end")
        elif event.char.isdigit():
            if len(current.get()) > 1:
                current.delete(1, "end")
            if index < 5:
                self.otp_entries[index + 1].focus()

    def verify_otp(self):
        if time.time() > self.expiry:
            messagebox.showerror("Expired", "OTP has expired.")
            self.generate_and_send_otp_and_show() # Re-send OTP if expired
            for entry in self.otp_entries:
                entry.delete(0, 'end')
            self.otp_entries[0].focus()
            return

        entered = ''.join(e.get().strip() for e in self.otp_entries)
        if entered == self.otp:
            messagebox.showinfo("Verified", "OTP verified successfully.")
            self.destroy()
            self.on_success()
        else:
            messagebox.showerror("Incorrect", "Incorrect OTP. Try again.")
            for entry in self.otp_entries:
                entry.delete(0, 'end')
            self.otp_entries[0].focus()

    def cancel_otp(self):
        self.cancelled = True
        messagebox.showinfo("Cancelled", "OTP process was cancelled.")
        self.destroy()

    def countdown(self):
        def run():
            for i in range(300, 0, -1):
                if self.cancelled:
                    return
                mins, secs = divmod(i, 60)
                self.countdown_label.configure(text=f"OTP expires in {mins}:{secs:02}")
                time.sleep(1)
            self.countdown_label.configure(text="OTP expired.")
        threading.Thread(target=run, daemon=True).start()
        
# ======== SignUp Page Class ========
class SignUpPage(ctk.CTkFrame):
    def __init__(self, parent, switch_to_login):
        super().__init__(parent)
        self.switch_to_login = switch_to_login
        self.user_info = {"profile_image": None}

        # ======== Background Image ========
        try:
            bg_image = Image.open("image/bg.jpg").resize((1500, 710), Image.Resampling.LANCZOS)
            self.bg_photo = ctk.CTkImage(light_image=bg_image, size=bg_image.size)
            self.bg_label = ctk.CTkLabel(self, image=self.bg_photo, text="")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print("Background image not found or failed to load:", e)

        # ======== Card Container ========
        self.card = ctk.CTkFrame(self, width=360, height=530, corner_radius=15, fg_color="white", border_width=3)
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)

        # ======== Profile Image Preview ========
        self.profile_img_label = ctk.CTkLabel(self.card, text="")
        self.profile_img_label.pack(pady=(15, 5))
        self.set_profile_image(None)

        # ======== Upload Photo Button ========
        upload_btn = ctk.CTkButton(self.card, text="Upload Photo", width=120, fg_color="#39ff14",
                                   hover_color="#28c20e", text_color="black", command=self.upload_photo)
        upload_btn.pack(pady=(0, 10))

        # ======== Title ========
        title = ctk.CTkLabel(self.card, text="Create an Account",
                             font=ctk.CTkFont(size=20, weight="bold"), text_color="#333")
        title.pack(pady=(20, 10))

        # ======== Input Fields ========
        self.username_entry = ctk.CTkEntry(self.card, placeholder_text="Username", width=300, height=40)
        self.username_entry.pack(pady=5)

        self.email_entry = ctk.CTkEntry(self.card, placeholder_text="Email", width=300, height=40)
        self.email_entry.pack(pady=5)

        # ======== Password Icons ========
        try:
            icon_closed_img = Image.open("image/closed.png").resize((25, 25), Image.Resampling.LANCZOS)
            icon_open_img = Image.open("image/open.png").resize((25, 25), Image.Resampling.LANCZOS)
            self.icon_closed = ctk.CTkImage(light_image=icon_closed_img, size=(25, 25))
            self.icon_open = ctk.CTkImage(light_image=icon_open_img, size=(25, 25))
        except Exception:
            self.icon_closed = None
            self.icon_open = None

        # ======== Password Entry ========
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

        # ======== Confirm Password Entry ========
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

        # ======== Register Button ========
        self.register_button = ctk.CTkButton(self.card, text="Register", width=300, height=40,
                                             fg_color="#39ff14", hover_color="#28c20e",
                                             text_color="black", command=self.register)
        self.register_button.pack(pady=(10, 0))

        # ======== Back to Login ========
        self.back_to_login = ctk.CTkLabel(self.card, text="Back to Login", text_color="#3b82f6", cursor="hand2")
        self.back_to_login.pack(pady=(5, 0))
        self.back_to_login.bind("<Button-1>", lambda e: self.switch_to_login())

    def set_profile_image(self, img_path):
        if img_path and os.path.exists(img_path):
            img = Image.open(img_path)
        else:
            img = Image.new("RGB", (200, 200), "#818080")
        circ_img = make_circle(img)
        ctk_img = ctk.CTkImage(light_image=circ_img, dark_image=circ_img, size=(120, 120))
        self.profile_img_label.configure(image=ctk_img)
        self.profile_img_label.image = ctk_img

    def upload_photo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
        if file_path:
            save_dir = "image"
            os.makedirs(save_dir, exist_ok=True)
            original_name = os.path.basename(file_path)
            name, ext = os.path.splitext(original_name)
            save_path = os.path.join(save_dir, f"{name} {ext}")
            shutil.copy(file_path, save_path)
            self.user_info["profile_image"] = save_path
            self.set_profile_image(save_path)

    def toggle_password_visibility(self):
        self.show_password = not self.show_password
        self.password_entry.configure(show="" if self.show_password else "*")
        if self.icon_open and self.icon_closed:
            self.toggle_password_button.configure(image=self.icon_open if self.show_password else self.icon_closed)

    def toggle_confirm_password_visibility(self):
        self.show_confirm_password = not self.show_confirm_password
        self.confirm_password_entry.configure(show="" if self.show_confirm_password else "*")
        if self.icon_open and self.icon_closed:
            self.toggle_confirm_password_button.configure(image=self.icon_open if self.show_confirm_password else self.icon_closed)

    
    def register(self):
        # ✅ FETCH FIELDS BEFORE VALIDATION
        email = self.email_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()
        image_path = self.user_info.get("profile_image", None)

        is_valid, msg = validate_user_data(email, username, password, confirm_password, image_path)
        if not is_valid:
            messagebox.showerror("Validation Failed", msg)
            return

        def after_otp_verified():
            success, final_msg = finalize_registration(email, username, password, image_path)
            if success:
                messagebox.showinfo("Success", final_msg)
                self.clear_fields()
                self.switch_to_login()
            else:
                messagebox.showerror("Registration Failed", final_msg)

        # Create the OtpPopup instance, but don't place it immediately
        otp_popup = OtpPopup(self, email=email, on_success=after_otp_verified)
        # Now, initiate the OTP sending process, which will then display the popup
        otp_popup.generate_and_send_otp_and_show()


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

        self.user_info["profile_image"] = None
        self.set_profile_image(None)