import os
import pickle
from pathlib import Path
from typing import Dict, List, Tuple
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from data_loader import load_and_chunk_by_dept

EMB_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
INDEX_DIR = Path("data/indexes")
INDEX_DIR.mkdir(parents=True, exist_ok=True)

def _index_paths(dept: str) -> Tuple[Path, Path]:
    return INDEX_DIR / f"{dept}.faiss", INDEX_DIR / f"{dept}.chunks.pkl"

def build_all_indices():
    model = SentenceTransformer(EMB_MODEL_NAME)
    per_dept_chunks = load_and_chunk_by_dept()

    # also build GLOBAL = union of all chunks
    all_chunks: List[str] = []
    for ch in per_dept_chunks.values():
        all_chunks.extend(ch)
    per_dept_chunks = {"global": all_chunks, **per_dept_chunks}

    for dept, chunks in per_dept_chunks.items():
        if not chunks:
            continue
        embeddings = model.encode(chunks, convert_to_numpy=True, show_progress_bar=True)
        faiss.normalize_L2(embeddings)
        dim = embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(embeddings)

        idx_path, ch_path = _index_paths(dept)
        faiss.write_index(index, str(idx_path))
        with open(ch_path, "wb") as f:
            pickle.dump(chunks, f)

def _load_index_and_chunks(dept: str):
    idx_path, ch_path = _index_paths(dept)
    if not (idx_path.exists() and ch_path.exists()):
        raise FileNotFoundError(f"Index for '{dept}' not found. Build indexes first.")
    index = faiss.read_index(str(idx_path))
    with open(ch_path, "rb") as f:
        chunks = pickle.load(f)
    return index, chunks

def search_in_dept(query: str, dept: str, k: int = 4) -> List[Tuple[str, float]]:
    index, chunks = _load_index_and_chunks(dept)
    model = SentenceTransformer(EMB_MODEL_NAME)
    q_emb = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(q_emb)
    D, I = index.search(q_emb, k)
    results = [(chunks[i], float(D[0][j])) for j, i in enumerate(I[0])]
    return results
