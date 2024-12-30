import os
from dotenv import load_dotenv
from openai import OpenAI
import time
import logging
import streamlit as st
import jsonlines
from PyPDF2 import PdfReader


def load_environment():
    import os
    load_dotenv()

# Only needed when it's a batch query
''' 
The OpenAI API provides the ability to stream responses back to a client in order to allow partial results for certain requests. To achieve this, we follow the Server-sent events standard. Our official Node and Python libraries include helpers to make parsing these events simpler.
'''
# def upload_file_to_openai(filepath,client, token):
#     import requests
#     url = "https://api.openai.com/v1/files"
#     headers = {
#         "Authorization": f"Bearer {token}",
#     }
#     files = {
#         "file": (os.path.basename(filepath), open(filepath, "rb")),
#         "purpose": (None, "fine-tune")
#     }
#     response = requests.post(url, headers=headers, files=files)
#     response.raise_for_status()  # Raise an error for bad status codes
#     return response.json()

# def create_assistant(model, file_id, client):
#     assistant = client.models.create(name="OpenAI-API-KnowledgeBase-Retrieval-System",
#     instructions="""You are a helpful assistant who knows a lot about understanding company's documentation.
#         Your role is to summarize papers, clarify terminology within context, and extract key figures and data.
#         Cross-reference information for additional insights and answer related questions comprehensively.
#         Analyze the papers, noting strengths and limitations.
#         Respond to queries effectively, incorporating feedback to enhance your accuracy.
#         Handle data securely and update your knowledge base with the latest research.
#         Adhere to ethical standards, respect intellectual property, and provide users with guidance on any limitations.
#         Maintain a feedback loop for continuous improvement and user support.
#         Your ultimate goal is to facilitate a deeper understanding of complex scientific material, making it more accessible and comprehensible.""",
#     tools=[{"type": "retrieval"}],
#     model=model,
#     file_ids=[file_id])
#     return assistant

# def create_thread(client):
#     response = client.chat.completions.create(model="gpt-3.5-turbo",
#     messages=[{"role": "system", "content": "You are a helpful assistant."}])
#     return response

def run_assistant(thread_id, assistant_id, instructions, client):
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": instructions}],
    stream=True,)
    return response

# def wait_for_run_completion(thread_id, run_id, client, sleep_interval=5):
#     while True:
#         try:
#             run = client.chat.completions.retrieve(thread_id=thread_id, run_id=run_id)
#             if run.status == "completed":
#                 elapsed_time = run.completed_at - run.created_at
#                 formatted_elapsed_time = time.strftime(
#                     "%H:%M:%S", time.gmtime(elapsed_time)
#                 )
#                 print(f"Run completed in {formatted_elapsed_time}")
#                 logging.info(f"Run completed in {formatted_elapsed_time}")
#                 messages = client.chat.completions.list(thread_id=thread_id)
#                 last_message = messages.choices[0].message.content
#                 print(f"Assistant Response: {last_message}")
#                 break
#         except Exception as e:
#             logging.error(f"An error occurred while retrieving the run: {e}")
#             break
#         logging.info("Waiting for run to complete...")
#         time.sleep(sleep_interval)

def main():
    load_environment()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    

    # Step 1: Upload a file to OpenAI embeddings
    filepath = "./FakeDomainDocumentation/Speaking_Band_Descriptors.pdf"
    client.files.create(file=open(filepath, "rb"), purpose="assistants")
    # only needed when it's a streaming fine-tune api
    # token =os.getenv("OPENAI_API_KEY")
    # upload_file_to_openai(filepath,client, token)

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


# def pdf_to_jsonl(pdf_filepath, jsonl_filepath):
#     with open(pdf_filepath, "rb") as pdf_file:
#         reader = PdfReader(pdf_file)
#         num_pages = len(reader.pages)
#         with jsonlines.open(jsonl_filepath, mode='w') as writer:
#             for page_num in range(num_pages):
#                 page = reader.pages[page_num]
#                 text = page.extract_text()
#                 writer.write({"text": text})

if __name__ == "__main__":

    # Convert PDF to JSONL if the streaming is needed
    # pdf_filepath = "./FakeDomainDocumentation/Speaking_Band_Descriptors.pdf"
    # jsonl_filepath = "./FakeDomainDocumentation/Speaking_Band_Descriptors.jsonl"
    # pdf_to_jsonl(pdf_filepath, jsonl_filepath)
    # print(f"Converted {pdf_filepath} to {jsonl_filepath}")

    main()