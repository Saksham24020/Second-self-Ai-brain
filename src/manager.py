# src/manager.py
"""Management service for SecondSelf.
Provides functions to ingest notes, URLs, and files (PDF/MD/TXT),
as well as listing and deleting captures with full index synchronization.
"""

import shutil
import pathlib
import re
import urllib.parse
from typing import Optional, List, Dict, Any
from loguru import logger

from src.storage.manifest import generate_capture_id, get_iso_timestamp, ensure_dirs, save_manifest, load_manifest, list_captures
from src.parsing.text_extract import extract_note, extract_url, extract_file
from src.classify import _classify_text, _write_classification
from src.storage.wiki_writer import _write_wiki_note
from src.embeddings.indexer import add_to_index, reset_index, _load_index_and_metadata
from src.link import link as run_link
from src.build_graph import generate_graph
import frontmatter

def ingest_content(
    source_type: str,
    raw_text: Optional[str] = None,
    url: Optional[str] = None,
    filename: Optional[str] = None,
    file_bytes: Optional[bytes] = None,
    custom_title: Optional[str] = None
) -> Dict[str, Any]:
    """Ingest a note, URL, or document and run classification + indexing."""
    ensure_dirs()
    cap_id = generate_capture_id()
    timestamp = get_iso_timestamp()
    
    extracted_text = ""
    error_msg = ""
    source_meta = {}
    
    raw_dir = pathlib.Path("raw") / cap_id
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    if source_type == "note":
        try:
            extracted_text = extract_note(raw_text or "")
        except Exception as e:
            error_msg = str(e)
            
    elif source_type == "url":
        source_meta["url"] = url
        try:
            extracted_text = extract_url(url or "")
        except Exception as e:
            error_msg = str(e)
            
    elif source_type == "file":
        source_meta["original_filename"] = filename
        temp_path = raw_dir / (filename or "uploaded_file")
        if file_bytes:
            with open(temp_path, "wb") as f:
                f.write(file_bytes)
        try:
            extracted_text = extract_file(str(temp_path))
        except Exception as e:
            error_msg = str(e)
            
    if error_msg or not extracted_text.strip():
        meta = {
            "id": cap_id,
            "timestamp": timestamp,
            "source_type": source_type,
            "source_metadata": source_meta,
            "status": "invalid",
            "extraction_error": error_msg or "No text could be extracted."
        }
        save_manifest(cap_id, meta)
        raise ValueError(f"Ingestion failed: {meta['extraction_error']}")
        
    # Write content.txt
    with open(raw_dir / "content.txt", "w", encoding="utf-8") as f:
        f.write(extracted_text)
        
    # Write initial manifest
    meta = {
        "id": cap_id,
        "timestamp": timestamp,
        "source_type": source_type,
        "source_metadata": source_meta,
        "status": "raw"
    }
    save_manifest(cap_id, meta)
    
    # Determine classification context hint
    hint = f"Source type: {source_type}"
    if filename:
        hint += f", Filename: {filename}"
    elif url:
        hint += f", Web URL: {url}"
        
    # Classify
    classification = _classify_text(extracted_text, context_hint=hint)
    if custom_title and custom_title.strip():
        classification.title = custom_title.strip()
    _write_classification(cap_id, classification)
    
    # Write wiki note
    category = classification.para_category
    _write_wiki_note(cap_id, meta, classification.dict(), extracted_text)
    wiki_path = str(pathlib.Path("wiki") / category / f"{cap_id}.md")
    
    # Add to FAISS index
    add_to_index(cap_id, wiki_path, classification.title, extracted_text)
    
    # Refresh links and graph
    try:
        run_link(capture_id=cap_id)
        generate_graph()
    except Exception as e:
        logger.warning(f"Error updating links/graph: {e}")
        
    return {
        "id": cap_id,
        "title": classification.title,
        "category": category,
        "summary": classification.summary,
        "tags": classification.tags,
        "wiki_path": wiki_path
    }

def delete_capture(capture_id: str) -> bool:
    """Delete a capture from raw, wiki, and re-sync FAISS index and graph."""
    deleted_any = False
    
    # 1. Remove raw folder
    raw_dir = pathlib.Path("raw") / capture_id
    if raw_dir.exists():
        shutil.rmtree(raw_dir, ignore_errors=True)
        deleted_any = True
        
    # 2. Remove wiki note
    wiki_root = pathlib.Path("wiki")
    if wiki_root.exists():
        for md_file in wiki_root.rglob(f"{capture_id}.md"):
            try:
                md_file.unlink()
                deleted_any = True
            except Exception as e:
                logger.warning(f"Error removing {md_file}: {e}")
                
    # 3. Clean and rebuild index from remaining wiki files
    rebuild_index_and_graph()
    return deleted_any

