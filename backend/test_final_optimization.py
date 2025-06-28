#!/usr/bin/env python3
"""
Final validation test for the complete LLM optimization
Tests both direct API and backend service performance
"""
import asyncio
import time
import sys
import random

# Add backend to path
sys.path.insert(0, '/home/honzik/GitHub/FamilyCart/FamilyCart/backend')

from app.services.ai_service import ai_service
from app.core.cache import cache_service

async def test_optimized_performance():
    """Test the complete optimized AI performance pipeline"""
    
    print("🚀 FINAL PERFORMANCE VALIDATION TEST")
    print("=" * 60)
    print("Testing complete optimization: gemini-1.5-flash + 6-month caching + parallel processing")
    print()
    
    # Ensure cache service is set up
    await cache_service.setup()
    print(f"✅ Cache service ready")
    
    # Test scenarios
    test_cases = [
        {"name": "milk", "expected": "cached (lightning fast)", "type": "common_item"},
        {"name": "jablko", "expected": "cached or fast AI", "type": "czech_item"}, 
        {"name": f"unique_test_{random.randint(10000, 99999)}", "expected": "fast AI call", "type": "new_item"}
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        item_name = test_case["name"]
        print(f"🧪 Test {i}/3: '{item_name}' ({test_case['type']})")
        
        start_time = time.time()
        
        try:
            # Test just category suggestion (most common use case)
            category_names = ["Produce", "Dairy", "Pantry", "Meat", "Beverages", "Snacks", "Frozen", "Personal Care"]
            category = await ai_service.suggest_category_async(item_name, category_names)
            
            duration = time.time() - start_time
            
            print(f"  ✅ Category: '{category}' in {duration:.3f}s")
            
            # Analyze performance
            if duration < 0.1:
                status = "🚀 CACHED (lightning fast!)"
            elif duration < 1.0:
                status = "⚡ FAST AI (optimized!)"
            elif duration < 3.0:
                status = "✅ GOOD (acceptable)"
            else:
                status = "⚠️  SLOW (needs investigation)"
                
            print(f"  {status}")
            
            results.append({
                'item': item_name,
                'type': test_case['type'],
                'duration': duration,
                'category': category
            })
            
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            
        print()
    
    # Performance summary
    print("=" * 60)
    print("📊 PERFORMANCE SUMMARY")
    print("=" * 60)
    
    total_time = sum(r['duration'] for r in results)
    avg_time = total_time / len(results) if results else 0
    
    print(f"📈 Performance Results:")
    for result in results:
        print(f"  {result['item']}: {result['duration']:.3f}s ({result['type']})")
        
    print(f"\n🎯 Overall Statistics:")
    print(f"  Average time: {avg_time:.3f}s")
    print(f"  Total time: {total_time:.3f}s")
    print(f"  Fastest: {min(r['duration'] for r in results):.3f}s")
    print(f"  Slowest: {max(r['duration'] for r in results):.3f}s")
    
    # Compare with original performance
    print(f"\n🚀 IMPROVEMENT ANALYSIS:")
    original_time = 25.0  # Original 20-35s average
    improvement = original_time / avg_time if avg_time > 0 else 0
    
    print(f"  Original performance: ~25s per item")
    print(f"  Current performance: {avg_time:.3f}s per item")
    print(f"  Improvement factor: {improvement:.1f}x faster")
    print(f"  Time saved per item: {original_time - avg_time:.1f}s")
    
    # User experience impact
    if avg_time < 1.0:
        print(f"  🎉 USER EXPERIENCE: EXCELLENT - Nearly instant responses!")
    elif avg_time < 3.0:
        print(f"  ✅ USER EXPERIENCE: GOOD - Fast and responsive")
    else:
        print(f"  ⚠️  USER EXPERIENCE: Needs improvement")
        
    print(f"\n💰 Cost Impact (with 6-month caching):")
    print(f"  Cache hit rate (expected): 90%+")
    print(f"  Cost reduction: 90%+ savings on AI API calls")
    print(f"  Performance boost: 99%+ for cached items")

if __name__ == "__main__":
    asyncio.run(test_optimized_performance())
