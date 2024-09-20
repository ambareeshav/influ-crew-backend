# Import necessary modules
from .keyword_scraper import kscraper
from .channel_scraper import cscraper
from .assistant import eval
from datetime import datetime
from crewai import Agent, Task, Crew, Process
print("before chatgroq import")
from langchain_groq import ChatGroq
print("init chatgroq")
#llm = ChatGroq(model_name='llama3-70b-8192')
from litellm import completion

# Configure LiteLLM to use ChatGroq
completion("groq/llama3-70b-8192", messages=[{"role": "user", "content": "Hello, how are you?"}])

def sort(data, channelid):
    # Get the videos array and video dates
    videos = data[channelid]["videos"]
    videos_dates = data[channelid]["video_dates"]
    
    # Sort the videos by date in descending order
    sorted_videos = sorted(videos, key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'), reverse=True)
    sorted_videos_dates = sorted(videos_dates, key=lambda x: datetime.strptime(x, '%Y-%m-%d'), reverse=True)
    
    # Update the videos array and video dates with the sorted lists
    data[channelid]["videos"] = sorted_videos
    data[channelid]["video_dates"] = sorted_videos_dates

    # Return the updated data
    return data

def sheets_crew(tools, eval_data):
    print("in sheets_crew before agent create")
    write_data_agent = Agent(
        role="Google Sheets Manager",
        goal="Create a Google Sheet and write influencer evaluation data to it",
        backstory="You are responsible for managing data in Google Sheets for an influencer evaluation system.",
        verbose=False,
        tools=tools,
        llm_config={
        "provider": "litellm",
        "model": "groq/llama3-70b-8192"
    },
        cache = False
    )
    print("after agent create, task create")
    create_and_write_task = Task(
        description=f"""
        1. Create a new Google Sheet named "Influencer Evaluation".
        2. Extract the 'spreadsheet_id' from the creation response.
        3. Write the following header row to the sheet as first row:["Influencer Name", "Relevance", "Impact", "Winnability", "Subscribers", "Frequency", "Views", "Rationale", "partnership_ideas"]
        4. Now write {eval_data} to the second row with the first row as key,DO NOT WRITE THE RAW INPUT DATA
        5. Return only the Google Sheet link - "https://docs.google.com/spreadsheets/d/<spreadsheetId>"
        """,
        agent=write_data_agent,
        expected_output="Google Sheet link"
    )
    print("my_crew")
    my_crew = Crew(agents=[ write_data_agent], tasks=[create_and_write_task], process= Process.sequential)
    print("kickoff")
    try:
        result = my_crew.kickoff()
    except Exception as e:
        result = e
    print(result)
    return result

def main(keyword, channels, tools):
    # STATE - "Searching YouTube"
    # Get links for the keyword
    links = kscraper(keyword, channels)
    channel_no = channels
    
    eval_data ={}
    # Iterate over each link
    for link in links:
        # Extract channel name from the link
        channel_name = link.split("@")[-1]
        #print(channel_name)
        # Get video details for the channel and save it to a json file
        
        vid_dets = cscraper(link)
        #print("got vid deets")
        # Get the channel ID and sort the video data
        channelid = list(vid_dets.keys())[0]
        data = str(sort(vid_dets, channelid))
        # STATE - f"Gathering channel {channel_no} data"
        channel_no+=1
        # STATE - "Analyzing channel"
        response = eval(data)
        print( "response in eval")
        if channel_name not in eval_data:
            eval_data[channel_name] = response
    link = sheets_crew(tools, eval_data)
    return link
    


