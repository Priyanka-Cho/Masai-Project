from fastapi import FastAPI
from app.schemas import AskRequest, AskResponse
from app.graph import run_graph
from app.ingestion import ingest
import os
app = FastAPI(title="Zepto Support Assistant")
@app.on_event("startup")
def startup():
    db_path = os.path.join(os.path.dirname(__file__), "chroma_db")
    if not os.path.exists(db_path) or len(os.listdir(db_path))==0:
        ingest()
@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    return run_graph(req.query)
@app.get("/")
def health():
    return {"status": "ok"}
