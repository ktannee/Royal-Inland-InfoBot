import streamlit as st
from data_loader import load_and_chunk_by_dept
from embeddings import build_all_indices
from rag_pipeline import retrieve_with_routing, generate_answer
from guardrails import pre_answer_guardrails, post_answer_guardrails, extract_contacts
from config import DISCLAIMER

st.set_page_config(page_title="RIH RAG Chatbot (Dept-Routed)", page_icon="🏥")
st.title("🏥 Royal Inland Hospital Chatbot — Dept-Routed RAG")
st.caption(DISCLAIMER)

with st.expander("📥 Build/Refresh Knowledge Base (per department)"):
    st.write("Place docs under `data/hospital_docs/<department>/` then build.")
    if st.button("Build / Rebuild All Indexes"):
        build_all_indices()
        st.success("All available department indexes rebuilt (including global).")

query = st.text_input("Ask a hospital-related question (no personal info):")

if query:
    try:
        contexts, scores, route_reason = retrieve_with_routing(query, k_per_dept=3, max_depts=2)

        # PRE-GUARDRAILS (uses similarity scores)
        allow, msg = pre_answer_guardrails(query, scores)
        if not allow:
            st.warning(msg)
        else:
            phones, flags = extract_contacts(contexts)
            if phones or flags:
                st.markdown("### Answer")
                lines = []
                if flags:
                    lines.append("• Call **{}**".format(",".join(flags)))
                    if phones:
                        lines.append("• Other numbers found: **{}**".format(",".join(phones)))
                    lines.append("• For general health advice in BC: **HealthLink BC at 811**")
                    st.write("\n".join(lines))
            else: 
                answer = generate_answer(query, contexts)
                ok, post_msg = post_answer_guardrails(answer)
                if not ok:
                    st.warning(post_msg)
                else:
                    st.markdown("### Answer")
                    st.write(answer)

            with st.expander("Routing & Sources"):
                st.write(f"**Routing**: {route_reason}")
                for i, (c, s) in enumerate(zip(contexts, scores), 1):
                    st.write(f"**Chunk {i}** (score ~ {s:.2f})")
                    st.write(c[:900] + ("…" if len(c) > 900 else ""))

    except FileNotFoundError:
        st.warning("Indexes not built yet. Open the expander above and click **Build**.")
