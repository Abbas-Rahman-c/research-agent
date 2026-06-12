from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
AZURE_FOUNDRY_ENDPOINT = os.getenv("AZURE_FOUNDRY_ENDPOINT")
AZURE_FOUNDRY_KEY = os.getenv("AZURE_FOUNDRY_KEY")
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
FOUNDRY_INDEX_NAME = os.getenv("FOUNDRY_INDEX_NAME", "research-index")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")