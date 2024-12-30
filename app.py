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

def run_assistant(thread_id, assistant_id, instructions, client):
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": instructions}],
    stream=True,)
    return response

def main():
    load_environment()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    

    # Step 1: Upload a file to OpenAI embeddings
    filepath = "./FakeDomainDocumentation/Speaking_Band_Descriptors.pdf"
    client.files.create(file=open(filepath, "rb"), purpose="assistants")

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