from openai import OpenAI
import time


def run_assistant(client, assistant_id, thread_id, data):
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

def eval(data):
  # Init OpenAI client and assistant ID
  client = OpenAI()

  assistant_id = "asst_bntkhaADDPGSwH54ypsd66u5"
  # Create thread or use existing thread
  thread = client.beta.threads.create()
  thread_id = thread.id

  response = run_assistant(client, assistant_id, thread_id, data)

  #print(responseee)

  return response

