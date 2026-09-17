# 🧠 Second Self — Personal AI Knowledge Brain

> **An intelligent "Second Brain" that reads, organizes, connects, and remembers everything for you — powered by Local Vector Search & LLMs.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Vector Search](https://img.shields.io/badge/FAISS-Vector%20Index-00599C?style=flat)](https://github.com/facebookresearch/faiss)
[![LLM Engine](https://img.shields.io/badge/Groq-Llama%203.1-F55036?style=flat)](https://groq.com)
[![Tests](https://img.shields.io/badge/pytest-13%20passed-brightgreen?style=flat&logo=pytest&logoColor=white)](https://pytest.org)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 💡 What is Second Self? (In Plain English)

Imagine you have a **super-smart digital assistant** sitting next to you. 

Every day, you read interesting articles on the web, read PDF documents for school or work, and write quick thoughts or ideas on your phone or computer. But within a few weeks:
- You forget which article had that crucial statistic.
- Your PDF downloads are lost in a messy "Downloads" folder.
- Your thoughts are scattered across random notes apps.

**Second Self solves this completely.** 

You simply drop anything into Second Self — a web link, a PDF document, or a quick sentence — and it acts like your own **private, 24/7 personal librarian**:
1. It **reads and understands** your notes and documents.
2. It **automatically files them** into neat, organized folders (using the famous PARA method: Projects, Areas, Resources, Archives).
3. It **draws invisible threads between related ideas** (realizing that a note you took today connects to an article you read three weeks ago).
4. You can **talk directly to your notes** in a clean web chat: ask questions in plain English, and it answers accurately using your own saved knowledge, showing you exactly which notes it pulled the answer from!

Best of all: **Everything stays private on your computer.**

---

## 🌟 Why It Matters

| The Old Way ❌ | The Second Self Way ✨ |
| :--- | :--- |
| Bookmarking 100 links and never reading them again | Drop the link: Second Self reads, extracts the main text, and files it. |
| Searching through messy folders hoping to find a lost PDF | Second Self indexes every word into a mathematical vector map. |
| Having to remember where you wrote something down | Ask: *"What was that method for optimizing neural networks?"* and get the exact answer instantly. |
| Storing your private thoughts on third-party cloud servers | Runs on your local machine with local vector storage. |

---

## 🔄 How It Works (The 4-Step Journey)

```text
       📥 Step 1: Ingestion
 [ Notes / Web Articles / PDF Docs ]
                 │
                 ▼
       🧠 Step 2: Auto-Organization
  [ AI Categorizes into PARA Folders ]
 (Projects, Areas, Resources, Archives)
                 │
                 ▼
       🔗 Step 3: Semantic Connecting
  [ FAISS Vector Index + Sentence-Transformers ]
 (Discovers hidden links & builds Knowledge Graph)
                 │
                 ▼
       🔮 Step 4: Natural Language Q&A
  [ Ask Questions via Web UI with Groq LLM ]
 (Instant answers with verifiable citations!)
```

1. **Capture (The Archivist)**: You feed Second Self raw information (type a quick thought, paste a URL, or upload a PDF/Markdown file).
2. **Auto-Sort (The Librarian)**: Powered by fast AI models, it automatically derives a clean title, tags the content, and sorts it into the right category.
3. **Connect (The Cartographer)**: Using Sentence-Transformers (`all-MiniLM-L6-v2`), it translates the meaning of your notes into mathematical vectors. Notes with similar meanings are automatically linked together into an interactive network map.
4. **Chat & Retrieve (The Oracle)**: Using Retrieval-Augmented Generation (RAG), you ask questions in natural language. Second Self retrieves the most relevant notes and synthesizes a crystal-clear answer with source citations.

---

## 🖥️ Interactive Web Dashboard

Second Self comes with a dark-mode **Streamlit web application** split into five intuitive workspaces:

- 🔮 **Ask SecondSelf (RAG Chatbot)**: Chat with your second brain! Ask questions, get referenced answers, and view confidence similarity scores.
- 📥 **Add Knowledge (Frictionless Ingestion)**: Clean tabs to type quick notes, paste website links for automated scraping, or upload files (`.pdf`, `.md`, `.txt`).
- 🗂️ **Manage Vault (Digital Library Canvas)**: Browse through all your captured knowledge, read cleanly formatted markdown cards, open original source links, or delete old notes.
- 🗺️ **Knowledge Graph (Visual Mind Map)**: Explore an interactive 2D/3D force-directed network showing how all your notes, concepts, and ideas connect to one another.
- ⚙️ **System & Settings**: Monitor system statistics (total notes, vector index health) and trigger manual re-indexing anytime.

---

## 🛠️ Tech Stack & Architecture

| Layer | Technology | Why We Chose It |
| :--- | :--- | :--- |
| **User Interface** | Streamlit, HTML5, Custom CSS | High-performance, reactive Python web dashboard with custom dark-mode aesthetics. |
| **Language Model (LLM)** | Groq API (`llama-3.1-8b-instant`) | Ultra-fast inference (< 500ms latency) for classification and RAG synthesis. |
| **Vector Embeddings** | `sentence-transformers` (`all-MiniLM-L6-v2`) | Lightweight, high-accuracy semantic embeddings running locally on your CPU. |
| **Vector Database** | Facebook AI Similarity Search (FAISS) | Millisecond similarity search and cosine-distance retrieval across local notes. |
| **Knowledge Graph** | NetworkX, PyVis, Streamlit-Agraph | Graph theory data modeling and force-directed interactive physics visualizations. |
| **Data Extraction** | BeautifulSoup4, Requests, PyPDF | Robust parsing of web pages (stripping ads/scripts) and multi-page PDF documents. |
| **CLI Engine** | Typer, Rich | Ergonomic command-line interface for terminal power-users. |
| **Testing & Reliability** | Pytest, Tenacity | Automated test suite with exponential backoff retries for network resilience. |

---

## 🚀 Quickstart Guide

Get Second Self up and running on your computer in under **3 minutes**:

### 1. Prerequisites
- **Python 3.11+** installed on your system
- A free **Groq API Key** (get one at [console.groq.com](https://console.groq.com))

### 2. Clone the Repository
```bash
git clone https://github.com/Saksham24020/Second-self-Ai-brain.git
cd Second-self-Ai-brain
```

### 3. Set Up Virtual Environment & Dependencies
```bash
# Create virtual environment
python -m venv .venv

# Activate on Windows:
.venv\Scripts\activate
# Or on macOS/Linux:
source .venv/bin/activate

# Install all required packages
pip install -r requirements.txt
```

### 4. Configure Your API Key
Copy the example environment file:
```bash
cp .env.example .env
```
Open `.env` in any text editor and paste your Groq API key:
```env
LLM_API_KEY=your_groq_api_key_here
```

### 5. Launch the Web Application! 🎈
```bash
streamlit run src/app.py
```
Your browser will automatically open `http://localhost:8501`. You can now start adding notes and chatting with your second brain!

---

## 💻 Terminal / CLI Usage (Optional)

If you prefer working directly in the terminal, Second Self provides complete CLI workflows:

```bash
# 1. Capture a quick thought
python -m src.capture --text "Gradient descent is an optimization algorithm for machine learning."

# 2. Capture a website
python -m src.capture --url "https://en.wikipedia.org/wiki/Second_Brain"

# 3. Capture a PDF or text file
python -m src.capture --file "path/to/research_paper.pdf"

# 4. Run the automated organization & linking pipeline
python -m src.pipeline

# 5. Ask your brain a question from the terminal
python -m src.ask "What is gradient descent?"
```

---

## 🧪 Automated Testing

The codebase includes an automated test suite verifying data extraction, manifest records, RAG prompt construction, and title sanitization.

To run tests:
```bash
pytest -v
```

Output:
```text
============================= test session starts =============================
collected 13 items

tests/test_manager.py::test_derive_clean_title_with_valid_original PASSED [  7%]
tests/test_manager.py::test_derive_clean_title_from_heading PASSED       [ 15%]
tests/test_manager.py::test_derive_clean_title_fallback PASSED           [ 23%]
tests/test_manager.py::test_derive_clean_summary_from_content PASSED     [ 30%]
tests/test_parsing.py::test_extract_note_valid PASSED                    [ 38%]
tests/test_parsing.py::test_extract_note_empty PASSED                    [ 46%]
tests/test_parsing.py::test_extract_file_markdown_and_txt PASSED         [ 53%]
tests/test_parsing.py::test_extract_file_nonexistent PASSED              [ 61%]
tests/test_parsing.py::test_extract_file_unsupported_type PASSED         [ 69%]
tests/test_rag.py::test_build_prompt_structure PASSED                    [ 76%]
tests/test_storage.py::test_generate_capture_id PASSED                   [ 84%]
tests/test_storage.py::test_get_iso_timestamp PASSED                     [ 92%]
tests/test_storage.py::test_save_and_load_manifest PASSED                [100%]

============================= 13 passed in 6.62s ==============================
```

---

## 📁 Clean Project Structure

```text
Second-self-Ai-brain/
├── .streamlit/             # Streamlit UI configuration and dark theme styling
├── src/                    # Core application source code
│   ├── app.py              # Streamlit Web Dashboard (5 Interactive Tabs)
│   ├── ask.py              # RAG query engine with FAISS retrieval + Groq LLM
│   ├── build_graph.py      # NetworkX & PyVis knowledge graph generator
│   ├── capture.py          # Multi-source data ingestion CLI
│   ├── classify.py         # PARA categorization engine (Projects, Areas, Resources, Archives)
│   ├── config.py           # Application settings and environment validation
│   ├── link.py             # Semantic linker based on vector cosine similarity
│   ├── manager.py          # Unified manager handling storage, indexing, and sync
│   ├── pipeline.py         # End-to-end pipeline orchestrator
│   ├── search_captures.py  # Local search utility
│   ├── embeddings/         # Local vector indexer (SentenceTransformers + FAISS)
│   ├── llm/                # Groq API client and prompt templates
│   ├── parsing/            # Text, URL, and PDF extractors
│   └── storage/            # Manifest and Markdown wiki writers
├── static/                 # Interactive graph visualizer templates (HTML/JS)
├── tests/                  # Automated Pytest suite (13 unit tests)
├── .env.example            # Environment variables template
├── .gitignore              # Privacy-first git ignore rules (protects user data)
├── requirements.txt        # Production dependency specifications
└── README.md               # Beginner-friendly project documentation
```

---

## 🏆 Project Roadmap & Status

- [x] **Phase 1: The Archivist (Multi-Source Ingestion)** — Clean ingestion pipeline for Notes, URLs, and PDF/MD/TXT documents.
- [x] **Phase 2: The Librarian (Auto-Classification)** — Intelligent PARA categorization and markdown wiki generator.
- [x] **Phase 3: The Synthesizer (Vector Indexing & Linking)** — Local FAISS vector indexer and semantic auto-linking.
- [x] **Phase 4: The Cartographer (Knowledge Graph)** — Interactive force-directed network graph of interconnected concepts.
- [x] **Phase 5: The Oracle (RAG Chat & Streamlit Web UI)** — Natural language Q&A engine with verifiable source citations and dark-mode UI.

---

## 🔒 Privacy & Data Ownership

Your personal knowledge is private. Second Self is built with a **local-first philosophy**:
- Raw captures, wiki notes, and vector indices reside exclusively on your local file system.
- Git ignores private data directories (`raw/`, `wiki/`, `index/`, `static/graph.json`) by default so your personal thoughts and documents will never be committed to public repositories.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
