import os
from pathlib import Path
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Locate the project root and load the .env file
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # MCP Server Configurations
    MCP_COMMAND = "uv"
    MCP_ARGS = ["run", "mcp_files/scraper_server.py"]
    
    # Storage Backend (MinIO/S3) for cached assets
    STORAGE_ENDPOINT = os.getenv("STORAGE_ENDPOINT", "localhost:9000")
    STORAGE_ACCESS_KEY = os.getenv("STORAGE_ACCESS_KEY", "minioadmin")
    STORAGE_SECRET_KEY = os.getenv("STORAGE_SECRET_KEY", "minioadmin")

    DEFAULT_MODEL = "gemini-2.5-flash"  # Great default balancing speed/cost
    FAST_MODEL = "gemini-3.5-flash"     # Flash is already incredibly fast
    RESEARCH_MODEL = "gemini-3.5-pro"   # Use Pro when you need deep reasoning for matching

    custom_client = AsyncOpenAI(
        api_key=GEMINI_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    custom_model = OpenAIChatCompletionsModel(
        model=DEFAULT_MODEL,
        openai_client=custom_client
    )
