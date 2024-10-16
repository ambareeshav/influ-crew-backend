from youtube_transcript_api import YouTubeTranscriptApi
from groq import Groq
import os
import gc
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Initialize the LLM
client = Groq(api_key=GROQ_API_KEY)

# Fetch transcript for a given YouTube video id
def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([item['text'] for item in transcript])
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def summarize_text(text):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": """You are a marketing assistant that will help analyze YouTube channels by summarizing transcripts and returning reports. Keep the report short but informative.
                    These reports will be used to find out if the YouTuber is a relevant influencer. Do not infer anything from the video, use only what is already present in the transcript.
                    The report should have a short outline of the video content, any brand deals, and mentions of sponsorships.
                    Extract useful information about sponsorships or products mentioned in the video. Conclude the summary by indicating any existing sponsorships or brand partnerships observed.""",
                },
                {
                    "role": "user",
                    "content": text,
                }
            ],
            model="llama-3.1-8b-instant",  # or mixtral-8x7b-32768 as needed
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error during summarization: {e}")
        return None

def transcript(video_id):
    # Fetch transcript
    transcript = get_transcript(video_id)

    if transcript:
        gc.collect()  # Force garbage collection
        return transcript
    else:
        return None
