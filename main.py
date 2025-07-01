from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from get_news_agent import get_news
from agent import executor
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://news-frontend.onrender.com"],  # Replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Intelligent News API. Use /news to fetch articles or /query for summarization/translation."}

@app.get("/news")
def news(category: str = Query(None)):
    return get_news(category)

class QueryInput(BaseModel):
    input: str

@app.post("/query")
async def query_agent(data: QueryInput):
    try:
        result = executor.invoke({"input": data.input})
        return {"output": result["output"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)