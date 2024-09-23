# Import necessary modules
from .keyword_scraper import kscraper
from .channel_scraper import cscraper
from .assistant import eval
from datetime import datetime
from crewai import Agent, Task, Crew, Process
import composio
import litellm
import os
from dotenv import load_dotenv

load_dotenv()
composio.LogLevel.ERROR
litellm.api_key = os.environ.get("GROQ_API_KEY")

def sort(data, channelid):
    # Get the videos array and video dates
    videos = data[channelid]["videos"]
    videos_dates = data[channelid]["video_dates"]
    
    # Sort the videos by date in descending order
    sorted_videos = sorted(videos, key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'), reverse=True)
    sorted_videos_dates = sorted(videos_dates, key=lambda x: datetime.strptime(x, '%Y-%m-%d'), reverse=True)
    
    # Update the videos array and video dates with the sorted list
    data[channelid]["videos"] = sorted_videos
    data[channelid]["video_dates"] = sorted_videos_dates

    # Return the updated data
    return data

def sheets_crew(tools, eval_data):
    

    print("STATE - Initializing Agent")
    write_data_agent = Agent(
        role="Google Sheets Manager",
        goal="Create a Google Sheet and write influencer evaluation data to it",
        backstory="You are responsible for managing data in Google Sheets for an influencer evaluation system.",
        verbose=True,
        tools=tools,
        llm = "groq/llama3-70b-8192",
        cache = False
    )
    print("STATE - Initializing Task")
    create_and_write_task = Task(
        description=f"""
        1. Create a new Google Sheet named "Influencer Evaluation".
        2. Extract the 'spreadsheet_id' from the creation response.
        3. Write the following header row to the sheet as first row:["Influencer Name", "Relevance", "Impact", "Winnability", "Subscribers", "Frequency", "Views", "Rationale", "partnership_ideas"]
        4. With the header row as key, write {eval_data} starting from the second row, DO NOT WRITE THE RAW INPUT DATA
        5. Your response must be only the link that the user can click to go to the sheet like this - https://docs.google.com/spreadsheets/d/<spreadsheetId>
        """,
        agent=write_data_agent,
        expected_output="Google Sheet link",
        verbose=True
    )
    print("STATE - Initializing Crew")
    my_crew = Crew(agents=[ write_data_agent], tasks=[create_and_write_task], process= Process.sequential)
    print("STATE - Crew Kickoff")
    try:
        result = my_crew.kickoff()
    except Exception as e:
        result = e
        print(result)
    print("STATE - Analysis Complete")
    return result

def main(keyword, channels, tools):
    print("STATE - 'Searching YouTube'")
    # Get links for the keyword
    links = kscraper(keyword, channels)
    print("STATE - Got Links")
    channel_no = 1
    
    eval_data ={}
    # Iterate over each link
    for link in links:
        # Extract channel name from the link
        channel_name = link.split("@")[-1]
        print(f"STATE - {channel_no}: {channel_name}")
        # Get video details for the channel and save it to a json file
        
        vid_dets = cscraper(link)
        print(f"STATE - Got {channel_name} Video Details")
        # Get the channel ID and sort the video data
        channelid = list(vid_dets.keys())[0]
        data = str(sort(vid_dets, channelid))
        
        print(f"STATE - Analyzing {channel_name}")
        response = eval(data)
        print(f"STATE - Analyzed {channel_name}")
        if channel_name not in eval_data:
            eval_data[channel_name] = response
        print(f"STATE - {channel_name} Analysis Stored")  
        channel_no+=1
    print(f"STATE - Analysis done for {channel_no} Channels")
    print(eval_data)
    link = sheets_crew(tools, eval_data)
    return link
    


