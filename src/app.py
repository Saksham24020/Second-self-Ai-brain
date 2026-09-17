# src/app.py
"""Streamlit interface for SecondSelf Knowledge Base.

A clean, human-centered second brain interface:
- Tab 1: 🔮 Ask SecondSelf (Natural language Q&A with Groq LLM & vector search)
- Tab 2: 📥 Add Knowledge (Upload documents, scrape web pages, save thoughts)
- Tab 3: 🗂️ Manage Vault (Review notes with clean reader canvas, direct web links, and easy deletion)
- Tab 4: 🗺️ Knowledge Graph (Interactive network visualization)
- Tab 5: ⚙️ System & Settings (Technical configuration tucked away)
"""

import sys
from pathlib import Path
import streamlit as st

# Ensure project root is in sys.path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Ensure UTF-8 console output on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.ask import ask_with_sources
from src.config import settings
import importlib
import src.manager
importlib.reload(src.manager)

from src.manager import (
    ingest_content,
    delete_capture,
    get_all_captures,
    rebuild_index_and_graph,
    get_capture_details,
    derive_clean_title,
)
from src.embeddings.indexer import _load_index_and_metadata

st.set_page_config(
    page_title="SecondSelf | AI Second Brain",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Premium 3D Styling, Deep Shadowing & Tactile Micro-Interactions
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* 3D App Header */
    .header-container {
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    }
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 0.2rem;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline-block;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #94a3b8;
        font-weight: 400;
        margin-top: 0.2rem;
    }

    /* 3D Tabs Navigation Container */
    [data-testid="stTabs"] div[role="tablist"],
    div[data-baseweb="tab-list"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
        border-radius: 16px !important;
        padding: 8px 12px !important;
        gap: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.7), 0 10px 25px -5px rgba(0, 0, 0, 0.5) !important;
        margin-bottom: 2rem !important;
        display: flex !important;
        flex-wrap: wrap !important;
    }

    [data-testid="stTabs"] div[data-baseweb="tab-highlight"],
    [data-testid="stTabs"] div[data-baseweb="tab-border"],
    div[data-baseweb="tab-highlight"],
    div[data-baseweb="tab-border"] {
        display: none !important;
    }

    /* Individual 3D Tabs */
    [data-testid="stTabs"] button[role="tab"],
    button[data-baseweb="tab"] {
        background: linear-gradient(180deg, #273549 0%, #172131 100%) !important;
        color: #94a3b8 !important;
        border-radius: 12px !important;
        padding: 11px 26px !important;
        font-weight: 700 !important;
        font-size: 0.96rem !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.15), 0 4px 10px rgba(0, 0, 0, 0.35) !important;
        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
    }

    [data-testid="stTabs"] button[role="tab"]:hover,
    button[data-baseweb="tab"]:hover {
        color: #ffffff !important;
        background: linear-gradient(180deg, #334155 0%, #1e293b 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.25), 0 8px 18px rgba(0, 0, 0, 0.45) !important;
        border-color: rgba(56, 189, 248, 0.4) !important;
    }

    [data-testid="stTabs"] button[role="tab"][aria-selected="true"],
    button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(180deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        border: 1px solid #38bdf8 !important;
        box-shadow: inset 0 1px 2px rgba(255, 255, 255, 0.5), 0 8px 24px rgba(56, 189, 248, 0.45) !important;
        transform: translateY(-2px) !important;
    }

    [data-testid="stTabs"] button[role="tab"]:active,
    button[data-baseweb="tab"]:active {
        transform: translateY(1px) !important;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.5), 0 2px 4px rgba(0, 0, 0, 0.3) !important;
    }

    /* 3D Elevated Cards */
    .note-card {
        background: linear-gradient(145deg, #1e293b 0%, #131b2e 100%);
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 14px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 12px 28px -6px rgba(0, 0, 0, 0.5), 0 6px 12px -4px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transition: all 0.25s ease;
    }

    .note-card:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 189, 248, 0.35);
        box-shadow: 0 18px 36px -8px rgba(0, 0, 0, 0.6), 0 0 20px rgba(56, 189, 248, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.15);
    }

    /* 3D Active Review Modal / Panel */
    .review-box {
        background: linear-gradient(160deg, #131d33 0%, #0b1120 100%);
        border-radius: 18px;
        padding: 26px 30px;
        margin: 20px 0 28px 0;
        border: 1px solid #38bdf8;
        box-shadow: 0 20px 50px -10px rgba(0, 0, 0, 0.8), 0 0 35px rgba(56, 189, 248, 0.25), inset 0 1px 1px rgba(255, 255, 255, 0.15);
    }

    /* Clean High-Contrast Document Reader Canvas */
    .document-reader-container {
        background: #090e17;
        border-radius: 14px;
        padding: 24px 28px;
        border: 1px solid #1e293b;
        color: #f1f5f9;
        line-height: 1.75;
        font-size: 1rem;
        max-height: 520px;
        overflow-y: auto;
        box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.7), 0 4px 12px rgba(0, 0, 0, 0.3);
        white-space: pre-wrap;
        word-break: break-word;
    }

    /* Custom Scrollbar */
    .document-reader-container::-webkit-scrollbar {
        width: 8px;
    }
    .document-reader-container::-webkit-scrollbar-track {
        background: #0f172a;
        border-radius: 4px;
    }
    .document-reader-container::-webkit-scrollbar-thumb {
        background: #334155;
        border-radius: 4px;
    }
    .document-reader-container::-webkit-scrollbar-thumb:hover {
        background: #38bdf8;
    }

    /* Badges */
    .badge-para {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 8px;
        font-size: 0.82rem;
        font-weight: 700;
        margin-right: 8px;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
    }
    .badge-resources { background: linear-gradient(135deg, #0284c7, #0369a1); color: white; border: 1px solid #38bdf8; }
    .badge-projects { background: linear-gradient(135deg, #d97706, #b45309); color: white; border: 1px solid #f59e0b; }
    .badge-areas { background: linear-gradient(135deg, #059669, #047857); color: white; border: 1px solid #10b981; }
    .badge-archives { background: linear-gradient(135deg, #7c3aed, #6d28d9); color: white; border: 1px solid #8b5cf6; }

    .badge-source {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 600;
        background: #1e293b;
        color: #94a3b8;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* Action Links & Buttons */
    .action-links-bar {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        margin: 16px 0 20px 0;
    }

    .btn-action-3d {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 10px 20px;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.92rem;
        text-decoration: none !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
    }

    .btn-web-direct {
        background: linear-gradient(180deg, #0284c7 0%, #0369a1 100%);
        color: #ffffff !important;
        border: 1px solid #38bdf8;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.35), 0 6px 14px rgba(2, 132, 199, 0.4);
    }
    .btn-web-direct:hover {
        transform: translateY(-2px);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.45), 0 8px 20px rgba(56, 189, 248, 0.5);
        color: #ffffff !important;
    }

    .btn-google-search {
        background: linear-gradient(180deg, #273549 0%, #172131 100%);
        color: #f1f5f9 !important;
        border: 1px solid rgba(255, 255, 255, 0.15);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.15), 0 4px 12px rgba(0, 0, 0, 0.35);
    }
    .btn-google-search:hover {
        transform: translateY(-2px);
        color: #ffffff !important;
        border-color: #38bdf8;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.25), 0 8px 18px rgba(0, 0, 0, 0.5);
    }

    /* 3D Button Press Animation */
    div.stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.18s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.15), 0 4px 10px rgba(0, 0, 0, 0.35) !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.25), 0 8px 18px rgba(0, 0, 0, 0.45) !important;
    }
    div.stButton > button:active {
        transform: translateY(1px) !important;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.5) !important;
    }

    .success-card {
        background: linear-gradient(145deg, #064e3b 0%, #022c22 100%);
        border-radius: 12px;
        padding: 20px 24px;
        margin-top: 18px;
        border: 1px solid #10b981;
        box-shadow: 0 10px 25px rgba(16, 185, 129, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.15);
        color: #ecfdf5;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="header-container">
        <div class="main-title">🧠 SecondSelf</div>
        <div class="sub-title">Your personal AI second brain — organizing, connecting, and answering from your knowledge.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Main 3D Navigation Tabs
tab_oracle, tab_ingest, tab_manage, tab_graph, tab_settings = st.tabs([
    "🔮 Ask SecondSelf",
    "📥 Add Knowledge",
    "🗂️ Manage Vault",
    "🗺️ Knowledge Graph",
    "⚙️ System & Settings"
])

# ==========================================
# TAB 1: ASK SECONDSELF (ORACLE)
# ==========================================
with tab_oracle:
    st.subheader("🔮 Ask Your Second Brain")
    st.caption("Ask questions in plain English. SecondSelf retrieves the most relevant knowledge and synthesizes clear answers.")

    # Quick Prompts
    col1, col2, col3 = st.columns(3)
    sample_query = None
    if col1.button("💡 What is SecondSelf?", use_container_width=True):
        sample_query = "What is SecondSelf?"
    if col2.button("🧠 Building an AI Second Brain", use_container_width=True):
        sample_query = "What notes talk about building an AI second brain?"
    if col3.button("📂 What topics are in my vault?", use_container_width=True):
        sample_query = "Summarize the key topics and categories stored in my notes."

    default_text = sample_query if sample_query else ""
    query = st.text_input("Ask a question:", value=default_text, placeholder="e.g. What are my notes about AI courses or university projects?")

    if query:
        with st.spinner("Searching knowledge base & generating answer..."):
            try:
                answer, contexts = ask_with_sources(query)
                st.markdown("### 📝 Answer")
                st.markdown(answer)
                
                st.divider()
                st.markdown(f"### 📚 Notes Referenced ({len(contexts)})")
                
                for idx, src in enumerate(contexts, 1):
                    wiki_path = src.get("wiki_path", "")
                    clean_title = src.get("title", f"Note {idx}")
                    score = src.get("score", 0.0)
                    match_pct = int(min(max(score * 100, 0), 100))
                    
                    excerpt = ""
                    try:
                        p = Path(wiki_path)
                        if p.exists():
                            raw_text = p.read_text(encoding="utf-8")
                            if raw_text.startswith("---") and "---" in raw_text[3:]:
                                parts = raw_text.split("---", 2)
                                excerpt = parts[2].strip()[:320]
                            else:
                                excerpt = raw_text[:320]
                    except Exception:
                        excerpt = "Preview unavailable."
                    
                    with st.expander(f"#{idx} | {clean_title}  (Relevance: {match_pct}%)"):
                        st.markdown(f"**Relevance Match:** `{match_pct}%`")
                        st.markdown(f"**Snippet Preview:**\n> {excerpt}...")
            except Exception as e:
                st.error(f"Error querying your second brain: {e}")

# ==========================================
# TAB 2: ADD KNOWLEDGE (INGEST)
# ==========================================
with tab_ingest:
    st.subheader("📥 Save New Knowledge")
    st.caption("Upload files, save web articles, or jot down notes. SecondSelf smartly categorizes them into Projects, Areas, or Resources without dumping into Archives.")
    
    ingest_type = st.radio("What would you like to add?", ["📄 Upload Document (PDF / Word / Text)", "🌐 Web Article / URL", "✍️ Quick Note or Thought"], horizontal=True)
    custom_title = st.text_input("Custom Title (optional):", placeholder="e.g. Deep Learning Lecture Notes (or leave blank for auto-title)")

    if ingest_type == "📄 Upload Document (PDF / Word / Text)":
        uploaded_file = st.file_uploader("Select a file to save:", type=["pdf", "txt", "md"])
        if uploaded_file and st.button("🚀 Save Document to Second Brain", type="primary"):
            with st.spinner(f"Reading, classifying, and connecting '{uploaded_file.name}'..."):
                try:
                    file_bytes = uploaded_file.read()
                    res = ingest_content(
                        source_type="file",
                        filename=uploaded_file.name,
                        file_bytes=file_bytes,
                        custom_title=custom_title
                    )
                    st.markdown(
                        f"""
                        <div class="success-card">
                            <h4>🎉 Document Successfully Added!</h4>
                            <p><strong>Title:</strong> {res['title']}</p>
                            <p><strong>Category:</strong> <span class="badge-para badge-{res['category'].lower()}">{res['category']}</span></p>
                            <p><strong>Summary:</strong> {res['summary']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                except Exception as e:
                    st.error(f"Could not process document: {e}")

    elif ingest_type == "🌐 Web Article / URL":
        url_input = st.text_input("Web page URL:", placeholder="https://example.com/ai-article")
        if url_input and st.button("🌐 Read & Save Web Article", type="primary"):
            with st.spinner("Extracting article content & organizing into your vault..."):
                try:
                    res = ingest_content(
                        source_type="url",
                        url=url_input,
                        custom_title=custom_title
                    )
                    st.markdown(
                        f"""
                        <div class="success-card">
                            <h4>🎉 Web Article Saved!</h4>
                            <p><strong>Title:</strong> {res['title']}</p>
                            <p><strong>Category:</strong> <span class="badge-para badge-{res['category'].lower()}">{res['category']}</span></p>
                            <p><strong>Summary:</strong> {res['summary']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                except Exception as e:
                    st.error(f"Could not save web article: {e}")

    elif ingest_type == "✍️ Quick Note or Thought":
        note_text = st.text_area("Write or paste your note:", height=150, placeholder="Type an idea, meeting takeaways, or study notes...")
        if note_text and st.button("✍️ Save Note", type="primary"):
            with st.spinner("Saving and analyzing note..."):
                try:
                    res = ingest_content(
                        source_type="note",
                        raw_text=note_text,
                        custom_title=custom_title
                    )
                    st.markdown(
                        f"""
                        <div class="success-card">
                            <h4>🎉 Note Saved!</h4>
                            <p><strong>Title:</strong> {res['title']}</p>
                            <p><strong>Category:</strong> <span class="badge-para badge-{res['category'].lower()}">{res['category']}</span></p>
                            <p><strong>Summary:</strong> {res['summary']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                except Exception as e:
                    st.error(f"Could not save note: {e}")

# ==========================================
# TAB 3: MANAGE VAULT (REVIEW & DELETE)
# ==========================================
with tab_manage:
    st.subheader("🗂️ Knowledge Vault Manager")
    st.caption("Review your saved captures with distraction-free reading, direct web links, and easy deletion.")
    
    captures = get_all_captures()
    
    # ------------------------------------------
    # ACTIVE NOTE REVIEW PANEL (HUMAN-CENTERED)
    # ------------------------------------------
    active_cid = st.session_state.get("active_view_cid")
    if active_cid:
        details = get_capture_details(active_cid)
        if details:
            cat = details.get("category", "Resources")
            badge_class = f"badge-{cat.lower()}"
            src_type = details.get("source_type", "note")
            src_label = {
                "note": "✍️ Quick Thought / Note",
                "file": f"📄 Document: {details.get('original_filename') or 'Uploaded File'}",
                "url": "🌐 Web Article"
            }.get(src_type, "Captured Item")
            
            st.markdown(
                f"""
                <div class="review-box">
                    <div>
                        <span class="badge-para {badge_class}">{cat}</span>
                        <span class="badge-source">{src_label}</span>
                        <h2 style="margin-top: 12px; margin-bottom: 8px; color: #f8fafc; font-size: 1.7rem; font-weight: 700;">{details['title']}</h2>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Action Links Bar (Open URL & Google Search)
            action_buttons_html = '<div class="action-links-bar">'
            if src_type == "url" and details.get("url"):
                action_buttons_html += f'<a href="{details["url"]}" target="_blank" class="btn-action-3d btn-web-direct">🌐 Open Original Webpage ↗</a>'
            
            if details.get("google_search_url"):
                action_buttons_html += f'<a href="{details["google_search_url"]}" target="_blank" class="btn-action-3d btn-google-search">🔍 Search Topic on Google ↗</a>'
            action_buttons_html += '</div>'
            
            st.markdown(action_buttons_html, unsafe_allow_html=True)
            
            # Content & Insights
            col_rev_info, col_rev_act = st.columns([3.8, 1.4])
            with col_rev_info:
                st.markdown("#### 💡 What is this about?")
                st.info(details.get("summary") or "A personal knowledge item saved in your second brain.")
                
                st.markdown("#### 📖 Document Reader")
                clean_body_text = details.get("body") or "*(No readable document text available)*"
                st.markdown(
                    f'<div class="document-reader-container">{clean_body_text}</div>',
                    unsafe_allow_html=True
                )
                
                # Tags
                if details.get("tags"):
                    st.markdown("<div style='margin-top: 14px;'><strong>Topic Tags:</strong> " + " ".join([f"<span class='badge-source'>#{t}</span>" for t in details["tags"]]) + "</div>", unsafe_allow_html=True)
                
                # Related Knowledge (Smart Navigation Chips)
                related_items = details.get("related_items", [])
                if related_items:
                    st.markdown("<div style='margin-top: 20px;'><strong>🔗 Connected Knowledge in Brain:</strong></div>", unsafe_allow_html=True)
                    chip_cols = st.columns(min(len(related_items), 3))
                    for idx_rel, rel_item in enumerate(related_items):
                        c_col = chip_cols[idx_rel % len(chip_cols)]
                        if c_col.button(f"🔗 {rel_item['title']}", key=f"rel_nav_{rel_item['id']}", use_container_width=True):
                            st.session_state["active_view_cid"] = rel_item["id"]
                            st.rerun()
                    
            with col_rev_act:
                st.markdown("#### 🎯 Decision Center")
                st.caption("Decide whether to keep this item in your second brain or remove it.")
                
                if st.button("✅ Keep & Close View", key="keep_close_btn", use_container_width=True):
                    st.session_state.pop("active_view_cid", None)
                    st.rerun()
                    
                st.divider()
                st.markdown("⚠️ **Danger Zone**")
                if st.button("🗑️ Delete This Note", key="del_from_viewer", type="secondary", use_container_width=True):
                    st.session_state[f"confirm_del_{active_cid}"] = True
                    
                if st.session_state.get(f"confirm_del_{active_cid}", False):
                    st.error("Permanently delete this item from your second brain and graph?")
                    col_y, col_n = st.columns(2)
                    if col_y.button("Confirm Delete", key="conf_del_viewer", type="primary"):
                        with st.spinner("Removing note and updating graph..."):
                            delete_capture(active_cid)
                            st.session_state.pop("active_view_cid", None)
                            st.session_state.pop(f"confirm_del_{active_cid}", None)
                            st.success("Note removed.")
                            st.rerun()
                    if col_n.button("Cancel", key="cancel_del_viewer"):
                        st.session_state.pop(f"confirm_del_{active_cid}", None)
                        st.rerun()
                        
            st.markdown("---")

    # Search and Filter Toolbar
    col_m1, col_m2 = st.columns([3, 1])
    search_term = col_m1.text_input("🔍 Search your vault:", placeholder="Search by title, topic, or keyword...")
    if col_m2.button("🔄 Sync & Rebuild Graph", help="Re-calculates connections and network relationships across all notes"):
        with st.spinner("Refreshing connections and network graph..."):
            rebuild_index_and_graph()
            st.success("Vault and graph synchronized!")
            st.rerun()

    filtered_captures = captures
    if search_term:
        term = search_term.lower()
        filtered_captures = [
            c for c in captures
            if term in c["title"].lower() or any(term in t.lower() for t in c.get("tags", [])) or term in c.get("summary","").lower()
        ]

    st.markdown(f"**Total Items in Brain:** `{len(captures)}` | **Showing:** `{len(filtered_captures)}`")
    st.divider()

    if not filtered_captures:
        st.info("No items found matching your search term.")
    else:
        for cap in filtered_captures:
            cid = cap["id"]
            cat = cap.get("category", "Resources")
            badge_class = f"badge-{cat.lower()}"
            src_type_label = {
                "note": "✍️ Quick Note",
                "file": "📄 Document",
                "url": "🌐 Web Article"
            }.get(cap.get("source_type", "note"), "Note")
            
            with st.container():
                col_info, col_view_btn, col_del_btn = st.columns([4.4, 1.1, 1.1])
                with col_info:
                    st.markdown(
                        f"""<span class="badge-para {badge_class}">{cat}</span> <span class="badge-source">{src_type_label}</span> **{cap['title']}**<br>
                        <small style="color:#94a3b8; margin-top: 4px; display: inline-block;">{cap.get('summary','')}</small>
                        """,
                        unsafe_allow_html=True
                    )
                
                with col_view_btn:
                    if st.button("👁️ View", key=f"btn_view_{cid}", use_container_width=True):
                        st.session_state["active_view_cid"] = cid
                        st.rerun()

                with col_del_btn:
                    if st.button("🗑️ Delete", key=f"btn_del_{cid}", type="secondary", use_container_width=True):
                        st.session_state[f"confirm_del_{cid}"] = True
                
                if st.session_state.get(f"confirm_del_{cid}", False):
                    st.warning(f"⚠️ Are you sure you want to permanently delete **{cap['title']}**?")
                    col_yes, col_no = st.columns(2)
                    if col_yes.button("Yes, Delete", key=f"yes_{cid}", type="primary"):
                        with st.spinner("Deleting note and re-syncing connections..."):
                            delete_capture(cid)
                            if st.session_state.get("active_view_cid") == cid:
                                st.session_state.pop("active_view_cid", None)
                            st.session_state.pop(f"confirm_del_{cid}", None)
                            st.success(f"Deleted '{cap['title']}'!")
                            st.rerun()
                    if col_no.button("Cancel", key=f"no_{cid}"):
                        st.session_state.pop(f"confirm_del_{cid}", None)
                        st.rerun()
                        
                st.divider()

# ==========================================
# TAB 4: KNOWLEDGE GRAPH
# ==========================================
with tab_graph:
    st.subheader("🗺️ Visual Knowledge Graph")
    st.caption("An interactive 2D network showing how your notes are semantically and topically connected.")
    
    graph_json_path = Path("static/graph.json")
    graph_html_path = Path("static/graph.html")
    
    if graph_html_path.exists() and graph_json_path.exists():
        try:
            # Read graph json and html
            graph_data_str = graph_json_path.read_text(encoding="utf-8")
            html_raw = graph_html_path.read_text(encoding="utf-8")
            
            # Inject graph data directly into HTML so it renders smoothly without iframe fetch blocks
            injected_script = f"<script>\nwindow.__INITIAL_GRAPH__ = {graph_data_str};\n"
            final_html = html_raw.replace("<script>", injected_script, 1)
            
            st.components.v1.html(final_html, height=720, scrolling=False)
        except Exception as e:
            st.warning(f"Could not render graph component: {e}. You can open `static/graph.html` directly in your browser.")
    else:
        st.info("Knowledge graph is being generated. Please click 'Sync & Rebuild Graph' in the Manage Vault tab.")

# ==========================================
# TAB 5: SYSTEM & SETTINGS (TECHNICAL DETAILS)
# ==========================================
with tab_settings:
    st.subheader("⚙️ System Status & Configuration")
    st.caption("Technical parameters and system health metrics.")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("#### 🤖 Intelligence Engine")
        st.write(f"**AI Model:** `{settings.LLM_MODEL}` (Groq)")
        st.write(f"**Embedding Model:** `{settings.EMBEDDING_MODEL}`")
        st.write(f"**Max Response Length:** `{settings.RAG_MAX_TOKENS} tokens`")
        
    with col_s2:
        st.markdown("#### 📐 Retrieval & Index Metrics")
        st.write(f"**Similarity Matching Threshold:** `{settings.LINK_SIM_THRESHOLD}`")
        st.write(f"**Top-K Retrieval Count:** `{settings.RAG_TOP_K}`")
        try:
            idx, meta = _load_index_and_metadata()
            st.metric("Total Indexed Vectors", idx.ntotal)
            st.metric("Indexed Notes", len(meta))
        except Exception:
            st.write("Index status: Initialized")
