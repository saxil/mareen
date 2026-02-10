import os
import subprocess
import pyautogui
import webbrowser
from AppOpener import open as open_app
# Import file operations from the new module. 
# Note: In a package structure, we might need 'modules.files' or '..modules.files' depending on import context.
# Since sys.path was appended in main.py, absolute import 'modules.files' should work.
from modules.files import open_explorer, select_and_open_file, find_files, show_search_results
from core.tts import speak

def execute_system_command(command):
    if command == "explorer":
        open_explorer()
        return

    if command == "pick_file":
        select_and_open_file()
        return
        
    if command.startswith("find_file:"):
        keyword = command.split(":", 1)[1]
        speak(f"Searching for {keyword}...")
        results = find_files(keyword)
        if results:
            count = len(results)
            speak(f"I found {count} files. Please select one from the list.")
            show_search_results(results)
        else:
            speak(f"Sorry, I couldn't find any file matching {keyword}.")
        return

    if command.startswith("open:"):
        app_name = command.split(":", 1)[1].strip()
        
        # Cleanup "my" (e.g., "open my gmail" -> "gmail")
        if app_name.lower().startswith("my "):
            app_name = app_name[3:].strip()

        print(f"Attempting to open: {app_name}")
        speak(f"Opening {app_name}.")

        # 1. Specific Web Overrides (Common ones)
        if "gmail" in app_name.lower() or "google mail" in app_name.lower():
            webbrowser.open("https://mail.google.com")
            return
        if "youtube" in app_name.lower():
            webbrowser.open("https://www.youtube.com")
            return

        # 2. Try Local Application
        try:
            # Match closest ensures "chrome" opens "Google Chrome"
            open_app(app_name, match_closest=True, throw_error=True)
            return 
        except Exception:
            pass # Fall through to web fallback

        # 3. Web Fallback (The "Every App" Solution)
        # If we can't find the app locally, assume it's a website.
        # Remove spaces for URL (e.g. "amazon prime" -> "amazonprime.com")
        url_name = app_name.replace(" ", "")
        web_url = f"https://www.{url_name}.com"
        print(f"App not found locally. Falling back to: {web_url}")
        webbrowser.open(web_url)

    elif command == "calc":
        subprocess.Popen("calc.exe")
    elif command == "notepad":
        subprocess.Popen("notepad.exe")
    else:
        print(f"Unknown command: {command}")
