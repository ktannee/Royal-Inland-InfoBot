import os
from huggingface_hub import hf_hub_download
from llama_cpp import Llama
from embeddings import search_with_scores

# Choose a free, widely used instruct model in GGUF format
# Good pick: TheBloke/Mistral-7B-Instruct-v0.2-GGUF (Q4_K_M works on CPU)
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
    llm = Llama(
        model_path=model_path,
        n_ctx=n_ctx,
        n_threads=n_threads,  # tune for your CPU
        verbose=False,
        # you can add "n_gpu_layers" if you have GPU
    )
    return llm

SYS_PROMPT = (
    "You are a helpful hospital assistant for Royal Inland Hospital (RIH). "
    "Only answer using facts present in the provided CONTEXT. "
    "If the answer is not fully supported by the context, say you don't know and suggest official channels. "
    "Never provide medical advice or interpret personal health information."
)

def format_prompt(question, contexts):
    joined = "\n\n---\n\n".join(contexts)
    return f"""[SYSTEM]
{SYS_PROMPT}

[CONTEXT]
{joined}

[USER QUESTION]
{question}

[ASSISTANT]
"""

# def rag_answer(question, k=4, max_tokens=512, temperature=0.1):
#     contexts = search(question, k=k)
#     prompt = format_prompt(question, contexts)
#     llm = load_llm()

#     out = llm(
#         prompt,
#         max_tokens=max_tokens,
#         temperature=temperature,
#         top_p=0.9,
#         stop=["[USER QUESTION]", "[SYSTEM]"]
#     )
#     text = out["choices"][0]["text"].strip()
#     return text, contexts


def retrieve(question, k=4):
    pairs = search_with_scores(question, k=k)
    ctx = [c for c, s in pairs]
    scores = [s for c, s in pairs]
    return ctx, scores

def generate_answer(question, contexts, max_tokens=512, temperature=0.1):
    prompt = format_prompt(question, contexts)
    llm = load_llm()
    out = llm(
        prompt, max_tokens=max_tokens, temperature=temperature,
        top_p=0.9, stop=["[USER QUESTION]", "[SYSTEM]"]
    )
    return out["choices"][0]["text"].strip()