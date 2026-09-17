import os
import json
import faiss
import pathlib
import numpy as np
from typing import List, Dict, Any, Tuple
from src.config import settings
from loguru import logger

INDEX_DIR = pathlib.Path("index")
FAISS_INDEX_PATH = INDEX_DIR / "faiss.index"
METADATA_PATH = INDEX_DIR / "metadata.json"

_model = None

def _get_model():
    global _model
    if _model is None:
        try:
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer(settings.EMBEDDING_MODEL)
        except ImportError:
            logger.warning("sentence_transformers not found. Using dummy embedding fallback.")
            _model = "dummy"
    return _model

def embed_text(text: str) -> List[float]:
    """Compute the embedding for a given text."""
    model = _get_model()
    if model == "dummy":
        import hashlib
        # deterministic dummy 384-d vector based on text hash
        h = int(hashlib.md5(text.encode('utf-8')).hexdigest(), 16)
        np.random.seed(h % (2**32))
        embedding = np.random.rand(384).astype(np.float32)
        # Normalize
        embedding = embedding / np.linalg.norm(embedding)
        return embedding.tolist()
        
    # SentenceTransformer returns a numpy array, convert to list of floats
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()

def _load_index_and_metadata() -> Tuple[faiss.Index, List[Dict[str, Any]]]:
    """Load the FAISS index and metadata list, or create new ones if they don't exist."""
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    
    metadata = []
    if METADATA_PATH.exists():
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            metadata = json.load(f)
            
    if FAISS_INDEX_PATH.exists():
        index = faiss.read_index(str(FAISS_INDEX_PATH))
    else:
        # Create a new IndexFlatL2 index. We need the dimension of the embeddings.
        # We can infer it from the model or assume 384 for all-MiniLM-L6-v2.
        # It's safer to ask the model for its dimension.
        model = _get_model()
        if model == "dummy":
            d = 384
        else:
            d = model.get_embedding_dimension() if hasattr(model, 'get_embedding_dimension') else model.get_sentence_embedding_dimension()
        index = faiss.IndexFlatIP(d) # Using Inner Product (cosine similarity if normalized)
        
    return index, metadata

def save_index_and_metadata(index: faiss.Index, metadata: List[Dict[str, Any]]) -> None:
    """Save the FAISS index and metadata to disk."""
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(FAISS_INDEX_PATH))
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

def add_to_index(capture_id: str, wiki_path: str, title: str, text: str) -> None:
    """Embed the text and add it to the FAISS index and metadata list."""
    embedding = embed_text(text)
    
    index, metadata = _load_index_and_metadata()
    
    # Check if capture_id already exists to avoid duplicates
    for i, meta in enumerate(metadata):
        if meta.get("id") == capture_id:
            # We would need to update the FAISS vector, which is tricky in FAISS (requires remove and add, but IndexFlatL2 doesn't support remove easily).
            # For this MVP, if it exists, we skip or we just don't handle updates perfectly.
            # In rebuild mode, we will rebuild the index from scratch.
            logger.warning(f"Capture {capture_id} already in index. Use rebuild to update.")
            return

    # Add to FAISS index
    # FAISS expects a 2D numpy array of float32
    embedding_np = np.array([embedding], dtype=np.float32)
    index.add(embedding_np)
    
    # Add to metadata (FAISS sequential ID will match metadata list index)
    metadata.append({
        "id": capture_id,
        "wiki_path": wiki_path,
        "title": title
    })
    
    save_index_and_metadata(index, metadata)

def search_index(query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
    """Search the FAISS index for the most similar items to the query embedding."""
    if not FAISS_INDEX_PATH.exists() or not METADATA_PATH.exists():
        return []
        
    index, metadata = _load_index_and_metadata()
    if index.ntotal == 0:
        return []
        
    embedding_np = np.array([query_embedding], dtype=np.float32)
    
    # Search returns squared L2 distances and indices
    k = min(top_k, index.ntotal)
    distances, indices = index.search(embedding_np, k)
    
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx != -1 and idx < len(metadata):
            # For IndexFlatIP, higher distance is more similar (it's the dot product/cosine similarity).
            similarity = float(dist)
            
            item = metadata[idx].copy()
            item["score"] = similarity
            item["distance"] = float(dist)
            results.append(item)
            
    return results

def reset_index() -> None:
    """Delete the existing index and metadata."""
    if FAISS_INDEX_PATH.exists():
        FAISS_INDEX_PATH.unlink()
    if METADATA_PATH.exists():
        METADATA_PATH.unlink()
