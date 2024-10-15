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
        return transcript
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Convert JSON to a string to pass to the LLM
def transcript_to_text(transcript):
    return " ".join([item['text'] for item in transcript])

def summarize_text(text):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": """You are a marketing assistant that will help analyze YouTube video transcripts and return reports. 
                    These reports will be used to find out if the YouTuber is a relevant influencer. Do not infer anything from the video, use only what is already present in the transcript.
                    The report should have an outline of the video content, any brand deals, and mentions of sponsorships.
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

def summarize(video_id):
    # Fetch transcript
    transcript = get_transcript(video_id)

    # Check if transcript is available and summarize if yes, else return None
    if transcript:
        transcript_text = transcript_to_text(transcript)

        # Free up memory from the transcript object
        del transcript
        gc.collect()  # Force garbage collection

        summary = summarize_text(transcript_text)

        # Free up memory from the transcript text
        del transcript_text
        gc.collect()  # Force garbage collection

        return summary
    else:
        return None
