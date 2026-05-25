from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright
import json
import urllib.parse
from playwright_stealth import Stealth

mcp = FastMCP("PriceAggregatorScraper")

@mcp.tool()
async def search_amazon(product_name: str) -> str:
    """Searches Amazon for a product in real-time and returns JSON data with titles and prices."""
    encoded_query = urllib.parse.quote(product_name)
    url = f"https://www.amazon.in/s?k={encoded_query}" 
    results = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        stealth = Stealth()
        await stealth.apply_stealth_async(page)

        try:
            await page.goto(url, timeout=25_000, wait_until="domcontentloaded")
            
            # Print the title to the terminal so you know if Amazon blocked you
            page_title = await page.title()
            print(f"\n[AMAZON] Page loaded as: {page_title}")

            if await page.query_selector("form[action='/errors/validateCaptcha']"):
                print("🚨 AMAZON CAPTCHA DETECTED! You have 20 seconds to solve it in the browser... 🚨")
                await page.wait_for_timeout(20000) # Hard pause to let you type
            else:
                # Add a brief pause just in case Amazon is slow to render the dynamic React elements
                await page.wait_for_timeout(3000)

            # Relaxed selector: Grabbing any search result item
            products = await page.query_selector_all("[data-component-type='s-search-result']")
            
            for product in products[:3]: 
                title_el = await product.query_selector("h2") # Simplified title selector
                price_el = await product.query_selector(".a-price .a-offscreen") # Alternative hidden price tag Amazon uses
                
                # Fallback to the visible whole price if offscreen isn't there
                if not price_el:
                    price_el = await product.query_selector(".a-price-whole")
                
                if title_el and price_el:
                    title = await title_el.inner_text()
                    # Playwright inner_text on hidden elements sometimes requires inner_html evaluation, but text_content is safer
                    price = await price_el.text_content() 
                    
                    results.append({
                        "platform": "Amazon",
                        "title": title.strip(),
                        "price": price.strip(),
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
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            geolocation={"latitude": 28.9845, "longitude": 77.7064}, 
            permissions=["geolocation"] 
        )
        page = await context.new_page()
        stealth = Stealth()
        await stealth.apply_stealth_async(page)
        
        try:
            await page.goto(url, timeout=25_000, wait_until="domcontentloaded")
            
            # --- THE HUMAN INTERVENTION PAUSE ---
            print("\n🛒 [ZEPTO] Please click 'Select Location' and type Meerut! You have 25 seconds... 🛒\n")
            await page.wait_for_timeout(25_000) # Increased from 15s to 25s

            # We use a try/except block specifically for the selector to catch if the UI changed
            try:
                await page.wait_for_selector("[data-testid='product-card']", timeout=20000) # Increased from 10s to 20s
            except Exception:
                print("⚠️ Zepto product card selector failed. Trying generic fallback...")
                # If they changed the test-id, wait for any link that looks like a product
                await page.wait_for_selector("a[href*='/pn/']", timeout=10000)

            products = await page.query_selector_all("[data-testid='product-card']")
            if not products:
                products = await page.query_selector_all("a[href*='/pn/']")
            
            for product in products[:3]:
                title_el = await product.query_selector("[data-testid='product-card-name']")
                price_el = await product.query_selector("[data-testid='product-card-price']")
                
                if title_el and price_el:
                    title = await title_el.inner_text()
                    price = await price_el.inner_text()
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
    mcp.run()