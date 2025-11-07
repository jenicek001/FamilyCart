#!/usr/bin/env python3
"""
Direct Gemini API performance test using Python requests
Tests the exact prompts used in our backend to identify performance bottlenecks
"""

import json
import os
import time

import requests

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
GEMINI_FAST_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

if not GOOGLE_API_KEY:
    print("❌ Error: GOOGLE_API_KEY environment variable is not set")
    print("Please set it with: export GOOGLE_API_KEY=your_api_key")
    exit(1)

print("🚀 Testing Direct Gemini API Performance")
print("=========================================")
print(f"API Key: {GOOGLE_API_KEY[:20]}...")
print()


def test_prompt(test_name, prompt, item, model_url=GEMINI_API_URL):
    """Test a prompt with the Gemini API"""

    print(f"🧪 Test: {test_name}")
    print(f"📝 Item: '{item}'")
    print(f"⏱️  Starting request...")

    # Prepare the request
    url = f"{model_url}?key={GOOGLE_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    # Make the request and measure time
    start_time = time.time()

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        end_time = time.time()
        duration = end_time - start_time

        print(f"📊 Results:")
        print(f"   HTTP Status: {response.status_code}")
        print(f"   Total Time: {duration:.3f}s")

        if response.status_code == 200:
            try:
                data = response.json()
                ai_response = data["candidates"][0]["content"]["parts"][0][
                    "text"
                ].strip()
                print(f"   ✅ AI Response: '{ai_response}'")

                # Validate response
                expected_categories = [
                    "Produce",
                    "Dairy",
                    "Meat",
                    "Pantry",
                    "Frozen",
                    "Beverages",
                    "Snacks",
                    "Personal Care",
                    "Household",
                    "Uncategorized",
                ]
                if ai_response in expected_categories:
                    print(f"   ✅ Success: Valid category returned")
                elif ai_response:
                    print(f"   ⚠️  Warning: Non-standard category returned")
                else:
                    print(f"   ❌ Error: Empty response")

            except (KeyError, IndexError, json.JSONDecodeError) as e:
                print(f"   ❌ Error parsing response: {e}")
                print(f"   Raw response: {response.text[:200]}...")

        else:
            print(f"   ❌ Error: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}...")

    except requests.exceptions.RequestException as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"   ❌ Request failed after {duration:.3f}s: {e}")

    print("---")
    print()


def main():
    # Test prompts

    # Test 1: Current backend prompt (verbose)
    prompt1 = '''Given the following list of existing shopping item categories:

Produce, Dairy, Meat, Pantry, Frozen, Beverages, Snacks, Personal Care, Household, Uncategorized

What is the best category for the item "jablko"?

IMPORTANT INSTRUCTIONS:
- The item name might be in Czech, German, Spanish, French, or other languages
- The category should be a single noun, in English, and singular
- If a suitable category from the list exists, return it exactly as written
- If not, suggest a new, appropriate category in English
- Return ONLY the category name and nothing else - no punctuation, no explanations

Examples:
- For "mléko" (Czech for milk), return: Dairy
- For "Granny Smith Apples", return: Produce
- For "Cheddar Cheese", return: Dairy
- For "pain" (French for bread), return: Pantry

Item to categorize: "jablko"'''

    # Test 2: AI endpoint prompt (concise)
    prompt2 = """You are an expert at organizing shopping lists.
Based on the item name, suggest a single, concise category.
The category should be a common supermarket category (e.g., "Produce", "Dairy", "Meat", "Pantry", "Frozen", "Beverages", "Snacks", "Personal Care", "Household", "Uncategorized").
Return only the category name, with no extra text or punctuation.

Item: "jablko"
Category:"""

    # Test 3: Minimal prompt
    prompt3 = """Categorize this shopping item into one category: Produce, Dairy, Meat, Pantry, Frozen, Beverages, Snacks, Personal Care, Household, Uncategorized.
Item: jablko
Category:"""

    # Test 4: Ultra minimal
    prompt4 = """Category for "jablko": Produce, Dairy, Meat, Pantry, or other?"""

    # Run tests with gemini-2.5-flash
    print("🔬 Testing with gemini-2.5-flash:")
    test_prompt("Backend Verbose Prompt", prompt1, "jablko")
    test_prompt("AI Endpoint Prompt", prompt2, "jablko")
    test_prompt("Minimal Prompt", prompt3, "jablko")
    test_prompt("Ultra Minimal Prompt", prompt4, "jablko")

    # Test with English item
    prompt2_en = prompt2.replace('"jablko"', '"apple"')
    test_prompt("English Item Test", prompt2_en, "apple")

    # Test with gemini-1.5-flash for comparison
    print("🚀 Testing with gemini-1.5-flash for comparison:")
    test_prompt("Minimal Prompt (1.5-flash)", prompt3, "jablko", GEMINI_FAST_URL)
    test_prompt("Ultra Minimal (1.5-flash)", prompt4, "jablko", GEMINI_FAST_URL)

    # Summary
    print("🎯 Summary:")
    print("- Direct API calls should be much faster than backend (target: <2s)")
    print("- Look for prompts that consistently return correct results")
    print("- Compare gemini-1.5-flash vs gemini-2.5-flash performance")
    print("- If direct API is fast, investigate backend overhead")


if __name__ == "__main__":
    main()
