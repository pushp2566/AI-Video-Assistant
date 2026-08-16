# 🎬 AI Video Assistant

An intelligent **Meeting Intelligence & Video Analysis System** built with **Streamlit**, **LangChain**, **Mistral AI**, **OpenAI Whisper**, **Sarvam AI**, and **ChromaDB**. 

Transform YouTube videos or local meeting recordings into automated titles, executive summaries, action items, key decisions, open questions, and an interactive **RAG (Retrieval-Augmented Generation)** chat assistant.

---

## ✨ Features

- 🎥 **Multi-Source Input**: Supports YouTube URLs and local video/audio files (`mp4`, `m4a`, `mp3`, `wav`, `webm`).
- 🔊 **Audio Preprocessing & Chunking**: Automatic conversion to 16kHz mono WAV format and chunking for smooth processing.
- 🎙️ **Dual-Engine Transcription**:
  - **OpenAI Whisper** (Local offline execution for English audio).
  - **Sarvam AI STT** (Real-time Speech-to-Text & Translation for **Hinglish/Hindi** audio into English).
- 🧠 **LLM Orchestration (LangChain LCEL + Mistral AI)**:
  - **Map-Reduce Summarization**: Handles long transcripts seamlessly.
  - **Smart Title Generation**: Creates concise session titles (max 8 words).
  - **Structured Extraction**: Extracts Action Items (Task, Owner, Deadline), Key Decisions, and Open Questions.
- 💬 **Interactive RAG Meeting Chat**: Embeds transcripts into a local vector store (**ChromaDB** + **HuggingFace Embeddings**) so you can ask any question about the meeting.
- 🎨 **Modern Cyberpunk UI**: Sleek dark-mode Streamlit interface with live pipeline status indicators.

---

## 🏗️ System Architecture

```
[ YouTube URL / Local Audio File ]
               │
               ▼
   [ Audio Preprocessor & Chunker ]  ── (pydub + ffmpeg)
               │
               ▼
     [ Speech-to-Text Engine ]
      ├── English  ➜ OpenAI Whisper (Local)
      └── Hinglish ➜ Sarvam AI API (Translate)
               │
               ▼
    [ Full Transcript Assembly ]
               │
      ┌────────┴───────────────────────────┐
      ▼                                   ▼
[ Mistral AI Analysis ]          [ Vector Database ]
  ├── Map-Reduce Summary           ├── HuggingFace Embeddings
  ├── Title Generation             └── ChromaDB Vector Store
  └── Extraction (Actions/Decisions)      │
                                          ▼
                               [ Interactive RAG Chat ]
```

---

## 🛠️ Prerequisites & Installation

### 1. System Requirements
- **Python**: Version `3.10`, `3.11`, or `3.12`.
- **FFmpeg** (Required for audio processing):
  - **Windows (PowerShell)**:
    ```powershell
    winget install Gyan.FFmpeg
    ```
  - **macOS**:
    ```bash
    brew install ffmpeg
    ```
  - **Linux (Ubuntu/Debian)**:
    ```bash
    sudo apt update && sudo apt install ffmpeg
    ```

---

### 2. Environment Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/pushp2566/AI-Video-Assistant.git
   cd AI-Video-Assistant
   ```

2. **Create and activate a virtual environment**:
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - **macOS / Linux**:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Install dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r Requirements.txt
   ```

---

### 3. Environment Variables (`.env`)

Create a `.env` file in the root directory:

```ini
# Required: Mistral AI API Key (Get key: https://console.mistral.ai/)
MISTRAL_API_KEY=your_mistral_api_key_here

# Optional: Local Whisper Model Size (tiny, base, small, medium, large)
WHISPER_MODEL=small

# Optional: Sarvam AI API Key (Required ONLY for Hinglish transcription - https://www.sarvam.ai/)
SARVAM_API_KEY=your_sarvam_api_key_here
SARVAM_STT_MODEL=saaras:v2.5
```

---

## 🚀 Usage

### Option 1: Streamlit Web UI (Recommended)
Launch the interactive web application:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

### Option 2: Command Line Interface (CLI)
Run the pipeline directly in the terminal:
```bash
python main.py
```

### Option 3: Quick Test Script
Test with a sample pre-configured YouTube video:
```bash
python test.py
```

---

## 📁 Repository Structure

```
.
├── app.py                  # Streamlit Web Application UI
├── main.py                 # CLI Interface Entry Point
├── test.py                 # Sample Test Script
├── Requirements.txt        # Python Dependencies
├── .env.example            # Environment Variable Template
├── .gitignore              # Ignored Files & Directories
├── README.md               # Repository Documentation
├── core/
│   ├── transcriber.py      # Whisper & Sarvam STT Handlers
│   ├── summarizer.py       # Map-Reduce Transcript Summarizer
│   ├── extractor.py        # Action Items & Decisions Extractor
│   ├── vector_store.py     # ChromaDB & Embeddings Engine
│   └── rag_engine.py       # LangChain RAG Question-Answering
└── utils/
    └── audio_processor.py  # Video/Audio Extractor & Chunker
```

---

## ❓ Troubleshooting

| Problem | Solution |
| :--- | :--- |
| `FileNotFoundError: [WinError 2] ffmpeg` | FFmpeg is missing. Install via `winget install Gyan.FFmpeg` and ensure it's in your System PATH. |
| `RuntimeError: MISTRAL_API_KEY is not set` | Ensure `.env` exists in root folder with a valid `MISTRAL_API_KEY`. |
| Sarvam API Error | Ensure `SARVAM_API_KEY` is provided when selecting `hinglish` mode. |

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
