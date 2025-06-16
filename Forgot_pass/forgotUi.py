import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
# wala tong backend ken 
#delete mo nalang din to ken comment ko

#======== Forgot Password Page Class ========
class ForgotPasswordPage(ctk.CTkFrame):
    def __init__(self, parent, switch_to_login):
        super().__init__(parent)
        self.parent = parent
        self.switch_to_login = switch_to_login

        #======== Background Image ========
        try:
            bg_image = Image.open("image/bg.jpg").resize((1200, 680), Image.Resampling.LANCZOS)
            self.bg_photo = ctk.CTkImage(light_image=bg_image, size=bg_image.size)
            self.bg_label = ctk.CTkLabel(self, image=self.bg_photo, text="")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print("Background image not found or failed to load:", e)

        #======== Card Container ========
        self.card = ctk.CTkFrame(self, width=360, height=230, corner_radius=15, fg_color="white", border_width=3)
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)

        #======== Page Title ========
        self.title = ctk.CTkLabel(self.card, text="Forgot Password",
                                  font=ctk.CTkFont(size=20, weight="bold"), text_color="#333")
        self.title.pack(pady=(20, 10))

        #======== Email Entry ========
        self.email_entry = ctk.CTkEntry(self.card, placeholder_text="Enter your email", width=300, height=40)
        self.email_entry.pack(pady=10)

        #======== Send Reset Link Button ========
        self.send_button = ctk.CTkButton(
            self.card, text="Send Reset Link", width=300, height=40,
            fg_color="#39ff14", hover_color="#28c20e", text_color="black",
            command=self.send_reset_link
        )
        self.send_button.pack(pady=10)

        #======== Back to Login Label ========
        self.back_to_login = ctk.CTkLabel(self.card, text="Back to Login", text_color="#3b82f6",
                                          cursor="hand2")
        self.back_to_login.pack()
        self.back_to_login.bind("<Button-1>", lambda e: self.switch_to_login())

    #======== Send Reset Link Logic ========
    def send_reset_link(self):
        email = self.email_entry.get()
        if not email:
            messagebox.showwarning("Input Error", "Please enter your email.")
            return
        # TODO: Add logic to check if email exists and send a reset link
        messagebox.showinfo("Forgot Password", "Reset link not implemented.")

    #======== Clear Fields When Page is Loaded ========
    def clear_fields(self):
        self.email_entry.delete(0, 'end')
        self.email_entry.configure(placeholder_text="Enter your email")
