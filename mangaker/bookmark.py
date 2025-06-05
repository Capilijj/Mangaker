#<<<<<<<<<BOOKMARK PAGE>>>>>>
import customtkinter as ctk

class BookmarkPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        # Scrollable frame setup
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.pack(fill="both", expand=True)



class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Bookmark Page Demo")
        self.geometry("400x500")
        bookmark_page = BookmarkPage(self)
        bookmark_page.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()

        

        
