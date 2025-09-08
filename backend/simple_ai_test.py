#!/usr/bin/env python3
"""
Simple test to check AI categorization issue
"""
import asyncio
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def test_gemini():
    """Test Gemini AI directly"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("No Google API key found")
        return

    print(f"API Key: {api_key[:20]}...")

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = """
        You are an expert at organizing shopping lists.
        Based on the item name, suggest a single, concise category.
        The category should be a common supermarket category (e.g., "Produce", "Dairy & Eggs", "Meat & Seafood", "Bakery", "Pantry", "Frozen Foods", "Beverages", "Household").
        Return only the category name, with no extra text or punctuation.

        Item: "apple"
        Category:
        """

        print("Sending request to Gemini...")
        response = await model.generate_content_async(prompt)
        print(f"Response: '{response.text}'")
        print(f"Response text stripped: '{response.text.strip()}'")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_gemini())
