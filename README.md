# Mareen - Voice Assistant 🎙️

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

> *A privacy-focused voice assistant with immersive 3D orb UI, powered by local AI*

## Overview
Mareen is a calm, immersive, voice-first AI assistant featuring a glowing particle sphere interface. Experience the future of private, offline AI interaction with beautiful visualizations and natural voice conversations.

**Powered by:**
- 🧠 **Ollama** - Local LLM processing (model `j`)
- 🎤 **Vosk** - Offline speech recognition
- 🔊 **EdgeTTS / pyttsx3** - Natural text-to-speech
- 🎨 **pywebview** - Stunning 3D Voice Orb UI

## ✨ Features

- 🎙️ **Voice Interaction** - Natural speech recognition with real-time transcription streaming
- 🌐 **Offline First** - Complete privacy with local LLM processing (no data leaves your machine)
- 🇮🇳 **Hindi Support** - Native Hindi language understanding and responses
- 🔮 **3D Orb UI** - Immersive particle sphere visualization with dynamic color states
- 🎯 **System Control** - Open applications, find files, and execute commands
- 🧠 **Smart Intent** - Understands natural language commands and context
- 🔊 **Text-to-Speech** - Natural voice responses with emotion
- ⚡ **Lightweight** - Runs efficiently on local hardware
- 🔒 **Privacy Focused** - No cloud dependencies, no telemetry

## Architecture

```
Microphone → Vosk STT → Intent Parser → Ollama LLM → Edge TTS → Speaker
                              ↓
                      System Commands
                      File Operations
```

## Screenshots

### 🔮 Main Interface - Glowing Orb States
*Coming soon: Screenshots of idle, listening, and speaking states*

<!-- Uncomment when screenshots are added
![Idle State](docs/screenshots/orb-idle.png)
![Listening Mode](docs/screenshots/orb-listening.png)
![Speaking Mode](docs/screenshots/orb-speaking.png)
-->

## Prerequisites

1. **Python 3.10+** - Ensure you have a compatible Python version installed
2. **Ollama** - Download and install from [ollama.com](https://ollama.com)
   - Pull a model: `ollama pull llama2` or create your custom model `j`
   - Verify installation: `ollama list`
3. **Microphone** - Set as default recording device in system settings
4. **Git** - For cloning the repository (optional)

## Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/saxil/mareen.git
cd mareen
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

**Note:** If you encounter errors with `PyAudio`:
- Windows: Download pre-built wheel from [unofficial binaries](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)
- Linux: `sudo apt-get install portaudio19-dev python3-pyaudio`
- macOS: `brew install portaudio && pip install pyaudio`

### 3️⃣ Setup Vosk Model (Optional but Recommended)
For better offline speech recognition:
```bash
python scripts/setup_model.py
```
This downloads the Vosk model for English and Hindi support.

### 4️⃣ Configure Ollama
Ensure your LLM model is ready:
```bash
ollama pull llama2
# Or use your custom model 'j'
```

## Usage

### Starting Mareen
```bash
python src/main.py
```

### Voice Commands
Once the orb appears and turns **yellow** (listening), try:
- 💬 **General conversation:** "Hello", "Tell me a joke", "What's the weather?"
- 🚀 **System commands:** 
  - "Open calculator"
  - "Open notepad"
  - "Open Chrome"
  - "Find files named report"
- 🛑 **Exit:** "Stop", "Exit", "Goodbye"

### UI States
- 🟡 **Amber** - Idle / Ready
- 🟢 **Yellow** - Listening
- 🔵 **Blue** - Speaking / Responding
- 🟣 **Purple** - Processing / Thinking

## Project Structure

```
mareen/
├── src/
│   ├── main.py              # Application entry point
│   ├── core/
│   │   ├── llm.py          # Ollama LLM integration
│   │   ├── stt.py          # Speech-to-text (Vosk)
│   │   ├── tts.py          # Text-to-speech
│   │   └── intent.py       # Command parser
│   ├── modules/
│   │   ├── system.py       # System commands
│   │   └── files.py        # File operations
│   └── ui/
│       ├── index.html      # 3D Orb interface
│       └── gui.py          # GUI components
├── models/                  # Vosk models directory
├── scripts/
│   └── setup_model.py      # Model downloader
└── requirements.txt        # Python dependencies
```

## Configuration

Edit [src/core/llm.py](src/core/llm.py) to customize:
- AI personality and language
- Response style and tone
- System prompts

## Troubleshooting

**Issue:** Microphone not detected
- **Solution:** Check system audio settings and set default input device

**Issue:** Ollama connection failed
- **Solution:** Ensure Ollama is running: `ollama serve`

**Issue:** Poor speech recognition
- **Solution:** Use Vosk models for better offline accuracy

**Issue:** Application won't start
- **Solution:** Check Python version (3.10+) and reinstall dependencies

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Roadmap

- [ ] Wake word detection ("Hey Mareen")
- [ ] Multi-language support (Spanish, French, etc.)
- [ ] Plugin system for custom commands
- [ ] Mobile companion app
- [ ] Voice cloning for personalized TTS
- [ ] Context-aware conversations with memory
- [ ] Integration with smart home devices

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Ollama** - For making local LLMs accessible
- **Vosk** - For offline speech recognition
- **pywebview** - For the beautiful UI framework
- **Edge TTS** - For natural voice synthesis

## Support

⭐ Star this repository if you find it helpful!

For issues and questions, please open an [issue](https://github.com/saxil/mareen/issues).

---

**Made with ❤️ for privacy-conscious AI enthusiasts**
