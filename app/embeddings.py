import os
import pickle
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

EMB_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
INDEX_PATH = "data/faiss.index"
CHUNKS_PATH = "data/chunks.pkl"

def build_faiss_index(chunks):
    model = SentenceTransformer(EMB_MODEL_NAME)
    embeddings = model.encode(chunks, convert_to_numpy=True, show_progress_bar=True)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # cosine sim with normalized vectors
    # normalize for cosine similarity
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
    # persist
    with open(CHUNKS_PATH, "wb") as f:
        pickle.dump(chunks, f)
    faiss.write_index(index, INDEX_PATH)

def load_faiss_index():
    if not (os.path.exists(INDEX_PATH) and os.path.exists(CHUNKS_PATH)):
        raise FileNotFoundError("Index not built yet. Run the build step first.")
    index = faiss.read_index(INDEX_PATH)
    with open(CHUNKS_PATH, "rb") as f:
        chunks = pickle.load(f)
    return index, chunks

def search(query, k=4):
    index, chunks = load_faiss_index()
    model = SentenceTransformer(EMB_MODEL_NAME)
    q_emb = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(q_emb)
    D, I = index.search(q_emb, k)
    results = [chunks[i] for i in I[0]]
    return results