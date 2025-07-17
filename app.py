import streamlit as st
import requests
import re

st.set_page_config(page_title="🎥 YouTube Video Summarizer", layout="centered")
st.title("🎬 YouTube Video Summarizer with DeepSeek AI")

# Input box
video_url = st.text_input("Enter YouTube Video URL:")

# Validate and extract video ID
def extract_video_id(url):
    match = re.search(r"(?:v=|youtu\.be/)([^&\n?#]+)", url)
    return match.group(1) if match else None

# On button click
if st.button("Summarize"):
    if not video_url:
        st.warning("Please enter a valid YouTube URL.")
    else:
        video_id = extract_video_id(video_url)
        if not video_id:
            st.error("❌ Could not extract video ID from the URL.")
        else:
            st.info("⏳ Processing using DeepSeek...")
            try:
                api_key = st.secrets["DEEPSEEK_API_KEY"]  # Set this in Streamlit Cloud
                endpoint = "https://api.deepseek.com/v1/youtube/summarize"

                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }

                response = requests.post(endpoint, json={"url": video_url}, headers=headers)

                if response.status_code == 200:
                    summary = response.json().get("summary", "No summary provided.")
                    st.success("✅ Summary Ready!")
                    st.markdown("### 📝 Summary")
                    st.write(summary)
                else:
                    st.error(f"🚫 API Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"🔥 Exception: {e}")
