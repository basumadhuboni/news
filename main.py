from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from get_news_agent import get_news
from agent import executor
import logging

logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG for more detail
logger = logging.getLogger(__name__)

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
    return {"message": "Intelligent News API. Use /news to fetch articles or /query for summarization/translation."}

@app.get("/news")
def news(category: str = Query(None)):
    """Fetch news articles using the LangChain agent for the specified category."""
    return get_news(category)

class QueryInput(BaseModel):
    input: str

@app.post("/query")
async def query_agent(data: QueryInput):
    """Process summarization and translation queries using the agent."""
    try:
        result = executor.invoke({"input": data.input})
        return {"output": result["output"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")