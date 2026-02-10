import customtkinter as ctk
import threading
import sys
import os
from PIL import Image

# Add src to path for direct running if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MareenGUI(ctk.CTk):
    def __init__(self, start_callback):
        super().__init__()

        self.title("Mareen v3.0")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self.header_frame = ctk.CTkFrame(self, height=50, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.title_label = ctk.CTkLabel(self.header_frame, text="M.A.R.E.E.N", font=("Roboto Medium", 20))
        self.title_label.pack(pady=10)

        # Chat Area
        self.chat_display = ctk.CTkTextbox(self, font=("Roboto", 14), activate_scrollbars=True)
        self.chat_display.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        self.chat_display.configure(state="disabled")

        # Status & Controls
        self.footer_frame = ctk.CTkFrame(self, height=100, corner_radius=0)
        self.footer_frame.grid(row=2, column=0, sticky="ew")

        self.status_label = ctk.CTkLabel(self.footer_frame, text="Initializing...", font=("Roboto", 16))
        self.status_label.pack(side="left", padx=20, pady=20)

        self.action_button = ctk.CTkButton(self.footer_frame, text="Start Listening", command=start_callback)
        self.action_button.pack(side="right", padx=20, pady=20)
        
        # Determine colors for text
        self.user_color = "#3B8ED0" # Blue
        self.mareen_color = "#2CC985" # Green

    def update_status(self, text):
        self.status_label.configure(text=text)

    def add_message(self, sender, message):
        self.chat_display.configure(state="normal")
        
        if sender == "User":
            text_color = self.user_color
            prefix = "YOU: "
        else:
            text_color = self.mareen_color
            prefix = "MAREEN: "
            
        self.chat_display.insert("end", f"\n{prefix}", ("prefix",))
        self.chat_display.insert("end", f"{message}\n")
        
        # Tag configuration might not be fully supported in basic ctk textbox in the same way 
        # but we can try basic formatting or just rely on color for now if we extended it.
        # For simplicity in ctk 5.x, simple text is best.  
        
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")

