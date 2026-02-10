import asyncio
import edge_tts
import pygame
import os
import sys
import time
import pyttsx3
import pyaudio
import audioop
import threading
import re

# Initialize pygame mixer for playback
try:
    pygame.mixer.init()
except:
    print("Warning: Pygame mixer failed to initialize. Audio might not work.")

IS_INTERRUPTED = False

def check_interruption():
    """Monitors microphone for loud noise to trigger interruption."""
    global IS_INTERRUPTED
    IS_INTERRUPTED = False
    
    chunk = 1024
    p = pyaudio.PyAudio()
    
    try:
        # Check if we have any input devices
        if p.get_device_count() == 0:
            return

        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=44100,
                        input=True,
                        frames_per_buffer=chunk)
        
        # Threshold: Adjusted for speech barge-in.
        THRESHOLD = 2000 
        
        while pygame.mixer.music.get_busy():
            try:
                data = stream.read(chunk, exception_on_overflow=False)
                # Calculate RMS (Root Mean Square) amplitude
                rms = audioop.rms(data, 2)
                
                if rms > THRESHOLD:
                    # Double check to prevent random spikes
                    data2 = stream.read(chunk, exception_on_overflow=False)
                    rms2 = audioop.rms(data2, 2)
                    
                    if rms2 > THRESHOLD:
                        pygame.mixer.music.stop()
                        IS_INTERRUPTED = True
                        print("\n[Interrupted by user]")
                        break
            except:
                break
                
        stream.stop_stream()
        stream.close()
    except Exception as e:
        # Silently fail if microphone access fails during playback
        pass
    finally:
        p.terminate()

async def generate_speech(text, output_file, voice="en-IN-NeerjaNeural"):
    # Rate change (-10%)
    communicate = edge_tts.Communicate(text, voice, rate="-10%")
    await communicate.save(output_file)

def split_text(text, max_length=500):
    """Splits text into chunks to ensure TTS stability."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_length:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def speak_neural(text):
    """Uses EdgeTTS for high-quality human speech with fallback voices."""
    if not text or not text.strip():
        return
    
    # Split text into chunks to handle long responses better
    chunks = split_text(text)
    
    for i, chunk in enumerate(chunks):
        if not chunk.strip(): 
            continue
            
        output_file = os.path.join(os.getcwd(), f"temp_voice_{i}.mp3")
        
        # List of voices to try
        voices_to_try = ["en-IN-NeerjaNeural", "hi-IN-SwaraNeural", "en-US-AriaNeural"]
        success = False
        
        for voice in voices_to_try:
            try:
                # Run async generation in a sync context
                asyncio.run(generate_speech(chunk, output_file, voice))
                
                # Check if file was created and has size
                if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                    success = True
                    break
            except Exception as e:
                # print(f"DEBUG: EdgeTTS failed with voice {voice}: {e}")
                continue

        if not success:
            print("EdgeTTS Error: switching to offline fallback for chunk.")
            speak_offline(chunk)
            continue

        try:
            # Play audio
            pygame.mixer.music.load(output_file)
            pygame.mixer.music.play()
            
            # Print text while playing (Typewriter effect)
            words = chunk.split()
            for word in words:
                if not pygame.mixer.music.get_busy():
                    # If audio finished faster than text, just print the rest quickly
                    sys.stdout.write(word + " ")
                    sys.stdout.flush()
                else: 
                    sys.stdout.write(word + " ")
                    sys.stdout.flush()
                    # Approximate duration per word or just let it flow
                    time.sleep(0.05) 
            
            # Block while playing remaining audio
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
            # Clean up
            pygame.mixer.music.unload()
            try:
                os.remove(output_file)
            except:
                pass
                
        except Exception as e:
            print(f"Audio Playback Error: {e}")
            speak_offline(chunk)
            
    print() # Newline at very end

# --- Offline Fallback (pyttsx3) ---
engine = pyttsx3.init()
def configure_voice_offline():
    try:
        voices = engine.getProperty('voices')
        for voice in voices:
            if "zira" in voice.name.lower() or "female" in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
        engine.setProperty('rate', 190) 
    except:
        pass
configure_voice_offline()

def speak_offline(text):
    """Fallback standard TTS."""
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Offline TTS Error: {e}")

# Main entry point - Defaults to Neural
def speak(text):
    speak_neural(text)
