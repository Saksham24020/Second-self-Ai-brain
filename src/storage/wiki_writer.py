import pathlib
import json
import yaml
from typing import List

from src.storage.manifest import load_manifest, list_captures


def _load_classification(capture_id: str) -> dict:
    """Load classification JSON from a capture directory.

    Returns the classification dict or an empty dict if not present.
    """
    classification_path = pathlib.Path('raw') / capture_id / 'classification.json'
    if not classification_path.exists():
        return {}
    with open(classification_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _load_content(capture_id: str) -> str:
    """Read the raw content of a capture.
    """
    content_path = pathlib.Path('raw') / capture_id / 'content.txt'
    if not content_path.exists():
        return ''
    with open(content_path, 'r', encoding='utf-8') as f:
        return f.read()


def _write_wiki_note(capture_id: str, meta: dict, classification: dict, content: str) -> None:
    """Write a markdown wiki note for a single capture.

    The note is stored under ``wiki/<para_category>/<capture_id>.md``.
    If the file already exists it is overwritten (idempotent).
    """
    category = classification.get('para_category', 'Resources')
    wiki_dir = pathlib.Path('wiki') / category
    wiki_dir.mkdir(parents=True, exist_ok=True)
    target_path = wiki_dir / f"{capture_id}.md"

    frontmatter = {
        'id': capture_id,
        'raw_id': capture_id,
        'para_category': category,
        'tags': classification.get('tags', []),
        'summary': classification.get('summary', ''),
        'title': classification.get('title', ''),
        'created_at': meta.get('timestamp', ''),
        'source_type': meta.get('source_type', ''),
        'source_metadata': meta.get('source_metadata', {}),
    }
    yaml_str = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True)
    markdown = f"---\n{yaml_str}---\n\n{content}\n"
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(markdown)


def write_all_wiki_notes(force: bool = False) -> List[str]:
    """Process all classified captures and generate wiki notes.

    Returns a list of processed capture IDs.
    """
    processed: List[str] = []
    for cid in list_captures():
        meta = load_manifest(cid)
        if meta.get('status') != 'classified':
            continue
        classification = meta.get('classification', _load_classification(cid))
        if not classification:
            continue
        target_path = pathlib.Path('wiki') / classification.get('para_category', 'Resources') / f"{cid}.md"
        if target_path.exists() and not force:
            continue
        content = _load_content(cid)
        _write_wiki_note(cid, meta, classification, content)
        processed.append(cid)
    return processed
