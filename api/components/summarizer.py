from youtube_transcript_api import YouTubeTranscriptApi
from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
#Initialize the LLM
client = Groq(api_key = GROQ_API_KEY)

#Fetch transcript for a given YouTube video id
def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

#Convert JSON to a string to pass to the LLM
def transcript_to_text(transcript):
    return " ".join([item['text'] for item in transcript])
    
def summarize_text(text):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": """You are a marketing assistant that will help analyze youtube video transcripts and return detailed reports, these reports will be used to find out if the youtuber is a relevant influencer. Do not infer anything from the video, use only what is already present in the transcript.
                    The report should be detailed, from the report it should be inferred what type of content the youtuber is talking about, if they have any brand deals, the report should provide a detailed outline of the video, keep the length lesser than 256000  
                    Extract the usefull information from the transcript, information talking about sponsorships or products are very important, at the end of the summary include any sponsorships, brand deals or if the influencer seems to be already be with another company""",
                },
                {
                    "role": "user",
                    "content": text,
                }
            ],
            model="llama-3.1-8b-instant", # mixtral-8x7b-32768
        )
        return(chat_completion.choices[0].message.content)
    
    except Exception as e:
        return e

def summarize(video_id):
    #Fetch transcript
    transcript = get_transcript(video_id)

    # Check if transcipt available and summarize if yes, else return None
    if transcript:
        transcript_text = transcript_to_text(transcript)

        summary = summarize_text(transcript_text)
        
        return summary
    else:
        return None


