import time
from groq import Groq
from tavily import TavilyClient
from backend.config import GROQ_API_KEY, MODEL_NAME, TAVILY_API_KEY
from backend.foundry_client import search_knowledge, format_context
from backend.prompts import DECOMPOSE_PROMPT, SYNTHESIZE_PROMPT

client = Groq(api_key=GROQ_API_KEY)
tavily = TavilyClient(api_key=TAVILY_API_KEY)


def llm_call(prompt: str, retries: int = 3) -> str:
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1024
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            if attempt < retries - 1:
                print(f"LLM call failed (attempt {attempt + 1}): {e}. Retrying...")
                time.sleep(2)
            else:
                raise Exception(f"LLM call failed after {retries} attempts: {e}")


def decompose_question(question: str) -> list[str]:
    try:
        prompt = DECOMPOSE_PROMPT.format(question=question)
        response = llm_call(prompt)

        sub_questions = []
        for line in response.strip().split("\n"):
            line = line.strip()
            if line and line[0].isdigit():
                cleaned = line.split(".", 1)[-1].strip()
                if cleaned:
                    sub_questions.append(cleaned)

        if not sub_questions:
            return [question]

        return sub_questions[:3]

    except Exception as e:
        print(f"Decomposition failed: {e}")
        return [question]


def search_foundry(sub_questions: list[str]) -> list[dict]:
    """Search Azure AI Search (Foundry IQ) knowledge base."""
    all_results = []
    seen_sources = set()

    for sq in sub_questions:
        try:
            print(f"  [Foundry IQ] Searching: {sq}")
            results = search_knowledge(sq, top_k=2)
            for r in results:
                if r["source"] not in seen_sources:
                    all_results.append({
                        "content": r["content"],
                        "source": r["source"],
                        "type": "foundry"
                    })
                    seen_sources.add(r["source"])
        except Exception as e:
            print(f"  Foundry search failed: {e}")

    return all_results


def search_web(sub_questions: list[str]) -> list[dict]:
    """Search the web using Tavily for real-time information."""
    all_results = []
    seen_urls = set()

    for sq in sub_questions:
        try:
            print(f"  [Tavily Web] Searching: {sq}")
            response = tavily.search(
                query=sq,
                search_depth="basic",
                max_results=2,
                include_answer=False
            )
            for r in response.get("results", []):
                url = r.get("url", "")
                if url not in seen_urls:
                    all_results.append({
                        "content": r.get("content", ""),
                        "source": r.get("title", url),
                        "url": url,
                        "type": "web"
                    })
                    seen_urls.add(url)
        except Exception as e:
            print(f"  Web search failed: {e}")

    return all_results


def format_combined_context(foundry_results: list[dict], web_results: list[dict]) -> str:
    """Format both Foundry IQ and web results into context for the LLM."""
    parts = []

    if foundry_results:
        parts.append("=== Knowledge Base (Foundry IQ) ===")
        for i, r in enumerate(foundry_results, 1):
            parts.append(f"[KB Source {i}: {r['source']}]\n{r['content']}")

    if web_results:
        parts.append("\n=== Web Search Results ===")
        for i, r in enumerate(web_results, 1):
            parts.append(f"[Web Source {i}: {r['source']}]\n{r['content']}")

    return "\n\n".join(parts) if parts else "No relevant information found."


def synthesize_answer(question: str, foundry_results: list[dict], web_results: list[dict]) -> str:
    try:
        context = format_combined_context(foundry_results, web_results)
        prompt = SYNTHESIZE_PROMPT.format(question=question, context=context)
        return llm_call(prompt)
    except Exception as e:
        return f"Unable to generate answer: {e}"


def run_agent(question: str) -> dict:
    question = question.strip()

    if len(question) < 5:
        return {
            "question": question,
            "sub_questions": [],
            "sources": [],
            "answer": "Please ask a more specific question."
        }

    if len(question) > 500:
        question = question[:500]

    print(f"\nQuestion: {question}")

    print("\nStep 1: Decomposing question...")
    sub_questions = decompose_question(question)
    for i, sq in enumerate(sub_questions, 1):
        print(f"  {i}. {sq}")

    print("\nStep 2: Retrieving from Foundry IQ + Web...")
    foundry_results = search_foundry(sub_questions)
    web_results = search_web(sub_questions)
    print(f"  Foundry IQ: {len(foundry_results)} sources")
    print(f"  Web: {len(web_results)} sources")

    all_sources = (
        [r["source"] for r in foundry_results] +
        [r["source"] for r in web_results]
    )

    if not foundry_results and not web_results:
        return {
            "question": question,
            "sub_questions": sub_questions,
            "sources": [],
            "answer": "I couldn't find relevant information for this question."
        }

    print("\nStep 3: Synthesizing answer...")
    answer = synthesize_answer(question, foundry_results, web_results)

    return {
        "question": question,
        "sub_questions": sub_questions,
        "sources": all_sources,
        "answer": answer
    }