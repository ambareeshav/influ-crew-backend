from youtube_transcript_api import YouTubeTranscriptApi
from groq import Groq
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from dotenv import load_dotenv
from litellm import completion
import os, gc, litellm, logging

logging.basicConfig(level=logging.ERROR)  
logger = logging.getLogger(__name__)

# Fetch transcript for a given YouTube video id
@retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(5), retry=retry_if_exception_type(Exception))
def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([item['text'] for item in transcript])
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
@retry(wait=wait_exponential(min=3, max=10), stop=stop_after_attempt(3), retry=retry_if_exception_type(Exception))
def summarize_text(text):
    litellm.api_key = os.environ.get("ASSISTANT_KEY")
    chat_completion = completion(
        model = "gpt-4o-mini",
        messages=[
            {    
                "content": """You are a marketing assistant that will help analyze YouTube channels by summarizing transcripts and returning reports. Keep the report short but informative.
                These reports will be used to find out if the YouTuber is a relevant influencer. Do not infer anything from the video, use only what is already present in the transcript.
                The report should have a short outline of the video content, any brand deals, and mentions of sponsorships.
                Extract useful information about sponsorships or products mentioned in the video. Conclude the summary by indicating any existing sponsorships or brand partnerships observed.""",
                "role": "system"
            },
            {         
                "content": text,
                "role": "user"
            }
        ], # or mixtral-8x7b-32768 as needed
    )
    return chat_completion.choices[0].message.content

def transcript(video_id):
    # Fetch transcript
    try:
        transcript = get_transcript(video_id)
    except Exception as e:
        logging.error(f"ERROR at YouTubeTranscriptApi - {e}")
    if transcript:
        gc.collect() 
        return transcript
    else:
        return None