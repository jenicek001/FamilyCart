#!/bin/bash
# Fixed curl test framework for benchmarking direct Gemini API performance

# Configuration
GOOGLE_API_KEY="${GOOGLE_API_KEY}"
GEMINI_API_URL="https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ Error: GOOGLE_API_KEY environment variable is not set"
    echo "Please set it with: export GOOGLE_API_KEY=your_api_key"
    exit 1
fi

echo "🚀 Testing Direct Gemini API Performance via curl"
echo "=================================================="
echo "Model: gemini-2.5-flash"
echo "API URL: $GEMINI_API_URL"
echo ""

# Test function with proper JSON escaping
test_prompt() {
    local test_name="$1"
    local prompt="$2"
    local item="$3"
    
    echo "🧪 Test: $test_name"
    echo "📝 Item: '$item'"
    echo "⏱️  Starting request..."
    
    # Record start time
    start_time=$(date +%s.%N)
    
    # Create JSON payload using python to handle escaping properly
    json_payload=$(python3 -c "
import json
prompt = '''$prompt'''
payload = {
    'contents': [{
        'parts': [{
            'text': prompt
        }]
    }]
}
print(json.dumps(payload))
")
    
    # Make the API call
    response=$(curl -s -w "\n%{http_code}\n%{time_total}" \
        -H "Content-Type: application/json" \
        -X POST \
        -d "$json_payload" \
        "${GEMINI_API_URL}?key=${GOOGLE_API_KEY}")
    
    # Extract response components
    http_code=$(echo "$response" | tail -n 2 | head -n 1)
    time_total=$(echo "$response" | tail -n 1)
    response_body=$(echo "$response" | head -n -2)
    
    # Calculate end time
    end_time=$(date +%s.%N)
    duration=$(echo "$end_time - $start_time" | bc)
    
    echo "📊 Results:"
    echo "   HTTP Status: $http_code"
    echo "   Total Time: ${time_total}s (curl measurement)"
    echo "   Script Time: ${duration}s (bash measurement)"
    
    if [ "$http_code" = "200" ]; then
        # Extract the AI response text using python for better JSON parsing
        ai_response=$(echo "$response_body" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    text = data['candidates'][0]['content']['parts'][0]['text'].strip()
    print(text)
except:
    print('PARSE_ERROR')
")
        echo "   ✅ AI Response: '$ai_response'"
        
        # Validate response
        if [ -n "$ai_response" ] && [ "$ai_response" != "PARSE_ERROR" ]; then
            echo "   ✅ Success: Valid response received"
        else
            echo "   ⚠️  Warning: Could not parse response"
            echo "   Raw response: $response_body"
        fi
    else
        echo "   ❌ Error: HTTP $http_code"
        echo "   Response: $response_body"
    fi
    
    echo "---"
    echo ""
}

# Test 1: Current backend prompt (verbose)
prompt1='Given the following list of existing shopping item categories:

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

Item to categorize: "jablko"'

# Test 2: AI endpoint prompt (concise)
prompt2='You are an expert at organizing shopping lists.
Based on the item name, suggest a single, concise category.
The category should be a common supermarket category (e.g., "Produce", "Dairy", "Meat", "Pantry", "Frozen", "Beverages", "Snacks", "Personal Care", "Household", "Uncategorized").
Return only the category name, with no extra text or punctuation.

Item: "jablko"
Category:'

# Test 3: Minimal prompt
prompt3='Categorize this shopping item into one category: Produce, Dairy, Meat, Pantry, Frozen, Beverages, Snacks, Personal Care, Household, Uncategorized.
Item: jablko
Category:'

# Test 4: Ultra minimal
prompt4='Category for "jablko": Produce, Dairy, Meat, Pantry, or other?'

# Run the tests
test_prompt "Backend Verbose Prompt" "$prompt1" "jablko"
test_prompt "AI Endpoint Prompt" "$prompt2" "jablko"
test_prompt "Minimal Prompt" "$prompt3" "jablko"
test_prompt "Ultra Minimal Prompt" "$prompt4" "jablko"

# Additional test with English item
test_prompt "English Item Test" "$prompt2" "apple"

echo "🎯 Summary:"
echo "- Direct API calls should be much faster than backend"
echo "- Look for prompts that consistently return correct results in <2s"
echo "- Identify backend overhead if direct API is fast"
