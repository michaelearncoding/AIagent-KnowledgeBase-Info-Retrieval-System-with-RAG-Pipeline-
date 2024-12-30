import os
from dotenv import load_dotenv
from openai import OpenAI
import requests
import json

import time
import logging
from datetime import datetime
import streamlit as st


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = "gpt-3.5-turbo"

# Initialize all the session
if "file_id_list" not in st.session_state:
    st.session_state.file_id_list = []

if "start_chat" not in st.session_state:
    st.session_state.start_chat = False

if "vector_store_id_list" not in st.session_state:
    st.session_state.vector_store_id_list = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

if "assistant_id" not in st.session_state:
    st.session_state.assistant_id = None

# Set up our front end page
st.set_page_config(page_title="Study Buddy - Chat and Learn", page_icon=":books:")


# ==== Function definitions etc =====
def upload_to_openai(filepath):
    with open(filepath, "rb") as file:
        response = client.files.create(file=file.read(), purpose="assistants")
    return response.id


def create_vector_store_file(filepath):
    # Create a vector store called "IELTS Documents"
    vector_store = client.beta.vector_stores.create(name="IELTS Documents")

    # Ensure filepath is a single file path string
    with open(filepath, "rb") as file_stream:
        file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id, files=[file_stream]
        )
    return vector_store.id

# === Sidebar - where users can upload files
file_uploaded = st.sidebar.file_uploader(
    "Upload a file to be transformed into embeddings", key="file_upload"
)


# Upload file button - store the file ID
if st.sidebar.button("Upload File"):
    if file_uploaded:
        with open(f"{file_uploaded.name}", "wb") as f:
            f.write(file_uploaded.getbuffer())
        another_file_id = upload_to_openai(f"{file_uploaded.name}")
        st.session_state.file_id_list.append(another_file_id)
        st.sidebar.write(f"File ID:: {another_file_id}")

        
        # 将文件转换为向量存储，并获取向量存储ID
        vector_store_id = create_vector_store_file(f"{file_uploaded.name}")
        st.session_state.vector_store_id_list.append(vector_store_id)
        st.sidebar.write(f"Vector Store ID:: {vector_store_id}")


        # apply file_search tool assistant
        assistant = client.beta.assistants.create(
            name="Document Reader",
            description="You are great at reading the extra document. You analyze content in this file to understand knowledge, and come up with relevant to those trends. You also share a brief text summary of the trends observed.",
            model="gpt-4o",
            tools=[{"type": "file_search"}],
            tool_resources={
                "file_search": {
                    "vector_store_ids": [vector_store_id]
                }
            }
        )
        assis_id = assistant.id # get the assistant ID
        st.session_state.assistant_id = assistant.id
        st.write("Assistant ID:", st.session_state.assistant_id)


# Display those file ids
if st.session_state.file_id_list:
    st.sidebar.write("Uploaded File IDs:")
    for file_id in st.session_state.file_id_list:
        st.sidebar.write(file_id)

# Button to initiate the chat session
if st.sidebar.button("Start Chatting..."):
    if st.session_state.file_id_list:
        st.session_state.start_chat = True

        # Create a new thread for this chat session
        chat_thread = client.beta.threads.create()
        st.session_state.thread_id = chat_thread.id
        st.write("Thread ID:", chat_thread.id)
    else:
        st.sidebar.warning(
            "No files found. Please upload at least one file to get started."
        )


