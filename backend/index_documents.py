import os
import json
import httpx
from backend.config import AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_KEY, FOUNDRY_INDEX_NAME

DOCS_PATH = "data/sample_docs"

def create_index():
    url = f"{AZURE_SEARCH_ENDPOINT}/indexes/{FOUNDRY_INDEX_NAME}?api-version=2024-05-01-preview"
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_SEARCH_KEY
    }
    schema = {
        "name": FOUNDRY_INDEX_NAME,
        "fields": [
            {"name": "id", "type": "Edm.String", "key": True, "filterable": True},
            {"name": "content", "type": "Edm.String", "searchable": True, "analyzer": "standard.lucene"},
            {"name": "source", "type": "Edm.String", "searchable": True, "filterable": True}
        ]
    }
    response = httpx.put(url, json=schema, headers=headers, timeout=30)
    if response.status_code in [200, 201]:
        print("Index created successfully")
    else:
        print(f"Index creation response: {response.status_code} - {response.text}")

def upload_documents():
    url = f"{AZURE_SEARCH_ENDPOINT}/indexes/{FOUNDRY_INDEX_NAME}/docs/index?api-version=2024-05-01-preview"
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_SEARCH_KEY
    }

    documents = []
    for i, filename in enumerate(os.listdir(DOCS_PATH)):
        if filename.endswith(".txt"):
            filepath = os.path.join(DOCS_PATH, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            documents.append({
                "@search.action": "mergeOrUpload",
                "id": str(i + 1),
                "content": content,
                "source": filename
            })
            print(f"Prepared: {filename}")

    body = {"value": documents}
    response = httpx.post(url, json=body, headers=headers, timeout=30)
    if response.status_code == 200:
        print(f"\nSuccessfully uploaded {len(documents)} documents to index")
    else:
        print(f"Upload error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("Step 1: Creating index...")
    create_index()
    print("\nStep 2: Uploading documents...")
    upload_documents()
    print("\nDone! Your knowledge base is ready.")