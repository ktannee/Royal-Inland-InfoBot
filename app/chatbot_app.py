import streamlit as st
from data_loader import load_raw_texts, chunk_texts
from embeddings import build_faiss_index
from rag_pipeline import rag_answer

st.set_page_config(page_title="RIH RAG Chatbot (Open-Source)", page_icon="🏥")
st.title("🏥 Royal Inland Hospital Chatbot — Open Source MVP")

with st.expander("📥 One-time: Build/Refresh Knowledge Base"):
    st.write("Add .html/.pdf/.txt into `data/hospital_docs` and click Build.")
    if st.button("Build / Rebuild Index"):
        texts = load_raw_texts("data/hospital_docs")
        if not texts:
            st.error("No documents found in data/hospital_docs")
        else:
            chunks = chunk_texts(texts)
            build_faiss_index(chunks)
            st.success(f"Indexed {len(chunks)} chunks.")

query = st.text_input("Ask a question about Royal Inland Hospital:")

if query:
    try:
        answer, ctx = rag_answer(query, k=4)
        st.markdown("### Answer")
        st.write(answer)
        with st.expander("Sources (retrieved context)"):
            for i, c in enumerate(ctx, 1):
                st.write(f"**Chunk {i}:**")
                st.write(c[:800] + ("…" if len(c) > 800 else ""))
    except FileNotFoundError:
        st.warning("Index not built yet. Open the expander above and click Build.")

