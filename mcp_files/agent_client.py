from config import Config
import json
from agents import Agent, Runner
from agents.mcp import MCPServerStdio

async def run_price_agent(user_query: str):
    print(f"Agent is investigating: '{user_query}'...")

    # 2. Start the MCP Server using the SDK's context manager
    # This automatically calls .connect() on start and .cleanup() on exit
    async with MCPServerStdio(
        name="Scraper Server",
        params={
            "command": Config.MCP_COMMAND,
            "args": Config.MCP_ARGS,
        }
    ) as mcp_server:

        # 3. Define the Agent and ATTACH the MCP server directly to it
        price_scout = Agent(
            name="Price Scout",
            instructions="You are a shopping assistant. Use your tools to find and compare prices.",
            model=Config.custom_model,
            mcp_servers=[mcp_server]  # <--- Pass the server instance here
        )

        # 4. Run the Agent
        # The Runner executes the agent, which inherently knows about its tools
        result = await Runner.run(
            price_scout, 
            input=user_query
        )

        print("\nFinal Normalized Result:\n", result.final_output)