#!/usr/bin/env python3
"""
Direct Gemini API benchmark test using curl
Tests different models and prompts to identify the fastest configuration
"""
import subprocess
import json
import time
import os

def test_gemini_api_direct():
    """Test Gemini API directly via curl to benchmark performance"""
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY environment variable not set!")
        print("Please run: export GOOGLE_API_KEY=\"your_api_key_here\"")
        return
    
    print("🚀 Testing Direct Gemini API Performance via curl")
    print("=" * 60)
    
    # Test configurations
    models = [
        "gemini-1.5-flash",
        "gemini-2.5-flash"
    ]
    
    prompts = {
        "backend_verbose": """Given the following list of existing shopping item categories:
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

Item to categorize: "jablko"
""",
        
        "ai_endpoint": """You are an expert at organizing shopping lists.
Based on the item name, suggest a single, concise category.
The category should be a common supermarket category (e.g., "Produce", "Dairy", "Meat", "Pantry", "Frozen", "Beverages", "Snacks", "Personal Care", "Household", "Uncategorized").
Return only the category name, with no extra text or punctuation.

Item: "jablko"
Category:
""",
        
        "minimal": """Categorize this shopping item into one word: Produce, Dairy, Meat, Pantry, Frozen, Beverages, Snacks, Personal Care, Household, or Uncategorized.

Item: jablko
Category:""",
        
        "ultra_minimal": """Item: jablko
Category:"""
    }
    
    results = []
    
    for model in models:
        print(f"\n📊 Testing Model: {model}")
        print("-" * 40)
        
        for prompt_name, prompt_text in prompts.items():
            print(f"🧪 Testing prompt: {prompt_name}")
            
            # Prepare the curl request
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            
            # Create the JSON payload
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt_text
                    }]
                }]
            }
            
            # Run curl command and measure time
            start_time = time.time()
            
            try:
                result = subprocess.run([
                    'curl', '-s', '-X', 'POST',
                    '-H', 'Content-Type: application/json',
                    '-d', json.dumps(payload),
                    url
                ], capture_output=True, text=True, timeout=30)
                
                duration = time.time() - start_time
                
                if result.returncode == 0:
                    try:
                        response_data = json.loads(result.stdout)
                        if 'candidates' in response_data:
                            generated_text = response_data['candidates'][0]['content']['parts'][0]['text'].strip()
                            print(f"  ✅ Duration: {duration:.3f}s")
                            print(f"  📝 Response: '{generated_text}'")
                            
                            # Check if response is what we expect
                            if 'produce' in generated_text.lower():
                                print(f"  🎯 Result: CORRECT")
                            else:
                                print(f"  ⚠️  Result: Unexpected")
                                
                            results.append({
                                'model': model,
                                'prompt': prompt_name,
                                'duration': duration,
                                'response': generated_text,
                                'correct': 'produce' in generated_text.lower()
                            })
                        else:
                            print(f"  ❌ Error: {response_data}")
                    except json.JSONDecodeError as e:
                        print(f"  ❌ JSON parse error: {e}")
                        print(f"  📄 Raw response: {result.stdout}")
                else:
                    print(f"  ❌ Curl failed: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                print(f"  ⏰ Timeout: >30s")
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 PERFORMANCE SUMMARY")
    print("=" * 60)
    
    if results:
        print("\n🏆 Best Performing Configurations:")
        
        # Sort by duration
        results.sort(key=lambda x: x['duration'])
        
        for i, result in enumerate(results[:5]):  # Top 5
            status = "✅ CORRECT" if result['correct'] else "❌ WRONG"
            print(f"{i+1}. {result['model']} + {result['prompt']}: {result['duration']:.3f}s {status}")
            
        print(f"\n🚀 RECOMMENDATION:")
        best = results[0]
        print(f"   Model: {best['model']}")
        print(f"   Prompt: {best['prompt']}")
        print(f"   Duration: {best['duration']:.3f}s")
        print(f"   Improvement vs slowest: {(results[-1]['duration'] / best['duration']):.1f}x faster")
        
        # Compare with current backend
        current_backend_time = 5.0  # Based on recent logs showing 5-10s
        improvement = current_backend_time / best['duration']
        print(f"   Improvement vs current backend: {improvement:.1f}x faster")
        
    else:
        print("❌ No successful results to analyze")

if __name__ == "__main__":
    test_gemini_api_direct()
