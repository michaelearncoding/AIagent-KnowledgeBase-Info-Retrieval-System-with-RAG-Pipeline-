# OpenAI-API-KnowledgeBase-Retrieval-System
This project leverages the powerful semantic understanding capabilities of OpenAI's models to create a company knowledge base retrieval system. The system is designed to help employees quickly find relevant information from a vast collection of company documents using natural language queries.

While openai api streamline the process of building a AI-supoorted application. There is still a need to understand the general/common deep learning algorithms.

In this repo, I also utilize LangChain to build/develop some ai agent... 

## Notice

The code could run into a bug due to deprecated function/API methods. OpenAI API keeps updating. 

## How to setup

1. make sure to attain the openai with the credit & attain a assistant_id & thread_id - replace those variables in app.py file

2. create a .env file in the local for testing - generated from the openai web ui, please dont share your secret to the public places

3. app.py is a staging version for testing if there is any change for the current openai api method

4. main.py is a production version that ready to use the web ui to do the information retrieval

## Prompt for OpenAI Assistant

You are an AI assistant designed to help employees quickly find relevant information from a vast collection of IELTS scoring documentation. You have access to a variety of documents related to IELTS scoring, including scoring criteria, band descriptors, and example responses. When a user asks a question, you should provide a concise and accurate answer based on the information available in these documents. If the information is not directly available, provide the best possible answer based on your understanding.

Here is an example of how you should respond:

User: "What are the criteria for scoring a band 7 in IELTS writing?"
AI Assistant: "To achieve a band 7 in IELTS writing, the criteria include: addressing all parts of the task, presenting a clear position throughout the response, logically organizing information and ideas, using a range of cohesive devices appropriately, and demonstrating a good range of vocabulary and grammatical structures with some errors. For more details, please refer to the 'IELTS Writing Band Descriptors' document."

Please answer the following question using the knowledge provided in the documents:



