import os
from typing import List, Tuple
from huggingface_hub import hf_hub_download
from llama_cpp import Llama
from router import route_departments
from embeddings import search_in_dept
from config import LOW_CONF_FALLBACK
from guardrails import pre_answer_guardrails
from config import RETRIEVAL_SIM_THRESHOLD

REPO_ID = "TheBloke/Mistral-7B-Instruct-v0.2-GGUF"
FNAME   = "mistral-7b-instruct-v0.2.Q4_K_M.gguf"
MODEL_PATH = os.path.join("models", FNAME)

def ensure_model():
    os.makedirs("models", exist_ok=True)
    if not os.path.exists(MODEL_PATH):
        hf_hub_download(repo_id=REPO_ID, filename=FNAME, local_dir="models")
    return MODEL_PATH

def load_llm(n_ctx=4096, n_threads=8):
    model_path = ensure_model()
    return Llama(model_path=model_path, n_ctx=n_ctx, n_threads=n_threads, verbose=False)

SYS_PROMPT = (
    "You are a helpful hospital assistant for Royal Inland Hospital (RIH). "
    "Only answer using facts present in the provided CONTEXT. "
    "If the answer is not fully supported by the context, say you don't know and suggest official channels. "
    "Never provide medical advice or interpret personal health information."
)

def format_prompt(question: str, contexts: List[str]) -> str:
    joined = "\n\n---\n\n".join(contexts)
    return f"""[SYSTEM]
{SYS_PROMPT}

[CONTEXT]
{joined}

[USER QUESTION]
{question}

[ASSISTANT]
"""

def retrieve_with_routing(question: str, k_per_dept: int = 3, max_depts: int = 2) -> Tuple[List[str], List[float], str]:
    """
    Route to top departments, search each, then merge results (by score).
    Fallback to 'global' if routing returns only 'global'.
    """
    depts, reason = route_departments(question, top_k=max_depts)
    pairs = []
    for d in depts:
        try:
            pairs.extend(search_in_dept(question, d, k=k_per_dept))
        except FileNotFoundError:
            # index not built for that dept — skip silently
            continue

    # if nothing meaningful, try global explicitly
    if not pairs:
        try:
            pairs.extend(search_in_dept(question, "global", k=k_per_dept))
            reason += " | Used global as fallback."
        except FileNotFoundError:
            pass

    # sort by score desc and dedupe text
    pairs = sorted(pairs, key=lambda x: x[1], reverse=True)
    seen = set()
    contexts, scores = [], []
    for c, s in pairs:
        if c not in seen:
            contexts.append(c)
            scores.append(s)
            seen.add(c)
        if len(contexts) >= 4:
            break
    return contexts, scores, reason

def generate_answer(question: str, contexts: List[str], max_tokens=512, temperature=0.1) -> str:
    prompt = format_prompt(question, contexts)
    llm = load_llm()
    out = llm(
        prompt, max_tokens=max_tokens, temperature=temperature,
        top_p=0.9, stop=["[USER QUESTION]", "[SYSTEM]"]
    )
    return out["choices"][0]["text"].strip()
