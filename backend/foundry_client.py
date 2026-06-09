import httpx
from backend.config import AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_KEY, FOUNDRY_INDEX_NAME


def search_knowledge(query: str, top_k: int = 3) -> list[dict]:
    """
    Search the Foundry IQ knowledge index for relevant documents.
    Returns a list of results with content and source citation.
    """
    url = (
        f"{AZURE_SEARCH_ENDPOINT}/indexes/{FOUNDRY_INDEX_NAME}"
        f"/docs/search?api-version=2024-05-01-preview"
    )
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_SEARCH_KEY
    }
    body = {
        "search": query,
        "top": top_k,
        "select": "content,source"
    }

    try:
        response = httpx.post(url, json=body, headers=headers, timeout=30)
        response.raise_for_status()
        results = response.json().get("value", [])

        return [
            {
                "content": r.get("content", ""),
                "source": r.get("source", "unknown"),
                "score": r.get("@search.score", 0)
            }
            for r in results
        ]
    except Exception as e:
        print(f"Search error: {e}")
        return []


def format_context(results: list[dict]) -> str:
    """
    Format search results into a readable context block for the LLM.
    """
    if not results:
        return "No relevant information found."

    context_parts = []
    for i, r in enumerate(results, 1):
        context_parts.append(
            f"[Source {i}: {r['source']}]\n{r['content']}"
        )

    return "\n\n".join(context_parts)