def rebuild_index_and_graph():
    """Rebuild FAISS index and knowledge graph from all existing wiki notes."""
    reset_index()
    wiki_root = pathlib.Path("wiki")
    if wiki_root.exists():
        for md_file in wiki_root.rglob("*.md"):
            try:
                post = frontmatter.load(str(md_file))
                cid = post.metadata.get("id", md_file.stem)
                title = post.metadata.get("title", md_file.stem)
                content = post.content
                add_to_index(cid, str(md_file), title, content)
            except Exception as e:
                logger.warning(f"Error indexing {md_file}: {e}")
                
    try:
        run_link(capture_id=None, rebuild=True)
        generate_graph()
    except Exception as e:
        logger.warning(f"Error rebuilding graph: {e}")

SEED_TITLES = {
    "cap_20260819_085847_28eceffe": "Welcome to SecondSelf & First Captured Thought",
    "cap_20260819_090615_5a0271b1": "Sample Documentation & Markdown Ingestion",
    "cap_20260823_090931_ab489368": "Building an AI Second Brain Guide",
    "cap_20260823_091206_1a92a132": "Personal Profile: Saksham Jindal",
    "cap_20260823_091441_31a182cf": "B.Tech Engineering Journey & Masai Loop",
    "cap_20260823_092248_0c8f9b1e": "GGSIPU Delhi: Seat Allotment Round 6",
    "cap_20260823_092438_1402fa52": "Joint Entrance Examination (JEE) Records",
    "cap_20260823_092718_71493dc4": "Masai x IIT Roorkee AI/ML Course Notes",
    "cap_20260823_092924_912eb857": "India's Top AI-Ready Programs (Masai & iHUB)",
    "cap_20260823_093033_9d628b8f": "Guru Gobind Singh Indraprastha University (GGSIPU)",
    "cap_20260824_085758_75ec44a4": "Knowledge Capture System Verification Note",
    "cap_20260826_145726_154e5b04": "Productivity Strategies: PARA Method & Daily Journal",
    "cap_20260826_145756_12c6de09": "Marketing Strategy & Youth Demographics Meeting",
    "cap_20260826_145836_94f8631c": "Future of Artificial Intelligence in Software Engineering",
    "cap_20260903_163142_ed407616": "JEE Application Confirmation & Admit Card Details",
}

def extract_clean_content(content: str) -> str:
    """Cleanly extract note body, stripping out raw markdown wikilinks, '## Related' sections, and technical noise."""
    if not content:
        return ""
        
    lines = content.splitlines()
    cleaned_lines = []
    in_related_section = False
    
    for line in lines:
        stripped = line.strip()
        # Cut off at the related notes / links section
        if stripped.startswith("## Related") or stripped.startswith("# Related") or stripped.startswith("### Related"):
            in_related_section = True
            continue
        if in_related_section:
            continue
        # Filter out standalone wikilinks like - [[...]]
        if stripped.startswith("- [[") or stripped.startswith("* [["):
            continue
        cleaned_lines.append(line)
        
    result = "\n".join(cleaned_lines).strip()
    # Clean inline wikilinks: [[id|Title]] -> Title, [[id]] -> id
    result = re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]', r'\2', result)
    result = re.sub(r'\[\[([^\]]+)\]\]', r'\1', result)
    return result

def derive_clean_title(capture_id: str, original_title: str, content: str) -> str:
    """Return an intelligent, human-friendly title instead of generic placeholder text."""
    if capture_id in SEED_TITLES:
        return SEED_TITLES[capture_id]
        
    if original_title and original_title.lower() != "placeholder title" and not original_title.startswith("cap_"):
        return original_title.strip()
        
    # Inspect content for headings or first meaningful line
    for line in content.splitlines():
        cleaned = line.strip()
        if not cleaned or cleaned.startswith("## Related") or cleaned.startswith("- [["):
            continue
        # Remove Markdown hash markers
        cleaned = cleaned.lstrip("#").strip()
        if cleaned:
            if len(cleaned) > 55:
                words = cleaned[:55].rsplit(" ", 1)[0]
                return words + "…"
            return cleaned
            
    return f"Note {capture_id[-8:]}"

def derive_clean_summary(capture_id: str, original_summary: str, content: str) -> str:
    """Return a clean, readable summary explaining what the note is about."""
    if original_summary and original_summary.lower() != "placeholder summary for testing.":
        return original_summary.strip()
        
    # Build a concise excerpt from actual note lines
    content_lines = []
    for line in content.splitlines():
        cleaned = line.strip()
        if not cleaned or cleaned.startswith("## Related") or cleaned.startswith("- [["):
            continue
        cleaned = cleaned.lstrip("#").strip()
        content_lines.append(cleaned)
        if len(" ".join(content_lines)) > 150:
            break
            
    excerpt = " ".join(content_lines).strip()
    if excerpt:
        if len(excerpt) > 180:
            return excerpt[:180].rsplit(" ", 1)[0] + "…"
        return excerpt
    return "Personal captured note stored in your second brain."

