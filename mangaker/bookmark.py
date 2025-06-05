import customtkinter as ctk

class BookmarkPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        # Scrollable frame setup
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.pack(fill="both", expand=True)

        

        
