import customtkinter as ctk

class ProfilePage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        label = ctk.CTkLabel(self, text="👤 Profile Page", font=ctk.CTkFont(size=24))
        label.pack(pady=50)
