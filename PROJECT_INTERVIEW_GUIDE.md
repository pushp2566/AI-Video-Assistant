# 🎬 AI Video Assistant - Complete Technical Guide & Interview Master File

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
   - Chunks long audio files into **10-minute segments** for memory safety.

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

## 💻 Section 3: Codebase Module Deep Dive

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

## 🔑 Section 4: Key AI & Machine Learning Concepts Explained Simply

### 1. What is RAG (Retrieval-Augmented Generation)?
> **Explanation**: RAG combines search (retrieval) with text generation (LLM). Instead of relying on a pre-trained LLM's static memory (which doesn't know about *your* private meeting video), RAG searches a vector database for the top 4 most relevant text snippets from your transcript and passes them into the prompt as context. This eliminates hallucinations and guarantees accurate answers.

### 2. What are Vector Embeddings & Vector Databases?
> **Explanation**: Vector embeddings convert text strings into numerical arrays (vectors in 384-dimensional space) where words/sentences with similar meanings are stored close to each other. **ChromaDB** is an open-source local vector database that indexes these embeddings and performs fast similarity searches (e.g. cosine distance).

### 3. What is Map-Reduce Summarization?
> **Explanation**: When a transcript is too long to fit into a single prompt, Map-Reduce splits the text into chunks. The **Map** step independently summarizes each chunk. The **Reduce** step feeds all partial summaries into the LLM to write one unified executive summary.

### 4. What is LCEL (LangChain Expression Language)?
> **Explanation**: LCEL is a declarative syntax provided by LangChain using the pipe `|` operator (e.g. `retriever | prompt | llm | output_parser`) to compose modular, streaming-ready AI pipelines cleanly.

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
