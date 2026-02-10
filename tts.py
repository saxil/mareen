from TTS.api import TTS

# Load XTTS model
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)

# Reference voice (5–30 sec clean WAV)
reference_wav = "voice_sample.wav"

text = "I am your local voice agent. I do not depend on broken APIs."

tts.tts_to_file(
    text=text,
    speaker_wav=reference_wav,
    language="en",
    file_path="output.wav"
)

print("Voice generated: output.wav")