# Define the function to process messages with citations
def process_message_with_citations(message, filename):
    """Extract content and annotations from the message and format citations as footnotes."""
    message_content = message.content[0].text.value
    # message_content = message.content[0].text
    # annotations = (
    #     message_content.annotations if hasattr(message_content, "annotations") else []
    # )
    # annotations = message_content.annotations if hasattr(message_content, "annotations") else []
    annotations = message.content[0].text.annotations if hasattr(message.content[0].text, "annotations") else []

    citations = []

    # Iterate over the annotations and add footnotes
    for index, annotation in enumerate(annotations):
        # Replace the text with a footnote
        # message_content.value = message_content.value.replace(
        #     annotation.text, f" [{index + 1}]"
        # )
        # message_content = message_content.replace(annotation['text'], f" [{index + 1}]")
        message_content = message_content.replace(annotation.text, f" [{index + 1}]")
        # # Gather citations based on annotation attributes
        # if file_citation := getattr(annotation, "file_citation", None):
        #     # Retrieve the cited file details (dummy response here since we can't call OpenAI)
        #     cited_file = {
        #         "filename": "Speaking_Band_Descriptors.pdf"
        #     }  # This should be replaced with actual file retrieval
        #     citations.append(
        #         f'[{index + 1}] {file_citation.quote} from {cited_file["filename"]}'
        #     )
        # elif file_path := getattr(annotation, "file_path", None):
        #     # Placeholder for file download citation
        #     cited_file = {
        #         "filename": "Speaking_Band_Descriptors.pdf"
        #     }  # TODO: This should be replaced with actual file retrieval
        #     citations.append(
        #         f'[{index + 1}] Click [here](#) to download {cited_file["filename"]}'
        #     )  # The download link should be replaced with the actual download path
            
        # Gather citations based on annotation attributes
        if 'file_citation' in annotation:
            file_citation = annotation['file_citation']
            # Retrieve the cited file details
            cited_file = client.files.retrieve(file_citation['file_id'])
            quote = file_citation.get('quote', "No quote available")
            citations.append(f'[{index + 1}] {quote} from {cited_file.filename}')
        elif 'file_path' in annotation:
            file_path = annotation['file_path']
            # Placeholder for file download citation
            cited_file = client.files.retrieve(file_path['file_id'])
            citations.append(f'[{index + 1}] Click [here](#) to download {cited_file.filename}')

    # Add footnotes to the end of the message content
    full_response = message_content + "\n\n" + "\n".join(citations)
    return full_response


# the main interface ...
st.title("Study Buddy")
st.write("Learn fast by chatting with your documents")


# Check sessions
if st.session_state.start_chat:
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-4-1106-preview"
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Show existing messages if any...
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # chat input for the user
    if prompt := st.chat_input("What's new?"):
        # Add user message to the state and display on the screen
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # add the user's message to the existing thread
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id, role="user", content=prompt
        )

        # Create a run with additioal instructions
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id= st.session_state.assistant_id, # assistant.id, assis_id
            instructions="""Please answer the questions using the knowledge provided in the files.
            when adding additional information, make sure to distinguish it with bold or underlined text.""",
        )
# None streaming response method
        # Show a spinner while the assistant is thinking...
        with st.spinner("Wait... Generating response..."):
            while run.status != "completed":
                time.sleep(1)
                # the response retrieve method here is actually against the streamming return methods
                # because it will wait until the response is completed
                # The way to go is to use the stream method to get the response in chunks
                # Rather than waiting for the response to be completed
                run = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id, run_id=run.id
                )
            # Retrieve messages added by the assistant
            messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            )
            # Process and display assis messages - filler the messages by run_id and role
            assistant_messages_for_run = [
                message
                for message in messages
                if message.run_id == run.id and message.role == "assistant"
            ]

            for message in assistant_messages_for_run:
                full_response = process_message_with_citations(message=message, filename=file_uploaded.name)
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )
                with st.chat_message("assistant"):
                    st.markdown(full_response, unsafe_allow_html=True)

# Streaming the response methods:
        # Initialize response_text
        # response_text = ""
            # Create a run with additional instructions
        # run = client.beta.threads.runs.create(
        #     thread_id=st.session_state.thread_id,
        #     assistant_id=st.session_state.assistant_id,  # assis_id,assistant.id
        #     instructions="""Please answer the questions using the knowledge provided in the files.
        #     when adding additional information, make sure to distinguish it with bold or underlined text.""",
        #     stream=True  # use the stream response method
        # )
        # Create a streaming request
        # stream = client.chat.completions.create(
        #     model="gpt-4o",
        #     messages=[{"role": "user", "content": prompt}],
        #     stream=True,
        # )
        # # Show a spinner while the assistant is thinking...
        # with st.spinner("Wait... Generating response..."):
        #     for chunk in stream:
        #         if chunk.choices[0].delta.content is not None:
        #             response_text += chunk.choices[0].delta.content
        #             st.write(response_text)
        # # Retrieve messages added by the assistant
        # messages = client.beta.threads.messages.list(
        #     thread_id=st.session_state.thread_id
        # )
        # # Process and display assistant messages
        # assistant_messages_for_run = [
        #     message
        #     for message in messages
        #     if message.role == "assistant"
        # ]
        # for message in assistant_messages_for_run:
        #     full_response = process_message_with_citations(message=message, filename=file_uploaded.name)
        #     st.session_state.messages.append(
        #         {"role": "assistant", "content": full_response}
        #     )
        #     with st.chat_message("assistant"):
        #         st.markdown(full_response, unsafe_allow_html=True)




    else:
        # Promopt users to start chat
        st.write(
            "Please upload at least a file to get started by clicking on the 'Start Chat' button"
        )