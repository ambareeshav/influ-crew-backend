# Import necessary modules
from .components.keyword_scraper import kscraper
from .components.channel_scraper import cscraper
from .components.assistant import eval as analyze
from crewai import Agent, Task, Crew, Process
from composio_crewai import Action
from composio.utils.logging import setup, LogLevel
import os, litellm, threading, json
import logging
import gc 

# Set logging 
setup(level=LogLevel.ERROR)
logger = logging.getLogger(__name__)

litellm.api_key = os.environ.get("GROQ_API_KEY")

# Main function that takes care of, scraping, analyzing and writing to google sheets.
def data(keyword, channel, tools, spreadsheet_id, assistant_id):

    # Get <keyword> number of channels for 
    links = kscraper(keyword, channel)

    row = 2
    # Iterate over each link
    for link in (links):
        # Init empty dict for storing channel data
        channel_data ={}
        
        # Extract channel name from the link
        channel_name = link.split("@")[-1]

        # Get video details for the channel 
        channel_data = cscraper(link)
        if not channel_data:
            continue

        # Send details to assistant to analyze and store in a dict
        try:
            response = analyze(str(channel_data), assistant_id)
        except Exception as e:
            logger.error(f"ERROR DURING ANALYSIS - {e}")
            continue
        eval_data =  {}
        eval_data[channel_name] = response
        data = json.loads(eval_data[channel_name])

        # Prepare Evaluated data for writing to Google Sheets
        evaluation_list = []
        evaluation_list.append(f"https://www.youtube.com/@{channel_name}")
        evaluation_list.append(channel_name)
        for key, value in data.items():
            if isinstance(value, dict) and "Evaluation" in value:
                evaluation_list.append(str(value["Evaluation"]))  
            elif key == "Subscribers":
                evaluation_list.append(str(value))  
            elif key == "Rationale":
                evaluation_list.append(value)  
            elif key == "partnership_ideas":
                partnership_ideas_str = "; ".join(value) if isinstance(value, list) else value
                evaluation_list.append(partnership_ideas_str)
        
        config = {
            "validation": {
                "ensure_valid_input": True,  # Validate input before passing to the tool
                "log_input_on_info": True    # Log the input if an info occurs
            },
            "retry": {
                "max_attempts": 3,           # Retry the task in case of failure
                "backoff_factor": 2          # Exponential backoff in retrying the task
            }
            }
        
        write_data_agent = Agent(
            role="Google Sheets Manager",
            goal="Write influencer evaluation data to a google sheet",
            backstory="You are responsible for writing data to Google Sheets as part of an influencer evaluation system. Given a list and google sheets information you will write the list to it",
            verbose=False,
            tools=tools,
            llm = "groq/llama3-70b-8192",
            cache = False
        )
    
        write_task = Task(
            description=f"""
            1. The data provided is already formatted and ready to write, DO NOT ALTER IT, your only task is to write to google sheets using the Action.GOOGLESHEETS_BATCH_UPDATE tool
            2. Write the entire list {evaluation_list} to {row} of the google sheet with SpreadshetId {spreadsheet_id}, all the data should be in one row. Do not modify the list in any way unless specified, write it as is.
            3. The first element of {evaluation_list} should be always be in A{row}
            4. The following are the only fields you must include in the Tool Input:
                "spreadsheet_id": "",
                "sheet_name": "Sheet1",
                "values": [],
                "first_cell_location": ""
                DO NOT INCLUDE includeValuesInResponse IN THE TOOL INPUT INPUT
            """,
            agent=write_data_agent,
            expected_output="Input data is written to given row in the given spreadsheet",
            verbose=False,
            config = config
        )
        
        # Run the crew
        write_crew = Crew(agents=[ write_data_agent], tasks=[write_task], process= Process.sequential)
        write_crew.kickoff()
        row+=1
        
        # Cleanup video data from memory after processing
        del eval_data
        del response
        gc.collect()  # Garbage collection to free memory
    
def run(keyword, channels, toolset, assistant_id):
    composio_tools = toolset.get_tools(actions=[Action.GOOGLESHEETS_CREATE_GOOGLE_SHEET1, Action.GOOGLESHEETS_BATCH_UPDATE])

    # Create a google sheet
    sheet_header_agent = Agent(
        role="Google Sheets Manager",
        goal="Create a Google Sheet and write header data to it",
        backstory="You are responsible for managing data in Google Sheets for an influencer evaluation system.",
        verbose=False,
        tools=composio_tools,
        llm="groq/llama3-70b-8192"
    )

    create_and_write_task = Task(
        description= 
     f"""1. Create a new Google Sheet named {keyword}.
        2. Extract the 'spreadsheet_id' from the creation response.
        3. Write the following header row to the sheet as first row:["Channel", "Influencer Name", "Relevance", "Impact", "Winnability", "Subscribers", "Frequency", "Views", "Rationale", "partnership_ideas"]
        4. After writing header data your response must be a link that the user can click to go the created spreadsheet """
        ,
        agent=sheet_header_agent,
        expected_output="Spreadsheet link is returned",
        verbose=False
    )
    
    my_crew = Crew(agents=[sheet_header_agent], tasks=[create_and_write_task], process=Process.sequential)
    link = my_crew.kickoff()
    
    # Extract spreadhseet id from sheet link
    spreadsheet_id = link.raw.split('/d/')[1].split('/')[0]

    composio_tools = toolset.get_tools(actions=[Action.GOOGLESHEETS_BATCH_UPDATE])

    # Return the sheet link first then start proccess, removes the need to wait for analysis to complete to view them.
    data_thread = threading.Thread(target=data, args=(keyword, channels, composio_tools, spreadsheet_id, assistant_id))
    data_thread.start()
    return link
