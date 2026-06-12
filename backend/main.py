from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, field_validator
from backend.agent import run_agent
import os
import json

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

templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "templates")
)

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")

# Default users always available
DEFAULT_USERS = {
    "abbas": "nust2026",
    "demo": "demo123",
    "judge": "judge2026"
}


def load_users() -> dict:
    users = dict(DEFAULT_USERS)
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                saved = json.load(f)
                users.update(saved)
        except Exception:
            pass
    return users


def save_user(username: str, password: str):
    users = {}
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                users = json.load(f)
        except Exception:
            pass
    users[username] = password
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)


class QueryRequest(BaseModel):
    question: str

    @field_validator("question")
    @classmethod
    def validate_question(cls, v):
        if not v or not v.strip():
            raise ValueError("Question cannot be empty")
        if len(v.strip()) < 5:
            raise ValueError("Question is too short")
        if len(v.strip()) > 500:
            return v.strip()[:500]
        return v.strip()


class QueryResponse(BaseModel):
    question: str
    sub_questions: list[str]
    sources: list[str]
    answer: str


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return RedirectResponse(url="/login")


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="login.html"
    )


@app.post("/login", response_class=HTMLResponse)
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    users = load_users()
    if username in users and users[username] == password:
        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie(key="user", value=username)
        return response
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": "Invalid username or password"}
    )


@app.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="signup.html"
    )


@app.post("/signup", response_class=HTMLResponse)
def signup(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    confirm: str = Form(...)
):
    users = load_users()

    if len(username) < 3:
        return templates.TemplateResponse(
            request=request,
            name="signup.html",
            context={"error": "Username must be at least 3 characters"}
        )
    if len(password) < 6:
        return templates.TemplateResponse(
            request=request,
            name="signup.html",
            context={"error": "Password must be at least 6 characters"}
        )
    if password != confirm:
        return templates.TemplateResponse(
            request=request,
            name="signup.html",
            context={"error": "Passwords do not match"}
        )
    if username in users:
        return templates.TemplateResponse(
            request=request,
            name="signup.html",
            context={"error": "Username already taken"}
        )

    save_user(username, password)
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(key="user", value=username)
    return response


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    user = request.cookies.get("user")
    users = load_users()
    if not user or user not in users:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"username": user}
    )


@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie("user")
    return response


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