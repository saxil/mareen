import os
import threading
import time
import webview
import sys

# Add src to path if needed (though running from root usually covers it)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Core Imports
from core.transcription import StreamingSTT
from core.llm import process_text
from core.tts import speak
from core.intent import basic_intent_parser
from modules.system import execute_system_command
# from modules.files import execute as file_exec

class JarvisAPI:
    def __init__(self):
        self._running = False
        self._window = None
        self._listening_paused = False
        self.stt = None

    def set_window(self, window):
        self._window = window

    def toggle_listening(self, active):
        """Called from JS to toggle listening state"""
        print(f"DEBUG: toggle_listening called with {active}")
        self._listening_paused = not active
        status = "LISTENING..." if not self._listening_paused else "PAUSED"
        self.update_status(status)

    def start_listening(self):
        """Called from JS or auto-start to begin the loop"""
        print("DEBUG: start_listening called")
        if not self._running:
            self._running = True
            print("DEBUG: Starting main_loop thread")
            threading.Thread(target=self.main_loop, daemon=True).start()

    def update_status(self, text):
        print(f"DEBUG: update_status -> {text}")
        if self._window:
            try:
                self._window.evaluate_js(f'py_updateStatus("{text}")')
            except Exception as e:
                print(f"DEBUG: Could not update UI status (JS possibly not ready): {e}")

    def add_message(self, sender, text):
        # Escape quotes for JS safety
        safe_text = text.replace('"', '\\"').replace('\n', ' ')
        if self._window:
            try:
                self._window.evaluate_js(f'py_addMessage("{sender}", "{safe_text}")')
            except Exception as e:
                print(f"DEBUG: Could not add message to UI: {e}")

    def update_user_streaming(self, text):
        safe_text = text.replace('"', '\\"').replace('\n', ' ')
        if self._window:
            try:
                self._window.evaluate_js(f'py_updateUserStreaming("{safe_text}")')
            except Exception as e:
                pass

    def process_command(self, text):
        if not text: return
        
        # Stop listening while processing/speaking
        if self.stt:
             self.stt.stop_stream()

        self.add_message("YOU", text)
        self.update_status("PROCESSING...")

        if "stop" in text.lower() or "exit" in text.lower():
            speak("Phr milenge.")
            self.update_status("OFFLINE")
            self._running = False
            if self._window:
                self._window.destroy()
            sys.exit()

        parsed_command = basic_intent_parser(text)
        
        if parsed_command:
            execute_system_command(parsed_command)
            self.add_message("JARVIS", f"Executed: {parsed_command}")
        else:
            self.update_status("THINKING...")
            response = process_text(text)
            self.update_status("SPEAKING")
            self.add_message("JARVIS", response)
            speak(response)
        
        self.update_status("IDLE")
        
        # Resume listening
        if self._running and not self._listening_paused:
             self.stt.start_stream()

    def main_loop(self):
        print("DEBUG: Entered main_loop")
        time.sleep(2) # Let UI load
        self.update_status("ONLINE & LISTENING")
        
        print("DEBUG: Initializing Streaming STT...")
        try:
             self.stt = StreamingSTT()
        except Exception as e:
             self.add_message("JARVIS", f"Error loading STT Model: {e}")
             print(f"STT Init Error: {e}")
             return

        print("DEBUG: About to speak welcome")
        try:
            speak("Namaste! I am online.")
        except Exception as e:
            print(f"DEBUG: Error speaking: {e}")
        
        time.sleep(1.0) 

        while self._running:
            if self._listening_paused:
                self.update_status("PAUSED")
                time.sleep(0.5)
                continue
            
            # Ensure stream is running
            if not self.stt.is_running_transcription:
                self.stt.start_stream()

            self.update_status("LISTENING...")
            
            try:
                for msg_type, text in self.stt.generator():
                    # Check external flags
                    if not self._running: break
                    if self._listening_paused: 
                        self.stt.stop_stream()
                        break
                    
                    if msg_type == "partial":
                        self.update_user_streaming(text)
                    
                    elif msg_type == "final":
                        self.process_command(text)
                        break
            except Exception as e:
                print(f"DEBUG: Error in STT loop: {e}")
                time.sleep(1) # Prevent tight loop on error

