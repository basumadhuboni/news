import os
import requests
import json
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util
import numpy as np

# Explicitly load .env file
load_dotenv()

# Verify environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY not found in .env file")
if not NEWS_API_KEY:
    print("Error: NEWS_API_KEY not found in .env file")

# Initialize SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Define the tool to fetch and cluster news headlines
@tool
def fetch_all_news_tool(category: str = "general") -> str:
    """Fetch top news headlines for the specified category using NewsAPI and cluster similar articles.
    The input should be the category name, such as 'business', 'sports', etc.
    If no category is provided, it defaults to 'general'."""
    if not NEWS_API_KEY:
        return json.dumps({"error": "NEWS_API_KEY not set in environment variables"})
    
    all_articles = []
    queries = [
        {"endpoint": "top-headlines", "params": {"category": category, "country": "in"}},
        {"endpoint": "everything", "params": {"q": f"{category} india", "sortBy": "publishedAt"}}
    ]
    for query in queries:
        try:
            endpoint = query["endpoint"]
            params = query["params"]
            params["apiKey"] = NEWS_API_KEY
            url = f"https://newsapi.org/v2/{endpoint}"
            print(f"Fetching news from {url} with params {params}")
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "ok":
                    articles = [article for article in data["articles"] if article.get("description") and "Google News" not in article["source"]["name"]]
                    for article in articles:
                        all_articles.append({
                            "title": article["title"],
                            "source": article["source"]["id"] or article["source"]["name"],
                            "description": article["description"],
                            "url": article["url"]
                        })
                else:
                    print(f"NewsAPI error for query {query}: {data.get('message', 'Unknown error')}")
            else:
                print(f"Failed to fetch news for query {query}: HTTP {response.status_code} - {response.text}")
        except requests.RequestException as e:
            print(f"Error fetching news for query {query}: {str(e)}")
    
    if not all_articles:
        return json.dumps({"error": f"No articles found for category: {category}. Check API key or rate limits."})

    # Cluster similar articles
    clustered_articles = cluster_articles(all_articles)
    return json.dumps(clustered_articles)

def cluster_articles(articles):
    """Cluster articles based on title and description similarity."""
    if not articles:
        return []

    # Combine title and description for embedding
    texts = [f"{article['title']} {article['description']}" for article in articles]
    embeddings = model.encode(texts, convert_to_tensor=True)

    # Compute cosine similarity
    similarity_matrix = util.cos_sim(embeddings, embeddings).numpy()
    clusters = []
    visited = set()

    for i in range(len(articles)):
        if i in visited:
            continue
        cluster = [articles[i]]
        visited.add(i)
        for j in range(i + 1, len(articles)):
            if j not in visited and similarity_matrix[i][j] > 0.8:  # Similarity threshold
                cluster.append(articles[j])
                visited.add(j)
        clusters.append(cluster)

    # Merge articles in each cluster
    merged_articles = []
    for cluster in clusters:
        if len(cluster) == 1:
            merged_articles.append(cluster[0])
        else:
            # Merge titles and descriptions, keep all URLs and sources
            merged_title = max([article["title"] for article in cluster], key=len)  # Choose longest title
            merged_description = max([article["description"] for article in cluster], key=len)  # Choose longest description
            sources = [article["source"] for article in cluster]
            urls = [article["url"] for article in cluster]
            merged_articles.append({
                "title": merged_title,
                "description": merged_description,
                "sources": sources,
                "urls": urls
            })
    
    return merged_articles

# Define the prompt template for the ReAct agent
prompt_template = PromptTemplate.from_template(
    """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}
"""
)

# Initialize the LLM with error handling
def initialize_llm():
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0,
            google_api_key=GOOGLE_API_KEY
        )
        print("Gemini LLM initialized successfully")
        return llm
    except Exception as e:
        print(f"Failed to initialize Gemini LLM: {str(e)}")
        raise Exception(f"LLM initialization failed: {str(e)}")

# Create the agent with the tool
llm = initialize_llm()
tools = [fetch_all_news_tool]

# Function to get news using the agent
def get_news(category: str = None):
    try:
        prompt = "fetch top news headlines" if category is None else f"fetch top {category} news headlines"
        print(f"Invoking agent with prompt: {prompt}")
        agent = create_react_agent(llm, tools, prompt_template)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, return_intermediate_steps=True)
        result = agent_executor.invoke({"input": prompt})
        if result["intermediate_steps"]:
            _, observation = result["intermediate_steps"][-1]
            print(f"Observation: {observation}")
            data = json.loads(observation)
            if isinstance(data, list):
                return {"news_articles": data}
            elif isinstance(data, dict) and "error" in data:
                return {"news_articles": [], "error": data["error"]}
            else:
                return {"news_articles": [], "error": "Unexpected data format from tool"}
        else:
            return {"news_articles": [], "error": "No intermediate steps found"}
    except Exception as e:
        print(f"Error in get_news: {str(e)}")
        return {"news_articles": [], "error": f"Failed to fetch news: {str(e)}"}