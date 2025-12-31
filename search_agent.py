import os
from dotenv import load_dotenv
from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search, AgentTool,FunctionTool
from google.genai import types  


load_dotenv()
Google_API_KEY = os.getenv("GOOGLE_API_KEY")

retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504], # Retry on these HTTP errors
)

google_search_agent = Agent(
    name="Google_Search_agent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config,
    ),
    instruction = """
    You are a Google Search Analysis Agent.

    Your task is to:
    1. Use google_search_tool to fetch web articles, blogs, and advertisement-related content for the given topic.
    2. Analyze ONLY the fetched web content.
    3. Extract structured marketing insights relevant for advertisements and user perception.

    IMPORTANT OUTPUT RULES:
    - You MUST return the output strictly in valid JSON.
    - Do NOT wrap the JSON in ```json``` or backticks.
    - Return raw JSON only.
    - You MUST follow the exact schema provided below.
    - Do NOT add extra fields.
    - Do NOT include explanations, markdown, or natural language outside JSON.
    - If some data is missing, return empty arrays or reasonable defaults.
    - Frequency counts should be approximate, based on repetition across articles.

    OUTPUT JSON SCHEMA:
    {
    "source": "google_search",
    "summary": "<concise overall summary of web-based insights>",
    "sentiment": {
        "overall": "positive | negative | mixed",
        "confidence": <number between 0 and 1>
    },
    "pain_points": [
        {
        "text": "<pain point mentioned in articles>",
        "frequency": <approx count>,
        "confidence": "high | medium | low"
        }
    ],
    "key_insights": [
        {
        "text": "<insight derived from web content>",
        "confidence": "high | medium | low"
        }
    ],
    "keywords": [
        {
        "term": "<important keyword>",
        "count": <approx count>
        }
    ],
    "trends": [
        {
        "text": "<observed market or advertising trend>",
        "direction": "increasing | decreasing | stable"
        }
    ],
    "evidence": {
        "items_analyzed": <number of articles>,
        "source_type": "web_articles"
    }
    }
    """,
    tools=[google_search],
    output_key="google_search_agent_output",
)

