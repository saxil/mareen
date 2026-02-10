import ctypes
import os
import sys

def run_fix():
    print("--- Searching for Mareen Window ---")
    target_hwnd = None
    
    def enum_cb(hwnd, extra):
        nonlocal target_hwnd
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        if length == 0: return 1
        
        buff = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
        title = buff.value
        
        if "Mareen" in title:
            print(f"Found Window: '{title}' | HWND: {hwnd}")
            target_hwnd = hwnd
            return 0 # Stop
        return 1

    cmp_func = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
    ctypes.windll.user32.EnumWindows(cmp_func(enum_cb), 0)
    
    if not target_hwnd:
        print("ERROR: Could not find 'Mareen' window.")
        return

    icon_path = os.path.abspath("following.ico")
    if not os.path.exists(icon_path):
        print(f"ERROR: Icon file not found at {icon_path}")
        return

    print(f"Loading icon from: {icon_path}")
    
    # 0x10 = LR_LOADFROMFILE
    # 1 = IMAGE_ICON
    h_icon = ctypes.windll.user32.LoadImageW(None, icon_path, 1, 0, 0, 0x10)
    
    if not h_icon:
        err = ctypes.GetLastError()
        print(f"ERROR: LoadImageW failed. Code: {err}")
        return
    
    # Send WM_SETICON (0x80)
    # 1 = Big Icon, 0 = Small Icon
    ctypes.windll.user32.SendMessageW(target_hwnd, 0x80, 1, h_icon)
    ctypes.windll.user32.SendMessageW(target_hwnd, 0x80, 0, h_icon)
    
    # Force Redraw: SWP_FRAMECHANGED (0x20) | SWP_NOMOVE (2) | SWP_NOSIZE (1) | SWP_NOZORDER (4) = 0x27
    ctypes.windll.user32.SetWindowPos(target_hwnd, 0, 0, 0, 0, 0, 0x27)
    
    print("SUCCESS: Icon updated manually.")

if __name__ == "__main__":
    run_fix()