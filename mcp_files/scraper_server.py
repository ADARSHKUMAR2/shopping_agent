from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright
import json
import urllib.parse

# Initialize the MCP Server
mcp = FastMCP("PriceAggregatorScraper")

@mcp.tool()
async def search_amazon(product_name: str) -> str:
    """Searches Amazon for a product in real-time and returns JSON data with titles and prices."""
    encoded_query = urllib.parse.quote(product_name)
    # Using amazon.in as an example, swap to .com if needed
    url = f"https://www.amazon.in/s?k={encoded_query}" 
    
    results = []
    
    async with async_playwright() as p:
        # Launch headless browser with a realistic User-Agent to avoid immediate blocks
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "stylesheet", "font"] else route.continue_())

        try:
            await page.goto(url, timeout=15000)
            # Wait for search results to load on the page
            await page.wait_for_selector(".s-result-item", timeout=5000)
            
            # Select individual product cards (filtering out purely promotional text)
            products = await page.query_selector_all(".s-result-item[data-component-type='s-search-result']")
            
            for product in products[:3]:  # Grab top 3 matches to avoid token bloat
                title_el = await product.query_selector("h2 a span")
                price_el = await product.query_selector(".a-price-whole")
                
                if title_el and price_el:
                    title = await title_el.inner_text()
                    price = await price_el.inner_text()
                    results.append({
                        "platform": "Amazon",
                        "title": title.strip(),
                        "price": f"₹{price.strip()}",
                        "delivery": "See site for details"
                    })
        except Exception as e:
            return json.dumps([{"error": f"Amazon scrape failed: {str(e)}"}])
        finally:
            await browser.close()
            
    return json.dumps(results if results else [{"message": "No matching products found on Amazon."}])


@mcp.tool()
async def search_zepto(product_name: str) -> str:
    """Searches Zepto for a product in real-time and returns JSON data with titles and prices."""
    encoded_query = urllib.parse.quote(product_name)
    url = f"https://www.zeptonow.com/search?q={encoded_query}"
    
    results = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "stylesheet", "font"] else route.continue_())
        
        try:
            await page.goto(url, timeout=15000)
            # Wait for Zepto's product grid items to register
            await page.wait_for_selector("[data-testid='product-card']", timeout=5000)
            
            products = await page.query_selector_all("[data-testid='product-card']")
            
            for product in products[:3]:
                title_el = await product.query_selector("[data-testid='product-card-name']")
                price_el = await product.query_selector("[data-testid='product-card-price']")
                
                if title_el and price_el:
                    title = await title_el.inner_text()
                    price = await price_el.inner_text()
                    
                    # Zepto often has discounted prices shown near raw prices; keep it clean
                    clean_price = price.split("\n")[0].strip() 
                    
                    results.append({
                        "platform": "Zepto",
                        "title": title.strip(),
                        "price": clean_price,
                        "delivery": "10 mins"
                    })
        except Exception as e:
            return json.dumps([{"error": f"Zepto scrape failed: {str(e)}"}])
        finally:
            await browser.close()
            
    return json.dumps(results if results else [{"message": "No matching products found on Zepto."}])

if __name__ == "__main__":
    # Runs the server using standard input/output
    mcp.run()