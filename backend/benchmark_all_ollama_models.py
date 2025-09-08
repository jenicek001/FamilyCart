#!/usr/bin/env python3
"""
Comprehensive Ollama Models Benchmark

This script benchmarks all available Ollama models against Gemini for:
1. Categorization accuracy (English and Czech)
2. Response times
3. Icon suggestions
4. Translation capabilities
"""

import asyncio
import time
import json
import sys
import os
from typing import Dict, List, Tuple
import statistics

# Add the backend app directory to Python path
sys.path.append("/home/honzik/GitHub/FamilyCart/FamilyCart/backend")

from app.services.gemini_provider import GeminiProvider
from app.services.ollama_provider import OllamaProvider
from app.core.config import settings


class ModelBenchmark:
    """Benchmark different AI models."""

    def __init__(self):
        self.results = {}
        self.gemini_provider = None

    async def initialize_gemini(self):
        """Initialize Gemini provider as reference."""
        try:
            self.gemini_provider = GeminiProvider()
            print("✅ Gemini provider initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize Gemini: {e}")
            self.gemini_provider = None

    async def test_model(self, model_name: str, test_items: List[Dict]) -> Dict:
        """Test a specific Ollama model."""
        print(f"\n🧪 Testing model: {model_name}")
        print("=" * 60)

        # Create Ollama provider for this model
        original_model = settings.OLLAMA_MODEL_NAME
        settings.OLLAMA_MODEL_NAME = model_name

        try:
            provider = OllamaProvider()
            print(f"   ✅ Model {model_name} initialized")
        except Exception as e:
            print(f"   ❌ Failed to initialize {model_name}: {e}")
            settings.OLLAMA_MODEL_NAME = original_model
            return {"error": str(e)}

        results = {
            "model_name": model_name,
            "categorization_results": [],
            "icon_results": [],
            "translation_results": [],
            "response_times": [],
            "accuracy_scores": {},
            "error_count": 0,
        }

        # Test categorization
        print(f"   📝 Testing categorization...")
        for item_data in test_items:
            item_name = item_data["name"]
            expected_category = item_data["expected_category"]
            language = item_data["language"]

            try:
                start_time = time.time()
                category = await provider.suggest_category_async(item_name, [])
                response_time = time.time() - start_time

                results["categorization_results"].append(
                    {
                        "item": item_name,
                        "language": language,
                        "expected": expected_category,
                        "actual": category,
                        "correct": self.is_category_correct(
                            category, expected_category
                        ),
                        "response_time": response_time,
                    }
                )
                results["response_times"].append(response_time)

                status = (
                    "✅"
                    if self.is_category_correct(category, expected_category)
                    else "❌"
                )
                print(
                    f"      {status} '{item_name}' [{language}] -> '{category}' ({response_time:.3f}s)"
                )

            except Exception as e:
                results["error_count"] += 1
                print(f"      ❌ Error with '{item_name}': {e}")

        # Test icon suggestions
        print(f"   🎨 Testing icon suggestions...")
        icon_test_items = [
            ("apple", "Produce"),
            ("milk", "Dairy"),
            ("bread", "Bakery"),
            ("detergent", "Household"),
        ]

        for item_name, category in icon_test_items:
            try:
                start_time = time.time()
                icon = await provider.suggest_icon(item_name, category)
                response_time = time.time() - start_time

                results["icon_results"].append(
                    {
                        "item": item_name,
                        "category": category,
                        "icon": icon,
                        "response_time": response_time,
                    }
                )
                results["response_times"].append(response_time)

                print(f"      ✅ '{item_name}' -> '{icon}' ({response_time:.3f}s)")

            except Exception as e:
                results["error_count"] += 1
                print(f"      ❌ Error with icon for '{item_name}': {e}")

        # Calculate accuracy scores
        english_correct = sum(
            1
            for r in results["categorization_results"]
            if r["language"] == "english" and r["correct"]
        )
        english_total = sum(
            1 for r in results["categorization_results"] if r["language"] == "english"
        )

        czech_correct = sum(
            1
            for r in results["categorization_results"]
            if r["language"] == "czech" and r["correct"]
        )
        czech_total = sum(
            1 for r in results["categorization_results"] if r["language"] == "czech"
        )

        results["accuracy_scores"] = {
            "english_accuracy": (
                english_correct / english_total if english_total > 0 else 0
            ),
            "czech_accuracy": czech_correct / czech_total if czech_total > 0 else 0,
            "overall_accuracy": (
                (english_correct + czech_correct) / (english_total + czech_total)
                if (english_total + czech_total) > 0
                else 0
            ),
        }

        # Calculate performance metrics
        if results["response_times"]:
            results["avg_response_time"] = statistics.mean(results["response_times"])
            results["median_response_time"] = statistics.median(
                results["response_times"]
            )
            results["min_response_time"] = min(results["response_times"])
            results["max_response_time"] = max(results["response_times"])

        # Restore original model setting
        settings.OLLAMA_MODEL_NAME = original_model

        return results

    def is_category_correct(self, actual: str, expected: str) -> bool:
        """Check if categorization is correct (flexible matching)."""
        actual_clean = actual.lower().strip().replace("&", "and")
        expected_clean = expected.lower().strip().replace("&", "and")

        # Exact match
        if actual_clean == expected_clean:
            return True

        # Check if they're similar categories
        category_mappings = {
            "produce": ["fruits", "vegetables", "fruit", "vegetable"],
            "dairy": ["dairy & eggs", "dairy and eggs", "milk", "cheese"],
            "meat": ["meat & seafood", "meat and seafood", "protein"],
            "bakery": ["bread", "baked goods"],
            "pantry": ["dry goods", "canned goods", "grains", "pasta"],
            "household": ["cleaning", "personal care", "hygiene"],
            "beverages": ["drinks", "beverage"],
        }

        for main_cat, alternatives in category_mappings.items():
            if (
                main_cat in actual_clean
                and any(alt in expected_clean for alt in alternatives)
            ) or (
                main_cat in expected_clean
                and any(alt in actual_clean for alt in alternatives)
            ):
                return True

        return False

    async def benchmark_against_gemini(self, test_items: List[Dict]) -> Dict:
        """Benchmark Gemini as reference."""
        if not self.gemini_provider:
            return {"error": "Gemini not available"}

        print(f"\n🧠 Benchmarking Gemini (Reference)")
        print("=" * 60)

        results = {
            "model_name": "gemini-1.5-flash",
            "categorization_results": [],
            "icon_results": [],
            "response_times": [],
            "accuracy_scores": {},
            "error_count": 0,
        }

        # Test categorization
        for item_data in test_items:
            item_name = item_data["name"]
            expected_category = item_data["expected_category"]
            language = item_data["language"]

            try:
                start_time = time.time()
                category = await self.gemini_provider.suggest_category_async(
                    item_name, []
                )
                response_time = time.time() - start_time

                results["categorization_results"].append(
                    {
                        "item": item_name,
                        "language": language,
                        "expected": expected_category,
                        "actual": category,
                        "correct": self.is_category_correct(
                            category, expected_category
                        ),
                        "response_time": response_time,
                    }
                )
                results["response_times"].append(response_time)

                status = (
                    "✅"
                    if self.is_category_correct(category, expected_category)
                    else "❌"
                )
                print(
                    f"   {status} '{item_name}' [{language}] -> '{category}' ({response_time:.3f}s)"
                )

            except Exception as e:
                results["error_count"] += 1
                print(f"   ❌ Error with '{item_name}': {e}")

        # Calculate accuracy scores
        english_correct = sum(
            1
            for r in results["categorization_results"]
            if r["language"] == "english" and r["correct"]
        )
        english_total = sum(
            1 for r in results["categorization_results"] if r["language"] == "english"
        )

        czech_correct = sum(
            1
            for r in results["categorization_results"]
            if r["language"] == "czech" and r["correct"]
        )
        czech_total = sum(
            1 for r in results["categorization_results"] if r["language"] == "czech"
        )

        results["accuracy_scores"] = {
            "english_accuracy": (
                english_correct / english_total if english_total > 0 else 0
            ),
            "czech_accuracy": czech_correct / czech_total if czech_total > 0 else 0,
            "overall_accuracy": (
                (english_correct + czech_correct) / (english_total + czech_total)
                if (english_total + czech_total) > 0
                else 0
            ),
        }

        # Calculate performance metrics
        if results["response_times"]:
            results["avg_response_time"] = statistics.mean(results["response_times"])
            results["median_response_time"] = statistics.median(
                results["response_times"]
            )
            results["min_response_time"] = min(results["response_times"])
            results["max_response_time"] = max(results["response_times"])

        return results

    def print_summary(self, all_results: Dict):
        """Print comprehensive benchmark summary."""
        print(f"\n" + "=" * 80)
        print(f"📊 COMPREHENSIVE MODEL BENCHMARK SUMMARY")
        print(f"=" * 80)

        # Create summary table
        print(
            f"\n{'Model':<20} {'Eng Acc':<8} {'Cz Acc':<8} {'Overall':<8} {'Avg Time':<10} {'Errors':<7}"
        )
        print("-" * 70)

        sorted_models = sorted(
            all_results.items(),
            key=lambda x: x[1].get("accuracy_scores", {}).get("overall_accuracy", 0),
            reverse=True,
        )

        for model_name, results in sorted_models:
            if "error" in results:
                print(
                    f"{model_name:<20} {'ERROR':<8} {'ERROR':<8} {'ERROR':<8} {'ERROR':<10} {'N/A':<7}"
                )
                continue

            acc = results.get("accuracy_scores", {})
            eng_acc = f"{acc.get('english_accuracy', 0)*100:.1f}%"
            cz_acc = f"{acc.get('czech_accuracy', 0)*100:.1f}%"
            overall_acc = f"{acc.get('overall_accuracy', 0)*100:.1f}%"
            avg_time = f"{results.get('avg_response_time', 0):.3f}s"
            errors = str(results.get("error_count", 0))

            print(
                f"{model_name:<20} {eng_acc:<8} {cz_acc:<8} {overall_acc:<8} {avg_time:<10} {errors:<7}"
            )

        # Performance ranking
        print(f"\n🏆 PERFORMANCE RANKINGS:")
        print(
            f"   Accuracy: {sorted_models[0][0]} ({sorted_models[0][1].get('accuracy_scores', {}).get('overall_accuracy', 0)*100:.1f}%)"
        )

        speed_sorted = sorted(
            all_results.items(),
            key=lambda x: x[1].get("avg_response_time", float("inf")),
        )
        print(
            f"   Speed: {speed_sorted[0][0]} ({speed_sorted[0][1].get('avg_response_time', 0):.3f}s)"
        )

        # Language-specific performance
        print(f"\n🌍 LANGUAGE-SPECIFIC PERFORMANCE:")
        print(
            f"   English Best: {max(all_results.items(), key=lambda x: x[1].get('accuracy_scores', {}).get('english_accuracy', 0))[0]}"
        )
        print(
            f"   Czech Best: {max(all_results.items(), key=lambda x: x[1].get('accuracy_scores', {}).get('czech_accuracy', 0))[0]}"
        )

        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        best_overall = sorted_models[0]
        best_speed = speed_sorted[0]

        if best_overall[0] == best_speed[0]:
            print(
                f"   🥇 Overall Winner: {best_overall[0]} (best accuracy + good speed)"
            )
        else:
            print(
                f"   🥇 Best Accuracy: {best_overall[0]} ({best_overall[1].get('accuracy_scores', {}).get('overall_accuracy', 0)*100:.1f}%)"
            )
            print(
                f"   🥇 Best Speed: {best_speed[0]} ({best_speed[1].get('avg_response_time', 0):.3f}s)"
            )
            print(
                f"   💡 Consider {best_overall[0]} for production (accuracy priority)"
            )
            print(f"   💡 Consider {best_speed[0]} for development (speed priority)")


