import json
import pyaudio
from vosk import Model, KaldiRecognizer
import os

# Constants
MODEL_PATH = os.path.join(os.getcwd(), "models", "vosk-model-small-hi")
SAMPLE_RATE = 16000

class StreamingSTT:
    def __init__(self):
        print(f"DEBUG: Loading Vosk Model from {MODEL_PATH}...")
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Please run scripts/setup_model.py")
        
        self.model = Model(MODEL_PATH)
        self.recognizer = KaldiRecognizer(self.model, SAMPLE_RATE)
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.is_running_transcription = False

    def start_stream(self):
        if self.stream is not None:
             self.stop_stream()
        
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=SAMPLE_RATE,
                                  input=True,
                                  frames_per_buffer=4000) # 4000 is 0.25s buffer
        self.stream.start_stream()
        self.is_running_transcription = True

    def stop_stream(self):
        self.is_running_transcription = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
    
    def generator(self):
        """
        Yields tuples: ('partial', text) or ('final', text)
        """
        if not self.stream:
            self.start_stream()
            
        print("DEBUG: STT Generator Started")
        
        while self.is_running_transcription:
            data = self.stream.read(4000, exception_on_overflow=False)
            if len(data) == 0:
                print("DEBUG: STT Empty Audio Chunk")
                break
                
            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                text = result.get('text', '')
                if text:
                     yield ('final', text)
            else:
                result = json.loads(self.recognizer.PartialResult())
                partial = result.get('partial', '')
                if partial:
                    yield ('partial', partial)
                    
    def __del__(self):
        self.stop_stream()
        self.p.terminate()
