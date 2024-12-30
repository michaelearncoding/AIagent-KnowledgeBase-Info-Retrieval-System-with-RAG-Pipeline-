import os
from dotenv import load_dotenv
import openai
import time
import logging
import streamlit as st

def load_environment():
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

def initialize_openai_client():
    return openai.OpenAI()

def upload_file_to_openai(client, filepath):
    with open(filepath, "rb") as file:
        response = client.files.create(file=file.read(), purpose="assistants")
    return response

def create_assistant(client, model, file_id):
    assistant = client.beta.assistants.create(
        name="OpenAI-API-KnowledgeBase-Retrieval-System",
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
        file_ids=[file_id],
    )
    return assistant

def create_thread(client):
    thread = client.beta.threads.create()
    return thread

def run_assistant(client, thread_id, assistant_id, instructions):
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions=instructions,
    )
    return run

def wait_for_run_completion(client, thread_id, run_id, sleep_interval=5):
    while True:
        try:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            if run.completed_at:
                elapsed_time = run.completed_at - run.created_at
                formatted_elapsed_time = time.strftime(
                    "%H:%M:%S", time.gmtime(elapsed_time)
                )
                print(f"Run completed in {formatted_elapsed_time}")
                logging.info(f"Run completed in {formatted_elapsed_time}")
                messages = client.beta.threads.messages.list(thread_id=thread_id)
                last_message = messages.data[0]
                response = last_message.content[0].text.value
                print(f"Assistant Response: {response}")
                break
        except Exception as e:
            logging.error(f"An error occurred while retrieving the run: {e}")
            break
        logging.info("Waiting for run to complete...")
        time.sleep(sleep_interval)

def main():
    load_environment()
    client = initialize_openai_client()
    model = "gpt-3.5-turbo"

    # Step 1: Upload a file to OpenAI embeddings
    filepath = "./FakeDomainDocumentation/Speaking_Band_Descriptors.pdf"
    file_object = upload_file_to_openai(client, filepath)

    # Step 2: Create an assistant (uncomment if needed)
    # assistant = create_assistant(client, model, file_object.id)
    # assis_id = assistant.id
    # print(f"Assistant ID: {assis_id}")

    # Step 3: Create a thread (uncomment if needed)
    # thread = create_thread(client)
    # thread_id = thread.id
    # print(f"Thread ID: {thread_id}")

    # Hardcoded IDs (replace with actual IDs if needed)
    thread_id = "thread_Qt4TBUJcPI1UMsi9uHRyFakh"
    assis_id = "asst_ounYgNZxDByhLFqfmQsb0UJd"

    # Run the assistant with a specific instruction
    question = "What are the criteria for scoring a band 7 in IELTS speaking?"
    instructions = f"Please answer the following question: {question}"
    run = run_assistant(client, thread_id, assis_id, instructions)
    wait_for_run_completion(client, thread_id, run.id)

    # Check the run steps - logs
    run_steps = client.beta.threads.runs.steps.list(thread_id=thread_id, run_id=run.id)
    print(f"Run Steps --> {run_steps.data[0]}")

if __name__ == "__main__":
    main()