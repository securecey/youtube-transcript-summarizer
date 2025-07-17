import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import re

st.set_page_config(page_title="🎬 YouTube Summarizer", layout="centered")
st.title("🎥 YouTube Video Summarizer (DeepSeek Chat API)")

video_url = st.text_input("Enter YouTube Video URL:")

# Extract YouTube video ID
def extract_video_id(url):
    match = re.search(r"(?:v=|youtu\.be/)([^&\n?#]+)", url)
    return match.group(1) if match else None

if st.button("Summarize"):
    if not video_url:
        st.warning("Please enter a valid YouTube URL.")
    else:
        video_id = extract_video_id(video_url)
        if not video_id:
            st.error("❌ Could not extract video ID.")
        else:
            st.info("📄 Fetching transcript...")
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                full_text = " ".join([t['text'] for t in transcript])

                st.success("✅ Transcript retrieved!")
                st.markdown("### 🧠 Generating Summary with DeepSeek...")

                api_key = st.secrets["DEEPSEEK_API_KEY"]
                endpoint = "https://api.deepseek.com/v1/chat/completions"

                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }

                prompt = f"Summarize the following YouTube transcript:\n\n{full_text}"

                payload = {
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.5
                }

                response = requests.post(endpoint, headers=headers, json=payload)

                if response.status_code == 200:
                    summary = response.json()["choices"][0]["message"]["content"]
                    st.success("📝 Summary Ready!")
                    st.markdown(summary)
                else:
                    st.error(f"❌ DeepSeek API Error {response.status_code}: {response.text}")

            except Exception as e:
                st.error(f"🔥 Error: {e}")
