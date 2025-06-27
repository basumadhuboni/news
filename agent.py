from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load API key
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise Exception("GOOGLE_API_KEY not found in environment variables.")

# Import tool functions
from tools import extract_article_text, summarize_text, translate_text

# Initialize LLM
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.4,
    )
except Exception as e:
    raise Exception(f"Failed to initialize LLM: {str(e)}")

# Define wrapper for translate_text to handle JSON input
def translate_text_tool(input_str: str) -> str:
    """Wrapper to parse JSON input for translate_text."""
    try:
        input_dict = json.loads(input_str)
        text = input_dict['text']
        target_language = input_dict['target_language']
        logger.info(f"Parsed translate_text input: text='{text[:50]}...', target_language='{target_language}'")
        return translate_text(text, target_language)
    except Exception as e:
        logger.error(f"Error parsing translate_text input: {str(e)}")
        return f"Error parsing input: {str(e)}"

# Define tools
extract_tool = Tool.from_function(
    func=extract_article_text,
    name="extract_article_text",
    description="Extracts main content from a news article URL. Input must be a valid news URL as a string."
)

summarize_tool = Tool.from_function(
    func=summarize_text,
    name="summarize_text",
    description="Summarizes long text into key points. Input must be the text to summarize as a string."
)

translate_tool = Tool.from_function(
    func=translate_text_tool,
    name="translate_text",
    description="Translates text to a specified language. Input must be a JSON string with 'text' and 'target_language' fields."
)

tools = [extract_tool, summarize_tool, translate_tool]

# Define the prompt with explicit examples
prompt = PromptTemplate.from_template(
    """Answer the following questions as best you can. You have access to the following tools:

{tools}

Here are examples of how to use the tools:

Example 1:
Question: Summarize this article: https://example.com/article
Thought: I need to extract the text from the article and then summarize it.
Action: extract_article_text
Action Input: "https://example.com/article"
Observation: [article text]
Thought: Now I will summarize the text.
Action: summarize_text
Action Input: "[article text]"
Observation: [summary]
Thought: I have the summary.
Final Answer: [summary]

Example 2:
Question: Translate this text to Spanish: Hello, how are you?
Thought: I need to translate the text to Spanish.
Action: translate_text
Action Input: {{"text": "Hello, how are you?", "target_language": "Spanish"}}
Observation: [translated text]
Thought: I have the translation.
Final Answer: [translated text]

Rules:
- For `extract_article_text` and `summarize_text`, the Action Input must be a string.
- For `translate_text`, the Action Input must be a JSON string with 'text' and 'target_language' fields.
- If the input format is unclear, infer the correct format from the question.
- If an error occurs (e.g., invalid URL or API issue), include the error message in the Observation and proceed accordingly.
- For translation queries like 'Translate this text to Hindi: [text]', extract the text after the colon and the language before it, and format as a JSON object.

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action, following the examples
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
{agent_scratchpad}"""
)

# Create the agent
try:
    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
except Exception as e:
    raise Exception(f"Failed to create agent: {str(e)}")

# Wrap it in an executor with verbose logging
try:
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
except Exception as e:
    raise Exception(f"Failed to create executor: {str(e)}")