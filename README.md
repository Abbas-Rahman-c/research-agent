# Career Research Agent 🤖

A multi-step AI reasoning agent that answers career and job market questions for engineers — powered by **Groq (LLaMA 3.3 70B)** and **Azure AI Search (Foundry IQ)**.

Built for the **Agents League Hackathon 2026** by Microsoft.

---

## What it does

You ask a career question. The agent:

1. **Decomposes** it into 3 targeted sub-questions
2. **Retrieves** relevant grounded information from a knowledge base via Azure AI Search (Foundry IQ)
3. **Synthesizes** a final cited answer using LLaMA 3.3 70B on Groq

Every answer includes citations back to the source documents — no hallucination, fully grounded.

---

## Demo

**Example questions to try:**
- What is the salary of an AI engineer in 2026?
- What skills should I learn for a high paying AI job?
- How do I write a strong AI engineering resume?
- How do I prepare for an AI engineering interview?
- How do I get a job at Google as an ML engineer?

---

## Architecture

```
User Question
      ↓
Streamlit UI (frontend/app.py)
      ↓
FastAPI Backend (backend/main.py)
      ↓
Reasoning Agent (backend/agent.py)
      ↓
┌──────────────────────────────────────┐
│  Step 1: Decompose into sub-questions │
│  Step 2: Retrieve via Foundry IQ      │
│  Step 3: Synthesize cited answer      │
└──────────────────────────────────────┘
      ↓
Cited Answer returned to UI
```

---

## Microsoft IQ Layer

This project uses **Azure AI Search (Foundry IQ)** as the required Microsoft IQ intelligence layer.

- Knowledge index hosted on Azure AI Search (UAE North)
- Documents indexed: AI jobs market, engineering salaries, top skills, resume tips, interview prep
- Retrieval returns grounded chunks with source citations
- Reduces hallucination by grounding every answer in retrieved documents

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq — LLaMA 3.3 70B Versatile |
| IQ Layer | Azure AI Search (Foundry IQ) |
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Language | Python 3.11 |

---

## Project Structure

```
research-agent/
│
├── backend/
│   ├── main.py              ← FastAPI app, POST /query endpoint
│   ├── agent.py             ← Multi-step reasoning loop
│   ├── foundry_client.py    ← Azure AI Search (Foundry IQ) retrieval
│   ├── prompts.py           ← Decompose + synthesize prompt templates
│   ├── config.py            ← Environment variable loader
│   └── index_documents.py  ← Script to index knowledge base documents
│
├── frontend/
│   └── app.py               ← Streamlit UI
│
├── data/
│   └── sample_docs/         ← Knowledge base documents
│       ├── ai_jobs_2026.txt
│       ├── engineering_salaries.txt
│       ├── top_skills_2026.txt
│       ├── resume_tips.txt
│       └── interview_prep.txt
│
├── .env.example             ← Environment variable template
├── requirements.txt         ← Python dependencies
└── README.md
```

---

## Setup & Installation

### Prerequisites
- Python 3.11+
- Azure account (free tier works)
- Groq API key (free at console.groq.com)

### 1. Clone the repo

### 2. Create virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\Activate.ps1

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Fill in your `.env`:

```
GROQ_API_KEY=your-groq-key
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_KEY=your-search-key
FOUNDRY_INDEX_NAME=research-index
MODEL_NAME=llama-3.3-70b-versatile
```

### 5. Index your documents

```bash
python -m backend.index_documents
```

### 6. Run the backend

```bash
uvicorn backend.main:app --reload --port 8000
```

### 7. Run the frontend (new terminal)

```bash
streamlit run frontend/app.py
```

Open `http://localhost:8501` in your browser.

---

## How the reasoning works

```
Question: "What skills do I need for a high paying AI job?"

Step 1 — Decompose:
  1. What are the most in-demand AI engineering skills in 2026?
  2. What technical skills command the highest salary premium?
  3. What certifications complement AI engineering skills?

Step 2 — Retrieve (Foundry IQ):
  → top_skills_2026.txt
  → engineering_salaries.txt
  → ai_jobs_2026.txt

Step 3 — Synthesize:
  → Final cited answer with [Source X] notation
```

---

## Judging criteria alignment

| Criterion | How this project addresses it |
|---|---|
| Accuracy & Relevance (20%) | Foundry IQ grounds every answer in real documents — no hallucination |
| Reasoning & Multi-step (20%) | Explicit decompose → retrieve → synthesize pipeline visible to user |
| Creativity & Originality (15%) | Career research agent with real-world value for engineers |
| User Experience (15%) | Clean Streamlit UI with quick-action buttons and reasoning trace |
| Reliability & Safety (20%) | Retry logic, input validation, graceful fallbacks on every layer |
| Community vote (10%) | — |

---

## API Reference

### POST /query

Request:
```json
{
  "question": "What is the salary of an AI engineer in 2026?"
}
```

Response:
```json
{
  "question": "What is the salary of an AI engineer in 2026?",
  "sub_questions": [
    "What is the average salary range for AI engineers in 2026?",
    "How does location affect AI engineer salaries?",
    "What factors influence AI engineering compensation?"
  ],
  "sources": [
    "ai_jobs_2026.txt",
    "engineering_salaries.txt"
  ],
  "answer": "According to [Source 1: ai_jobs_2026.txt], entry-level AI engineer salaries range from $120,000 to $160,000 in the United States..."
}
```

---

## Built by

**Abbas Rahman** — EE Student, NUST Islamabad
ML Research Intern @ SINES NUST | ML Engineer Intern @ PM Accelerator

---

*Agents League Hackathon 2026 · Microsoft Foundry IQ*
