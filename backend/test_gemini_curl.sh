#!/bin/bash
"""
Curl test framework for benchmarking direct Gemini API performance
Tests the exact prompts used in our backend to identify performance bottlenecks
"""

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

# Test function
test_prompt() {
    local test_name="$1"
    local prompt="$2"
    local item="$3"
    
    echo "🧪 Test: $test_name"
    echo "📝 Item: '$item'"
    echo "⏱️  Starting request..."
    
    # Record start time
    start_time=$(date +%s.%N)
    
    # Create JSON payload
    json_payload=$(cat <<EOF
{
  "contents": [{
    "parts": [{
      "text": "$prompt"
    }]
  }]
}
EOF
)
    
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
        # Extract the AI response text
        ai_response=$(echo "$response_body" | grep -o '"text":"[^"]*"' | sed 's/"text":"\([^"]*\)"/\1/' | head -n 1)
        echo "   ✅ AI Response: '$ai_response'"
        
        # Validate response
        if [ -n "$ai_response" ] && [ "$ai_response" != "null" ]; then
            echo "   ✅ Success: Valid response received"
        else
            echo "   ⚠️  Warning: Empty or null response"
        fi
    else
        echo "   ❌ Error: HTTP $http_code"
        echo "   Response: $response_body"
    fi
    
    echo "---"
    echo ""
}

# Test 1: Current backend prompt (verbose)
prompt1="Given the following list of existing shopping item categories:

Produce, Dairy, Meat, Pantry, Frozen, Beverages, Snacks, Personal Care, Household, Uncategorized

What is the best category for the item \"jablko\"?

IMPORTANT INSTRUCTIONS:
- The item name might be in Czech, German, Spanish, French, or other languages
- The category should be a single noun, in English, and singular
- If a suitable category from the list exists, return it exactly as written
- If not, suggest a new, appropriate category in English
- Return ONLY the category name and nothing else - no punctuation, no explanations

Examples:
- For \"mléko\" (Czech for milk), return: Dairy
- For \"Granny Smith Apples\", return: Produce
- For \"Cheddar Cheese\", return: Dairy
- For \"pain\" (French for bread), return: Pantry

Item to categorize: \"jablko\""

# Test 2: AI endpoint prompt (concise)
prompt2="You are an expert at organizing shopping lists.
Based on the item name, suggest a single, concise category.
The category should be a common supermarket category (e.g., \"Produce\", \"Dairy\", \"Meat\", \"Pantry\", \"Frozen\", \"Beverages\", \"Snacks\", \"Personal Care\", \"Household\", \"Uncategorized\").
Return only the category name, with no extra text or punctuation.

Item: \"jablko\"
Category:"

# Test 3: Minimal prompt
prompt3="Categorize this shopping item into one category: Produce, Dairy, Meat, Pantry, Frozen, Beverages, Snacks, Personal Care, Household, Uncategorized.
Item: jablko
Category:"

# Run the tests
test_prompt "Backend Verbose Prompt" "$prompt1" "jablko"
test_prompt "AI Endpoint Prompt" "$prompt2" "jablko"
test_prompt "Minimal Prompt" "$prompt3" "jablko"

# Additional test with English item
test_prompt "English Item Test" "$prompt2" "apple"

# Test with different model (if needed)
echo "🔄 Testing with gemini-1.5-flash for comparison..."
GEMINI_FAST_URL="https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

test_prompt_fast() {
    local test_name="$1"
    local prompt="$2"
    local item="$3"
    
    echo "🧪 Test (1.5-flash): $test_name"
    echo "📝 Item: '$item'"
    echo "⏱️  Starting request..."
    
    start_time=$(date +%s.%N)
    
    json_payload=$(cat <<EOF
{
  "contents": [{
    "parts": [{
      "text": "$prompt"
    }]
  }]
}
EOF
)
    
    response=$(curl -s -w "\n%{http_code}\n%{time_total}" \
        -H "Content-Type: application/json" \
        -X POST \
        -d "$json_payload" \
        "${GEMINI_FAST_URL}?key=${GOOGLE_API_KEY}")
    
    http_code=$(echo "$response" | tail -n 2 | head -n 1)
    time_total=$(echo "$response" | tail -n 1)
    response_body=$(echo "$response" | head -n -2)
    
    end_time=$(date +%s.%N)
    duration=$(echo "$end_time - $start_time" | bc)
    
    echo "📊 Results (1.5-flash):"
    echo "   HTTP Status: $http_code"
    echo "   Total Time: ${time_total}s"
    echo "   Script Time: ${duration}s"
    
    if [ "$http_code" = "200" ]; then
        ai_response=$(echo "$response_body" | grep -o '"text":"[^"]*"' | sed 's/"text":"\([^"]*\)"/\1/' | head -n 1)
        echo "   ✅ AI Response: '$ai_response'"
    else
        echo "   ❌ Error: HTTP $http_code"
    fi
    
    echo "---"
    echo ""
}

test_prompt_fast "Minimal Prompt (1.5-flash)" "$prompt3" "jablko"

echo "🎯 Summary:"
echo "- Compare response times between prompts"
echo "- Check if gemini-1.5-flash is faster than gemini-2.5-flash"
echo "- Identify the most efficient prompt structure"
echo "- Note: Backend overhead should be minimal if direct API is ~2s"
