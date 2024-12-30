import os
from dotenv import load_dotenv
from openai import OpenAI
import time
import logging
import streamlit as st

def load_environment():
    import os
    load_dotenv()


def upload_file_to_openai(filepath, client):
    with open(filepath, "rb") as file:
        response = client.files.create(file=file, purpose="fine-tune")
    return response


def create_assistant(model, file_id, client):
    assistant = client.models.create(name="OpenAI-API-KnowledgeBase-Retrieval-System",
    instructions="""You are a helpful assistant who knows a lot about understanding company's documentation.
        Your role is to summarize papers, clarify terminology within context, and extract key figures and data.
        Cross-reference information for additional insights and answer related questions comprehensively.
        Analyze the papers, noting strengths and limitations.
        Respond to queries effectively, incorporating feedback to enhance your accuracy.
        Handle data securely and update your knowledge base with the latest research.
        Adhere to ethical standards, respect intellectual property, and provide users with guidance on any limitations.
        Maintain a feedback loop for continuous improvement and user support.
        Your ultimate goal is to facilitate a deeper understanding of complex scientific material, making it more accessible and comprehensible.""",
    tools=[{"type": "retrieval"}],
    model=model,
    file_ids=[file_id])
    return assistant

def create_thread(client):
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[{"role": "system", "content": "You are a helpful assistant."}])
    return response

def run_assistant(thread_id, assistant_id, instructions, client):
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": instructions}],
    stream=True,)
    return response

def wait_for_run_completion(thread_id, run_id, client, sleep_interval=5):
    while True:
        try:
            run = client.chat.completions.retrieve(thread_id=thread_id, run_id=run_id)
            if run.status == "completed":
                elapsed_time = run.completed_at - run.created_at
                formatted_elapsed_time = time.strftime(
                    "%H:%M:%S", time.gmtime(elapsed_time)
                )
                print(f"Run completed in {formatted_elapsed_time}")
                logging.info(f"Run completed in {formatted_elapsed_time}")
                messages = client.chat.completions.list(thread_id=thread_id)
                last_message = messages.choices[0].message.content
                print(f"Assistant Response: {last_message}")
                break
        except Exception as e:
            logging.error(f"An error occurred while retrieving the run: {e}")
            break
        logging.info("Waiting for run to complete...")
        time.sleep(sleep_interval)

def main():
    load_environment()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    

    # Step 1: Upload a file to OpenAI embeddings
    filepath = "./FakeDomainDocumentation/Speaking_Band_Descriptors.pdf"
    # file_object
    # upload_file_to_openai(filepath,client)

    # Hardcoded IDs (replace with actual IDs if needed)
    thread_id = "thread_Qt4TBUJcPI1UMsi9uHRyFakh"
    assis_id = "asst_ounYgNZxDByhLFqfmQsb0UJd"

    # Run the assistant with a specific instruction

    # To-do: This part could be parts of the Streamlit app
    question = "What are the criteria for scoring a band 7 in IELTS speaking?"
    instructions = f"Please answer the following question: {question}"

    # Then the app will use the run_assistant function to get the response
    stream = run_assistant(thread_id, assis_id, instructions, client)
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="")
    # ref: https://platform.openai.com/docs/api-reference/streaming

if __name__ == "__main__":
    main()