from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from backend.agent import run_agent

app = FastAPI(
    title="Career Research Agent",
    description="Multi-step reasoning agent for AI engineering career advice",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


class QueryRequest(BaseModel):
    question: str

    @field_validator("question")
    @classmethod
    def validate_question(cls, v):
        if not v or not v.strip():
            raise ValueError("Question cannot be empty")
        if len(v.strip()) < 5:
            raise ValueError("Question is too short — please be more specific")
        if len(v.strip()) > 500:
            return v.strip()[:500]
        return v.strip()


class QueryResponse(BaseModel):
    question: str
    sub_questions: list[str]
    sources: list[str]
    answer: str


@app.get("/")
def root():
    return {
        "status": "Career Research Agent is running",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    try:
        result = run_agent(request.question)
        return QueryResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Agent error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Agent encountered an error. Please try again."
        )