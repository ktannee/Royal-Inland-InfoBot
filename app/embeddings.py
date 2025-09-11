import os
import pickle
from pathlib import Path
from typing import Dict, List, Tuple
from sentence_transformers import SentenceTransformer
import faiss
from data_loader import load_and_chunk_by_dept
from slug import slug

EMB_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
INDEX_DIR = Path("data/indexes")
INDEX_DIR.mkdir(parents=True, exist_ok=True)

def _index_paths(dept: str) -> Tuple[Path, Path]:
    d = slug(dept)
    return INDEX_DIR / f"{d}.faiss", INDEX_DIR / f"{d}.chunks.pkl"

def build_all_indices():
    model = SentenceTransformer(EMB_MODEL_NAME)
    per_dept_chunks = load_and_chunk_by_dept()

    # GLOBAL = union
    all_chunks: List[str] = []
    for ch in per_dept_chunks.values():
        all_chunks.extend(ch)
    per_dept_chunks = {"global": all_chunks, **per_dept_chunks}

    summary = {}
    for dept_raw, chunks in per_dept_chunks.items():
        dept = slug(dept_raw)
        if not chunks:
            summary[dept] = {"chunks": 0, "built": False}
            continue
        emb = model.encode(chunks, convert_to_numpy=True, show_progress_bar=True)
        faiss.normalize_L2(emb)
        index = faiss.IndexFlatIP(emb.shape[1])
        index.add(emb)

        idx_path, ch_path = _index_paths(dept)
        faiss.write_index(index, str(idx_path))
        with open(ch_path, "wb") as f:
            pickle.dump(chunks, f)

        summary[dept] = {"chunks": len(chunks), "built": True}
    return summary

def _load_index_and_chunks(dept: str):
    idx_path, ch_path = _index_paths(dept)  # already slugged
    if not (idx_path.exists() and ch_path.exists()):
        raise FileNotFoundError(f"Index for '{dept}' not found. Build indexes first.")
    index = faiss.read_index(str(idx_path))
    with open(ch_path, "rb") as f:
        chunks = pickle.load(f)
    return index, chunks

def search_in_dept(query: str, dept: str, k: int = 4):
    index, chunks = _load_index_and_chunks(dept)  # dept can be any form; paths are slugged
    model = SentenceTransformer(EMB_MODEL_NAME)
    q_emb = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(q_emb)
    D, I = index.search(q_emb, k)
    return [(chunks[i], float(D[0][j])) for j, i in enumerate(I[0])]