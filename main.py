from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from dotenv import load_dotenv
import os

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

# Get API key from environment variable
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# News sources to fetch from
SOURCES = ["bbc-news", "cnn", "reuters", "al-jazeera-english", "the-guardian-uk"]

@app.get("/")
def read_root():
    """Root endpoint to confirm the API is running."""
    return {"message": "Intelligent News API. Use /news to fetch articles."}

def fetch_articles(source):
    """Fetch top headlines from a specific news source."""
    url = f"https://newsapi.org/v2/top-headlines?sources={source}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return [article for article in response.json()["articles"] if article["description"]]
    return []

@app.get("/news")
def get_news():
    """Fetch news articles from multiple sources."""
    all_articles = []
    for source in SOURCES:
        articles = fetch_articles(source)
        for article in articles:
            all_articles.append({
                "title": article["title"],
                "source": source,
                "description": article["description"],
                "url": article["url"]
            })
    return {"news_articles": all_articles}