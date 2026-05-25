import mcp.client.session
from openai import AsyncOpenAI
from agents import Agent, Runner
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from agents.mcp import MCPServerStdio
from config import Config
import datetime

# 1. Save the original call_tool method in memory
original_call_tool = mcp.client.session.ClientSession.call_tool

# 2. Create a custom wrapper using the EXACT parameter name MCP expects
async def custom_call_tool(self, name: str, arguments: dict = None, **kwargs):
    # Use 'read_timeout_seconds' and a timedelta object!
    kwargs['read_timeout_seconds'] = datetime.timedelta(seconds=30.0) 
    return await original_call_tool(self, name, arguments, **kwargs)

# 3. Overwrite the SDK's method with our custom wrapper
mcp.client.session.ClientSession.call_tool = custom_call_tool

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
            mcp_servers=[mcp_server]  
        )

        # 4. Run the Agent
        # The Runner executes the agent, which inherently knows about its tools
        result = await Runner.run(
            price_scout, 
            input=user_query
        )

        print("\nFinal Normalized Result:\n", result.final_output)