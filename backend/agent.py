import time
from groq import Groq
from backend.config import GROQ_API_KEY, MODEL_NAME
from backend.foundry_client import search_knowledge, format_context
from backend.prompts import DECOMPOSE_PROMPT, SYNTHESIZE_PROMPT

client = Groq(api_key=GROQ_API_KEY)


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
            print("Decomposition parsing failed, using original question")
            return [question]

        return sub_questions[:3]

    except Exception as e:
        print(f"Decomposition failed: {e}")
        return [question]


def retrieve_for_subquestions(sub_questions: list[str]) -> list[dict]:
    all_results = []
    seen_sources = set()

    for sq in sub_questions:
        try:
            print(f"  Searching: {sq}")
            results = search_knowledge(sq, top_k=2)
            for r in results:
                if r["source"] not in seen_sources:
                    all_results.append(r)
                    seen_sources.add(r["source"])
        except Exception as e:
            print(f"  Search failed for sub-question: {e}")
            continue

    return all_results


def synthesize_answer(question: str, results: list[dict]) -> str:
    try:
        context = format_context(results)
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

    print("\nStep 2: Retrieving from Foundry IQ...")
    results = retrieve_for_subquestions(sub_questions)
    print(f"  Found {len(results)} unique sources")

    if not results:
        return {
            "question": question,
            "sub_questions": sub_questions,
            "sources": [],
            "answer": "I couldn't find relevant information for this question. Try asking about AI engineering careers, salaries, skills, or interview preparation."
        }

    print("\nStep 3: Synthesizing answer...")
    answer = synthesize_answer(question, results)

    return {
        "question": question,
        "sub_questions": sub_questions,
        "sources": [r["source"] for r in results],
        "answer": answer
    }