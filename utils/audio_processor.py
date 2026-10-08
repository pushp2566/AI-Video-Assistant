import yt_dlp
from pydub import AudioSegment
import os

import shutil

DOWNLOAD_DIR = 'downloades'
os.makedirs(DOWNLOAD_DIR,exist_ok = True)

def download_youtube_audio(url: str) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s")
    
    ffmpeg_bin = shutil.which("ffmpeg")
    ffmpeg_dir = os.path.dirname(ffmpeg_bin) if ffmpeg_bin else None

    # Check if YOUTUBE_COOKIES is provided via environment/secrets
    cookiefile_path = None
    cookies_content = os.getenv("YOUTUBE_COOKIES")
    if cookies_content:
        cookiefile_path = os.path.join(DOWNLOAD_DIR, "youtube_cookies.txt")
        with open(cookiefile_path, "w", encoding="utf-8") as f:
            f.write(cookies_content)

    base_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "quiet": True,
        "nocheckcertificate": True,
        "geo_bypass": True,
    }
    if cookiefile_path and os.path.exists(cookiefile_path):
        base_opts["cookiefile"] = cookiefile_path

    configs = []
    
    # If cookies are present, try standard web/mweb first as it is authenticated
    if cookiefile_path and os.path.exists(cookiefile_path):
        configs.append({
            **base_opts,
            "extractor_args": {
                "youtube": {
                    "player_client": ["web", "mweb"]
                }
            }
        })

    configs.extend([
        # Strategy 1: iOS & Android client
        {
            **base_opts,
            "extractor_args": {
                "youtube": {
                    "player_client": ["ios", "android"]
                }
            }
        },
        # Strategy 2: TV client fallback
        {
            **base_opts,
            "extractor_args": {
                "youtube": {
                    "player_client": ["tv"]
                }
            }
        },
        # Strategy 3: Standard default
        {
            **base_opts,
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            }
        }
    ])

    last_error = None
    for ydl_opts in configs:
        if ffmpeg_dir:
            ydl_opts["ffmpeg_location"] = ffmpeg_dir
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                raw_filename = ydl.prepare_filename(info)
                wav_filename = convert_to_wav(raw_filename)
                if os.path.exists(raw_filename) and raw_filename != wav_filename:
                    try:
                        os.remove(raw_filename)
                    except Exception:
                        pass
                return wav_filename
        except Exception as e:
            last_error = e

    if last_error:
        raise last_error



def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using pydub."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000) #16khz
    audio.export(output_path, format="wav")
    return output_path



def chunk_audio(wav_path : str , chunk_minutes : int = 10) -> list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000 

    chunks = []

    for i, start in enumerate(range(0,len(audio),chunk_ms)):
        chunk = audio[start : start + chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path , format = "wav")

        chunks.append(chunk_path)
    
    return chunks

def process_input(source: str) -> list:
    source = source.strip()
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        if not os.path.exists(source):
            raise FileNotFoundError(
                f"Invalid input: '{source[:60]}...' is neither a valid YouTube URL nor an existing local file. Please enter a YouTube link (e.g., https://www.youtube.com/watch?v=...) or a valid local file path."
            )
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks


