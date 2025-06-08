from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from get_news_agent import get_news

# Load environment variables
load_dotenv()

app = FastAPI()

# Add CORS middleware to allow React frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """Root endpoint to confirm the API is running."""
    return {"message": "Intelligent News API. Use /news to fetch articles."}

@app.get("/news")
def news(category: str = Query(None)):
    """Fetch news articles using the LangChain agent for the specified category."""
    return get_news(category)