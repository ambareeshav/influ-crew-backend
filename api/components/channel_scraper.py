# Import necessary libraries
from apify_client import ApifyClient
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()
KEY = os.getenv("APIFY_API_KEY")

client = ApifyClient(KEY)
# Import custom modules
import api.components.summarizer as summarizer
import api.components.webdriver as webdriver

def video_det_store(run, channel_info):
    # Iterate through videos in the dataset
    for video in client.dataset(run["defaultDatasetId"]).iterate_items():
        # Extract channel ID from the URL
        channelId = video.get('channelUrl').split("/")[-1]
        
        # If channel not in channel_info, add it
        if channelId not in channel_info:
            try:
                # Scrape recent video titles from the channel
                titles = webdriver.scrape_channel(f"{video.get('inputChannelUrl')}/videos")
            except:
                titles = None
            # Initialize channel information
            channel_info[channelId] = {
                'channel_name': video.get('channelName'),
                'channel_description_links': video.get('channelDescriptionLinks'),
                'subscriber_count': video.get('numberOfSubscribers'),
                #'recent_videos': titles,
                'video_dates': [],
                'videos': []
                }
        
        # Add video date to the channel's video_dates list
        channel_info[channelId]['video_dates'].append(str((datetime.fromisoformat(video.get('date'))).date()))
        # Get video transcript
        transcript = summarizer.get_transcript(video.get('id'))
        if transcript is not None:
            full_transcript = ' '.join([item['text'] for item in transcript])
        else:
            full_transcript = None
        # Add video details to the channel's videos list
        channel_info[channelId]['videos'].append({
            'date': str((datetime.fromisoformat(video.get('date'))).date()),
            'title': video.get('title'),
            'viewCount': video.get('viewCount'),
            'likeCount': video.get('likes'),
            'commentsCount': video.get('commentsCount'),
            'summarized_transcript': summarizer.summarize(video.get('id')),
            'full_transcript': full_transcript,
            'duration': video.get('duration'),
            'description': video.get('text'),
            'description_links': video.get('descriptionLinks')
        })

def get_video_det(channel_info, link):
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
        "maxResultStreams": 0,
        "maxResults": 1,
        "maxResultsShorts": 0,
        "preferAutoGeneratedSubtitles": False,
        "saveSubsToKVS": False,
        "startUrls": [
        {
            "url": link
        }
        ],
        "subtitlesLanguage": "any",
        "subtitlesFormat": "srt"
    }
    # Run YouTube scraper
    run = client.actor("streamers/youtube-scraper").call(run_input=input)
    # Store details of current video in iteration
    video_det_store(run, channel_info)

    return channel_info


def scrape(link):
    # Initialize channel_info dictionary
    channel_info = {}
    # Get video details for the given link
    channel_info = get_video_det(channel_info, link)

    return channel_info

  



