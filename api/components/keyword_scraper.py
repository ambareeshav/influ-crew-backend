# Import necessary libraries
from apify_client import ApifyClient
from dotenv import load_dotenv  
import os
import gc  # Import the garbage collection module

load_dotenv()
KEY = os.getenv("APIFY_API_KEY")
client = ApifyClient(KEY)

# Function to get channel IDs using the YouTube scraper Actor
def get_channelid(keyword, channels):
    # Define input parameters for YouTube scraper
    run_input = {
        "searchKeywords": f"{keyword}",
        "maxResults": channels,
        "maxResultsShorts": 0,
        "maxResultStreams": 0,
        "startUrls": [],
        "subtitlesLanguage": "any",
        "subtitlesFormat": "srt",
    }
    # Run the YouTube scraper Actor and return the result
    run = client.actor("streamers/youtube-scraper").call(run_input=run_input)
    return run

# Function to scrape channel URLs
def kscraper(keyword, channels):
    links = []
    
    # Get channel IDs for the given keyword
    run = get_channelid(keyword, channels)
    
    # Iterate through the dataset and extract channel URLs
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        links.append(item.get("channelUrl"))
    
    # Clean up the 'run' variable after processing
    del run
    gc.collect()  # Trigger garbage collection manually

    # Clean up each 'item' after the iteration (optional)
    del item
    gc.collect()

    return links
