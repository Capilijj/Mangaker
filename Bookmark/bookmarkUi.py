import customtkinter as ctk

class BookmarkPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        # ===== Scrollable frame setup =====
        self.scrollable_frame = ctk.CTkScrollableFrame(self, height=700)
        self.scrollable_frame.pack(fill="both", expand=True, padx=5)

        # ===== Header Container (Black Box) =====
        self.header_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="black", corner_radius=0)
        self.header_frame.pack(pady=40, anchor="center")

        # ===== Header Text =====
        instruction_text = (
            "You can save a list of manga titles here up to 50.\n"
            "The list approves based on the latest update date."
            "The list of manga is stored in a browser that you can use right now."
        )

        self.instruction_label = ctk.CTkLabel(
            self.header_frame,
            text=instruction_text,
            font=ctk.CTkFont(size=16, weight="bold"),
            wraplength=500,
            justify="center",
            text_color="#39ff14"
        )
        self.instruction_label.pack(padx=20, pady=20)


# ==== App Runner for Demo ====
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Bookmark Page Demo")
        self.geometry("700x700")
        bookmark_page = BookmarkPage(self)
        bookmark_page.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()
