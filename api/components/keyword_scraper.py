from apify_client import ApifyClient
from dotenv import load_dotenv  
import os, gc 

load_dotenv()
KEY = os.getenv("APIFY_API_KEY")
client = ApifyClient(KEY)

# Get channel IDs using the YouTube scraper Actor
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

# Extract links from raw api data
def kscraper(keyword, channels):
    links = []
    
    # Get channel IDs for the given keyword
    run = get_channelid(keyword, channels)
    
    # Iterate through the dataset and extract channel URLs
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        links.append(item.get("channelUrl"))
    
    # Clean up the variables after processing
    del run
    del item
    gc.collect()  # Trigger garbage collection 

    return links
