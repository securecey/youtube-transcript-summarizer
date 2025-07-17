import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import requests
import subprocess
import os
import uuid

# --- UI ---
st.set_page_config(page_title="YouTube Summarizer", layout="centered")
st.title("📽️ YouTube Transcript & Summarizer (DeepSeek)")
video_url = st.text_input("🔗 Enter YouTube Video URL:")

# --- Extract Video ID ---
def extract_video_id(url):
    import re
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None

# --- Get Transcript ---
def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([t["text"] for t in transcript])
    except (TranscriptsDisabled, NoTranscriptFound):
        return None

# --- Transcribe Using DeepSeek ---
def transcribe_with_deepseek(video_url, api_key):
    unique_id = str(uuid.uuid4())
    audio_file = f"{unique_id}.mp3"

    # Download audio using yt-dlp
    ydl_cmd = f"yt-dlp -x --audio-format mp3 -o {audio_file} {video_url}"
    os.system(ydl_cmd)

    if not os.path.exists(audio_file):
        return None

    # Upload to DeepSeek API
    with open(audio_file, "rb") as f:
        headers = {"Authorization": f"Bearer {api_key}"}
        files = {"file": f}
        response = requests.post(
            "https://api.deepseek.com/v1/audio/transcriptions",
            headers=headers,
            files=files,
        )

    os.remove(audio_file)

    if response.status_code == 200:
        return response.json().get("text")
    else:
        return None

# --- Summarize Using DeepSeek ---
def summarize_with_deepseek(transcript, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are an expert summarizer."},
            {"role": "user", "content": f"Summarize the following transcript:\n\n{transcript}"}
        ]
    }
    res = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload)
    if res.status_code == 200:
        return res.json()['choices'][0]['message']['content']
    return "❌ Error summarizing with DeepSeek"

# --- Main Logic ---
if video_url:
    video_id = extract_video_id(video_url)
    if not video_id:
        st.error("❌ Invalid YouTube URL.")
    else:
        st.info("📜 Fetching transcript...")
        transcript = get_transcript(video_id)
        if not transcript:
            st.warning("🧠 No transcript found. Transcribing with DeepSeek...")
            transcript = transcribe_with_deepseek(video_url, st.secrets["DEEPSEEK_API_KEY"])
        
        if transcript:
            st.success("✅ Transcript ready. Generating summary...")
            summary = summarize_with_deepseek(transcript, st.secrets["DEEPSEEK_API_KEY"])
            st.markdown("### 📝 Summary")
            st.write(summary)
        else:
            st.error("❌ Transcript not available and transcription failed.")
