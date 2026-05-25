import asyncio
import config
from mcp_files.agent_client import run_price_agent
from agents import set_tracing_export_api_key, trace, set_tracing_disabled
from config import Config

set_tracing_disabled(False)
set_tracing_export_api_key(Config.OPENAI_API_KEY)

def main():
    print("Hello from shopping-agent!")
    with trace("shopping-agent"):
        asyncio.run(run_price_agent("Find me the price of Maggi noodles on Zepto and Amazon and compare them."))

if __name__ == "__main__":
    main()
