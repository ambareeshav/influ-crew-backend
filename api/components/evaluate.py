# Import necessary modules
from .keyword_scraper import kscraper
from .channel_scraper import scrape
from .assistant import eval
from datetime import datetime
from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq
import json
llm = ChatGroq(model_name='llama3-70b-8192')

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
    write_data_a = Agent(
        role="To create a google sheet and write data to it",
        goal="Data written to google sheets and link of google sheet shared",
        backstory=(
            "You are part of a influencer evaluation system, your job is to take the evaluation data and write it to google sheets so the user can view the data"
        ),
        verbose=True,
        tools=tools,
        llm=llm,
    )
    #format = {"Influencer Name", "Relevance", "Impact", "Winnability, Subscribers", "Frequency", "Views", "Rationale", "partnership_ideas"}
    create_sheet= Task(
    description=f"Create a google sheet to write data to and get the 'spreadsheet_id'",
    agent = write_data_a,
    expected_output="'spreadsheet_id' is returned",
    verbose = True
    )
    write_data= Task(
    context = [create_sheet],
    description=f"Write {eval_data} into the already created google sheet, return only the google sheets link",
    agent = write_data_a,
    expected_output="Link is shared and execution is ended",
    verbose = True,
    )


    my_crew = Crew(agents=[write_data_a], tasks=[create_sheet, write_data], process= Process.sequential)
    result = my_crew.kickoff()
    """ print("result", result)
    op = write_data.output
    print(op)
    print(json.dumps(op.json_dict, indent=2)) """
    return result

def main(keyword, channels):
    #print("got deets")
    # Get links for the keyword
    links = kscraper(keyword, channels)
    #print("got links", links)
    eval_data ={}
    # Iterate over each link
    for link in links:
        # Extract channel name from the link
        channel_name = link.split("@")[-1]
        #print(channel_name)
        # Get video details for the channel and save it to a json file
        vid_dets = scrape(link)
        #print("got vid deets")
        # Get the channel ID and sort the video data and save
        channelid = list(vid_dets.keys())[0]
        data = str(sort(vid_dets, channelid))

        """ print("send to ass")
        print(type(data)) """
        # Get assistant's response on the data and save it to a json file
        response = eval(data)
        #print("eval in evaluate file -------------------")
        if channel_name not in eval_data:
            eval_data[channel_name] = response
        #print("got ass resp",eval_data)

    return eval_data
    


