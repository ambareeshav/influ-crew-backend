from openai import OpenAI
from dotenv import load_dotenv
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
import time, os, logging, gc

logging.basicConfig(level=logging.ERROR)  
logger = logging.getLogger(__name__)

load_dotenv()
OPENAI_API_KEY = os.environ.get("ASSISTANT_KEY")

@retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(5), retry=retry_if_exception_type(Exception))
def run_assistant(client, assistant_id, thread_id, data):

  # Create message in the thread
  message = client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=data
  )

  # Run the thread and poll for completion
  run = client.beta.threads.runs.create_and_poll(
    thread_id=thread_id,
    assistant_id=assistant_id
  )

  # Wait until the run is completed
  while run.status != 'completed':
    time.sleep(1)

  # Retrieve the messages from the thread
  messages = client.beta.threads.messages.list(thread_id=thread_id)
  return messages.data[0].content[0].text.value


def eval(data, id):
  # Init OpenAI client and assistant ID
  client = OpenAI(api_key = OPENAI_API_KEY)

  # Create thread 
  thread = client.beta.threads.create()
  thread_id = thread.id

  response = run_assistant(client, id, thread_id, data)

  gc.collect()

  return response

