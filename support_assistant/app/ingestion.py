import os
import chromadb
import hashlib
DOCS_DIR = os.path.join(os.path.dirname(__file__), "../docs")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "../chroma_db")
COLLECTION_NAME = "zepto_policies"
def load_docs():
    chunks = []
    for i in range(1,9):
        path = os.path.join(DOCS_DIR, f"doc_0{i}.txt")
        with open(path, "r", encoding="utf-8") as f:
            text = f.read().strip()
            chunks.append({"id": f"doc_0{i}", "text": text, "source": f"doc_0{i}.txt"})
    return chunks
def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    return client.get_or_create_collection(name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"})
def dummy_embed(texts):
    embeddings = []
    for t in texts:
        h = hashlib.sha256(t.encode()).digest()
        vec = [float(b)/255.0 for b in h * 12][:384]
        embeddings.append(vec)
    return embeddings
def ingest():
    chunks = load_docs()
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    try:
        client.delete_collection(COLLECTION_NAME)
    except:
        pass
    collection = client.create_collection(name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"})
    ids = [c["id"] for c in chunks]
    texts = [c["text"] for c in chunks]
    embeddings = dummy_embed(texts)
    collection.add(ids=ids, documents=texts, embeddings=embeddings, metadatas=[{"source": c["source"]} for c in chunks])
    print(f"Ingested {len(chunks)} docs")
    return collection
