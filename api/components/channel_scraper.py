import gc  # Import garbage collection module
from apify_client import ApifyClient
from datetime import datetime
import os
from dotenv import load_dotenv
import logging  
from typing import Dict, Any, Generator  # Import Generator

load_dotenv()
KEY = os.getenv("APIFY_API_KEY")
client = ApifyClient(KEY)

# Import custom modules
import api.components.summarizer as summarizer

# Configure logging
logging.basicConfig(level=logging.ERROR)  
logger = logging.getLogger(__name__)

def video_det_store(run: Dict[str, Any], channel_info: Dict[str, Any]) -> None:  
    # Iterate through videos in the dataset
    for video in client.dataset(run["defaultDatasetId"]).iterate_items():
        try:
            channelId = video.get('channelUrl').split("/")[-1]
            
            # If channel not in channel_info, add it
            if channelId not in channel_info:
                # Initialize channel information
                channel_info[channelId] = {
                    'channel_name': video.get('channelName'),
                    'channel_description_links': video.get('channelDescriptionLinks'),
                    'subscriber_count': video.get('numberOfSubscribers'),
                    'video_dates': [],
                    'videos': []
                }
            
            # Add video date to the channel's video_dates list
            try:
                video_date = datetime.fromisoformat(video.get('date')).date()
                channel_info[channelId]['video_dates'].append(str(video_date))
            except Exception as e:
                logging.error(f"DATE ERROR - {e}")
            
            # Get video transcript
            transcript = summarizer.transcript(video.get('id'))
            if transcript:
                try:
                    summarized_transcript = summarizer.summarize_text(transcript)
                except Exception as e:
                    summarized_transcript = None
                    logger.error(f"SUMMARIZED TRANSCRIPT ERROR - {e}")

            # Add video details to the channel's videos list
            try:
                channel_info[channelId]['videos'].append({
                    'date': str(video_date),
                    'title': video.get('title'),
                    'viewCount': video.get('viewCount'),
                    'likeCount': video.get('likes'),
                    'commentsCount': video.get('commentsCount'),
                    'full_transcript': transcript,
                    'transcript_report': summarized_transcript,
                    'duration': video.get('duration'),
                    'description': video.get('text'),
                    'description_links': video.get('descriptionLinks')
                })
            except Exception as e:
                logger.error(f"ERROR - {e}") 

        except Exception as e:
            logger.error(f"store_vid_dets - {e}") 
        
        # Manually trigger garbage collection after processing each video to free up memory
        gc.collect()

def get_video_det(channel_info: Dict[str, Any], link: str) -> Dict[str, Any]:
    # Define input parameters for YouTube scraper
    input = {
        "downloadSubtitles": False,
        "hasCC": False,
        "hasLocation": False,
        "hasSubtitles": False,
        "is360": False,
        "is3D": False,
        "is4K": False,
        "isBought": False,
        "isHD": False,
        "isHDR": False,
        "isLive": False,
        "isVR180": False,
        "lengthFilter": "between420",
        "maxResultStreams": 0,
        "maxResults": 5,
        "maxResultsShorts": 0,
        "preferAutoGeneratedSubtitles": False,
        "saveSubsToKVS": False,
        "startUrls": [{"url": link}],
        "subtitlesLanguage": "any",
        "subtitlesFormat": "srt"
    }

    # Run YouTube scraper
    run = client.actor("streamers/youtube-scraper").call(run_input=input)

    # Store details of current video in iteration
    print("STATE - Storing Video Details")
    video_det_store(run, channel_info)

    return channel_info

def cscraper(link: str) -> Dict[str, Any]:
    # Initialize channel_info dictionary
    channel_info = {}

    # Get video details for the given link
    channel_info = get_video_det(channel_info, link)

    # Final garbage collection after the entire operation
    gc.collect()

    return channel_info
