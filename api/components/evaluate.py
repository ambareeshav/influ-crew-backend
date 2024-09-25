# Import necessary modules
from .keyword_scraper import kscraper
from .channel_scraper import cscraper
from .assistant import eval
from datetime import datetime
from crewai import Agent, Task, Crew, Process
from composio_crewai import Action
import composio, os, litellm, threading, json
from dotenv import load_dotenv
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

# Initialize once before starting any threads


load_dotenv()

composio.LogLevel.FATAL
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


def data(keyword, channels, tools, id):
    print("STATE - Searching YouTube")
    # Get links for the keyword
    links = kscraper(keyword, channels)
    print("STATE - Got Links")

    # Iterate over each link
    for channel_no, link in enumerate(links):
        eval_data ={}

        # Extract channel name from the link
        channel_name = link.split("@")[-1]
        print(f"STATE - {channel_no+1}: {channel_name}")

        # Get video details for the channel and save it to a json file
        vid_dets = cscraper(link)
        print(f"STATE - Got {channel_name} Video Details")

        # Get the channel ID and sort the video data
        channelid = list(vid_dets.keys())[0]
        data = str(sort(vid_dets, channelid))
        
        print(f"STATE - Analyzing {channel_name}")
        response = eval(data)
        #print(response)
        print(f"STATE - Analyzed {channel_name}")

        eval_data[channel_name] = response
        #print(eval_data)
        print(f"STATE - {channel_name} Analysis Stored")

        #sheets_crew(tools, eval_data, id, channel_no+2)
        """ write_thread = threading.Thread(target=sheets_crew, args=(tools, eval_data, id, channel_no+2))
        write_thread.start() """
        

        data = json.loads(eval_data[channel_name])

        # Extract evaluation values (e.g., "irrelevant", "low")
        evaluation_list = []
        evaluation_list.append(channel_name)
        for key, value in data.items():
            if isinstance(value, dict) and "Evaluation" in value:
                evaluation_list.append(value["Evaluation"])
            elif key == "Subscribers":
                evaluation_list.append(value)  # Extract the subscriber count
            elif key == "Rationale":
                evaluation_list.append(value)  # Extract the rationale
            elif key == "partnership_ideas":
                evaluation_list.append(value)  # Extract partnership ideas


        row = channel_no+2

        write_data_agent = Agent(
        role="Google Sheets Manager",
        goal="Write influencer evaluation data to a google sheet",
        backstory="You are responsible for writing data to Google Sheets as part of an influencer evaluation system. Given a list and google sheets information you will write the list to it",
        verbose=False,
        tools=tools,
        llm = "groq/llama3-70b-8192",
        cache = False
        )
        print("STATE - Initializing Task")
        write_task = Task(
            description=f"""
            1. The data provided is already formatted, your only task is to write to google sheets using the Action.GOOGLESHEETS_BATCH_UPDATE tool
            2. Write the list {evaluation_list} to row {row} of the google sheet with SpreadshetId {id}
            3. End execution once data is written
            """,
            agent=write_data_agent,
            expected_output="Input data is written to given row in the given spreadsheet",
            verbose=False
        )
        print("STATE - Initializing Crew")
        write_crew = Crew(agents=[ write_data_agent], tasks=[write_task], process= Process.sequential)
        print("STATE - Crew Kickoff")
        write_crew.kickoff()
        print(f"STATE - Wrote channel {row-1} eval data to Sheet")


    print(f"STATE - Analysis done for {channel_no+1} Channels")
    #print(eval_data)
    
def create_sheet(keyword, channels, toolset):
    composio_tools = toolset.get_tools(actions=[Action.GOOGLESHEETS_CREATE_GOOGLE_SHEET1, Action.GOOGLESHEETS_BATCH_UPDATE])
    sheet_header_agent = Agent(
        role="Google Sheets Manager",
        goal="Create a Google Sheet and write header data to it",
        backstory="You are responsible for managing data in Google Sheets for an influencer evaluation system.",
        verbose=False,
        tools=composio_tools,
        llm="groq/llama3-70b-8192"
    )
    create_and_write_task = Task(
        description="""
        1. Create a new Google Sheet named "Influencer Evaluation".
        2. Extract the 'spreadsheet_id' from the creation response.
        3. Write the following header row to the sheet as first row:["Influencer Name", "Relevance", "Impact", "Winnability", "Subscribers", "Frequency", "Views", "Rationale", "partnership_ideas"]
        4. After writing header data your response must be a link that the user can click to go the created spreadsheet , 
        """,
        agent=sheet_header_agent,
        expected_output="Spreadsheet link is returned",
        verbose=False
    )
    
    my_crew = Crew(agents=[sheet_header_agent], tasks=[create_and_write_task], process=Process.sequential)
    link = my_crew.kickoff()
    id = link.raw.split('/d/')[1].split('/')[0]
    composio_tools = toolset.get_tools(actions=[Action.GOOGLESHEETS_BATCH_UPDATE])
    #data(keyword, channels, composio_tools, id)
    #data(keyword, channels, composio_tools, id)
    data_thread = threading.Thread(target=data, args=(keyword, channels, composio_tools, id))
    trace.set_tracer_provider(TracerProvider())
    data_thread.start()
    return link

def main(keyword, channels, toolset):
    link = create_sheet(keyword, channels, toolset)
    return link



