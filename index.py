'''
this module contains methods to load ,tokenize and index document into vector database
'''

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_community.document_loaders import PDFPlumberLoader
import os
  
# creating a pdf reader object 
def tokenize_en():
    '''
    reads pdf files and tokenizes them

    Returns:
        doc_splits (list): list of tokenized doc
    '''

    cwd = os.path.join(os.getcwd(),'doc/english')
    for file in os.listdir(cwd):
        loader = PDFPlumberLoader(os.path.join(cwd,file))
        docs = loader.load_and_split()

        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=1000, chunk_overlap=0
        )
        doc_splits = text_splitter.split_documents(docs)

        return doc_splits


def index(doc_splits):
    '''
    indexes the tokenized documents into vector database

    Args:
        doc_splits (list): list of tokenized doc

    Returns:
        retriever (method): vector store retriver method
    '''
    # Add to vectorDB
    vectorstore = Chroma.from_documents(
        documents=doc_splits,
        collection_name="rag-chroma",
        embedding=GPT4AllEmbeddings(),
        persist_directory = 'db/'
    )
    retriever = vectorstore.as_retriever()

    return retriever

def Retriever():
    '''
    datapipeline which tokenizes and indexes pdf

    Returns:
        retriever (method): vector store retriver method
    '''
    return index(tokenize_en())

if __name__=="__main__":
    pass
    