api = JarvisAPI()

# ---- Manual Icon Set Helper for Windows ----
def set_window_icon(title, icon_path):
    import ctypes
    from ctypes import wintypes

    # Constants
    WM_SETICON = 0x80
    ICON_SMALL = 0
    ICON_BIG = 1
    IMAGE_ICON = 1
    LR_LOADFROMFILE = 0x00000010

    # Find Window handle
    hwnd = ctypes.windll.user32.FindWindowW(None, title)
    if not hwnd:
        print(f"DEBUG: Could not find window with title '{title}' to set icon.")
        return

    print(f"DEBUG: Found window hwnd: {hwnd}. Setting icon manually.")

    # Load Icons
    h_icon_big = ctypes.windll.user32.LoadImageW(None, icon_path, IMAGE_ICON, 0, 0, LR_LOADFROMFILE) 
    h_icon_small = ctypes.windll.user32.LoadImageW(None, icon_path, IMAGE_ICON, 16, 16, LR_LOADFROMFILE)

    if h_icon_big:
        ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, h_icon_big)
    if h_icon_small:
        ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, h_icon_small)

def on_loaded():
    # Attempt to set icon manually via Win32 API
    try:
        import time
        # Wait a bit for window to initialize
        time.sleep(1.0)
        
        # Robust icon finding logic
        possible_icons = [
            os.path.abspath("following.ico"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "following.ico"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "following.ico")
        ]
        
        found_icon = None
        for icon in possible_icons:
            if os.path.exists(icon):
                found_icon = icon
                break
        
        if found_icon:
             print(f"DEBUG: Found icon for manual set: {found_icon}")
             # Retry finding window a few times
             for _ in range(3):
                 set_window_icon('Swati', found_icon)
                 time.sleep(0.5)
        else:
             print("DEBUG: Could not find following.ico for manual set.")

    except Exception as e:
        print(f"DEBUG: Manual icon set failed: {e}")

    # Auto-start listening when window loads
    api.start_listening()

if __name__ == '__main__':
    # Fix for Windows Taskbar Icon: Detach from python.exe group
    import ctypes
    try:
        # Use a fresh ID to ensure no caching issues
        myappid = 'jarvis.assistant.app.v3.1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception as e:
        print(f"DEBUG: Could not set AppUserModelID: {e}")

    # Support for PyInstaller
    if hasattr(sys, '_MEIPASS'):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    # Get absolute path to html
    html_path = os.path.join(base_dir, 'ui', 'index.html')

    if not os.path.exists(html_path):
        # Fallback for dev mode not finding it if CWD is different
        # Make sure we look in src/ui relative to CWD if all else fails
        fallback = os.path.abspath(os.path.join(os.getcwd(), 'src', 'ui', 'index.html'))
        if os.path.exists(fallback):
            html_path = fallback

    print(f"DEBUG: Loading UI from {html_path}")
    print(f"DEBUG: HTML file exists: {os.path.exists(html_path)}")

    # print(f"DEBUG: Loading UI from {html_path}")

    # Define icon path - Ensure absolute path for pywebview
    icon_path = os.path.abspath(os.path.join(base_dir, '..', 'following.ico'))

    if not os.path.exists(icon_path):
        # Try finding it in CWD if running from a different context
        cwd_path = os.path.abspath(os.path.join(os.getcwd(), 'following.ico'))
        if os.path.exists(cwd_path):
            icon_path = cwd_path

    print(f"DEBUG: Resolving Icon Path: {icon_path}")
    print(f"DEBUG: Icon File Exists: {os.path.exists(icon_path)}")

    # Ensure html_path is a valid URI
    if not os.path.exists(html_path):
         print(f"ERROR: HTML path not found: {html_path}")
    
    print(f"DEBUG: Loading UI from: {html_path}")

    # Create the window with API access
    window = webview.create_window('Swati', url=html_path, width=500, height=800, background_color='#000000', js_api=api)
    api.set_window(window)

    # Start the webview
    webview.start(on_loaded, debug=False, icon=icon_path)