def get_all_captures() -> List[Dict[str, Any]]:
    """Return a list of all captures with clean titles, summaries, categories, and wiki paths."""
    captures = []
    wiki_root = pathlib.Path("wiki")
    if wiki_root.exists():
        for md_file in wiki_root.rglob("*.md"):
            try:
                post = frontmatter.load(str(md_file))
                meta = post.metadata
                cid = meta.get("id", md_file.stem)
                content = post.content
                
                clean_title = derive_clean_title(cid, meta.get("title", ""), content)
                clean_summary = derive_clean_summary(cid, meta.get("summary", ""), content)
                
                captures.append({
                    "id": cid,
                    "title": clean_title,
                    "category": meta.get("para_category", md_file.parent.name),
                    "tags": meta.get("tags", []),
                    "created_at": meta.get("created_at", ""),
                    "source_type": meta.get("source_type", "note"),
                    "wiki_path": str(md_file),
                    "summary": clean_summary
                })
            except Exception as e:
                logger.warning(f"Error reading {md_file}: {e}")
    # Sort descending by id/creation
    captures.sort(key=lambda x: x.get("id", ""), reverse=True)
    return captures

def get_capture_details(capture_id: str) -> Optional[Dict[str, Any]]:
    """Fetch complete details, clean human body content, source metadata, and related notes."""
    wiki_root = pathlib.Path("wiki")
    if not wiki_root.exists():
        return None
    for md_file in wiki_root.rglob(f"{capture_id}.md"):
        try:
            post = frontmatter.load(str(md_file))
            raw_text = md_file.read_text(encoding="utf-8")
            meta = post.metadata
            content = post.content
            
            clean_title = derive_clean_title(capture_id, meta.get("title", ""), content)
            clean_summary = derive_clean_summary(capture_id, meta.get("summary", ""), content)
            clean_body = extract_clean_content(content)
            
            # Fetch source metadata (e.g. original URL or filename)
            src_meta = meta.get("source_metadata") or {}
            if not src_meta:
                raw_manifest = load_manifest(capture_id)
                if raw_manifest:
                    src_meta = raw_manifest.get("source_metadata", {})
                    
            source_url = src_meta.get("url")
            orig_filename = src_meta.get("original_filename")
            
            # Formulate Google Search URL
            search_query = clean_title if clean_title and "placeholder" not in clean_title.lower() else "Second Brain Note"
            google_search_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(search_query)}"
            
            # Resolve related links into human-friendly items
            raw_links = meta.get("links", [])
            related_items = []
            for target_cid in raw_links:
                if target_cid and target_cid != capture_id:
                    t_title = derive_clean_title(target_cid, "", "")
                    related_items.append({
                        "id": target_cid,
                        "title": t_title
                    })
            
            return {
                "id": meta.get("id", capture_id),
                "title": clean_title,
                "category": meta.get("para_category", md_file.parent.name),
                "tags": meta.get("tags", []),
                "created_at": meta.get("created_at", ""),
                "source_type": meta.get("source_type", "note"),
                "summary": clean_summary,
                "links": meta.get("links", []),
                "related_items": related_items,
                "body": clean_body,
                "raw_text": raw_text,
                "wiki_path": str(md_file),
                "url": source_url,
                "original_filename": orig_filename,
                "google_search_url": google_search_url
            }
        except Exception as e:
            logger.warning(f"Error loading capture details for {capture_id}: {e}")
    return None

def move_and_reclassify_capture(capture_id: str, new_category: str) -> bool:
    """Move a capture from its current PARA folder to new_category, updating frontmatter and indices."""
    wiki_root = pathlib.Path("wiki")
    found_file = None
    if wiki_root.exists():
        for md_file in wiki_root.rglob(f"{capture_id}.md"):
            found_file = md_file
            break
            
    if not found_file:
        return False
        
    new_dir = wiki_root / new_category
    new_dir.mkdir(parents=True, exist_ok=True)
    new_path = new_dir / f"{capture_id}.md"
    
    post = frontmatter.load(str(found_file))
    post.metadata["para_category"] = new_category
    
    # Write updated file to new path
    with open(new_path, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))
        
    # Remove old file if path differs
    if str(found_file.resolve()) != str(new_path.resolve()):
        found_file.unlink(missing_ok=True)
        
    # Update manifest and raw classification
    raw_dir = pathlib.Path("raw") / capture_id
    if raw_dir.exists():
        cls_file = raw_dir / "classification.json"
        if cls_file.exists():
            try:
                import json
                with open(cls_file, "r", encoding="utf-8") as f:
                    cls_data = json.load(f)
                cls_data["para_category"] = new_category
                with open(cls_file, "w", encoding="utf-8") as f:
                    json.dump(cls_data, f, indent=2)
            except Exception:
                pass
        man = load_manifest(capture_id)
        if man:
            if "classification" in man:
                man["classification"]["para_category"] = new_category
            save_manifest(capture_id, man)
            
    # Rebuild index and graph
    rebuild_index_and_graph()
    return True

