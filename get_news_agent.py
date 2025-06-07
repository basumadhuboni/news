import os
import requests
import json
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate

# Define the tool to fetch news from all sources
@tool
def fetch_all_news_tool(_: str = "") -> str:
    """Fetch top headlines from multiple news sources and return as JSON string."""
    SOURCES = ["bbc-news", "cnn", "reuters", "al-jazeera-english", "the-guardian-uk"]
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    if not NEWS_API_KEY:
        return json.dumps({"error": "NEWS_API_KEY not set in environment variables"})
    
    all_articles = []
    for source in SOURCES:
        try:
            url = f"https://newsapi.org/v2/top-headlines?sources={source}&apiKey={NEWS_API_KEY}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                articles = [article for article in response.json()["articles"] if article.get("description")]
                for article in articles:
                    all_articles.append({
                        "title": article["title"],
                        "source": source,
                        "description": article["description"],
                        "url": article["url"]
                    })
            else:
                print(f"Failed to fetch news from {source}: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error fetching news from {source}: {str(e)}")
    
    return json.dumps(all_articles)

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
            # Create and invoke the agent if LLM is available
            agent = create_react_agent(llm, tools, prompt_template)
            agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
            result = agent_executor.invoke({"input": "fetch news"})
            articles = json.loads(result["output"])
        else:
            # Fallback to direct tool call if LLM initialization failed
            print("Falling back to direct NewsAPI call due to LLM failure")
            articles = json.loads(fetch_all_news_tool.invoke(""))
        return {"news_articles": articles}
    except Exception as e:
        print(f"Error in get_news: {str(e)}")
        return {"news_articles": [], "error": f"Failed to fetch news: {str(e)}"}