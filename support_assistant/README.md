# Zepto Support Assistant - Module 3
## Architecture Description - RAG Pipeline
Flow: ingestion -> embedding -> retrieval -> generation
1. Ingestion (app/ingestion.py:load_docs()): Loads 8 txt files from docs/, per-document chunking (1 doc = 1 chunk). Function load_docs() handles it.
2. Embedding (app/ingestion.py:ingest()): Uses sentence-transformers/all-MiniLM-L6-v2 locally via SentenceTransformer.encode(). No API needed. For Colab Python 3.13 demo, uses deterministic dummy hash embedding to avoid numpy 2.x compatibility issue; Docker image (python:3.10-slim) uses real MiniLM.
3. Storage: ChromaDB PersistentClient at./chroma_db, collection zepto_policies, cosine similarity (hnsw:space=cosine).
4. Retrieval (app/graph.py:retrieve_and_answer node): Embeds query with same model, queries ChromaDB top-3 via collection.query(). ALWAYS runs real in both modes.
5. Generation: classify_intent routes via conditional edge, retrieve_and_answer generates grounded answer, direct_answer handles general queries. Routing does NOT depend on MOCK_LLM, only generation inside nodes does.
MOCK_LLM Toggle: Default MOCK_LLM=1 (graded baseline): No LLM call. classify uses keyword heuristic (delivery, return, refund, membership, tracking, cancel, gift card, support hours). retrieve_and_answer returns Based on retrieved context + top_chunk[:200]. direct_answer returns fixed canned string. Pydantic populated deterministically. Optional MOCK_LLM=0: Uses Groq llama3-8b-8192, uses structured prompt template from prompt_template.py (role/context/task/format/length + negative constraint + few-shot), includes retry 2 times logic on validation failure.
Diagram: [User Query] -> [classify_intent] --conditional edge--> policy_question -> [retrieve_and_answer: Chroma top-3 -> Mock template OR LLM] / general_question -> [direct_answer: canned OR LLM] -> [AskResponse]
## Local Run
pip install -r requirements.txt
python -m app.ingestion
MOCK_LLM=1 uvicorn main:app --host 0.0.0.0 --port 7860
Docker: docker build -t zepto-support. / docker run -p 7860:7860 -e MOCK_LLM=1 zepto-support
## Example Calls - MOCK_LLM=1 (Graded Baseline)
Example 1 - Policy question - routes to retrieve_and_answer: Request: {"query": "What is the delivery fee for orders below 149?"} Response: {"answer": "Based on the retrieved context: Zepto delivers grocery and household essentials to serviceable pin codes within 10 to 30 minutes of order confirmation...", "sources": ["doc_01", "doc_03", "doc_05"], "confidence": 1.0}
Example 2 - General question - routes to direct_answer: Request: {"query": "Tell me a joke about groceries"} Response: {"answer": "I can only answer questions about Zepto policies right now.", "sources": [], "confidence": 1.0}
