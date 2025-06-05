#<<<<< PROFILE PAGE >>>>>
import customtkinter as ctk

class ProfilePage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        label = ctk.CTkLabel(self, text="👤 Profile Page", font=ctk.CTkFont(size=24))
        label.pack(pady=50)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Profile Page Demo")
        self.geometry("400x300")

        profile_page = ProfilePage(self)
        profile_page.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()