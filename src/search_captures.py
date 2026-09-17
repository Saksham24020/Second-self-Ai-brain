import argparse
import json
import pathlib
import sys
from typing import List, Dict, Any

from src.embeddings.indexer import embed_text, search_index, _load_index_and_metadata

RAW_DIR = pathlib.Path('raw')

def load_capture(capture_id: str) -> Dict[str, Any]:
    cap_dir = RAW_DIR / capture_id
    data: Dict[str, Any] = {'id': capture_id}
    # Load meta.json (status etc.)
    try:
        with open(cap_dir / 'meta.json', 'r', encoding='utf-8') as f:
            data['meta'] = json.load(f)
    except FileNotFoundError:
        data['meta'] = {}
    # Load classification.json
    try:
        with open(cap_dir / 'classification.json', 'r', encoding='utf-8') as f:
            data['classification'] = json.load(f)
    except FileNotFoundError:
        data['classification'] = {}
    # Load content (first 200 chars for preview)
    try:
        with open(cap_dir / 'content.txt', 'r', encoding='utf-8') as f:
            full = f.read()
            data['preview'] = full[:200].replace('\n', ' ')
    except FileNotFoundError:
        data['preview'] = ''
    return data

def keyword_search(keyword: str) -> List[Dict[str, Any]]:
    matches: List[Dict[str, Any]] = []
    for cap_dir in RAW_DIR.iterdir():
        if not cap_dir.is_dir():
            continue
        txt_path = cap_dir / 'content.txt'
        if not txt_path.exists():
            continue
        try:
            text = txt_path.read_text(encoding='utf-8')
        except Exception:
            continue
        if keyword.lower() in text.lower():
            matches.append(load_capture(cap_dir.name))
    return matches

def tag_search(tag: str) -> List[Dict[str, Any]]:
    matches: List[Dict[str, Any]] = []
    for cap_dir in RAW_DIR.iterdir():
        if not cap_dir.is_dir():
            continue
        class_path = cap_dir / 'classification.json'
        if not class_path.exists():
            continue
        try:
            classif = json.load(open(class_path, 'r', encoding='utf-8'))
        except Exception:
            continue
        tags = classif.get('tags', [])
        if isinstance(tags, list) and tag.lower() in (t.lower() for t in tags):
            matches.append(load_capture(cap_dir.name))
    return matches

def semantic_search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    # Compute query embedding
    query_vec = embed_text(query)
    results = search_index(query_vec, top_k=top_k)
    # Load full data for each hit
    hits: List[Dict[str, Any]] = []
    for r in results:
        hits.append(load_capture(r['id']))
    return hits

def print_summary(captures: List[Dict[str, Any]]):
    if not captures:
        print('No captures found.')
        return
    for cap in captures:
        cid = cap.get('id', '<unknown>')
        meta = cap.get('meta', {})
        cls = cap.get('classification', {})
        title = cls.get('title') or meta.get('title') or '<no title>'
        category = cls.get('para_category', '<no category>')
        tags = ', '.join(cls.get('tags', []))
        summary = cls.get('summary', '')
        preview = cap.get('preview', '')
        print(f"--- Capture ID: {cid}")
        print(f"Title       : {title}")
        print(f"Category    : {category}")
        print(f"Tags        : {tags}")
        print(f"Summary     : {summary}")
        print(f"Preview (200 chars): {preview}")
        print(f"Status      : {meta.get('status', '<unknown>')}")
        print()

def main():
    parser = argparse.ArgumentParser(description='Search captures by keyword, tag, or semantic query.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--keyword', help='Plain‑text keyword to search inside raw content.')
    group.add_argument('--tag', help='Tag name to match in classification.json.')
    group.add_argument('--query', help='Semantic query – uses the embedding index.')
    parser.add_argument('--top', type=int, default=5, help='How many results to return for semantic search.')
    args = parser.parse_args()

    if args.keyword:
        caps = keyword_search(args.keyword)
        print_summary(caps)
    elif args.tag:
        caps = tag_search(args.tag)
        print_summary(caps)
    elif args.query:
        caps = semantic_search(args.query, top_k=args.top)
        print_summary(caps)

if __name__ == '__main__':
    # Ensure we are running from the project root so relative paths work
    cwd = pathlib.Path.cwd()
    if not (cwd / 'raw').exists():
        print('Error: this script must be run from the project root (where the "raw" folder lives).', file=sys.stderr)
        sys.exit(1)
    main()
