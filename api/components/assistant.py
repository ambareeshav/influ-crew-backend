from openai import OpenAI
import time, os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.ERROR)  
logger = logging.getLogger(__name__)

load_dotenv()
OPENAI_API_KEY = os.environ.get("ASSISTANT_KEY")

def run_assistant(client, assistant_id, thread_id, data):
  try:
    #Create message in the thread
    message = client.beta.threads.messages.create(
      thread_id=thread_id,
      role="user",
      content=data
    )
    #Run the thread and poll for completion
    run = client.beta.threads.runs.create_and_poll(
      thread_id=thread_id,
      assistant_id=assistant_id
    )
    #wait until the run is completed
    while run.status != 'completed':
      time.sleep(1)

    #Retrieve the messages from the thread
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    return messages.data[0].content[0].text.value
  
  except Exception as e:
    logging.error(f"ERROR DURING ANALYSIS - {e}")
    return None

def eval(data, id):
  # Init OpenAI client and assistant ID
  client = OpenAI(api_key = OPENAI_API_KEY)
  if id == None:
    assistant_id = "asst_bntkhaADDPGSwH54ypsd66u5"
  else:
    assistant_id = id
  # Create thread or use existing thread
  thread = client.beta.threads.create()
  thread_id = thread.id

  response = run_assistant(client, assistant_id, thread_id, data)

  return response

