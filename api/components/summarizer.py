from youtube_transcript_api import YouTubeTranscriptApi
from groq import Groq

#Initialize the LLM
client = Groq()

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
                    "content": """You are a marketing assistant that will help analyze youtube video transcripts and return detailed reports to find out if the youtuber is a fit for our company
                    here is some information about our product:
                    Product: Swipe Pages
                        
                        Description: A landing page builder that helps marketers create high-converting, mobile-friendly landing pages without any code. Features include:
                        
                        Page Speed and Mobile Optimization: Unique mobile-specific experiences called Mobile Slides.
                        150+ Modern Templates: Extensive library for various use cases.
                        Swipe Genie: AI-driven page creation tool.
                        Global Blocks and Saved Sections: For scalable page creation.
                        Sales Funnels: Create and sell digital products with upsells and downsells.
                        
                    2. Ideal Customer Profiles (ICPs)
                    Marketers and Marketing Agencies: Focused on running and optimizing paid ad campaigns for lead generation or product sales. Typically work with substantial ad budgets and need tools to improve campaign performance.
                    Solo Entrepreneurs and Creators: Individuals who manage their own marketing efforts, often with limited resources but require effective tools for high-converting landing pages.
                    Businesses in Specific Industries:
                    Ecommerce: Need fast, mobile-optimized landing pages to convert ad traffic into sales.
                    SaaS: Require landing pages that capture leads and convert them into paying customers.
                    Education (EdTech, Universities, Knowledge Entrepreneurs): Focus on lead generation and student enrollment.
                    SMBs and Local Businesses: Looking to attract local customers through targeted ad campaigns.
                    Health & Medical: Clinics and practices that use online marketing to attract and book appointments.
                    Travel: Need landing pages to convert ad traffic into bookings or inquiries.
                    Performance Marketers: Professionals specialized in running and optimizing paid ad campaigns across platforms like Google Ads and Facebook Ads, often working in agencies or in-house teams with a focus on ROI and ad spend efficiency.
                        
                        Key Differentiators:
                        Superior page speed and mobile optimization.
                        AI-driven page creation with Swipe Genie.
                        Competitive pricing with higher traffic and usage limits.
                        Sales funnels for additional revenue streams.
                        
                        Solutions Offered by Swipe Pages:
                        High-Quality, Mobile-Optimized Pages: Faster load times and better mobile optimization.
                        Ease of Use: Intuitive interface and AI-driven tools.
                        Cost-Effective Solutions: Competitive pricing with comprehensive features.
                        Flexible Customization: Extensive customization options without coding.
                        
                        using the above information, extract the usefull information from the transcript, information talking about sponsorships, products or any of our USPs are very important, at the end of the summary include any sponsorships, brand deals or if the infleuncer seems to be already be with another company or is promoting other channels of media such as instagram twitter etc..""",
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


