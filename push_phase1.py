import os, json, sys, base64, requests

def read_file(path):
    with open(path, "rb") as f:
        return f.read()

def main():
    token = os.getenv("GH_TOKEN")
    if not token:
        print("Error: GH_TOKEN environment variable not set.")
        sys.exit(1)
    owner = "Saksham24020"
    repo = "Second-self-Ai-brain"
    commit_message = "Feat: Complete Phase 1 - Core Data Capture Architecture"
    api_base = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}

    # Try to get default branch ref (main first, then master)
    ref_resp = requests.get(f"{api_base}/git/ref/heads/main", headers=headers)
    if ref_resp.status_code == 404:
        ref_resp = requests.get(f"{api_base}/git/ref/heads/master", headers=headers)
    # Determine if repository is empty (409 response) or no ref exists
    if ref_resp.status_code in (404, 409):
        base_tree_sha = None
        base_sha = None
    else:
        base_sha = ref_resp.json()["object"]["sha"]
        commit_resp = requests.get(f"{api_base}/git/commits/{base_sha}", headers=headers)
        commit_data = commit_resp.json()
        base_tree_sha = commit_data["tree"]["sha"]

    # Files we want to push (exclude private data)
    files_to_push = [
        ".gitignore",
        "README.md",
        "requirements.txt",
        ".env.example",
        "src/__init__.py",
        "src/capture.py",
        "src/parsing/__init__.py",
        "src/parsing/text_extract.py",
        "src/storage/__init__.py",
        "src/storage/manifest.py",
        "src/llm/__init__.py",
        "src/llm/client.py",
        "src/llm/prompts.py",
    ]

    blobs = []
    for rel_path in files_to_push:
        abs_path = os.path.abspath(rel_path)
        if not os.path.isfile(abs_path):
            print(f"Skipping missing file: {rel_path}")
            continue
        content = read_file(abs_path)
        b64_content = base64.b64encode(content).decode('utf-8')
        blob_resp = requests.post(
            f"{api_base}/git/blobs",
            headers=headers,
            json={"content": b64_content, "encoding": "base64"},
        )
        if blob_resp.status_code != 201:
            print(f"Failed to create blob for {rel_path}: {blob_resp.status_code} {blob_resp.text}")
            sys.exit(1)
        blob_sha = blob_resp.json()["sha"]
        blobs.append({"path": rel_path, "mode": "100644", "type": "blob", "sha": blob_sha})
        print(f"Created blob for {rel_path}")

    # Create a tree (empty base if repo empty)
    tree_payload = {"tree": blobs}
    if base_tree_sha:
        tree_payload["base_tree"] = base_tree_sha
    tree_resp = requests.post(
        f"{api_base}/git/trees",
        headers=headers,
        json=tree_payload,
    )
    if tree_resp.status_code != 201:
        print(f"Failed to create tree: {tree_resp.status_code} {tree_resp.text}")
        sys.exit(1)
    new_tree_sha = tree_resp.json()["sha"]
    print(f"Created new tree: {new_tree_sha}")

    # Create commit
    commit_payload = {"message": commit_message, "tree": new_tree_sha}
    if base_sha:
        commit_payload["parents"] = [base_sha]
    commit_resp = requests.post(
        f"{api_base}/git/commits",
        headers=headers,
        json=commit_payload,
    )
    if commit_resp.status_code != 201:
        print(f"Failed to create commit: {commit_resp.status_code} {commit_resp.text}")
        sys.exit(1)
    new_commit_sha = commit_resp.json()["sha"]
    print(f"Created commit: {new_commit_sha}")

    # Create or update branch ref (main)
    ref_body = {"ref": "refs/heads/main", "sha": new_commit_sha}
    ref_create_resp = requests.post(f"{api_base}/git/refs", headers=headers, json=ref_body)
    if ref_create_resp.status_code == 422:  # already exists
        ref_update_resp = requests.patch(f"{api_base}/git/refs/heads/main", headers=headers, json={"sha": new_commit_sha, "force": True})
        if ref_update_resp.status_code not in (200, 201):
            print(f"Failed to update branch ref: {ref_update_resp.status_code} {ref_update_resp.text}")
            sys.exit(1)
        print("Branch reference updated.")
    elif ref_create_resp.status_code in (201, 200):
        print("Branch reference created.")
    else:
        print(f"Failed to create branch ref: {ref_create_resp.status_code} {ref_create_resp.text}")
        sys.exit(1)
    print("✅ Push to GitHub completed successfully!")

if __name__ == "__main__":
    main()
