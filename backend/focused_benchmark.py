#!/usr/bin/env python3
"""
Focused AI Provider Benchmark

This script does a quick focused benchmark with just 3 items to compare
Gemini vs Ollama performance without hitting rate limits.
"""

import asyncio
import time
import statistics
import sys

# Add the backend app directory to Python path
sys.path.append("/home/honzik/GitHub/FamilyCart/FamilyCart/backend")

from app.core.config import settings
from app.services.ai_factory import AIProviderFactory
from app.services.gemini_provider import GeminiProvider
from app.services.ollama_provider import OllamaProvider


class FocusedBenchmark:
    def __init__(self):
        self.test_items = ["organic apples", "whole milk", "chicken breast"]
        self.operations = ["categorization", "icon_suggestion", "text_generation"]

    async def benchmark_operation(self, provider, provider_name, operation, item):
        """Benchmark a single operation."""
        start_time = time.time()
        try:
            if operation == "categorization":
                result = await provider.suggest_category_async(item, [])
            elif operation == "icon_suggestion":
                result = await provider.suggest_icon(item, "General")
            elif operation == "text_generation":
                result = await provider.generate_text(
                    f"Describe '{item}' in one sentence."
                )

            response_time = time.time() - start_time
            return {
                "provider": provider_name,
                "operation": operation,
                "item": item,
                "success": True,
                "time": response_time,
                "result": result[:50] + "..." if len(result) > 50 else result,
            }
        except Exception as e:
            response_time = time.time() - start_time
            return {
                "provider": provider_name,
                "operation": operation,
                "item": item,
                "success": False,
                "time": response_time,
                "error": str(e),
            }

    async def run_provider_benchmark(self, provider, provider_name):
        """Run benchmark for one provider."""
        print(f"\n🚀 Benchmarking {provider_name}")
        print("-" * 40)

        results = []
        for item in self.test_items:
            print(f"\n📝 Testing: {item}")
            for operation in self.operations:
                result = await self.benchmark_operation(
                    provider, provider_name, operation, item
                )
                results.append(result)

                if result["success"]:
                    print(
                        f"  ✅ {operation}: {result['time']:.3f}s - {result['result']}"
                    )
                else:
                    print(
                        f"  ❌ {operation}: {result['time']:.3f}s - {result['error']}"
                    )

                # Small delay to be nice to APIs
                await asyncio.sleep(0.2)

        return results

    def analyze_results(self, gemini_results, ollama_results):
        """Analyze and compare results."""
        print("\n" + "=" * 60)
        print("📊 BENCHMARK ANALYSIS")
        print("=" * 60)

        # Overall statistics
        def get_stats(results):
            successful = [r for r in results if r["success"]]
            if not successful:
                return None
            times = [r["time"] for r in successful]
            return {
                "total": len(results),
                "successful": len(successful),
                "success_rate": len(successful) / len(results) * 100,
                "avg_time": statistics.mean(times),
                "min_time": min(times),
                "max_time": max(times),
                "median_time": statistics.median(times),
            }

        if gemini_results:
            gemini_stats = get_stats(gemini_results)
            if gemini_stats:
                print(f"\n🧠 GEMINI RESULTS:")
                print(f"   Success Rate: {gemini_stats['success_rate']:.1f}%")
                print(f"   Average Time: {gemini_stats['avg_time']:.3f}s")
                print(
                    f"   Range: {gemini_stats['min_time']:.3f}s - {gemini_stats['max_time']:.3f}s"
                )
                print(f"   Median: {gemini_stats['median_time']:.3f}s")

        if ollama_results:
            ollama_stats = get_stats(ollama_results)
            if ollama_stats:
                print(f"\n🦙 OLLAMA RESULTS:")
                print(f"   Success Rate: {ollama_stats['success_rate']:.1f}%")
                print(f"   Average Time: {ollama_stats['avg_time']:.3f}s")
                print(
                    f"   Range: {ollama_stats['min_time']:.3f}s - {ollama_stats['max_time']:.3f}s"
                )
                print(f"   Median: {ollama_stats['median_time']:.3f}s")

        # Comparison
        if gemini_results and ollama_results and gemini_stats and ollama_stats:
            print(f"\n⚡ PERFORMANCE COMPARISON:")
            speed_ratio = gemini_stats["avg_time"] / ollama_stats["avg_time"]
            if speed_ratio > 1:
                print(f"   Ollama is {speed_ratio:.1f}x faster than Gemini")
            else:
                print(f"   Gemini is {1/speed_ratio:.1f}x faster than Ollama")

        # Operation breakdown
        print(f"\n📋 OPERATION BREAKDOWN:")
        for operation in self.operations:
            print(f"\n   {operation.upper()}:")

            if gemini_results:
                gemini_op = [
                    r
                    for r in gemini_results
                    if r["operation"] == operation and r["success"]
                ]
                if gemini_op:
                    avg_time = statistics.mean([r["time"] for r in gemini_op])
                    print(f"     Gemini: {avg_time:.3f}s avg")

            if ollama_results:
                ollama_op = [
                    r
                    for r in ollama_results
                    if r["operation"] == operation and r["success"]
                ]
                if ollama_op:
                    avg_time = statistics.mean([r["time"] for r in ollama_op])
                    print(f"     Ollama: {avg_time:.3f}s avg")

    async def run(self):
        """Run the focused benchmark."""
        print("🎯 Focused AI Provider Benchmark")
        print("Test Items:", ", ".join(self.test_items))
        print("Operations:", ", ".join(self.operations))

        gemini_results = []
        ollama_results = []

        # Wait a bit for any rate limits to reset
        print("\n⏳ Waiting 10 seconds for API rate limits to reset...")
        await asyncio.sleep(10)

        # Test Gemini (with retry logic for rate limits)
        if settings.GOOGLE_API_KEY:
            try:
                gemini_provider = GeminiProvider()
                gemini_results = await self.run_provider_benchmark(
                    gemini_provider, "Gemini"
                )
            except Exception as e:
                print(f"❌ Gemini benchmark failed: {e}")

        # Test Ollama
        try:
            ollama_provider = OllamaProvider()
            ollama_results = await self.run_provider_benchmark(
                ollama_provider, "Ollama"
            )
        except Exception as e:
            print(f"❌ Ollama benchmark failed: {e}")

        # Analyze results
        self.analyze_results(gemini_results, ollama_results)


async def main():
    benchmark = FocusedBenchmark()
    await benchmark.run()


if __name__ == "__main__":
    asyncio.run(main())
