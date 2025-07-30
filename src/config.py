# config.py
from langchain_groq import ChatGroq
from tavily import TavilyClient
from googleapiclient.discovery import build
import os 
import json
from dotenv import load_dotenv
load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
os.environ["YOUTUBE_API_KEY"] = os.getenv("YOUTUBE_API_KEY")
def load_config():
    """Load API keys and initialize clients."""

    # Initialize LLM
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.environ["GROQ_API_KEY"],
        temperature=0.5,
    )

    # Initialize Tavily for web search
    tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

    # Initialize YouTube API
    youtube = build('youtube', 'v3', developerKey=os.environ["YOUTUBE_API_KEY"])

    return {
        "llm": llm,
        "tavily_client": tavily_client,
        "youtube": youtube
    }