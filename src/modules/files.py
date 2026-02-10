import os
import subprocess
import tkinter as tk
from tkinter import filedialog

def open_explorer(path=None):
    """Opens Windows File Explorer. If path is provided, opens at that location."""
    try:
        if path:
            os.startfile(path)
        else:
            subprocess.Popen(["explorer.exe"])
        print("File Explorer opened.")
    except Exception as e:
        print(f"Error opening explorer: {e}")

def select_and_open_file():
    """Opens a file picker dialog and then opens the selected file."""
    try:
        # Create a hidden root window
        root = tk.Tk()
        root.withdraw()
        root.wm_attributes('-topmost', 1)  # Ensure dialog is top-most

        print("Opening file dialog...")
        file_path = filedialog.askopenfilename(title="Select a file to open")
        root.destroy()

        if file_path:
            print(f"Selected: {file_path}")
            os.startfile(file_path)
            return file_path
        else:
            print("No file selected.")
            return None
    except Exception as e:
        print(f"Error in file selection: {e}")
        return None

def find_files(keyword):
    """Searches for files containing keyword in common user directories."""
    search_path = os.path.expanduser("~")
    matches = []
    print(f"Searching for '{keyword}'...")
    
    # Restrict search to common user folders to avoid scanning AppData/System
    common_dirs = ["Desktop", "Documents", "Downloads", "Pictures", "Videos", "Music"]
    target_paths = [os.path.join(search_path, d) for d in common_dirs]
    
    for path in target_paths:
        if not os.path.exists(path):
            continue
            
        # Walk limits recursion depth implicitly by folder choice, but still can be deep.
        for root, dirs, files in os.walk(path):
            # Stop if we have enough results
            if len(matches) >= 10: 
                return matches
                
            for filename in files:
                if keyword.lower() in filename.lower():
                    matches.append(os.path.join(root, filename))
    
    return matches

def show_search_results(files):
    """Displays a GUI list of found files to open."""
    if not files:
        return

    def open_selected():
        selection = listbox.curselection()
        if selection:
            file_path = listbox.get(selection[0])
            try:
                os.startfile(file_path)
                root.destroy()
            except Exception as e:
                print(f"Error opening file: {e}")

    def open_folder():
        selection = listbox.curselection()
        if selection:
            file_path = listbox.get(selection[0])
            try:
                folder = os.path.dirname(file_path)
                os.startfile(folder)
            except Exception as e:
                print(f"Error opening folder: {e}")

    root = tk.Tk()
    root.title("Jarvis - Files Found")
    root.geometry("600x400")
    root.wm_attributes('-topmost', 1)

    label = tk.Label(root, text=f"Found {len(files)} files:", font=("Arial", 12))
    label.pack(pady=5)

    listbox = tk.Listbox(root, width=80, height=15)
    listbox.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

    for f in files:
        listbox.insert(tk.END, f)

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)

    btn_open = tk.Button(btn_frame, text="Open File", command=open_selected, width=15)
    btn_open.pack(side=tk.LEFT, padx=5)

    btn_folder = tk.Button(btn_frame, text="Open Folder", command=open_folder, width=15)
    btn_folder.pack(side=tk.LEFT, padx=5)

    btn_close = tk.Button(btn_frame, text="Close", command=root.destroy, width=10)
    btn_close.pack(side=tk.LEFT, padx=5)

    root.mainloop()
