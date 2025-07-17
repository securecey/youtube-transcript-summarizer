import streamlit as st
from pytube import YouTube
import requests

# Set your DeepSeek API key
DEEPSEEK_API_KEY = "your_api_key_here"

st.title("📽️ YouTube Transcript & Summarizer (DeepSeek)")

video_url = st.text_input("🔗 Enter YouTube Video URL:")

if video_url:
    try:
        yt = YouTube(video_url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_url = audio_stream.url  # no downloading

        st.success("🔊 Extracted Audio Stream URL")

        if st.button("Summarize"):
            with st.spinner("Sending to DeepSeek..."):
                # Call DeepSeek with audio URL
                headers = {
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "input": audio_url,
                    "task": "transcribe_and_summarize"
                }

                response = requests.post("https://api.deepseek.com/audio", json=payload, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    st.markdown("### 📝 Transcript")
                    st.write(data.get("transcript", "No transcript found."))

                    st.markdown("### ✨ Summary")
                    st.write(data.get("summary", "No summary found."))
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")

    except Exception as e:
        st.error(f"❌ Error processing video: {str(e)}")
