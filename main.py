import customtkinter as ctk

from ui.main_view import MainView

ctk.set_appearance_mode("light")   # "light" | "system"
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("RF-Audio for Beginner v1.0")
        self.geometry("1920x1080")
        self.update_idletasks()    # layout xong hết
        self.after(100, self.deiconify)
        self.after(5,lambda:self.state("zoomed"))
        MainView(self).pack(fill="both", expand=True)
        
if __name__ == "__main__":
    app = App()
    app.mainloop()
