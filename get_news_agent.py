import os
import requests
import json
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate

# Define the tool to fetch top news headlines
@tool
def fetch_all_news_tool(_: str = "") -> str:
    """Fetch top news headlines from a wide variety of sources using NewsAPI and return as JSON string."""
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    if not NEWS_API_KEY:
        return json.dumps({"error": "NEWS_API_KEY not set in environment variables"})
    
    all_articles = []
    # Try multiple queries to maximize article retrieval
    queries = [
        {"endpoint": "top-headlines", "params": {"country": "in"}},
        {"endpoint": "top-headlines", "params": {"country": "us"}},
        {"endpoint": "top-headlines", "params": {"country": "gb"}},
        {"endpoint": "top-headlines", "params": {"country": "au"}},
        {"endpoint": "top-headlines", "params": {"country": "ca"}},
        {"endpoint": "top-headlines", "params": {"country": "de"}},
        {"endpoint": "top-headlines", "params": {"category": "general"}},
        {"endpoint": "top-headlines", "params": {"category": "world"}}
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
    
    # Remove duplicates based on URL
    unique_articles = {article["url"]: article for article in all_articles}.values()
    if not unique_articles:
        return json.dumps({"error": "No articles found from NewsAPI. Check API key or rate limits."})
    return json.dumps(list(unique_articles))

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
        return ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    except Exception as e:
        print(f"Failed to initialize OpenAI LLM: {str(e)}")
        return None

llm = initialize_llm()

# Create the agent with the tool
tools = [fetch_all_news_tool]

# Function to get news using the agent or fallback
def get_news():
    try:
        if llm:
            # Create and invoke the agent with "fetch top news headlines"
            agent = create_react_agent(llm, tools, prompt_template)
            agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
            result = agent_executor.invoke({"input": "fetch top news headlines"})
            articles = json.loads(result["output"])
        else:
            # Fallback to direct tool call if LLM initialization failed
            print("Falling back to direct NewsAPI call due to LLM failure")
            articles = json.loads(fetch_all_news_tool.invoke(""))
        return {"news_articles": articles}
    except Exception as e:
        print(f"Error in get_news: {str(e)}")
        return {"news_articles": [], "error": f"Failed to fetch news: {str(e)}"}