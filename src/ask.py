# src/ask.py
"""Retrieval‑Augmented Generation (RAG) utilities.

- Embeds a query using the same model as the linker.
- Searches the FAISS index for the top `RAG_TOP_K` similar notes.
- Sends the retrieved snippets to the Groq LLM and returns the answer.
"""

import os
import sys
from typing import List, Dict, Tuple

# Ensure UTF-8 output on Windows consoles to prevent cp1252 encoding errors
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.config import settings
from src.embeddings.indexer import embed_text, search_index

# Lazily initialise Groq client – only when needed
_groq_client = None

def _get_groq_client():
    """Create and cache a Groq client using the API key from settings."""
    global _groq_client
    if _groq_client is None:
        try:
            from groq import Groq
        except ImportError as e:
            raise RuntimeError("The 'groq' package is not installed. Run '.venv\\Scripts\\pip install groq'.") from e
        api_key = settings.LLM_API_KEY or os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("Groq API key not found. Set LLM_API_KEY in .env or GROQ_API_KEY env var.")
        _groq_client = Groq(api_key=api_key)
    return _groq_client

def retrieve(query: str) -> List[Dict]:
    """Return the top `settings.RAG_TOP_K` documents for *query*.

    Each dict contains the original metadata (`id`, `title`, `wiki_path`, `score`).
    """
    from src.manager import derive_clean_title
    embedding = embed_text(query)
    results = search_index(embedding, top_k=settings.RAG_TOP_K)
    for item in results:
        cid = item.get("id", "")
        item["title"] = derive_clean_title(cid, item.get("title", ""), "")
    return results

def _build_prompt(query: str, contexts: List[Dict]) -> str:
    """Create a prompt that includes the query and excerpts of the retrieved notes."""
    snippets = []
    for ctx in contexts:
        path = ctx.get("wiki_path", "")
        content = ""
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    raw = f.read()
            else:
                raw = ""
            # Separate YAML frontmatter if present
            if raw.startswith("---"):
                parts = raw.split("---", 2)
                front = parts[1].strip() if len(parts) >= 2 else ""
                body = parts[2].strip() if len(parts) >= 3 else ""
                content = f"{front}\n\nContent:\n{body}"
            else:
                content = raw.strip()
        except Exception:
            content = ""
        
        excerpt = content[:1500].strip()
        snippets.append(f"Title: {ctx.get('title','')}\nPath: {path}\nScore: {ctx.get('score',0):.3f}\nDetails:\n{excerpt}\n---")
    
    snippets_block = "\n".join(snippets)
    prompt = (
        "You are an intelligent knowledge assistant for a personal second brain.\n"
        "Answer the user's question using the retrieved context notes provided below.\n"
        "Cite relevant note titles or IDs when applicable.\n"
        "If the information is not present in the notes, answer based on the best available details and clarify what is in the notes.\n\n"
        f"Question: {query}\n\nRetrieved Notes:\n{snippets_block}\n\nAnswer:"
    )
    return prompt

def generate_answer(query: str, contexts: List[Dict]) -> str:
    """Send the composed prompt to Groq and return the model's answer."""
    client = _get_groq_client()
    prompt = _build_prompt(query, contexts)
    response = client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=settings.RAG_MAX_TOKENS,
    )
    return response.choices[0].message.content.strip()

def ask(query: str) -> str:
    """High‑level helper: retrieve context and generate an answer."""
    answer, _ = ask_with_sources(query)
    return answer

def ask_with_sources(query: str) -> Tuple[str, List[Dict]]:
    """Retrieve context notes and generate an answer, returning both."""
    contexts = retrieve(query)
    answer = generate_answer(query, contexts)
    return answer, contexts

if __name__ == "__main__":
    if len(sys.argv) > 1:
        q = " ".join(sys.argv[1:])
        print(ask(q))
    else:
        print("Usage: python -m src.ask \"your question\"")
