# 🎬 AI Video Assistant - Complete Technical Guide & Beginner-Friendly Interview File

> **Author:** Pushpendra Choure  
> **Project:** AI Video & Meeting Intelligence Assistant  
> **Repository:** [pushp2566/AI-Video-Assistant](https://github.com/pushp2566/AI-Video-Assistant)  
> **Tech Stack:** Python, Streamlit, LangChain, OpenAI Whisper, Sarvam AI, Mistral AI, ChromaDB, HuggingFace Embeddings, PyTorch, pydub, FFmpeg, yt-dlp

---

## 📌 Section 1: Executive Summary & 30-Second Elevator Pitch

### 🎤 30-Second Elevator Pitch (For Interviewers)
> *"I built **AI Video Assistant**, an intelligent meeting intelligence platform that converts raw video/audio content—such as YouTube links or local video files—into structured meeting insights and enables interactive conversational Q&A over the transcript. 
>
> The pipeline uses **yt-dlp** and **FFmpeg** for audio extraction and 16kHz WAV preprocessing, local **OpenAI Whisper** and **Sarvam AI** for multilingual Speech-to-Text (English & Hinglish), **Mistral AI** via **LangChain** for Map-Reduce summarization and structured extraction (action items, decisions, open questions), and **ChromaDB** with **HuggingFace Embeddings** for a low-latency **Retrieval-Augmented Generation (RAG)** chat interface built on **Streamlit**."*

---

## 🏗️ Section 2: End-to-End System Architecture & Data Flow

```
┌─────────────────┐       ┌──────────────────────┐       ┌──────────────────────┐
│  Input Source   │  ───> │  Audio Preprocessing │  ───> │   Speech-to-Text     │
│ (YouTube / File)│       │  (yt-dlp + FFmpeg)   │       │ (Whisper / Sarvam)   │
└─────────────────┘       └──────────────────────┘       └──────────────────────┘
                                                                    │
                                                                    ▼
┌─────────────────┐       ┌──────────────────────┐       ┌──────────────────────┐
│  RAG Chat Engine│  <─── │ Vector DB (ChromaDB) │  <─── │ Full Text Transcript │
│ (Mistral + LCEL)│       │(all-MiniLM-L6-v2)    │       └──────────────────────┘
└─────────────────┘       └──────────────────────┘                  │
                                                                    ▼
                                                         ┌──────────────────────┐
                                                         │ Mistral AI Extractors│
                                                         │ (Summary, Actions,   │
                                                         │  Decisions, Q&A)     │
                                                         └──────────────────────┘
```

### Step-by-Step Data Flow:
1. **Audio Ingestion & Preprocessing (`utils/audio_processor.py`)**:
   - Downloads audio from YouTube URLs using `yt-dlp` with `android`/`web` player fallback options to bypass YouTube anti-bot restriction 403.
   - Converts media files to standardized 16kHz mono `.wav` audio format via `pydub` and `FFmpeg`.
   - Chunks long audio files into **10-minute segments** for memory safety (OOM prevention).

2. **Multilingual Transcription (`core/transcriber.py`)**:
   - **English Option**: Runs local **OpenAI Whisper** (`base` / `small` model) on CPU/GPU.
   - **Hinglish / Hindi Option**: Sends audio slices (≤25 seconds each) to **Sarvam AI STT API** (`saaras:v2.5`).
   - Merges chunk transcripts into a unified full meeting text transcript.

3. **LLM Summarization & Structured Extraction (`core/summarizer.py` & `core/extractor.py`)**:
   - Uses **Mistral AI** (`mistral-small-latest`) via **LangChain Expression Language (LCEL)**.
   - **Map-Reduce Summarization**: Splits large transcripts into 3,000-character chunks, summarizes each chunk (Map step), and combines partial summaries into a polished meeting executive summary (Reduce step).
   - **Structured Extraction**: Extracts:
     - **Title**: Short, punchy session title.
     - **Action Items**: Task description, owner, deadline.
     - **Key Decisions**: Explicit decisions agreed upon.
     - **Open Questions**: Unresolved topics needing follow-up.

4. **Vector Store & RAG Engine (`core/vector_store.py` & `core/rag_engine.py`)**:
   - Splits full transcript into 500-character chunks (overlap: 50) using `RecursiveCharacterTextSplitter`.
   - Generates 384-dimensional vector embeddings using HuggingFace's `all-MiniLM-L6-v2` model.
   - Stores vectors in a local **ChromaDB** vector database.
   - Sets up a RAG chain (`retriever | prompt | Mistral AI | StrOutputParser`) allowing real-time Q&A strictly grounded in the transcript context.

5. **Web Interface (`app.py`)**:
   - Interactive **Streamlit** dashboard with dark theme CSS.
   - Real-time pipeline step status indicators (`Audio` ➔ `Transcript` ➔ `Title` ➔ `Summary` ➔ `Extract` ➔ `RAG`).
   - Instant startup using lazy module loading.

---

## 📘 Section 3: Beginner-Friendly Glossary & Plain-English Term Explanations

If you are new to AI/ML terms, use these simple explanations and real-world analogies to understand every piece of technology used in this project:

### 1. Audio Chunking & Memory Safety (OOM Prevention)
- **Simple Analogy (Eating Pizza Slices vs. One Giant Bite)**: 
  - Imagine trying to swallow a whole 2-hour giant pizza in a single bite. Your mouth can't hold it, and you choke!
  - Instead, you cut the pizza into small 10-minute slices and eat them one by one. Your stomach easily handles one slice at a time.
- **Technical Meaning**: 
  - A 2-hour raw `.wav` audio file can be **1 to 2 Gigabytes (GB)** in size. When Whisper processes audio, it creates massive mathematical tensors in computer memory (RAM).
  - If you load a 2-hour file all at once, Python requests 4GB–8GB of RAM simultaneously. If your computer doesn't have enough RAM, it crashes with an **Out-Of-Memory (OOM)** error.
- **In This Project**: `chunk_audio(wav_path, chunk_minutes=10)` in `utils/audio_processor.py` cuts the audio into 10-minute pieces. Python processes 10 minutes (~50 MB) at a time, frees up RAM, and moves to the next piece. This allows even laptops with modest RAM to transcribe long 3-hour videos smoothly without crashing!

---

### 2. LLM (Large Language Model)
- **Simple Analogy**: Think of an LLM as a super-smart human assistant who has read almost the entire internet and can write, translate, summarize, and answer questions.
- **Technical Meaning**: A deep learning AI model trained on massive text datasets to understand and generate human language.
- **In This Project**: We use **Mistral AI** (`mistral-small-latest`) as our LLM for writing summaries, extracting action items, and answering chat questions.

---

### 3. Speech-to-Text (STT) / ASR (Automatic Speech Recognition)
- **Simple Analogy**: Dictating a message on your phone's voice keyboard and having it turn your voice into text.
- **Technical Meaning**: An AI pipeline that processes acoustic audio signals and converts spoken words into written text transcripts.
- **In This Project**: We use **OpenAI Whisper** for English speech and **Sarvam AI** for Hinglish/Hindi speech.

---

### 4. OpenAI Whisper
- **Simple Analogy**: An AI listening expert that listens to an audio file on your computer and writes down every spoken word.
- **Technical Meaning**: An open-source, neural network-based automatic speech recognition model trained on 680,000 hours of multilingual audio.
- **In This Project**: It runs locally on your laptop CPU/GPU (`WHISPER_MODEL=base`) so transcription is **100% free** and private.

---

### 5. Sarvam AI
- **Simple Analogy**: An AI specialized in understanding Indian languages and accents (like Hinglish or Hindi) and translating them to English.
- **Technical Meaning**: An AI cloud platform designed specifically for Indic languages.
- **In This Project**: When a user selects `hinglish`, audio is sent to Sarvam's API model (`saaras:v2.5`), which translates spoken Hinglish/Hindi directly into English text.

---

### 6. RAG (Retrieval-Augmented Generation)
- **Simple Analogy (Open-Book Exam)**: 
  - *Without RAG (Closed-Book)*: Asking an AI a question about *your private meeting*. The AI tries to guess or lies (hallucinates) because it never attended your meeting.
  - *With RAG (Open-Book)*: When you ask a question, the system first opens the meeting transcript, finds the exact 2-3 paragraphs containing the answer, pastes those paragraphs into the AI's prompt, and tells the AI: *"Read these 2 paragraphs and answer the question based strictly on them."*
- **Technical Meaning**: An architecture that combines information retrieval (searching a vector DB) with text generation (LLM) to ground model answers in specific external context.
- **In This Project**: Powers the **"Chat with your Meeting"** feature.

---

### 7. Embeddings (Vector Embeddings)
- **Simple Analogy**: Imagine giving every sentence a unique GPS coordinate map based on its meaning. Sentences with similar meanings (e.g. *"The meeting starts at 5 PM"* and *"We will begin at 17:00"*) get placed right next to each other on the map, even if they use completely different words!
- **Technical Meaning**: A mathematical process that converts text into high-dimensional numerical arrays (vectors). 
- **In This Project**: We use HuggingFace's `all-MiniLM-L6-v2` model to convert 500-character transcript chunks into 384-dimensional vectors.

---

### 8. Vector Database (ChromaDB)
- **Simple Analogy**: A specialized digital library filing cabinet designed to store and search text based on **meaning** rather than exact keyword matches.
- **Technical Meaning**: A database optimized for storing, indexing, and searching high-dimensional vector embeddings using spatial algorithms (like Cosine Similarity or Euclidean distance).
- **In This Project**: **ChromaDB** runs locally inside your project folder (`vector_db/`) to store your transcript embeddings.

---

### 9. Text Chunking & Overlap
- **Simple Analogy**: Cutting a long 50-page book into small 1-page index cards so you can easily search for topics. Overlapping the edges ensures no sentence is chopped in half across two cards.
- **Technical Meaning**: Segmenting large text bodies into smaller windows (e.g., 500 characters) with overlapping boundaries (e.g., 50 characters) to preserve contextual continuity.
- **In This Project**: Used in `core/vector_store.py` (`RecursiveCharacterTextSplitter`) before saving chunks to ChromaDB.

---

### 10. Map-Reduce Summarization
- **Simple Analogy**: Summarizing a multi-chapter book by assigning 5 people to summarize 1 chapter each (**Map**), and then having a chief editor combine those 5 mini-summaries into 1 final summary (**Reduce**).
- **Technical Meaning**: A distributed processing pattern where text chunks are independently processed/summarized (*Map step*) and their outputs are combined into a final synthesized result (*Reduce step*).
- **In This Project**: Used in `core/summarizer.py` so long 2-hour meeting transcripts can be summarized without hitting LLM input character limits.

---

### 11. LangChain & LCEL (LangChain Expression Language)
- **Simple Analogy**: LEGO blocks for building AI applications. Instead of writing complex manual code to connect prompts, LLMs, and parsers, LangChain lets you snap them together using the pipe `|` symbol.
- **Technical Meaning**: A framework for building LLM-powered applications. LCEL is its declarative syntax (e.g., `retriever | prompt | llm | StrOutputParser()`).
- **In This Project**: Used throughout `core/rag_engine.py`, `core/summarizer.py`, and `core/extractor.py`.

---

### 12. FFmpeg & Pydub
- **Simple Analogy**: A universal Swiss Army knife tool for audio and video files. It can cut, resize, change format, change volume, and change sample rate.
- **Technical Meaning**: `FFmpeg` is an open-source multimedia processing framework binary. `pydub` is a Python wrapper library that controls FFmpeg commands easily in code.
- **In This Project**: Used in `utils/audio_processor.py` to resample media into standardized **16,000 Hz single-channel (mono) WAV** audio files.

---

### 13. yt-dlp
- **Simple Analogy**: A command-line program that can download video/audio streams from YouTube and other video sites.
- **Technical Meaning**: An active open-source fork of `youtube-dl` with updated extractors and anti-bot bypass mechanisms.
- **In This Project**: Downloads raw YouTube audio when a user inputs a YouTube link.

---

### 14. Streamlit & Session State
- **Simple Analogy**: A tool that allows Python developers to turn Python scripts into interactive websites with buttons, inputs, sidebars, and dark themes without writing complex HTML/JS from scratch. **Session state** is the app's notebook where it remembers what you clicked or typed even when the webpage refreshes.
- **Technical Meaning**: A Python web frontend framework. `st.session_state` preserves state variables across user execution reruns.
- **In This Project**: Renders the complete web interface (`app.py`).

---

### 15. Hallucination (AI Hallucination)
- **Simple Analogy**: When an AI model confidently makes up facts or gives a completely false answer because it doesn't know the real answer.
- **Technical Meaning**: An unexpected or incorrect output produced by a generative AI model that is not grounded in real data.
- **In This Project**: Prevented by our **RAG System** which forces Mistral AI to answer strictly using retrieved meeting transcript text.

---

## 💻 Section 4: Codebase Module Deep Dive

### 1. `app.py` (Streamlit Web Dashboard)
- **Role**: Entry point for the web application interface.
- **Key Functions**:
  - `st.set_page_config`: Configures browser tab title, icon, and wide layout (placed as line 1 to avoid Streamlit state errors).
  - `get_pipeline_modules()`: Lazy-loads heavy ML dependencies (`torch`, `whisper`, `chromadb`, `langchain`) inside execution functions rather than on script startup, accelerating app launch from ~40s to **<1s**.
  - `st.session_state`: Manages session state for pipeline steps, results dict, and chat history.

### 2. `utils/audio_processor.py` (Audio Processing Pipeline)
- **Role**: Handles media download, format conversion, and chunking.
- **Key Functions**:
  - `download_youtube_audio(url)`: Downloads raw streams using `yt-dlp`. Configures `nocheckcertificate: True` and `extractor_args: {"youtube": {"player_client": ["android", "web"]}}` to bypass HTTP 403 Forbidden blocks.
  - `convert_to_wav(input_path)`: Uses `pydub.AudioSegment` to resample audio to 16,000 Hz single-channel (mono) WAV for optimal Whisper / STT processing.
  - `chunk_audio(wav_path, chunk_minutes=10)`: Slices long WAV files into 10-minute sub-files to prevent Out-Of-Memory (OOM) errors during STT.

### 3. `core/transcriber.py` (Multilingual Speech-to-Text)
- **Role**: Converts audio chunks into text.
- **Key Functions**:
  - `load_model()`: Singleton pattern to load OpenAI Whisper model (`WHISPER_MODEL` env var, default: `base`) once into memory.
  - `transcribe_chunk_whisper(chunk_path)`: Calls `model.transcribe()` to run local transcription on CPU/GPU.
  - `_send_to_sarvam(piece_path)`: Slices audio into 25-second pieces to respect Sarvam AI's ≤30s API payload limit and posts to `https://api.sarvam.ai/speech-to-text-translate`.

### 4. `core/summarizer.py` (Map-Reduce Summarization)
- **Role**: Summarizes long transcripts without exceeding LLM context window limits.
- **Key Functions**:
  - `split_transcript()`: Splits full transcript into 3,000-character chunks (overlap: 200).
  - `summarize(transcript)`: Executes a **Map-Reduce pipeline**:
    - **Map**: Summarizes each chunk independently using `map_chain = map_prompt | llm | StrOutputParser()`.
    - **Reduce**: Combines all partial summaries into a final cohesive executive bullet-point summary using `combined_chain`.
  - `generate_title()`: Prompts LLM to return a concise 4-7 word title.

### 5. `core/extractor.py` (Information Extraction)
- **Role**: Extracts structured meeting intelligence.
- **Key Functions**:
  - `build_chain(system_prompt)`: Reusable LCEL helper (`RunnablePassthrough() | prompt | llm | StrOutputParser()`).
  - `extract_action_items()`: Extracts Task Description, Owner, and Deadline.
  - `extract_key_decisions()`: Extracts key agreements.
  - `extract_questions()`: Extracts unresolved questions and follow-ups.

### 6. `core/vector_store.py` (ChromaDB & Embeddings)
- **Role**: Manages semantic vector index.
- **Key Functions**:
  - `get_embeddings()`: Initializes `HuggingFaceEmbeddings` with `all-MiniLM-L6-v2` (384 dimensions, CPU execution).
  - `build_vector_store(transcript)`: Chunks text (chunk_size: 500, overlap: 50), generates embeddings, and persists to local directory `vector_db/`.

### 7. `core/rag_engine.py` (RAG Chain & Q&A)
- **Role**: Context-grounded conversational Q&A.
- **Key Functions**:
  - `build_rag_chain(transcript)`: Connects retriever (`k=4`) with custom prompt instruct ("*Answer based ONLY on context below. If not found, say 'I could not find this information in the meeting transcript'*").

---

## 🎯 Section 5: Top 15 Technical Interview Questions & Answers

#### Q1: Why did you use local OpenAI Whisper instead of an external API for English transcription?
> **Answer**: Local Whisper runs completely on-device without incurring per-minute API costs or sending audio data to third-party servers, enhancing privacy and cost efficiency. We used `WHISPER_MODEL=base` (139 MB / 74M params) to achieve a sweet spot of ~5x faster execution on standard CPUs while maintaining strong English accuracy.

#### Q2: How do you handle YouTube HTTP 403 Forbidden errors in `yt-dlp`?
> **Answer**: YouTube frequently updates anti-bot checks on standard web player endpoints. In `utils/audio_processor.py`, I configured `yt-dlp` with `nocheckcertificate: True` and passed `extractor_args: {"youtube": {"player_client": ["android", "web"]}}` to force client player fallbacks. Additionally, raw media streams are downloaded first and converted to 16kHz WAV using `pydub` and `FFmpeg` to prevent `ffprobe` postprocessing failures.

#### Q3: How do you handle long transcripts that exceed the LLM's context window?
> **Answer**: In `core/summarizer.py`, I implemented a **Map-Reduce summarization pattern**. The transcript is split into 3,000-character chunks with a 200-character overlap using `RecursiveCharacterTextSplitter`. Each chunk is summarized separately (Map), and the combined summaries are passed to a final prompt (Reduce).

#### Q4: Why choose ChromaDB and HuggingFace `all-MiniLM-L6-v2` for embeddings?
> **Answer**: `all-MiniLM-L6-v2` is a lightweight, high-performance sentence transformer producing 384-dimensional dense vectors with fast CPU inference. **ChromaDB** is lightweight, serverless, and runs locally without requiring a dedicated vector database cloud subscription (like Pinecone).

#### Q5: How do you prevent hallucinations in the RAG chat?
> **Answer**: In `core/rag_engine.py`, the system prompt explicitly enforces strict grounding: *"Answer the user's question based ONLY on the meeting transcript context provided below. If the answer is not found in the context, say 'I could not find this information in the meeting transcript.'"*

#### Q6: Why did you slice audio into 25-second pieces for Sarvam AI?
> **Answer**: Sarvam AI's synchronous speech-to-text-translate endpoint enforces a strict payload limit of ≤30 seconds per request. In `core/transcriber.py`, I implemented `_send_to_sarvam` which uses `pydub` to slice audio chunks into 25-second segments (with a 5-second safety margin) before sending.

#### Q7: How did you optimize Streamlit launch performance?
> **Answer**: Heavy ML libraries like `torch`, `transformers`, `whisper`, and `chromadb` can take ~40 seconds to import on script execution. By placing `st.set_page_config()` at line 1 and wrapping heavy module imports inside a lazy `get_pipeline_modules()` function, the Streamlit UI loads instantly (**<1 second**).

#### Q8: What text splitter chunk size and overlap did you select for RAG, and why?
> **Answer**: For vector retrieval in `core/vector_store.py`, I used `chunk_size = 500` characters and `chunk_overlap = 50`. 500 characters corresponds to ~2-3 sentences (ideal granularity for specific Q&A lookup), and the 50-character overlap prevents cutting sentences in half at boundary edges.

#### Q9: What model is used for LLM extraction and summarization?
> **Answer**: **Mistral AI** (`mistral-small-latest`) via `langchain_mistralai`. It provides fast response times and high instruction-following quality for structured extraction at low temperature settings (`temperature=0.2` - `0.3`).

#### Q10: What is the difference between Hinglish and English transcription in your app?
> **Answer**: English transcription uses local **OpenAI Whisper**. Hinglish/Hindi transcription uses **Sarvam AI**'s specialized `saaras:v2.5` model via their STT-translate API, which automatically translates Hinglish/Hindi speech into clean English text.

#### Q11: How is audio formatted before feeding into Whisper/STT?
> **Answer**: The pipeline resamples all input media to single-channel (mono) 16,000 Hz WAV files using `pydub.AudioSegment.set_channels(1).set_frame_rate(16000)`. 16kHz mono WAV is the exact standard input format required by Whisper's audio feature extractor.

#### Q12: What vector similarity metric does ChromaDB use?
> **Answer**: By default, ChromaDB uses **Cosine Similarity** (or L2 distance) to compute similarity scores between the user query embedding and the 500-character transcript chunk embeddings.

#### Q13: How is state maintained across user interactions in Streamlit?
> **Answer**: Streamlit reruns the script on every user interaction. We maintain persistence using `st.session_state` keys (`result`, `chat_history`, `pipeline_done`, `pipeline_steps`).

#### Q14: How are action items extracted from the transcript?
> **Answer**: In `core/extractor.py`, `extract_action_items()` passes the transcript to Mistral AI with a structured system prompt requiring 3 fields per item: Task Description, Owner, and Deadline.

#### Q15: How would you scale this application for long 2-hour videos in production?
> **Answer**: 
> 1. Move audio download & STT processing to background async workers (e.g. **Celery** with **Redis** or **AWS SQS**).
> 2. Use GPU acceleration (CUDA) for Whisper or hosted Whisper API.
> 3. Store vector embeddings in a scalable cloud vector DB (e.g. Pinecone / Milvus).
> 4. Use WebSockets or Server-Sent Events (SSE) to stream transcription and summary updates to the front-end UI.

---

## ⚡ Section 6: Summary of Production Trade-offs & Engineering Decisions

| Feature | Choice Made | Trade-off / Rationale |
| :--- | :--- | :--- |
| **STT Model** | Local Whisper `base` | Free, private, lightweight (139 MB); slightly lower accuracy than `large-v3` but 10x faster on CPU. |
| **Vector DB** | Local ChromaDB | Embedded & zero-config; suitable for single-user/session RAG. |
| **LLM Provider** | Mistral AI (`mistral-small-latest`) | Cost-effective, fast inference, high quality for structured JSON/bullet extraction. |
| **Summarization** | Map-Reduce Strategy | Prevents LLM context limit truncation on long meetings. |
| **App Architecture** | Streamlit + Lazy Imports | Fast prototyping with custom dark CSS; instant launch (<1s) by lazy-loading heavy modules. |

---
*Created and verified for Pushpendra Choure — AI Video Assistant Repository*
