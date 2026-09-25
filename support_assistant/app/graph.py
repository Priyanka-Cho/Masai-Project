import os
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from app.ingestion import get_collection, dummy_embed
from app.schemas import AskResponse
IS_MOCK = os.getenv("MOCK_LLM", "1")!= "0"
class GraphState(TypedDict):
    query: str
    intent: str
    answer: str
    sources: List[str]
    confidence: float
    retrieved_chunks: List[dict]
KEYWORDS = ["delivery", "return", "refund", "membership", "tracking", "cancel", "gift card", "support hours"]
def classify_intent(state: GraphState):
    ql = state["query"].lower()
    intent = "general_question"
    for kw in KEYWORDS:
        if kw in ql:
            intent = "policy_question"
            break
    state["intent"] = intent
    return state
def retrieve_and_answer(state: GraphState):
    collection = get_collection()
    q_emb = dummy_embed([state["query"]])
    results = collection.query(query_embeddings=q_emb, n_results=3)
    docs = results["documents"][0]
    ids = results["ids"][0]
    retrieved = [{"id": ids[i], "text": docs[i]} for i in range(len(docs))]
    state["retrieved_chunks"] = retrieved
    top = retrieved[0]["text"] if retrieved else ""
    state["answer"] = f"Based on the retrieved context: {top[:200]}"
    state["sources"] = ids
    state["confidence"] = 1.0
    return state
def direct_answer(state: GraphState):
    state["answer"] = "I can only answer questions about Zepto policies right now."
    state["sources"] = []
    state["confidence"] = 1.0
    return state
def route_intent(state: GraphState):
    return "retrieve_and_answer" if state["intent"] == "policy_question" else "direct_answer"
workflow = StateGraph(GraphState)
workflow.add_node("classify_intent", classify_intent)
workflow.add_node("retrieve_and_answer", retrieve_and_answer)
workflow.add_node("direct_answer", direct_answer)
workflow.set_entry_point("classify_intent")
workflow.add_conditional_edges("classify_intent", route_intent, {"retrieve_and_answer": "retrieve_and_answer", "direct_answer": "direct_answer"})
workflow.add_edge("retrieve_and_answer", END)
workflow.add_edge("direct_answer", END)
graph_app = workflow.compile()
def run_graph(query: str) -> AskResponse:
    initial = {"query": query, "intent": "", "answer": "", "sources": [], "confidence": 0.0, "retrieved_chunks": []}
    final = graph_app.invoke(initial)
    return AskResponse(answer=final["answer"], sources=final["sources"], confidence=final["confidence"])
