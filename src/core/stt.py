import speech_recognition as sr

def listen():
    print("DEBUG: Inside listen()")
    r = sr.Recognizer()
    
    # List mics only once to debug (or everytime if needed)
    # for index, name in enumerate(sr.Microphone.list_microphone_names()):
    #     print(f"Microphone with name \"{name}\" found for `Microphone(device_index={index})`")

    try:
        print("DEBUG: Initializing Microphone...")
        # device_index=None uses default. If it fails, try specific index based on list above.
        with sr.Microphone() as source:
            print("DEBUG: Microphone initialized. Calibrating...")
            
            # Dynamic adjustment is good, but sometimes sets threshold too high if there's noise.
            # r.adjust_for_ambient_noise(source, duration=1) 
            
            # Manual threshold for testing sensitivity
            r.energy_threshold = 300  
            r.dynamic_energy_threshold = True # Let it adjust from 300 upwards
            
            print(f"DEBUG: Listening now... (Threshold: {r.energy_threshold})")
            try:
                # Increased timeout and added phrase_time_limit
                audio = r.listen(source, timeout=8, phrase_time_limit=10)
                
                # Using Google temporarily for MVP if Vosk not configured
                text = r.recognize_google(audio)
                print(f"DEBUG: Recognized text: {text}")
                return text
            except sr.UnknownValueError:
                print("DEBUG: Google Speech could not understand audio")
                return ""
            except sr.RequestError as e:
                print(f"DEBUG: Could not request results from Google Speech service; {e}")
                return ""
            except sr.WaitTimeoutError:
                print("DEBUG: Listening timed out while waiting for phrase to start")
                return ""
            except Exception as e:
                print(f"DEBUG: Generic STT Error: {e}")
                return ""
    except OSError:
        print("Microphone not found or PyAudio not installed.")
        print("Input: ", end="", flush=True)
        return input()
    except AttributeError:
        # Happens if PyAudio is not installed and sr.Microphone is accessed
        print("PyAudio is not installed. Voice input disabled.")
        print("Input: ", end="", flush=True)
        return input()
