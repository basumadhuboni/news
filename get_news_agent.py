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
import urllib.parse

# Explicitly load .env file
load_dotenv()

# Verify environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
COMPANY_ENRICH_API_KEY = os.getenv("COMPANY_ENRICH_API_KEY")

if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY not found in .env file")
if not NEWS_API_KEY:
    print("Error: NEWS_API_KEY not found in .env file")
if not COMPANY_ENRICH_API_KEY:
    print("Error: COMPANY_ENRICH_API_KEY not found in .env file")

# Cache for logo URLs
logo_cache = {}

# Default logo URL
DEFAULT_LOGO_URL = "https://placehold.co/24x24"

# Lazy loading of the SentenceTransformer model
_model = None

def get_model():
    global _model
    if _model is None:
        cache_folder = 'model_cache'  # Local cache directory in project root
        try:
            _model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder=cache_folder)
        except Exception as e:
            print(f"Error loading model from cache: {str(e)}")
            # Fallback to downloading the model if cache fails
            _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def get_domain_from_url(url):
    """Extract the domain from a given URL."""
    parsed = urllib.parse.urlparse(url)
    netloc = parsed.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return netloc

def get_logo_url(domain):
    """Fetch the logo URL for a given domain using Company Enrich API, fall back to Clearbit, or use default."""
    if domain in logo_cache:
        return logo_cache[domain]
    api_key = COMPANY_ENRICH_API_KEY
    if not api_key:
        print("Error: COMPANY_ENRICH_API_KEY not set")
        logo_cache[domain] = DEFAULT_LOGO_URL
        return logo_cache[domain]
    url = f"https://api.companyenrich.com/companies/enrich?domain={domain}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            logo = data.get("logo") or data.get("logo_url") or data.get("image") or (data.get("images") and data.get("images")[0])
            if logo:
                logo_cache[domain] = logo
            else:
                print(f"No logo found in Company Enrich API response for domain {domain}")
                logo_cache[domain] = f"https://logo.clearbit.com/{domain}"
        else:
            print(f"Company Enrich API error for domain {domain}: HTTP {response.status_code}")
            logo_cache[domain] = f"https://logo.clearbit.com/{domain}"
    except Exception as e:
        print(f"Error fetching logo for domain {domain}: {str(e)}")
        logo_cache[domain] = f"https://logo.clearbit.com/{domain}"
    
    # Test if Clearbit URL is valid; if not, use default
    try:
        response = requests.head(logo_cache[domain], timeout=5)
        if response.status_code != 200:
            print(f"Clearbit logo URL invalid for domain {domain}: HTTP {response.status_code}")
            logo_cache[domain] = DEFAULT_LOGO_URL
    except Exception as e:
        print(f"Error validating Clearbit logo for domain {domain}: {str(e)}")
        logo_cache[domain] = DEFAULT_LOGO_URL
    return logo_cache[domain]

@tool
def fetch_all_news_tool(category: str = "general") -> str:
    """Fetch top news headlines for the specified category using NewsAPI and cluster similar articles."""
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
    """Cluster articles based on title and description similarity and include source logos."""
    if not articles:
        return []
    texts = [f"{article['title']} {article['description']}" for article in articles]
    model = get_model()  # Lazy load the model
    embeddings = model.encode(texts, convert_to_tensor=True)
    similarity_matrix = util.cos_sim(embeddings, embeddings).numpy()
    clusters = []
    visited = set()
    for i in range(len(articles)):
        if i in visited:
            continue
        cluster = [articles[i]]
        visited.add(i)
        for j in range(i + 1, len(articles)):
            if j not in visited and similarity_matrix[i][j] > 0.8:
                cluster.append(articles[j])
                visited.add(j)
        clusters.append(cluster)
    merged_articles = []
    for cluster in clusters:
        merged_title = max([article["title"] for article in cluster], key=len) if len(cluster) > 1 else cluster[0]["title"]
        merged_description = max([article["description"] for article in cluster], key=len) if len(cluster) > 1 else cluster[0]["description"]
        sources = [
            {
                "name": article["source"],
                "url": article["url"],
                "logo": get_logo_url(get_domain_from_url(article["url"]))
            }
            for article in cluster
        ]
        merged_articles.append({
            "title": merged_title,
            "description": merged_description,
            "sources": sources
        })
    return merged_articles

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

llm = initialize_llm()
tools = [fetch_all_news_tool]

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