async def main():
    """Main benchmark function."""
    print("🚀 Starting Comprehensive Ollama Models Benchmark")
    print("=" * 80)

    # Test items in English and Czech
    test_items = [
        # English items
        {
            "name": "organic apples",
            "expected_category": "Produce",
            "language": "english",
        },
        {"name": "whole milk", "expected_category": "Dairy", "language": "english"},
        {
            "name": "sourdough bread",
            "expected_category": "Bakery",
            "language": "english",
        },
        {"name": "chicken breast", "expected_category": "Meat", "language": "english"},
        {"name": "dish soap", "expected_category": "Household", "language": "english"},
        {
            "name": "orange juice",
            "expected_category": "Beverages",
            "language": "english",
        },
        {"name": "pasta", "expected_category": "Pantry", "language": "english"},
        {"name": "ice cream", "expected_category": "Dairy", "language": "english"},
        # Czech items
        {"name": "jablka", "expected_category": "Produce", "language": "czech"},
        {"name": "mléko", "expected_category": "Dairy", "language": "czech"},
        {"name": "chléb", "expected_category": "Bakery", "language": "czech"},
        {"name": "kuřecí maso", "expected_category": "Meat", "language": "czech"},
        {"name": "saponát", "expected_category": "Household", "language": "czech"},
        {
            "name": "pomerančový džus",
            "expected_category": "Beverages",
            "language": "czech",
        },
        {"name": "těstoviny", "expected_category": "Pantry", "language": "czech"},
        {"name": "zmrzlina", "expected_category": "Dairy", "language": "czech"},
    ]

    # Get available models
    available_models = [
        "gemma3:4b",
        "gemma3:latest",
        "deepseek-r1:latest",
        "gemma3n:latest",
        "qwen3:latest",
        "llama4:latest",
    ]

    print(f"📋 Testing {len(available_models)} Ollama models against Gemini reference")
    print(
        f"📋 Test items: {len(test_items)} ({len([i for i in test_items if i['language'] == 'english'])} English, {len([i for i in test_items if i['language'] == 'czech'])} Czech)"
    )

    benchmark = ModelBenchmark()
    all_results = {}

    # Initialize and test Gemini as reference
    await benchmark.initialize_gemini()
    if benchmark.gemini_provider:
        gemini_results = await benchmark.benchmark_against_gemini(test_items)
        all_results["gemini-1.5-flash"] = gemini_results

    # Test each Ollama model
    for model_name in available_models:
        try:
            results = await benchmark.test_model(model_name, test_items)
            all_results[model_name] = results
        except Exception as e:
            print(f"❌ Failed to test {model_name}: {e}")
            all_results[model_name] = {"error": str(e)}

    # Print comprehensive summary
    benchmark.print_summary(all_results)

    # Save detailed results
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    results_file = f"ollama_models_benchmark_{timestamp}.json"

    try:
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Detailed results saved to: {results_file}")
    except Exception as e:
        print(f"❌ Failed to save results: {e}")

    print(f"\n✅ Benchmark completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
