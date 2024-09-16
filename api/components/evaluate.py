# Import necessary modules
from .keyword_scraper import kscraper
from .channel_scraper import scrape
from .assistant import eval
from datetime import datetime
from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq
# Global LLM instance
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
        role="Google Sheets expert",
        goal="Write data to google sheets",
        backstory=(
            "You are the best personal assistant that handles influencer analysis data."
        ),
        verbose=False,
        tools=tools,
        llm=llm,
    )
    #format = {"Influencer Name", "Relevance", "Impact", "Winnability, Subscribers", "Frequency", "Views", "Rationale", "partnership_ideas"}
    write_data= Task(
    description=f"Write the input data {eval_data} to a google sheet",
    agent = write_data_a,
    expected_output="Data is written to the sheet and link is shared, end exucution once link is shared",
    config = {
        "input": eval_data
    },
    verbose = False
    )

    my_crew = Crew(agents=[write_data_a], tasks=[write_data], process=Process.sequential)
    result = my_crew.kickoff()
    return result

def main(keyword, channels):
    print("got deets")
    # Get links for the keyword
    links = kscraper(keyword, channels)
    print("got links", links)
    eval_data ={}
    # Iterate over each link
    for link in links:
        # Extract channel name from the link
        channel_name = link.split("@")[-1]
        print(channel_name)
        # Get video details for the channel and save it to a json file
        vid_dets = scrape(link)
        print("got vid deets")
        # Get the channel ID and sort the video data and save
        channelid = list(vid_dets.keys())[0]
        data = str(sort(vid_dets, channelid))

        """ with open(f'data/{keyword}/raw/{channel_name}.json', 'w') as file:
            json.dump(data, file, indent=4) """ 

        print(f"Video data saved to {channel_name}.json") 
        print("send to ass")
        print(type(data))
        # Get assistant's response on the data and save it to a json file
        response = eval(data)
        print("eval in evaluate file -------------------")
        if channel_name not in eval_data:
            eval_data[channel_name] = response
        print("got ass resp",eval_data)
        """ with open(f"data/{keyword}/eval_data.json", "w") as file:
            json.dump(eval_data, file) """
    return eval_data
    


