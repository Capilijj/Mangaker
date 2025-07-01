import customtkinter as ctk
from tkinter import messagebox
from user_model import update_user_password, user_exists  # <-- import user_exists
from Forgot_pass.forgotBackend import send_otp_email
from PIL import Image
import random
import time
import os

#=========================================================================================
                        #SAME LOGIC LANG SA LOGIN UI AND BACKEND OTP METHOD  
#=========================================================================================
# ======== OTP Popup for Forgot Password ========
class ForgotOtpPopup(ctk.CTkFrame):
    def __init__(self, parent, email, on_success):
        super().__init__(parent, width=550, height=300, corner_radius=20, fg_color="black", border_width=2, border_color="#A0A0A0")
        self.email = email
        self.on_success = on_success
        self.otp = None
        self.expiry = None
        self.otp_entries = []
        self.cancelled = False

        self.build_ui()

    def generate_and_send_otp_and_show(self):
        self.otp = str(random.randint(100000, 999999))
        self.expiry = time.time() + 300
        success = send_otp_email(self.email, self.otp)
        if success:
            messagebox.showinfo("OTP Sent", "OTP sent to your email.")
            self.place(relx=0.5, rely=0.5, anchor="center")
            self.countdown()
        else:
            messagebox.showerror("Error", "Failed to send OTP.")
            self.destroy()

    def build_ui(self):
        ctk.CTkLabel(self, text="Enter the 6-digit OTP", font=("Arial", 20), text_color="white").pack(pady=20)
        otp_frame = ctk.CTkFrame(self, fg_color="transparent")
        otp_frame.pack(pady=10)
        for i in range(6):
            entry = ctk.CTkEntry(
                otp_frame, width=60, height=60, justify='center',
                font=("Arial", 24), corner_radius=12, fg_color="#FFFFFF",
                text_color="black", border_width=2, border_color="#0F0F0F"
            )
            entry.grid(row=0, column=i, padx=10)
            entry.bind("<KeyRelease>", lambda e, idx=i: self.handle_key(e, idx))
            self.otp_entries.append(entry)
        self.otp_entries[0].focus()
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=20)
        ctk.CTkButton(button_frame, text="Verify", command=self.verify_otp, text_color="black",
                      fg_color="#39ff14", hover_color="#1f8112", width=120, height=40).pack(side="left", padx=20)
        ctk.CTkButton(button_frame, text="Cancel", command=self.cancel_otp, text_color="black",
                      fg_color="gray", hover_color="red", width=120, height=40).pack(side="left", padx=20)
        self.countdown_label = ctk.CTkLabel(self, text="", text_color="white")
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
            self.generate_and_send_otp_and_show()
            for entry in self.otp_entries:
                entry.delete(0, 'end')
            self.otp_entries[0].focus()
            return
        entered = ''.join(e.get().strip() for e in self.otp_entries)
        if entered == self.otp:
            self.cancelled = True
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
        import threading
        def run():
            for i in range(300, 0, -1):
                if self.cancelled or not self.winfo_exists():
                    return
                mins, secs = divmod(i, 60)
                try:
                    if self.countdown_label.winfo_exists():
                        self.countdown_label.configure(text=f"OTP expires in {mins}:{secs:02}")
                except Exception:
                    return
                time.sleep(1)
            try:
                if self.countdown_label.winfo_exists():
                    self.countdown_label.configure(text="OTP expired.")
            except Exception:
                pass
        threading.Thread(target=run, daemon=True).start()

#======== Forgot Password Page Class ========
class ForgotPasswordPage(ctk.CTkFrame):
    def __init__(self, parent, switch_to_login):
        super().__init__(parent)
        self.parent = parent
        self.switch_to_login = switch_to_login
        self.show_password = False

        #======== Background Image ========
        try:
            bg_image = Image.open("image/bg.jpg").resize((1500, 710), Image.Resampling.LANCZOS)
            self.bg_photo = ctk.CTkImage(light_image=bg_image, size=bg_image.size)
            self.bg_label = ctk.CTkLabel(self, image=self.bg_photo, text="")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print("Background image not found or failed to load:", e)

        #======== Card Container ========
        self.card = ctk.CTkFrame(self, width=360, height=280, corner_radius=15, fg_color="white", border_width=3)
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)

        #======== Page Title ========
        self.title = ctk.CTkLabel(self.card, text="Forgot Password",
                                  font=ctk.CTkFont(size=20, weight="bold"), text_color="#333")
        self.title.pack(pady=(20, 10))

        #======== Email Entry ========
        self.email_entry = ctk.CTkEntry(self.card, placeholder_text="Enter your email", width=300, height=40)
        self.email_entry.pack(pady=5)

        #======== Password input with toggle ========
        password_frame = ctk.CTkFrame(self.card, width=300, height=40)
        password_frame.pack(pady=(5, 5))
        password_frame.pack_propagate(False)

        self.password_entry = ctk.CTkEntry(password_frame, placeholder_text="New Password", show="*", width=270, height=40)
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

        self.toggle_password_button = ctk.CTkButton(
            password_frame, image=self.icon_closed, text="", width=30, height=40,
            fg_color="transparent", hover=False, command=self.toggle_password_visibility
        )
        self.toggle_password_button.pack(side="right")

        #======== Submit Button ========
        self.send_button = ctk.CTkButton(
            self.card, text="Submit", width=300, height=40,
            fg_color="#39ff14", hover_color="#28c20e", text_color="black",
            command=self.send_reset_link
        )
        self.send_button.pack(pady=10)

        #======== Back to Login Label ========
        self.back_to_login = ctk.CTkLabel(self.card, text="Back to Login", text_color="#3b82f6",
                                          cursor="hand2")
        self.back_to_login.pack()
        self.back_to_login.bind("<Button-1>", lambda e: self.switch_to_login())

    def toggle_password_visibility(self):
        self.show_password = not self.show_password
        if self.show_password:
            self.password_entry.configure(show="")
            if self.icon_open:
                self.toggle_password_button.configure(image=self.icon_open)
        else:
            self.password_entry.configure(show="*")
            if self.icon_closed:
                self.toggle_password_button.configure(image=self.icon_closed)

    #======== Send Reset Link Logic ========
    def send_reset_link(self):
        email = self.email_entry.get().strip()
        new_password = self.password_entry.get().strip()

        if not email or not new_password:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return
        if not (6 <= len(new_password) <= 15):
            messagebox.showerror("Input Error", "Password must be 6-15 characters.")
            return

        # ======== Email existence validation ========
        if not user_exists(email):
            messagebox.showerror("Error", "Email does not exist in our records.")
            return

        def after_otp_verified():
            try:
                success, msg = update_user_password(email, new_password)
                if success:
                    messagebox.showinfo("Success", "Password changed successfully!")
                    self.clear_fields()
                    self.switch_to_login()
                else:
                    messagebox.showerror("Error", msg)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update password: {e}")

        otp_popup = ForgotOtpPopup(self.parent, email=email, on_success=after_otp_verified)
        otp_popup.generate_and_send_otp_and_show()

    #======== Clear Fields When Page is Loaded ========
    def clear_fields(self):
        self.email_entry.delete(0, 'end')
        self.email_entry.configure(placeholder_text="Enter your email")
        self.password_entry.delete(0, 'end')
        self.password_entry.configure(placeholder_text="New Password")