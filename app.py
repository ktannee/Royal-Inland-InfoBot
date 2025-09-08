# app.py
import streamlit as st
from urllib.parse import urlencode

st.set_page_config(page_title="RIH Demo + Chat", page_icon="🏥", layout="wide")

# ---- Optional: wire up your RAG here ----
def get_answer(user_msg: str) -> str:
    # TODO: replace with your real RAG call, e.g.:
    # from app.rag_pipeline import rag_answer
    # ans, ctx = rag_answer(user_msg, k=4)
    # return ans
    return "Demo reply: this is where your RAG answer would appear."

# ---- Routing by query param ----
params = st.experimental_get_query_params()
mode = params.get("mode", ["site"])[0]

# ================== CHAT MODE ==================
if mode == "chat":
    st.markdown(
        """
        <style>
            .chatwrap { position: relative; height: 100vh; padding: 0 0.5rem 5rem; }
            .chatbox  { height: calc(100vh - 140px); overflow-y: auto; border: 1px solid #ddd; border-radius: 10px; padding: 0.75rem; background: #fff; }
            .inputbar { position: fixed; bottom: 10px; left: 10px; right: 10px; display: flex; gap: .5rem; }
            .msg-user { background:#E8F0FE; padding:.5rem .75rem; border-radius:12px; margin:.25rem 0; }
            .msg-bot  { background:#F1F3F4; padding:.5rem .75rem; border-radius:12px; margin:.25rem 0; }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown("### 🗨️ Hospital Assistant (Demo)")

    if "chat" not in st.session_state:
        st.session_state.chat = [{"role":"assistant","content":"Hi! Ask me about hospital location, lab hours, or visitor info."}]

    with st.container():
        st.markdown('<div class="chatwrap">', unsafe_allow_html=True)
        # history
        st.markdown('<div class="chatbox">', unsafe_allow_html=True)
        for m in st.session_state.chat:
            klass = "msg-bot" if m["role"]=="assistant" else "msg-user"
            st.markdown(f'<div class="{klass}">{m["content"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # input
        with st.form(key="chat_form", clear_on_submit=True):
            st.markdown('<div class="inputbar">', unsafe_allow_html=True)
            user_msg = st.text_input("Message", label_visibility="collapsed", placeholder="Type your question…")
            submitted = st.form_submit_button("Send")
            st.markdown('</div>', unsafe_allow_html=True)

        if submitted and user_msg.strip():
            st.session_state.chat.append({"role":"user","content":user_msg})
            reply = get_answer(user_msg)
            st.session_state.chat.append({"role":"assistant","content":reply})
            st.experimental_rerun()

        st.markdown('</div>', unsafe_allow_html=True)

# ================== SITE MODE (MOCKED HOMEPAGE) ==================
else:
    # Header / hero (keep generic for demo—do not copy brand assets verbatim)
    left, right = st.columns([3,2])
    with left:
        st.markdown("## Royal Inland Hospital — Demo Homepage")
        st.write("Tertiary acute care hospital serving the Thompson–Cariboo–Shuswap region.")
        st.write("Address: 311 Columbia St, Kamloops, BC  •  Phone: (250) 374-5111")
        st.write("This is a demo layout for internal prototyping only (not an official site).")
    with right:
        st.image("https://images.unsplash.com/photo-1586773860418-d37222d8fce3?q=80&w=1200&auto=format&fit=crop")  # generic hospital stock

    st.markdown("---")
    a,b,c = st.columns(3)
    with a:
        st.markdown("### 🧭 Getting Here")
        st.write("Parking, entrances, and tower directions.")
    with b:
        st.markdown("### 🧪 Labs & Imaging")
        st.write("Outpatient lab hours, MRI/CT booking links.")
    with c:
        st.markdown("### 👪 Visitors")
        st.write("Visiting guidelines, amenities, food services.")

    st.markdown("#### News & Alerts (Demo)")
    st.info("⚠️ Example: Temporary changes to maternity services this weekend. For details, ask the chat assistant.")

    # Floating chat widget (button + slide-up panel with iframe to ?mode=chat)
    # We render an HTML block that pins bottom-right and toggles the chat panel with JS.
    query = urlencode({"mode":"chat"})
    chat_url = f"/?{query}"  # same app, different mode

    st.components.v1.html(
        f"""
        <style>
            #chat-fab {{
                position: fixed; z-index: 9999; right: 22px; bottom: 22px;
                width: 58px; height: 58px; border-radius: 50%;
                background: #2563eb; color: white; border: none;
                box-shadow: 0 8px 24px rgba(0,0,0,.2); cursor: pointer;
                display:flex; align-items:center; justify-content:center; font-size:26px;
            }}
            #chat-panel {{
                position: fixed; z-index: 9998; right: 22px; bottom: 90px; width: 380px; height: 520px;
                border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,.25); overflow: hidden;
                display: none; background: #fff;
            }}
            #chat-header {{
                height: 44px; background:#1f2937; color:#fff; display:flex; align-items:center; justify-content:space-between; padding:0 10px; font-family: system-ui, sans-serif;
            }}
            #chat-iframe {{
                width: 100%; height: calc(100% - 44px); border: 0;
            }}
            .chat-close {{
                background: transparent; color: #fff; border: none; font-size: 20px; cursor: pointer;
            }}
            @media (max-width: 480px) {{
                #chat-panel {{ right: 10px; left: 10px; width: auto; height: 70vh; }}
            }}
        </style>

        <div id="chat-panel">
            <div id="chat-header">
                <div>🏥 Hospital Assistant</div>
                <button class="chat-close" onclick="document.getElementById('chat-panel').style.display='none'">✕</button>
            </div>
            <iframe id="chat-iframe" src="{chat_url}" allow="clipboard-read; clipboard-write"></iframe>
        </div>

        <button id="chat-fab" title="Chat">
            💬
        </button>

        <script>
          const fab = document.getElementById('chat-fab');
          const panel = document.getElementById('chat-panel');
          fab.addEventListener('click', () => {{
            panel.style.display = (panel.style.display === 'none' || panel.style.display === '') ? 'block' : 'none';
          }});
        </script>
        """,
        height=620,  # the elements are fixed-position; we don't need vertical space in the layout
    )

