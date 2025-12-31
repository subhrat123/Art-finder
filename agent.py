import os
from dotenv import load_dotenv
from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search, AgentTool,FunctionTool
from google.genai import types
from comments_agent import youtube
from search_agent import google_search_agent
from pydantic import BaseModel,Field
from typing import List, Literal

load_dotenv()
Google_API_KEY = os.getenv("GOOGLE_API_KEY")

retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504], # Retry on these HTTP errors
)

class Sentiment(BaseModel):
    overall: Literal["positive", "negative", "mixed"]
    confidence: float

class PainPoint(BaseModel):
    text: str
    frequency: int | None = None
    confidence: Literal["high", "medium", "low"]

class Insight(BaseModel):
    text: str
    confidence: Literal["high", "medium", "low"]

class Keyword(BaseModel):
    term: str
    count: int | None = None

class Trend(BaseModel):
    text: str
    direction: Literal["increasing", "decreasing", "stable"]

class Evidence(BaseModel):
    items_analyzed: int
    source_type: str

class AgentAnalysis(BaseModel):
    source: str
    summary: str
    sentiment: Sentiment
    pain_points: list[PainPoint]
    key_insights: list[Insight]
    keywords: list[Keyword]
    trends: list[Trend]
    evidence: Evidence
    
class SourceAnalysis(BaseModel):
    source: str
    analysis: AgentAnalysis

class CombinedAnalysis(BaseModel):
    overall_summary: str
    overall_sentiment: Sentiment
    top_pain_points: List[PainPoint]
    top_keywords: List[Keyword]
    key_takeaways: List[str]

class FinalReportSchema(BaseModel):
    sources: List[SourceAnalysis]
    combined_analysis: CombinedAnalysis

analysis_orchestrator = Agent(
    name="analysis_orchestrator",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config,
    ),
    instruction = """
        You are a Research Orchestrator Agent.

        THIS IS A STRICT TOOL-ORCHESTRATION TASK.

        RULES (MANDATORY):
        - Do NOT summarize.
        - Do NOT explain.
        - Do NOT infer.
        - Do NOT generate insights.
        - Do NOT generate natural language.
        - Do NOT modify tool outputs.

        YOUR ONLY JOB:
        1. Call the YouTube Analysis Agent.
        2. Call the Google Search Analysis Agent.
        3. Collect their returned JSON outputs.
        4. Return them EXACTLY as received in a single JSON object.

        YOU MUST:
        - Use the tools.
        - Return ONLY raw JSON.
        - Follow this exact output format.

        OUTPUT FORMAT:
        {
        "youtube_analysis": <output returned by YouTube agent>,
        "google_search_analysis": <output returned by Google Search agent>
        }
    """,
    tools=[AgentTool(youtube), AgentTool(google_search_agent)],
    output_key="raw_research_data"
)

report_agent= Agent(
    name="report_agent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config,
    ),
  instruction = """
    You are a Report Builder Agent.

    You will receive structured analysis results from multiple sources
    in the following JSON format:

    {
    "youtube_analysis": {...},
    "google_search_analysis": {...}
    }

    TASK:
    Generate a final unified research report.

    AGGREGATION RULES:
    - Deduplicate similar pain points and keywords.
    - If an insight appears in multiple sources, increase confidence.
    - If sentiments conflict, label overall sentiment as 'mixed'.
    - Do NOT invent new insights.
    - Preserve source attribution.

    IMPORTANT RULES:
    - Do NOT use tools.
    - Do NOT output free-form text.
    - Output MUST strictly follow the provided output schema.
    """,
    output_schema=FinalReportSchema,
    output_key="final_research_report",
)

orchestrator_agent= SequentialAgent(
    name="root_agent",
    description="An agent that orchestrates research analysis and report generation.",
    sub_agents=[analysis_orchestrator,report_agent],
)

root_agent=orchestrator_agent
































# research_agent= Agent(
#     name="Research Agent",
#     model=Gemini(
#         model="gemini-2.5-flash-lite",
#         retry_options=retry_config,
#     ),
#     instruction="""You are a research agent. Your only job is to find relevant information on the given topic using provided tools and provide the findings with citations.""",
#     tools=[google_search],
#     output_key="research_findings",
# )

# summarizer_agent = Agent(
#     name="SummarizerAgent",
#     model=Gemini(
#         model="gemini-2.5-flash-lite",
#         retry_options=retry_config
#     ),
#     # The instruction is modified to request a bulleted list for a clear output format.
#     instruction="""Read the provided research findings: {research_findings}
# Create a concise summary as a bulleted list with 3-5 key points.""",
#     output_key="final_summary",
# )

