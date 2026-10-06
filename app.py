import streamlit as st
import requests
import time
import os
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip

# --- 1. UI SETUP (Streamlit) ---
st.set_page_config(page_title="Yo-AI Video Studio", page_icon="🎬", layout="centered")
st.title("🎬 Yo-AI Video Generator (HD)")
st.write("अपना प्रॉम्प्ट लिखो और 2D एनीमेशन, AI वॉइस और वीडियो एक साथ बनाओ!")

# --- 2. API KEYS (Sidebar) ---
st.sidebar.header("🔑 API Keys")
st.sidebar.write("यहाँ अपनी API Keys डालें:")
elevenlabs_key = st.sidebar.text_input("ElevenLabs API Key", type="password")
fal_key = st.sidebar.text_input("Fal.ai API Key", type="password")

# --- 3. USER INPUTS ---
video_prompt = st.text_area("🎥 वीडियो का प्रॉम्प्ट लिखें (English बेस्ट रहेगा):", 
                            "High quality 2D animation of Virat Kohli hitting a cover drive in a stadium, vibrant colors, cinematic lighting.")
voice_text = st.text_area("🎙️ वॉयसओवर टेक्स्ट (हिंदी या इंग्लिश):", 
                          "विराट कोहली का यह कवर ड्राइव क्रिकेट के इतिहास के सबसे बेहतरीन शॉट्स में से एक है।")

# --- 4. CORE FUNCTIONS ---
def generate_voice(text, api_key):
    """ElevenLabs से रियलिस्टिक आवाज़ बनाना"""
    url = "https://api.elevenlabs.io/v1/text-to-speech/JBFqnCBcs6RMkjGVYIVt"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        with open("voice.mp3", "wb") as f:
            f.write(response.content)
        return "voice.mp3"
    else:
        st.error(f"Voice Error: {response.text}")
        return None

def generate_video(prompt, api_key):
    """Fal.ai (Minimax) से HD वीडियो जनरेट करना"""
    url = "https://fal.run/fal-ai/minimax-video"
    headers = {
        "Authorization": f"Key {api_key}",
        "Content-Type": "application/json"
    }
    payload = {"prompt": prompt}
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        video_url = response.json().get("video", {}).get("url")
        if video_url:
            vid_data = requests.get(video_url).content
            with open("video.mp4", "wb") as f:
                f.write(vid_data)
            return "video.mp4"
    st.error(f"Video Error: {response.text}")
    return None

def merge_audio_video(video_path, audio_path, output_path="final_output.mp4"):
    """MoviePy से वीडियो और ऑडियो को मिक्स करना"""
    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path)
    
    final_video = video_clip.set_audio(audio_clip).set_duration(audio_clip.duration)
    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24, logger=None)
    return output_path

# --- 5. EXECUTION LOGIC ---
if st.button("🚀 Generate HD Video"):
    if not elevenlabs_key or not fal_key:
        st.error("⚠️ कृपया साइडबार में ElevenLabs और Fal.ai की API Keys डालें!")
    else:
        with st.spinner("सिस्टम काम कर रहा है... (2-3 मिनट लग सकते हैं)"):
            
            # Step 1: Voice
            st.info("🎙️ 1/3: आवाज़ तैयार हो रही है...")
            voice_file = generate_voice(voice_text, elevenlabs_key)
            
            # Step 2: Video
            if voice_file:
                st.info("🎥 2/3: 2D एनीमेशन जनरेट हो रहा है...")
                video_file = generate_video(video_prompt, fal_key)
                
                # Step 3: Mix
                if video_file:
                    st.info("🎬 3/3: वीडियो और ऑडियो को मिक्स किया जा रहा है...")
                    final_file = merge_audio_video(video_file, voice_file)
                    
                    st.success("✅ तुम्हारा वीडियो तैयार है!")
                    st.video(final_file)
                    
                    with open(final_file, "rb") as file:
                        st.download_button(
                            label="⬇️ Download HD Video",
                            data=file,
                            file_name="yo_ai_video.mp4",
                            mime="video/mp4"
                        )
