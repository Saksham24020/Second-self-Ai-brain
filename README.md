# Second Self AI Brain (Phase 1: Data Capture)

Second Self is an end-to-end knowledge management architecture designed to be your Personal AI Second Brain. It allows you to seamlessly capture unstructured data from various sources, auto-organize it using AI, and query it via Retrieval-Augmented Generation (RAG).

**Currently, Phase 1 (Core Data Capture Architecture) has been completed and deployed.**

## Features

### 1. Robust Data Capture Engine
The system exposes a powerful Typer-based CLI designed for frictionless data ingestion:
- **Text Notes:** Quickly jot down thoughts, ideas, or reminders straight from the terminal.
- **Web Pages (URLs):** Fetch and intelligently extract reading content (stripping scripts and styles) using `requests` and `BeautifulSoup4`.
- **Files & Documents:** Parses text locally from Markdown (`.md`), Plaintext (`.txt`), and PDF (`.pdf`) files via `pypdf`.

### 2. Lossless Ingestion
- Every captured item generates a unique, deterministic ID (`cap_YYYYMMDD_HHMMSS_<uuid>`).
- Original files are safely preserved.
- Metadata (timestamps, source types, origin URLs/paths, and extraction statuses) is cleanly tracked via `meta.json`.
- Fail-safes ensure that even if extraction fails (e.g. encrypted PDF, unresolvable URL), the metadata is securely captured and appropriately flagged without breaking the pipeline.

## Getting Started

### Prerequisites
- Python 3.11+
- Git

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Saksham24020/Second-self-Ai-brain.git
   cd Second-self-Ai-brain
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the environment template:
   ```bash
   cp .env.example .env
   ```
   *(Update `.env` with your API keys if you plan to extend to Phase 2)*

### Usage Guide
Use the `capture.py` CLI module to begin building your knowledge base:

```bash
# Capture a quick note
python -m src.capture --text "The future of knowledge work is AI-assisted synthesis."

# Capture a web article
python -m src.capture --url "https://en.wikipedia.org/wiki/Second_Brain"

# Capture a local document
python -m src.capture --file "C:/path/to/research_paper.pdf"
```

*Note: Your captured data will securely land in a `raw/` directory (ignored by git by default to preserve privacy).*

---

## Project Roadmap

- [x] **Phase 1: The Archivist (Data Capture)** — CLI pipeline for raw data ingestion (Notes, URLs, Files).
- [ ] **Phase 2: The Sorting Hat (Data Processing & Brain Engine)** — LLM-powered PARA classification and automated wiki-generation.
- [ ] **Phase 3: The Librarian (Semantic Auto-Linking)** — Local embedding generation (`sentence-transformers` & FAISS) to discover and interlink related knowledge.
- [ ] **Phase 4: The Cartographer (Graph Visualization)** — Interactive, force-directed graph UI representing the knowledge network.
- [ ] **Phase 5: The Oracle (RAG & Streamlit UI)** — Full Chatbot interface allowing you to chat directly with your second brain.
