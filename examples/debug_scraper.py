"""
Debug script to see what Publix website actually contains

This helps us understand the structure and improve the scraper.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from playwright.sync_api import sync_playwright
import json


def debug_publix_page(state: str = "FL"):
    """Debug what's actually on the Publix page"""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Show browser so you can see
        page = browser.new_page()

        print("Loading Publix store locator...")
        page.goto(
            "https://www.publix.com/shopping/store-locator",
            wait_until="domcontentloaded",
        )

        import time

        time.sleep(5)  # Wait for JavaScript

        print("\n=== Checking for JavaScript Variables ===")
        js_vars = page.evaluate(
            """
            () => {
                const vars = {};
                for (let key in window) {
                    if (key.toLowerCase().includes('store') || 
                        key.toLowerCase().includes('location') ||
                        key.toLowerCase().includes('publix')) {
                        try {
                            vars[key] = typeof window[key];
                        } catch(e) {}
                    }
                }
                return vars;
            }
        """
        )
        print("JavaScript variables found:")
        for key, val_type in js_vars.items():
            print(f"  - {key}: {val_type}")

        print("\n=== Checking for Script Tags ===")
        scripts = page.evaluate(
            """
            () => {
                const scripts = document.querySelectorAll('script');
                const results = [];
                for (let script of scripts) {
                    const text = script.textContent || '';
                    if (text.includes('store') || text.includes('location') || text.includes('publix')) {
                        results.push({
                            type: script.type,
                            length: text.length,
                            preview: text.substring(0, 200)
                        });
                    }
                }
                return results;
            }
        """
        )
        print(f"Found {len(scripts)} relevant script tags")
        for i, script in enumerate(scripts[:5], 1):
            print(f"\n{i}. Type: {script['type']}, Length: {script['length']}")
            print(f"   Preview: {script['preview'][:150]}...")

        print("\n=== Checking for Store Elements ===")
        elements = page.query_selector_all(
            "div, article, li, [class*='store'], [class*='location']"
        )
        print(f"Found {len(elements)} potential elements")

        # Check first few elements
        for i, el in enumerate(elements[:10], 1):
            text = el.inner_text()[:100]
            classes = el.get_attribute("class") or ""
            if "publix" in text.lower() or "store" in text.lower():
                print(f"\n{i}. Classes: {classes[:50]}")
                print(f"   Text: {text}")

        print("\n=== Checking Network Requests ===")
        api_calls = []

        def handle_response(response):
            url = response.url
            if any(kw in url.lower() for kw in ["store", "location", "api", "locator"]):
                api_calls.append(url)

        page.on("response", handle_response)

        # Try searching
        try:
            search_input = page.query_selector(
                "input[type='search'], input[placeholder*='search' i]"
            )
            if search_input:
                search_input.fill(state)
                time.sleep(1)
                search_button = page.query_selector(
                    "button[type='submit'], button:has-text('Search')"
                )
                if search_button:
                    search_button.click()
                    time.sleep(3)
        except:
            pass

        print(f"\nFound {len(api_calls)} relevant API calls:")
        for url in api_calls[:10]:
            print(f"  - {url}")

        print("\n=== Page HTML Sample ===")
        html_sample = page.evaluate("() => document.body.innerHTML.substring(0, 2000)")
        print(html_sample[:500])

        print("\n\nPress Enter to close browser...")
        input()

        browser.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--state", default="FL")
    args = parser.parse_args()
    debug_publix_page(args.state)
