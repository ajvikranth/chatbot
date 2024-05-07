
from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict
from typing import List
from generate import generate, grade_documents, route_question, \
decide_to_generate, grade_generation_v_documents_and_question, not_useful, not_supported
from search import web_search, retrieve
from pprint import pprint


# question = "what is Vanessa Lehr contact info?"
# vec = index(tokenize_en())
# print(retrivalGrader(vec,question))
# gen =generate(vec,question)
# print(gen)
# print(hallucinationGrader(vec,question,gen))



### State


class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        web_search: whether to add search
        documents: list of documents
    """

    question: str
    generation: str
    web_search: str
    tag: str
    documents: List[str]



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

# Test
inputs = {"question": "Can you provide me Vanessa Lehr's contact info?"}
for output in app.stream(inputs):
    for key, value in output.items():
        pprint(f"Finished running: {key}:")
pprint(value.keys())
print(value["generation"],value['documents'])


