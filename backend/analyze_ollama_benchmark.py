#!/usr/bin/env python3
"""
Analyze Ollama Models Benchmark Results

This script analyzes the benchmark results from the JSON file and provides
a comprehensive comparison of all models tested.
"""

import json
import sys
import os
from collections import defaultdict


def analyze_benchmark_results(json_file):
    """Analyze the benchmark results and generate a comprehensive report."""

    # Load the benchmark data
    with open(json_file, "r") as f:
        data = json.load(f)

    print("🔬 OLLAMA MODELS BENCHMARK ANALYSIS")
    print("=" * 60)
    print(f"📊 Data source: {json_file}")
    print()

    # Initialize summary data
    model_summaries = {}

    for model_key, model_data in data.items():
        model_name = model_data.get("model_name", model_key)
        results = model_data.get("categorization_results", [])

        # Calculate metrics
        total_tests = len(results)
        english_tests = [r for r in results if r.get("language") == "english"]
        czech_tests = [r for r in results if r.get("language") == "czech"]

        correct_total = sum(1 for r in results if r.get("correct"))
        correct_english = sum(1 for r in english_tests if r.get("correct"))
        correct_czech = sum(1 for r in czech_tests if r.get("correct"))

        # Calculate response times
        response_times = [
            r.get("response_time", 0) for r in results if r.get("response_time")
        ]
        avg_response_time = (
            sum(response_times) / len(response_times) if response_times else 0
        )

        english_times = [
            r.get("response_time", 0) for r in english_tests if r.get("response_time")
        ]
        czech_times = [
            r.get("response_time", 0) for r in czech_tests if r.get("response_time")
        ]

        avg_english_time = (
            sum(english_times) / len(english_times) if english_times else 0
        )
        avg_czech_time = sum(czech_times) / len(czech_times) if czech_times else 0

        # Store summary
        model_summaries[model_name] = {
            "total_tests": total_tests,
            "english_tests": len(english_tests),
            "czech_tests": len(czech_tests),
            "accuracy_total": (
                correct_total / total_tests * 100 if total_tests > 0 else 0
            ),
            "accuracy_english": (
                correct_english / len(english_tests) * 100 if english_tests else 0
            ),
            "accuracy_czech": (
                correct_czech / len(czech_tests) * 100 if czech_tests else 0
            ),
            "avg_response_time": avg_response_time,
            "avg_english_time": avg_english_time,
            "avg_czech_time": avg_czech_time,
            "correct_total": correct_total,
            "correct_english": correct_english,
            "correct_czech": correct_czech,
        }

    # Print detailed results
    print("📋 DETAILED RESULTS BY MODEL")
    print("-" * 60)

    for model_name, summary in model_summaries.items():
        print(f"\n🤖 {model_name}")
        print(
            f"   Tests: {summary['total_tests']} total ({summary['english_tests']} EN, {summary['czech_tests']} CZ)"
        )
        print(
            f"   Overall Accuracy: {summary['accuracy_total']:.1f}% ({summary['correct_total']}/{summary['total_tests']})"
        )
        print(
            f"   English Accuracy: {summary['accuracy_english']:.1f}% ({summary['correct_english']}/{summary['english_tests']})"
        )
        print(
            f"   Czech Accuracy: {summary['accuracy_czech']:.1f}% ({summary['correct_czech']}/{summary['czech_tests']})"
        )
        print(f"   Avg Response Time: {summary['avg_response_time']:.3f}s")
        print(f"   English Avg Time: {summary['avg_english_time']:.3f}s")
        print(f"   Czech Avg Time: {summary['avg_czech_time']:.3f}s")

    # Comparison tables
    print("\n\n📊 ACCURACY COMPARISON")
    print("-" * 60)
    print(f"{'Model':<20} {'Overall':<10} {'English':<10} {'Czech':<10}")
    print("-" * 60)

    # Sort by overall accuracy
    sorted_models = sorted(
        model_summaries.items(), key=lambda x: x[1]["accuracy_total"], reverse=True
    )

    for model_name, summary in sorted_models:
        print(
            f"{model_name:<20} {summary['accuracy_total']:<10.1f}% {summary['accuracy_english']:<10.1f}% {summary['accuracy_czech']:<10.1f}%"
        )

    print("\n\n⚡ PERFORMANCE COMPARISON")
    print("-" * 60)
    print(f"{'Model':<20} {'Overall':<12} {'English':<12} {'Czech':<12}")
    print("-" * 60)

    # Sort by response time (fastest first)
    sorted_models = sorted(
        model_summaries.items(), key=lambda x: x[1]["avg_response_time"]
    )

    for model_name, summary in sorted_models:
        print(
            f"{model_name:<20} {summary['avg_response_time']:<12.3f}s {summary['avg_english_time']:<12.3f}s {summary['avg_czech_time']:<12.3f}s"
        )

    # Recommendations
    print("\n\n🏆 RECOMMENDATIONS")
    print("-" * 60)

    best_accuracy = max(model_summaries.items(), key=lambda x: x[1]["accuracy_total"])
    best_english = max(model_summaries.items(), key=lambda x: x[1]["accuracy_english"])
    best_czech = max(model_summaries.items(), key=lambda x: x[1]["accuracy_czech"])
    fastest = min(model_summaries.items(), key=lambda x: x[1]["avg_response_time"])

    print(
        f"🎯 Best Overall Accuracy: {best_accuracy[0]} ({best_accuracy[1]['accuracy_total']:.1f}%)"
    )
    print(
        f"🇺🇸 Best English Accuracy: {best_english[0]} ({best_english[1]['accuracy_english']:.1f}%)"
    )
    print(
        f"🇨🇿 Best Czech Accuracy: {best_czech[0]} ({best_czech[1]['accuracy_czech']:.1f}%)"
    )
    print(f"⚡ Fastest Response: {fastest[0]} ({fastest[1]['avg_response_time']:.3f}s)")

    # Find balanced recommendation (good accuracy + reasonable speed)
    balanced_scores = {}
    for model_name, summary in model_summaries.items():
        # Normalize metrics (higher is better for both)
        accuracy_score = summary["accuracy_total"] / 100
        speed_score = 1 / (summary["avg_response_time"] + 0.1)  # Avoid division by zero
        balanced_scores[model_name] = (accuracy_score + speed_score) / 2

    best_balanced = max(balanced_scores.items(), key=lambda x: x[1])
    best_balanced_model = model_summaries[best_balanced[0]]

    print(f"⚖️  Best Balance (Accuracy + Speed): {best_balanced[0]}")
    print(
        f"    ({best_balanced_model['accuracy_total']:.1f}% accuracy, {best_balanced_model['avg_response_time']:.3f}s response)"
    )

    # Fallback recommendation
    print(f"\n🔄 Fallback Configuration Recommendation:")
    print(
        f"   Primary: {best_accuracy[0]} (best accuracy: {best_accuracy[1]['accuracy_total']:.1f}%)"
    )
    print(
        f"   Fallback: {fastest[0]} (fastest: {fastest[1]['avg_response_time']:.3f}s)"
    )

    # Check specific error patterns
    print("\n\n🔍 ERROR ANALYSIS")
    print("-" * 60)

    for model_key, model_data in data.items():
        model_name = model_data.get("model_name", model_key)
        results = model_data.get("categorization_results", [])
        errors = [r for r in results if not r.get("correct")]

        if errors:
            print(f"\n❌ {model_name} Errors ({len(errors)} total):")
            for error in errors[:5]:  # Show first 5 errors
                print(
                    f"   • '{error.get('item')}' ({error.get('language')}) -> got '{error.get('actual')}', expected '{error.get('expected')}'"
                )
            if len(errors) > 5:
                print(f"   ... and {len(errors) - 5} more errors")


if __name__ == "__main__":
    benchmark_file = "ollama_models_benchmark_20250703_112132.json"

    if not os.path.exists(benchmark_file):
        print(f"❌ Benchmark file {benchmark_file} not found!")
        print("Please run the benchmark script first.")
        sys.exit(1)

    analyze_benchmark_results(benchmark_file)
