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
- 💾 **Conversation Memory** - Persistent logging of all sessions and conversations
- 🛡️ **Soul Protection** - Immutable personality protected from prompt injection attacks
- 🧠 **RAG System** - Retrieval-Augmented Generation for context-aware responses

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

## 💾 Memory System

Mareen now includes a comprehensive memory system that logs every conversation and session to a local SQLite database.

### Features
- 📝 **Automatic Logging** - Every message (user and assistant) is saved automatically
- 🕒 **Session Tracking** - Each conversation session is tracked with timestamps
- 🔍 **Search Capability** - Search through all past conversations
- 📊 **Statistics** - View usage statistics and patterns
- 📤 **Export** - Export sessions to JSON format for backup or analysis
├── intent.py       # Command parser
│   │   └── memory.py       # Conversation memory system
│   ├── modules/
│   │   ├── system.py       # System commands
│   │   └── files.py        # File operations
│   └── ui/
│       ├── index.html      # 3D Orb interface
│       └── gui.py          # GUI components
├── models/                  # Vosk models directory
├── scripts/
│   └── setup_model.py      # Model downloader
├── view_memory.py          # Memory viewer utility
├── memory.db               # Conversation database (auto-created)
python view_memory.py stats

# List all sessions
python view_memory.py sessions

# View specific session
python view_memory.py view <session_id>

# Search conversations
python view_memory.py search "hello"

# Export session to JSON
python view_memory.py export <session_id> output.json
```

### Memory Database Location
All conversations are stored in `memory.db` in the project root directory. This file is created automatically on first run.

### Privacy Note
Your conversation history is stored **locally only** on your machine. No data is sent to external servers. You can delete `memory.db` at any time to clear your history.

## 🛡️ Soul Protection System

Mareen's personality is protected by a **Soul System** that prevents prompt injection attacks and personality manipulation.

### What is the Soul?
The soul ([soul.md](soul.md)) is Mareen's core identity file that defines:
- Personality traits and behavior
- Language preferences (Hindi)
- Response guidelines
- Protected instructions that cannot be overridden

### Injection Protection
Mareen automatically detects and blocks attempts to:
- Override system instructions
- Change personality or identity
- Ignore core directives
- Pretend to be other AI assistants
- Execute harmful commands through manipulation

### Testing Protection
```bash
# Test the soul protection system
python test_soul.py
```

### How It Works
1. **Soul Loading**: System prompt loaded from `soul.md` (immutable)
2. **Input Scanning**: Every user input checked for 34+ injection patterns
3. **Automatic Blocking**: Injection attempts rejected with polite Hindi responses
4. **Memory Logging**: All injection attempts logged for security review

### Why This Matters
Prevents users from:
- "Jailbreaking" the assistant
- Making Mareen act inappropriately
- Bypassing safety guidelines
- Compromising the user experience for others

## 🧠 RAG System (Retrieval-Augmented Generation)

Mareen uses **RAG** to remember past conversations and provide contextual responses based on your history.

### What is RAG?
RAG combines your conversation memory with AI responses:
1. When you ask a question, Mareen searches past conversations
2. Relevant context is retrieved and added to the prompt
3. The LLM generates a response aware of your history
4. You get personalized, context-aware answers

### Features
- 🔍 **Semantic Search** - Finds relevant past conversations (not just keywords)
- ⏰ **Time Decay** - Recent conversations weighted higher
- 🎯 **Smart Context** - Top 3 most relevant memories included
- 💾 **Embedding Cache** - Fast retrieval with cached vectors
- 🔄 **Fallback Mode** - Works with keyword matching if embeddings unavailable

### How It Works
```python
User: "How do I learn Python?"
  ↓
RAG searches memory for similar past conversations
  ↓
Finds: "Can you help me with programming?"
  ↓
Adds context to LLM prompt
  ↓
Mareen: "जैसा कि मैंने पहले बताया था programming के लिए..."
```

### Testing RAG
```bash
python test_rag.py
```

### Optional: Semantic Embeddings
For better context matching, install sentence-transformers:
```bash
pip install sentence-transformers
```

Without it, RAG uses keyword matching (still effective but less nuanced).

## Project Structure

```
mareen/
├── src/
│   ├── main.py              # Application entry point
│   ├── core/
│   │   ├── llm.py          # Ollama LLM integration
│   │   ├── stt.py          # Speech-to-text (Vosk)
│   │   ├── tts.py          # Text-to-speech
│   │   ├── intent.py       # Command parser
│   │   ├── memory.py       # Conversation memory system
   │   ├── soul.py         # Soul protection system
   │   └── rag.py          # RAG retrieval system
│   ├── modules/
│   │   ├── system.py       # System commands
│   │   └── files.py        # File operations
│   └── ui/
│       ├── index.html      # 3D Orb interface
│       └── gui.py          # GUI components
├── models/                  # Vosk models directory
├── scripts/
│   └── setup_model.py      # Model downloader
├── soul.md                 # Protected personality definition
├── view_memory.py          # Memory viewer utility
├── test_soul.py            # Soul protection tests
├── test_rag.py             # RAG system tests
├── memory.db               # Conversation database (auto-created)
├── embeddings_cache.pkl    # RAG embeddings cache (auto-created)
└── requirements.txt        # Python dependencies
```

## Configuration

### Customizing Personality
Edit [soul.md](soul.md) to customize:
- AI personality and language
- Response style and tone
- System prompts
- Behavioral guidelines

**Note**: After editing `soul.md`, restart the application or use the reload feature.

### Developer Options
Edit [src/core/llm.py](src/core/llm.py) for:
- Model selection (default: 'j2')
- Advanced LLM parameters

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

- [x] Context-aware conversations with memory
- [x] Soul protection against prompt injection
- [x] RAG system for contextual responses
- [ ] Wake word detection ("Hey Mareen")
- [ ] Multi-language support (Spanish, French, etc.)
- [ ] Plugin system for custom commands
- [ ] Mobile companion app
- [ ] Voice cloning for personalized TTS
- [ ] Integration with smart home devices
- [ ] Memory-based context retention across sessions
- [ ] Advanced injection detection with ML

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
