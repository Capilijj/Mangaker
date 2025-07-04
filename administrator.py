import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image, ImageDraw
import os
from user_model import get_user_prof, get_current_username, clear_current_user
import sqlite3
from datetime import datetime, timedelta
import shutil

# Re-define make_circle here just in case, though it's also in main.py
# If you prefer a single source, you could import it, but having it local
# to components that heavily use it is also common.
def make_circle(img: Image.Image) -> Image.Image:
    size = (min(img.size),) * 2
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    img = img.convert("RGBA").resize(size, Image.Resampling.LANCZOS)
    img.putalpha(mask)
    return img

class AdminPage(ctk.CTkScrollableFrame):
    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)


        admin_header = ctk.CTkFrame(self, fg_color="#39ff14", corner_radius=0)
        admin_header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=(0, 10))
        admin_header.grid_columnconfigure(0, weight=1)

        admin_label = ctk.CTkLabel(admin_header, text="ADMINISTRATOR",
                                   font=ctk.CTkFont(size=28, weight="bold"),
                                   text_color="black")
        admin_label.grid(row=0, column=0, pady=15, sticky="ew")

        self.sidebar = ctk.CTkFrame(self, width=350, border_color="#39ff14", border_width=2)
        self.sidebar.grid(row=1, column=0, sticky="nsw", padx=(10, 5), pady=(0, 10))
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)
       
        self.profile_label = ctk.CTkLabel(self.sidebar, text="")
        self.profile_label.grid(row=0, column=0, pady=(20, 5), sticky="ew")

        self.username_label = ctk.CTkLabel(self.sidebar, text="", font=ctk.CTkFont(size=14, weight="bold"))
        self.username_label.grid(row=1, column=0, sticky="ew")

        logout_btn = ctk.CTkButton(self.sidebar, text="Logout", command=self.logout, fg_color="red",
                                   hover_color="#cc0000", text_color="white", width=100)
        logout_btn.grid(row=2, column=0, pady=10, sticky="ew", padx=(50,50))

        divider = ctk.CTkLabel(self.sidebar, text="─" * 30, text_color="#aaa")
        divider.grid(row=3, column=0, pady=5, sticky="ew", padx=(20,20))

        user_req_label = ctk.CTkLabel(self.sidebar, text="User Requests", font=ctk.CTkFont(size=12, weight="bold"))
        user_req_label.grid(row=4, column=0, sticky="ew")

        self.user_scroll = ctk.CTkScrollableFrame(self.sidebar, width=200, height=400)
        self.user_scroll.grid(row=5, column=0, pady=10, padx=10, sticky="nsew")
        self.sidebar.grid_rowconfigure(5, weight=1)
        self.load_user_requests() # showing all user requests on the sidebar

        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=(0, 10))
        self.content.grid_columnconfigure(0, weight=1)

        header_frame = ctk.CTkFrame(self.content, fg_color="#39ff14", corner_radius=10)
        header_frame.grid(row=0, column=0, pady=(10, 10), padx=10, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header_frame, text="ADD MANGA",
                     font=ctk.CTkFont(size=24, weight="bold"), text_color="black", justify="center").grid(row=0, column=0, pady=10, sticky="ew")

        self.image_box = ctk.CTkFrame(self.content, width=200, height=250, fg_color="#ddd",
                               border_width=1, border_color="#888")
        self.image_box.grid(row=1, column=0, pady=10)
        self.image_box.grid_propagate(False)

        self.image_label = ctk.CTkLabel(self.image_box, text="Upload Image", text_color="#666")
        self.image_label.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkButton(self.content, text="Upload Image", command=self.upload_photo,
              fg_color="#39ff14", hover_color="#1f8112", text_color="black", width=120, height=32).grid(row=2, column=0, pady=(0, 10))

        ctk.CTkLabel(self.content, text="Manga Title:", anchor="w", font=ctk.CTkFont(size=16, weight="bold")).grid(row=3, column=0, sticky="ew", padx=10)
        self.manga_title = ctk.CTkEntry(self.content, placeholder_text="Enter manga title")
        self.manga_title.grid(row=4, column=0, sticky="ew", padx=10, pady=5)

        ctk.CTkLabel(self.content, text="Genre:", anchor="w", font=ctk.CTkFont(size=16, weight="bold")).grid(row=5, column=0, sticky="ew", padx=10)
        self.genres_container_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.genres_container_frame.grid(row=6, column=0, sticky="ew", padx=10, pady=5)

        self.genre_vars = {}
        genres = ["Action", "Adventure", "Comedy", "Drama", "Fantasy", "Romance",
                  "Shounen", "Shoujo", "Seinen", "Josei", "Sci-Fi", "Horror",
                  "Sports", "Slice of Life", "Mystery", "Mecha", "Supernatural",
                  "Historical", "Ecchi", "Isekai"]

        max_columns = 5
        row = 0
        col = 0

        for genre in genres:
            var = ctk.BooleanVar()
            cb = ctk.CTkCheckBox(self.genres_container_frame, text=genre, variable=var,
                                 checkmark_color="#39ff14", fg_color="#222222", border_color="#2DFA0E")
            cb.grid(row=row, column=col, padx=5, pady=5, sticky="w")
            self.genre_vars[genre] = var
            col += 1
            if col >= max_columns:
                col = 0
                row += 1

        ctk.CTkLabel(self.content, text="Status:", anchor="w", font=ctk.CTkFont(size=16, weight="bold")).grid(row=7, column=0, sticky="ew", padx=10)
        self.status = ctk.CTkOptionMenu(self.content,
                                         values=["Ongoing", "Completed", "Hiatus"],
                                         fg_color="#39ff14", text_color="black", button_color="#28c20e")
        self.status.set("Select Status")
        self.status.grid(row=8, column=0, sticky="ew", padx=10, pady=5)

        ctk.CTkLabel(self.content, text="Author:", anchor="w", font=ctk.CTkFont(size=16, weight="bold")).grid(row=9, column=0, sticky="ew", padx=10)
        self.author_entry = ctk.CTkEntry(self.content, placeholder_text="Enter author name")
        self.author_entry.grid(row=10, column=0, sticky="ew", padx=10, pady=5)

        ctk.CTkLabel(self.content, text="Description:", anchor="w", font=ctk.CTkFont(size=16, weight="bold")).grid(row=11, column=0, sticky="ew", padx=10)
        self.description = ctk.CTkTextbox(self.content, height=100)
        self.description.grid(row=12, column=0, sticky="ew", padx=10, pady=5)

        ctk.CTkButton(self.content, text="Submit", command=self.submit_manga,
                      fg_color="#39ff14", hover_color="#1f8112", text_color="black").grid(row=13, column=0, pady=15, sticky="ew")

        ctk.CTkFrame(self.content, height=2, fg_color="#39ff14").grid(row=14, column=0, sticky="ew", padx=10, pady=(5, 10))

       # ------------------ UPDATE MANGA CHAPTER section (full-width like ADD MANGA) ------------------
        chapter_header_frame = ctk.CTkFrame(self.content, fg_color="#39ff14", corner_radius=10)
        chapter_header_frame.grid(row=15, column=0, pady=(10, 10), padx=10, sticky="ew")
        chapter_header_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(chapter_header_frame, text="UPDATE MANGA CHAPTER",
                    font=ctk.CTkFont(size=24, weight="bold"), text_color="black").grid(row=0, column=0, pady=10, sticky="ew")

        self.update_container = ctk.CTkFrame(self.content, fg_color="#1a1a1a", corner_radius=10)
        self.update_container.grid(row=16, column=0, pady=(0, 20), padx=10, sticky="ew")
        self.update_container.grid_columnconfigure(0, weight=1)
        

        # Manga List Label
        ctk.CTkLabel(self.update_container, text="Manga List:", anchor="w",
                    font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        #=====================================================================================================================
        #    DITO YUNG DROP DOWN NA KAILANGAN MO LAGYAN NG LAMAN YUNG TITLE  + name kung dimo pa nababago yung MGA MANGA NATIN
        #=====================================================================================================================
        # Manga List Dropdown
        self.manga_list_dropdown = ctk.CTkOptionMenu(self.update_container,
                                                    values= self.manga_titles(),  # Display all manga titles
                                                    fg_color="#39ff14", text_color="black", button_color="#28c20e")
        self.manga_list_dropdown.set("Select Manga")
        self.manga_list_dropdown.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        # Status Label and Dropdown (row 2 and 3)
        ctk.CTkLabel(self.update_container, text="Status:", anchor="w", font=ctk.CTkFont(size=16, weight="bold")).grid(row=2, column=0, sticky="ew", padx=10)
        self.update_status = ctk.CTkOptionMenu(self.update_container,
                                               values=["Ongoing", "Completed", "Hiatus"],
                                               fg_color="#39ff14", text_color="black", button_color="#28c20e")
        self.update_status.set("Select Status")
        self.update_status.grid(row=3, column=0, sticky="ew", padx=10, pady=5)

        # Chapter Number Label and Entry (row 4 and 5)
        ctk.CTkLabel(self.update_container, text="Chapter Number:", anchor="w",
                    font=ctk.CTkFont(size=16, weight="bold")).grid(row=4, column=0, sticky="ew", padx=10, pady=(10, 0))
        self.chapter_number_entry = ctk.CTkEntry(self.update_container, placeholder_text="Enter chapter number")
        self.chapter_number_entry.grid(row=5, column=0, sticky="ew", padx=10, pady=5)

        # Update Button (row 6)
        ctk.CTkButton(self.update_container, text="Update Chapter", command=self.update_chapter,
                    fg_color="#39ff14", hover_color="#1f8112", text_color="black").grid(row=6, column=0, pady=(5, 10), padx=10, sticky="ew")

        # Call refresh_profile_display here to load admin info when the page is initialized
        self.refresh_profile_display()


#==============================================================================================
                  # BACKEND LOGIC Pero hindi pa conntected sa db
#=============================================================================================
     #[===============DITO YUNG LOGIC========================]
    # Update Chapter Logic dito yung logic ng update dipa connected sa db
    def update_chapter(self):
        manga_title = self.manga_list_dropdown.get()
        chapter_num = self.chapter_number_entry.get()
        status = self.update_status.get()

        # validation if the fields are not filled out properly
        if manga_title == "Select Manga":
            messagebox.showerror("Error", "Please select a manga from the list.")
            return

        if status == "Select Status":
            messagebox.showerror("Error", "Please select a status.")
            return

        if not chapter_num:
            messagebox.showerror("Error", "Please fill out the chapter number.")
            return
        
        # Updating the manga details in the database
        connection = sqlite3.connect('user.db')
        cursor = connection.cursor()
        cursor.execute(""" 
            UPDATE Manga
            SET latest = ?, status = ?
            WHERE title = ?
                       """, (chapter_num, status, manga_title))
        
        connection.commit()
        connection.close()

        messagebox.showinfo("Success", f"Chapter {chapter_num} updated successfully!")



        # resetting the fields after update
        self.chapter_number_entry.delete(0, "end")
        self.manga_list_dropdown.set("Select Manga")
        self.update_status.set("Select Status")

    def manga_titles(self):
        # Connect to the database and fetch manga titles
        connection = sqlite3.connect('user.db')
        cursor = connection.cursor()
        cursor.execute("SELECT title FROM Manga ORDER BY title ASC") # fetching titles in alphabetical order
        titles = [row[0] for row in cursor.fetchall()]
        connection.close()
        return titles if titles else ["No Manga Found"]

    #dito yung mag upload ng image============
    def load_profile_image(self):
        user_info = get_user_prof()
        # The user_model's get_user_prof already returns a default if CURRENT_USER is empty.
        # This means 'profile_image' will either be from DB or 'image/default_profile.png'
        img_path = user_info.get("profile_image")
        size = 80
        if img_path and os.path.exists(img_path):
            try:
                img = Image.open(img_path).resize((size, size), Image.Resampling.LANCZOS)
                img = make_circle(img)
                self.profile_icon = ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
                self.profile_label.configure(image=self.profile_icon, text="")
            except Exception as e:
                print(f"Error loading profile image '{img_path}': {e}")
                self.profile_label.configure(text="👤", font=ctk.CTkFont(size=30)) # Fallback to text icon
        

    def refresh_profile_display(self):
        self.load_profile_image()
        if hasattr(self, 'username_label'):
            # get_current_username() will return None if CURRENT_USER is not set
            username = get_current_username()
            self.username_label.configure(text=username if username else "Admin User") # Fallback text for username


    #logic ng photo ====================================================================================
    def upload_photo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            save_dir = "image"

            os.makedirs(save_dir, exist_ok=True)  # Ensure the directory exists
            
            # Get the original file name and extension
            original_name = os.path.basename(file_path)
            name, ext = os.path.splitext(original_name)
            
            # Construct a new file path in the image directory
            save_path = os.path.join(save_dir, f"{name}{ext}")


            try:
                shutil.copy(file_path, save_path)
                print(f"Image successfully moved to: {save_path}")  # Debug message to verify path

                
                img = Image.open(file_path).resize((180, 220), Image.Resampling.LANCZOS)
                image_ctk = ctk.CTkImage(light_image=img, dark_image=img, size=(180, 220))
                self.image_label.configure(image=image_ctk, text="")
                self.image_label.image = image_ctk
                self.current_image_path = save_path
            except Exception as e:
                messagebox.showerror("Upload Error", str(e))
    #=================================================================================================================
    #dito boi dito mag didisplay ang manga request dito mo iconnect yung sa database ito yung ui para sa request
    # alisin mo nalang yang mga sample request

    def load_user_requests(self):
        for widget in self.user_scroll.winfo_children():
            widget.destroy()


        # Connect to the database and fetch user requests
        connection = sqlite3.connect('user.db')
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Requests")

        requests_rows = cursor.fetchall()
        connection.close()

        requests = [] # List to hold request texts

        # storing all request text to requests list
        for rows in requests_rows:
            request_text = rows[2]
            requests.append(request_text)

        # displaying requests in the scrollable frame
        for idx, req in enumerate(requests):
            ctk.CTkLabel(self.user_scroll, text=req, anchor="w", wraplength=170).grid(row=idx, column=0, sticky="w", padx=5, pady=2)
    #=================================================================================================================
    #Dito yung logic ng submit ng manga may printing nadin sa terminal overall wala patong function na maupdate ang database
    def submit_manga(self):
            # Collecting data from the form to store in db
        title = self.manga_title.get()
        genres = [g for g, v in self.genre_vars.items() if v.get()]
        status = self.status.get()
        author = self.author_entry.get()
        desc = self.description.get("1.0", "end").strip()
        img_path = getattr(self, 'current_image_path', None) # get the path of uploaded image

        if not title or not genres or status == "Select Status" or not author or not desc:
            messagebox.showerror("Error", "Please complete all fields.")
            return

        try:
            # setting timezone to UTC+8 for the update date
            ph_time = datetime.utcnow() + timedelta(hours=8)
            ph_timestamp = ph_time.strftime('%Y-%m-%d %H:%M:%S')

            # Connect to the database and insert the manga data
            connection = sqlite3.connect('user.db')
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO Manga (title, author, latest, status, img_path, description, update_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (title, author, 1, status, img_path, desc, ph_timestamp))
            
            manga_id = cursor.lastrowid  # Get the ID of the newly inserted manga

            for genre in genres:
                cursor.execute("INSERT INTO Genres (mangaId, genre) VALUES (?, ?)", (manga_id, genre))

            connection.commit()
            connection.close()
            messagebox.showinfo("Success", "Manga submitted!")
            self.clear_fields()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to submit manga: {e}")
    #=================================================================================================================
    #hindi na cleclear yung image awit hayaan nalang siguro nag try ako ng ibang way ayaw padin eh try mo
    def clear_fields(self):
        self.manga_title.delete(0, "end")
        for var in self.genre_vars.values():
            var.set(False)
        self.status.set("Select Status")
        self.author_entry.delete(0, "end")
        self.description.delete("1.0", "end")

        # To clear the image, set the image property to None and update the label text

        self.image_label.configure(image=None, text="Upload Image")
        self.image_label.image = None # Important to prevent garbage collection for CTkImage 
   
    #=================================================================================================================
    #log out logic (back to log in)
    def logout(self):
        clear_current_user() # Clear the global CURRENT_USER variable
        if self.controller and hasattr(self.controller, 'show_login'):
            self.controller.show_login() # Go back to login page
        else:
            # Fallback if controller is not set (e.g., if AdminPage is run standalone, which it shouldn't be now)
            self.master.destroy()
        

#temporary runner for testing the AdminPage
if __name__ == "__main__":
    import customtkinter as ctk

    root = ctk.CTk()
    root.title("Admin Page Test")
    root.geometry("1100x800")
    admin_page = AdminPage(root)
    admin_page.pack(fill="both", expand=True)
    root.mainloop()