from mcp.server.fastmcp import FastMCP
import json

# Initialize the MCP Server
mcp = FastMCP("PriceAggregatorScraper")

@mcp.tool()
def search_zepto(product_name: str) -> str:
    """Searches Zepto for a product and returns JSON data with prices."""
    # TODO: Implement actual Zepto internal API call here
    mock_data = [
        {"platform": "Zepto", "title": f"{product_name} 140g", "price": 28.00, "delivery": "10 mins"}
    ]
    return json.dumps(mock_data)

@mcp.tool()
def search_amazon(product_name: str) -> str:
    """Searches Amazon for a product and returns JSON data with prices."""
    # TODO: Implement actual Playwright/Selenium scraping here
    mock_data = [
        {"platform": "Amazon", "title": f"{product_name} Pack of 2", "price": 55.00, "delivery": "Next Day"}
    ]
    return json.dumps(mock_data)

if __name__ == "__main__":
    # Runs the server using standard input/output
    mcp.run()