# Swati (formerly Jarvis v3.0) - Voice Assistant

## Overview
Swati is a calm, immersive, voice-first AI assistant featuring a glowing orb interface. Under the hood, it is powered by:
- **Ollama** for local LLM processing (model `j`).
- **SpeechRecognition** for STT.
- **EdgeTTS / pyttsx3** for TTS.
- **pywebview** for the Voice Orb UI.

## Prerequisites
1. **Python 3.10+**
2. **Ollama**: Download and install from [ollama.com](https://ollama.com).
   - Ensure you have your custom model ready: `ollama pull j` (or ensure 'j' is created).
3. **Microphone**: Ensure your microphone is set as the default recording device.

## Installation
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: If you encounter errors with `pyaudio`, voice input will be disabled and fallback to text input. PyAudio often requires Python 3.10-3.12 or manual installation of compilation tools.*

2. (Optional) For offline Speech Recognition significantly better than basic Sphinx, consider setting up a Vosk model or Whisper.

## Usage
Run the main script:
```bash
python src/main.py
```
Wake word: "Jarvis" (Implied in conversation flow for now)
commands:
- "Open calculator"
- "Open notepad"- "Open [any app name]" (e.g., "Open Spotify", "Open Chrome")- Any general question (processed by LLaMA 3)

## Features
- **Voice Interaction**: Speaks back responses.
- **Local Intelligence**: Uses local LLaMA model via Ollama.
- **Privacy Focused**: Designed to run offline.
