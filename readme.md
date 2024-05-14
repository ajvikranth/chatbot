# Chatbot Application

This repository contains the code for a Retrieval-Augmented Generation (RAG) model-based chatbot application. The chatbot uses LLAMA3 to help students answer queries by orchestrating a flow through various modules and displaying the results on a frontend interface.

## Features

- **Retrieval-Augmented Generation (RAG):** Combines document retrieval and generation to provide accurate and context-aware answers.
- **State Management:** Uses a state graph to manage the flow of data and decisions.
- **Grading and Routing:** Grades documents and routes questions to the appropriate modules.
- **Web Search Integration:** Integrates web search to enhance responses.
- **SQLite Logging:** Logs interactions into an SQLite database.
- **Frontend Interface:** Utilizes Gradio for a user-friendly chat interface.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/ajvikranth/chatbot.git
   cd chatbot


2. **Install the required packages:**

    ```bash
    pipenv install
    pipenv shell

3. **Set up the SQLite database:**

    ```bash
    sqlite3 log.db < schema.sql

3. **Set up the google api key:**

- create a .env file which contains google api key and custom search engine ID as below

api_key = "xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
cse_id = 'xxxxxxxxxxxxxx'

**Note:** install LLAMA3 locally with help of OLAMA

## Usage
1. **Run the application:**

    ```bash
    python app.py

2. **Access the frontend:**

Open your web browser and go to the local URL provided by Gradio (usually http://127.0.0.1:7860).

## Code Overview

**app.py**
This is the main file that orchestrates the LangChain flow and displays the results on the frontend.

- **GraphState Class:** Defines the state passed through each node of the state graph, including the question, generation, tag, web search flag, and documents list.
- **predict Function:** Manages the flow of data through various nodes such as retrieval, web search, grading documents, generation, and final decision making. It logs the final state into an SQLite database and returns the generated response.
- **Gradio Interface:** Launches a Gradio chat interface to interact with the chatbot.

**generate.py**
this file contains all nodes required in langgraph flow

- **generate:** Generate answer using RAG on retrieved documents
- **grade_documents:** Determines whether the retrieved documents are relevant to the question If any document is not relevant, we will
set a flag to run web search
- **route_question:** Route question to web search or RAG
- **decide_to_generate:** Determines whether to generate an answer, or add web search
- **grade_generation_v_documents_and_question:** Determines whether the generation is grounded in the document and answers question.
- **not_useful:** Changes the tag to not useful
- **not_supported:** Changes the tag to not supported

**index.py**
this file contains methods to load ,tokenize and index document into vector database

- **tokenize_en:** reads pdf files and tokenizes them
- **index:** indexes the tokenized documents into vector database
- **Retriever:** pipeline function which tokenizes and indexes pdf

**search.py**
this file contains methods to retrieve document from vector database or from website

- **retrieve:** Retrieve documents from vectorstore
- **web_search:** Web search based based on the question

## Schema
The SQLite database schema is defined in schema.sql and includes a table for logging interactions with the following fields:

- question
- generation
- tag
- web_search
- documents