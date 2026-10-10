# 🎬 AI Video Assistant - Complete Technical Guide & Beginner-Friendly Interview File

> **Author:** Pushpendra Choure  
> **Project:** AI Video Intelligence & RAG Assistant  
> **Repository:** [pushp2566/AI-Video-Assistant](https://github.com/pushp2566/AI-Video-Assistant)  
> **Live Demo:** [AI Video Assistant App](https://ai-video-assistant-dazevw4wymcq5f6nd2735a.streamlit.app/)  
> **Tech Stack:** Python, Streamlit, LangChain, Groq API (GPT-OSS-20B), Mistral AI, OpenAI Whisper, Sarvam AI, RapidAPI, ChromaDB, HuggingFace Embeddings, PyTorch, pydub, FFmpeg, yt-dlp

---

## 📌 Section 1: Executive Summary & 30-Second Elevator Pitch

### 🎤 30-Second Elevator Pitch (For Interviewers)
> *"I built **AI Video Assistant**, a full-stack AI video intelligence platform deployed on Streamlit Cloud that converts YouTube links or local video/audio uploads into structured summaries, key takeaways, and an interactive RAG chat interface.
>
> To bypass cloud datacenter IP blocks (HTTP 403), I engineered a multi-tiered ingestion pipeline combining **`youtube-transcript-api`**, **RapidAPI residential proxies**, and **`yt-dlp`**. For audio, it leverages **OpenAI Whisper** and **Sarvam AI** for multilingual transcription (English & Hinglish), **Groq LLM (GPT-OSS-20B)** via **LangChain** for smart single-pass and Map-Reduce summarization, and an **in-memory ChromaDB** vector store with **UUID-tagged collections** to guarantee zero cross-video data leakage."*

---

## 🏗️ Section 2: End-to-End System Architecture & Data Flow

```
┌────────────────────────────────┐       ┌───────────────────────────────────────┐
│          Input Source          │       │        Multi-Tiered Ingestion          │
│ (YouTube URL / Video File Upload)  ──> │ (Captions API / RapidAPI / yt-dlp)    │
└────────────────────────────────┘       └───────────────────────────────────────┘
                                                             │
                                                             ▼
┌────────────────────────────────┐       ┌───────────────────────────────────────┐
│     Multilingual Speech STT    │       │         Audio Preprocessing           │
│   (Whisper / Sarvam AI API)    │ <───  │    (FFmpeg 16kHz Mono WAV Slicing)    │
└────────────────────────────────┘       └───────────────────────────────────────┘
                │
                ▼
┌────────────────────────────────┐       ┌───────────────────────────────────────┐
│     Full Text Transcript       │ ───>  │        RAG Chat Engine (ChromaDB)     │
│  (Direct / Speech Transcribed) │       │ (In-Memory UUID + HuggingFace Vector) │
└────────────────────────────────┘       └───────────────────────────────────────┘
                │                                            │
                ▼                                            ▼
┌────────────────────────────────┐       ┌───────────────────────────────────────┐
│      LLM Pipeline (Groq)       │       │    Interactive Streamlit Web App      │
│  (Title, Summary, Takeaways)   │ ───>  │     (Dark Mode UI, No Data Leakage)   │
└────────────────────────────────┘       └───────────────────────────────────────┘
```

### Step-by-Step Data Flow:
1. **Multi-Tiered Video Ingestion (`utils/audio_processor.py`)**:
   - **Tier 1 (Instant Caption Fetch)**: Uses `youtube-transcript-api` (supporting multi-version fallbacks for `list()` & `fetch()`) to retrieve captions without downloading audio.
   - **Tier 2 (Cloud IP Block Bypass)**: Routes queries through **RapidAPI residential proxy service** (`youtube-transcript3`) to guarantee 100% block-free fetching on Streamlit Cloud (bypassing AWS 403 Forbidden blocks).
   - **Tier 3 (yt-dlp Fallback)**: Downloads raw audio streams using `yt-dlp` with client player fallbacks.
   - **Tier 4 (Direct File Upload)**: Supports direct drag-and-drop uploader for `.mp4`, `.mp3`, `.wav`, `.m4a`, `.webm`, `.mkv` files.

2. **Multilingual Speech-to-Text (`core/transcriber.py`)**:
   - **English Option**: Runs local **OpenAI Whisper** (`tiny` / `small` model) on CPU/GPU.
   - **Hinglish / Hindi Option**: Slices audio into 25-second WAV segments and sends them to **Sarvam AI STT API** (`saaras:v2.5`) which transcribes and translates Hinglish speech directly to English text.

3. **LLM Summarization & Structured Extraction (`core/summarizer.py` & `core/extractor.py`)**:
   - Uses **Groq LLM** (`openai/gpt-oss-20b`) via **LangChain LCEL** (with fallbacks to **Mistral AI** or **Ollama**).
   - **Smart Adaptive Summarization**:
     - **Short Transcripts (<3,000 chars / Shorts)**: Direct single-pass prompt to eliminate conversational LLM meta-talk ("I am ready to combine...").
     - **Long Transcripts**: Map-Reduce summarization strategy (splits into 3,000-char chunks, summarizes each, and merges into final bullet points).
   - **Structured Intelligence**: Extracts Title, Key Takeaways, Action Items, Decisions, and Open Questions.
   - **Dynamic Card Rendering**: UI automatically hides empty "No items found" cards to keep the layout clean.

4. **In-Memory UUID Vector Store & RAG Engine (`core/vector_store.py` & `core/rag_engine.py`)**:
   - Splits transcript into 500-character chunks (overlap: 50) via `RecursiveCharacterTextSplitter`.
   - Generates 384-dimensional vector embeddings using HuggingFace's `all-MiniLM-L6-v2`.
   - **Data Isolation & Lock-Free Storage**: Stores vectors in **In-Memory ChromaDB** using **unique UUID collection tags** (`video_a1b2c3d4...`). This completely prevents SQLite disk lock errors (`code 1032`) and guarantees 0% cross-video data leakage.
   - **RAG Q&A**: Connects retriever (`k=4`) with strict context grounding prompts to answer user questions without hallucination.

5. **Web Dashboard (`app.py`)**:
   - Built on **Streamlit** with custom dark-mode CSS styling.
   - Stripped away default Streamlit branding, top headers, and footers for a clean, standalone user experience.

---

## 📘 Section 3: Beginner-Friendly Glossary & Plain-English Term Explanations

### 1. In-Memory Vector Store & UUID Isolation
- **Simple Analogy (Private Hotel Rooms vs. One Shared Locker)**:
  - *Old Way*: Throwing every customer's luggage into one big shared locker. When Customer B looks for their bag, they accidentally grab Customer A's jacket.
  - *New Way (UUID Isolation)*: Assigning each customer a brand-new, private, temporary room key (`video_uuid123`). When they check out, the room is wiped clean.
- **Technical Meaning**: Using ChromaDB in memory (RAM) with uniquely generated collection names (`video_a1b2c3d4...`).
- **In This Project**: Solved cross-video transcript leakage and eliminated SQLite file permission errors (`code 1032 readonly database`).

---

### 2. Multi-Tiered Ingestion & Proxy Bypassing
- **Simple Analogy**: If the front door (direct download) is locked by security (YouTube 403 Forbidden), you use the side VIP pass (RapidAPI proxy) to walk right in without waiting.
- **Technical Meaning**: Routing requests through residential proxies and caption APIs to prevent datacenter IP blocks.
- **In This Project**: Ensures YouTube video links work 100% reliably on Streamlit Cloud servers.

---

### 3. RAG (Retrieval-Augmented Generation)
- **Simple Analogy (Open-Book Exam)**: 
  - *Without RAG (Closed-Book)*: Asking an AI a question about your video. The AI tries to guess or lies (hallucinates) because it never watched your video.
  - *With RAG (Open-Book)*: The system searches the video transcript, finds the exact 2-3 paragraphs containing the answer, pastes them into the AI prompt, and tells the AI: *"Answer based strictly on these paragraphs."*
- **Technical Meaning**: An architecture combining information retrieval (vector DB search) with generative LLM prompts.

---

### 4. Embeddings (Vector Embeddings)
- **Simple Analogy**: Giving every sentence a unique GPS coordinate based on its meaning. Sentences with similar meanings get placed right next to each other on the map.
- **Technical Meaning**: Converting text into high-dimensional numerical arrays (384 dimensions via `all-MiniLM-L6-v2`).

---

### 5. Single-Pass vs. Map-Reduce Summarization
- **Simple Analogy**: Reading a 1-page essay in one quick glance (**Single-Pass**) vs. assigning 5 people to summarize 5 different chapters of a long book and combining their notes (**Map-Reduce**).
- **Technical Meaning**: Adaptive summarization logic chosen based on transcript character length.

---

## 💻 Section 4: Codebase Module Deep Dive

### 1. `app.py` (Streamlit Interface)
- **Role**: Renders the frontend dark-theme UI.
- **Key Features**: Hides Streamlit default branding/headers, dynamically renders active insight cards, manages session state, and executes the processing pipeline.

### 2. `utils/audio_processor.py` (Multi-Tiered Ingestion)
- **Role**: Handles media acquisition, caption extraction, proxy fallbacks, and audio resampling.
- **Key Functions**:
  - `fetch_rapidapi_youtube_transcript(video_id)`: Fetches captions via RapidAPI proxy service.
  - `try_fetch_youtube_captions(url)`: Multiversion fallback for `youtube-transcript-api`.
  - `download_youtube_audio(url)`: `yt-dlp` download fallback.
  - `convert_to_wav(input_path)`: Resamples audio to 16,000 Hz single-channel (mono) WAV using `pydub` and `FFmpeg`.

### 3. `core/transcriber.py` (Multilingual STT)
- **Role**: Converts audio chunks into text.
- **Key Functions**:
  - `transcribe_chunk_whisper()`: Local OpenAI Whisper execution for English.
  - `transcribe_chunk_sarvam()`: Slices audio into 25s pieces and calls Sarvam AI API (`saaras:v2.5`) for Hinglish speech translation.
  - `get_sarvam_api_key()`: Dynamic API key resolution from environment or Streamlit Secrets.

### 4. `core/summarizer.py` (Adaptive Summarizer)
- **Role**: Summarizes short and long video transcripts.
- **Key Functions**:
  - `summarize()`: Automatically selects single-pass for short transcripts (<3,000 chars) or Map-Reduce for long transcripts.

### 5. `core/vector_store.py` (In-Memory ChromaDB)
- **Role**: Manages isolated vector embeddings.
- **Key Functions**:
  - `build_vector_store()`: Creates an in-memory Chroma instance with a unique UUID collection name (`video_uuid`).

### 6. `core/rag_engine.py` (RAG Q&A Engine)
- **Role**: Answers user questions using transcript context.
- **Key Functions**:
  - `build_rag_chain()`: Connects retriever (`k=4`) with strict grounding prompts to prevent hallucination.

---

## 🎯 Section 5: Top 15 Technical Interview Questions & Answers

#### Q1: How did you solve YouTube HTTP 403 Forbidden errors when deploying to Streamlit Cloud?
> **Answer**: Streamlit Cloud runs on AWS datacenter IPs, which YouTube blocks. I engineered a multi-tiered ingestion ladder in `utils/audio_processor.py`: it first attempts direct caption extraction via `youtube-transcript-api`, falls back to **RapidAPI residential proxies** (`youtube-transcript3`), and uses `yt-dlp` or direct file uploads as final fallbacks.

#### Q2: How did you prevent cross-video data contamination in RAG Chat?
> **Answer**: Originally, ChromaDB persisted vector embeddings under a static collection name, causing chunks from previous videos to leak into new video Q&A. I updated `core/vector_store.py` to use **In-Memory ChromaDB** with **UUID-tagged collection names** (`video_a1b2c3d4...`). Every video analysis runs in complete memory isolation.

#### Q3: How did you fix the SQLite `code 1032 attempt to write a readonly database` error on Cloud hosting?
> **Answer**: On Streamlit Cloud's Linux environment, attempting to overwrite or delete SQLite files (`chroma.sqlite3`) while the Python server process is active causes permission locks. Switching ChromaDB to run **100% in-memory (RAM)** completely eliminated file locks while boosting vector retrieval speed.

#### Q4: Why did you implement single-pass summarization for short transcripts?
> **Answer**: For short YouTube Shorts or 1-minute videos, Map-Reduce chunking resulted in the LLM outputting conversational meta-talk (*"I am ready to combine..."*). I added adaptive logic: transcripts under 3,000 characters undergo a direct single-pass summary with strict prompt directives forbidding conversational filler.

#### Q5: How does Sarvam AI handle Hinglish audio in your project?
> **Answer**: Sarvam AI's synchronous API enforces a ≤30 second payload limit per call. In `core/transcriber.py`, `transcribe_chunk_sarvam` uses `pydub` to slice Hinglish audio into 25-second WAV pieces, sends them to Sarvam's `saaras:v2.5` model, and joins the translated English text chunks.

#### Q6: Why choose Groq API (`openai/gpt-oss-20b`) over standard cloud LLMs?
> **Answer**: Groq's LPU (Language Processing Unit) architecture provides ultra-low latency inference (~300+ tokens/sec) at zero cost on their developer tier, making summarization and RAG Q&A practically instantaneous.

#### Q7: How do you prevent hallucinations in your RAG pipeline?
> **Answer**: In `core/rag_engine.py`, the system prompt explicitly restricts the LLM: *"Answer the user's question based ONLY on the video transcript context provided below. If the answer is not found, say 'I could not find this information in the video transcript.'"*

#### Q8: What embedding model did you select, and why?
> **Answer**: HuggingFace's `all-MiniLM-L6-v2`. It generates 384-dimensional dense vectors with low CPU memory overhead and high semantic retrieval performance.

#### Q9: How is audio formatted before feeding into Whisper/STT?
> **Answer**: The pipeline resamples all input media to single-channel (mono) 16,000 Hz WAV files using `pydub.AudioSegment.set_channels(1).set_frame_rate(16000)`.

#### Q10: How did you optimize Streamlit launch performance?
> **Answer**: By using lazy module loading (`get_pipeline_modules()`), heavy ML imports (`torch`, `whisper`, `chromadb`) are deferred until user submission, allowing the Streamlit UI to load in **<1 second**.

#### Q11: What text splitter chunk size and overlap did you select for RAG?
> **Answer**: `chunk_size = 500` characters with `chunk_overlap = 50`. 500 characters corresponds to ~2-3 sentences (ideal granularity for specific Q&A lookup), while the overlap maintains boundary context.

#### Q12: How do you handle UI cards when no action items or key decisions exist?
> **Answer**: In `app.py`, the UI checks if extracted fields contain "No items found" and dynamically hides empty cards to maintain a clean layout.

#### Q13: How is state maintained across user interactions in Streamlit?
> **Answer**: Persistence is maintained across script reruns using `st.session_state` (`result`, `chat_history`, `pipeline_done`, `pipeline_steps`).

#### Q14: How did you remove default Streamlit branding?
> **Answer**: Added CSS rules to `app.py` hiding `#MainMenu`, `footer`, `header`, `[data-testid="stHeader"]`, and `[data-testid="stToolbar"]`.

#### Q15: How would you scale this application for enterprise video processing?
> **Answer**: 
> 1. Use background async task queues (**Celery** with **Redis**).
> 2. Upgrade to GPU acceleration (CUDA) for Whisper or hosted STT APIs.
> 3. Store embeddings in a distributed cloud vector DB (Pinecone / Qdrant).
> 4. Use WebSockets to stream real-time transcription and summary tokens.

---

## ⚡ Section 5: Summary of Production Trade-offs & Engineering Decisions

| Component | Choice Made | Rationale / Engineering Trade-off |
| :--- | :--- | :--- |
| **Ingestion** | Multi-Tier (RapidAPI + Captions + `yt-dlp`) | Bypasses AWS datacenter 403 Forbidden blocks on Streamlit Cloud. |
| **Vector DB** | In-Memory ChromaDB (UUID Tagged) | 0 SQLite file locks (`code 1032`), 10x faster retrieval, 100% data isolation per video. |
| **LLM Provider** | Groq API (`openai/gpt-oss-20b`) | Ultra-fast token generation speed (~300 tokens/sec) with zero cost. |
| **Summarization** | Adaptive (Single-Pass & Map-Reduce) | Direct single-pass for Shorts eliminates conversational LLM filler. |
| **UI Design** | Streamlit + Custom CSS | Clean, dark-mode, unbranded UI loading in <1 second. |

---
*Updated and verified for Pushpendra Choure — AI Video Assistant Repository*
