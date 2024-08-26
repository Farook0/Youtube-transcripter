import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
from pathlib import Path
import streamlit as st
from gtts import gTTS
import tempfile

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

prompt = """
    You are an expert Youtube video summarizer. You will take the transcript text and summarize
    the entire video, providing the important summary points within 250 words. Please provide the summary of the text given here:
"""

# Extracting the transcript from YouTube
def extraction_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("v=")[1].split("&")[0]
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([i["text"] for i in transcript])
        return transcript_text
    except Exception as e:
        raise e

# Generating the summary based on the prompt from Google Gemini Pro
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt + transcript_text)
    return response.text

# Function to convert text to speech
def text_to_speech(text):
    tts = gTTS(text)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        return fp.name

# Streamlit initialization
st.title("YouTube Video Summarizer")
youtube_video_url = st.text_input("Enter the YouTube Video URL")

if youtube_video_url:
    try:
        video_id = youtube_video_url.split("v=")[1].split("&")[0]
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
        st.image(thumbnail_url, use_column_width=True)
    except IndexError:
        st.error("Invalid YouTube URL. Please check the format.")

if st.button("Get Detailed Notes"):
    transcript_text = extraction_transcript_details(youtube_video_url)
    if transcript_text:
        summary = generate_gemini_content(transcript_text, prompt)
        st.markdown("## Detailed Notes:")
        st.write(summary)
        
        # Convert the summary to speech and create a button to play it
        audio_file = text_to_speech(summary)
        st.audio(audio_file, format="audio/mp3")
