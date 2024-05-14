'''
this module contains methods to retrieve document from vector database or from website
'''
from langchain_google_community import GoogleSearchAPIWrapper
from langchain_core.tools import Tool
from langchain.schema import Document
from index import Retriever
from langchain_community.document_loaders import AsyncChromiumLoader
from langchain_community.document_transformers import BeautifulSoupTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

import os
from dotenv import load_dotenv



def retrieve(state):
    """
    Retrieve documents from vectorstore

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    print("---RETRIEVE---")
    question = state["question"]

    # Retrieval
    retriever = Retriever() 
    documents = retriever.invoke(question)
    return {"documents": documents, "question": question}


def web_search(state):
    """
    Web search based based on the question

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Appended web results to documents
    """

    print("---WEB SEARCH---")

    load_dotenv()

    cse_id = os.getenv('cse_id')
    api_key = os.getenv('api_key')

    search = GoogleSearchAPIWrapper(google_api_key=api_key ,google_cse_id=cse_id)

    question = state["question"]
    documents = state["documents"]
                
    def top1_results(query):
        return search.results(query, 1)


    web_search_tool = Tool(
        name="Google Search Snippets",
        description="Search Google for recent results.",
        func=top1_results,
    )

    # Web search
    docs = web_search_tool.invoke({"query": question})
    link = docs[0]['link']
    
    loader = AsyncChromiumLoader([link])
    html = loader.load()
    bs_transformer = BeautifulSoupTransformer()
    docs_transformed = bs_transformer.transform_documents(html, tags_to_extract=["p",'span','li','#text'])
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000, chunk_overlap=0
    )
    splits = splitter.split_documents(docs_transformed)
    
    web_results = '\n'.join([str(x) for x in splits])

    web_results = Document(page_content=web_results)
    
    if documents is not None:
        documents.append(web_results)
    else:
        documents = [web_results]
        
    return {"documents": documents, "question": question}

if __name__=="__main__":
    pass