"""
This module is the main file which orchestrates langchain flow and displays in frontend
"""

from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict
from typing import List
from generate import generate, grade_documents, route_question, \
decide_to_generate, grade_generation_v_documents_and_question, not_useful, not_supported
from search import web_search, retrieve
from pprint import pprint
import gradio as gr
import sqlite3

### State that is passed through each node of langgraph
class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        tag: tag specifing if the generation is userful, not supported, or not useful 
        web_search: whether to add search
        documents: list of documents
    """

    question: str
    generation: str
    web_search: str
    tag: str
    documents: List[str]


def predict(query,history):
    '''
    returns predicted response from LLM to frontend

    Args:
        query (str): user question
        history (str): user question history

    Returns:
        generation (str): LLM generation
    '''
    workflow = StateGraph(GraphState)

    # Define the nodes
    workflow.add_node("retrieve", retrieve)  # retrieve
    workflow.add_node("websearch", web_search)  # web search
    workflow.add_node("grade_documents", grade_documents)  # grade documents
    workflow.add_node("generate", generate)  # generatae
    workflow.add_node("not_supported", not_supported)
    workflow.add_node("not_useful", not_useful)

    # Build graph
    workflow.set_conditional_entry_point(
        route_question,
        {
            "websearch": "websearch",
            "vectorstore": "retrieve",
        },
    )

    workflow.add_edge("retrieve", "grade_documents")
    workflow.add_conditional_edges(
        "grade_documents",
        decide_to_generate,
        {
            "websearch": "websearch",
            "generate": "generate",
        },
    )
    workflow.add_edge("websearch", "generate")
    workflow.add_conditional_edges(
        "generate",
        grade_generation_v_documents_and_question,
        {
            "not supported": "not_supported",
            "useful": END,
            "not useful":"not_useful",
        },
    )
    workflow.add_edge("not_supported", END)
    workflow.add_edge("not_useful", END)

    # Compile
    app = workflow.compile()

    inputs = {"question": query}
    for output in app.stream(inputs):
        for key, value in output.items():
            pprint(f"Finished running: {key}:")
    
    # Logs the final state into sqlite DB
    conn = sqlite3.connect('log.db')
    sql = ''' INSERT INTO log(question,generation,tag,web_search,documents)
                VALUES(?,?,?,?,?) '''

    task = (value["question"],value["generation"],value["tag"],value["web_search"],value["documents"])
    cur = conn.cursor()
    cur.execute(sql, task)
    conn.commit()

    return value["generation"]

if __name__ == "__main__":
    #frontend 
    gr.ChatInterface(predict).launch()


