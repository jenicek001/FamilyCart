#!/usr/bin/env python3
"""
AI Provider Benchmarking Script for FamilyCart

This script benchmarks and compares response times and result quality between
Gemini and Ollama AI providers for key AI-powered features:
1. Item categorization
2. Icon suggestion
3. Item name standardization & translation
4. Text generation

Usage:
    python benchmark_ai_providers.py [--runs=10] [--timeout=120]

Requirements:
    - Backend server running with both Gemini and Ollama configured
    - Environment variables set for API keys and Ollama configuration
    - Test items list for consistent benchmarking
"""

import argparse
import asyncio
import json
import os
import statistics
import sys
import time
from dataclasses import asdict
from datetime import datetime
from typing import Any, Dict, List, Tuple

import httpx

from benchmark_config import (
    DEFAULT_CONFIG,
    TEST_ITEMS,
    TEST_PROMPTS,
    BenchmarkResult,
    ProviderStats,
    print_benchmark_results,
)

# Add the backend app directory to Python path
sys.path.append("/home/honzik/GitHub/FamilyCart/FamilyCart/backend")

from app.core.config import settings
from app.services.ai_factory import get_ai_provider
from app.services.gemini_provider import GeminiProvider
from app.services.ollama_provider import OllamaProvider


class AIProviderBenchmark:
    """Benchmark runner for AI providers."""

    def __init__(self, runs: int = 10, timeout: int = 120):
        self.runs = runs
        self.timeout = timeout
        self.results: List[BenchmarkResult] = []

        # Use test items from config
        self.test_items = TEST_ITEMS

        # Initialize providers
        self.gemini_provider = None
        self.ollama_provider = None

    async def setup_providers(self):
        """Initialize both AI providers."""
        print("🔧 Setting up AI providers...")

        # Setup Gemini provider
        try:
            if settings.GOOGLE_API_KEY:
                # Import the factory to reset it
                from app.services.ai_factory import AIProviderFactory

                # Temporarily set provider to gemini
                original_provider = settings.AI_PROVIDER
                settings.AI_PROVIDER = "gemini"
                AIProviderFactory.reset_provider()  # Reset cached instance
                self.gemini_provider = get_ai_provider()
                settings.AI_PROVIDER = original_provider
                print("✅ Gemini provider initialized")
            else:
                print("❌ Gemini provider not available (no API key)")
        except Exception as e:
            print(f"❌ Failed to initialize Gemini provider: {e}")

        # Setup Ollama provider
        try:
            # Test if Ollama server is running
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=5
                )
                if response.status_code == 200:
                    # Import the factory to reset it
                    from app.services.ai_factory import AIProviderFactory

                    # Temporarily set provider to ollama
                    original_provider = settings.AI_PROVIDER
                    settings.AI_PROVIDER = "ollama"
                    AIProviderFactory.reset_provider()  # Reset cached instance
                    self.ollama_provider = get_ai_provider()
                    settings.AI_PROVIDER = original_provider
                    print("✅ Ollama provider initialized")
                else:
                    print(
                        f"❌ Ollama server not available (status: {response.status_code})"
                    )
        except Exception as e:
            print(f"❌ Failed to initialize Ollama provider: {e}")

    async def benchmark_categorization(
        self, provider, provider_name: str, item_name: str
    ) -> BenchmarkResult:
        """Benchmark item categorization."""
        start_time = time.time()
        try:
            # Use the provider's suggest_category_async method
            category = await provider.suggest_category_async(item_name, [])
            end_time = time.time()

            return BenchmarkResult(
                provider=provider_name,
                operation="categorization",
                item_name=item_name,
                response_time=end_time - start_time,
                success=True,
                response=category,
            )
        except Exception as e:
            end_time = time.time()
            return BenchmarkResult(
                provider=provider_name,
                operation="categorization",
                item_name=item_name,
                response_time=end_time - start_time,
                success=False,
                response="",
                error=str(e),
            )

    async def benchmark_icon_suggestion(
        self, provider, provider_name: str, item_name: str
    ) -> BenchmarkResult:
        """Benchmark icon suggestion."""
        start_time = time.time()
        try:
            # First get a category, then suggest icon
            category = await provider.suggest_category_async(item_name, [])
            icon = await provider.suggest_icon(item_name, category)
            end_time = time.time()

            return BenchmarkResult(
                provider=provider_name,
                operation="icon_suggestion",
                item_name=item_name,
                response_time=end_time - start_time,
                success=True,
                response=icon,
            )
        except Exception as e:
            end_time = time.time()
            return BenchmarkResult(
                provider=provider_name,
                operation="icon_suggestion",
                item_name=item_name,
                response_time=end_time - start_time,
                success=False,
                response="",
                error=str(e),
            )

    async def benchmark_standardization(
        self, provider, provider_name: str, item_name: str
    ) -> BenchmarkResult:
        """Benchmark item name standardization & translation."""
        start_time = time.time()
        try:
            result = await provider.standardize_and_translate_item_name(item_name)
            end_time = time.time()

            return BenchmarkResult(
                provider=provider_name,
                operation="standardization",
                item_name=item_name,
                response_time=end_time - start_time,
                success=True,
                response=json.dumps(result, indent=2),
            )
        except Exception as e:
            end_time = time.time()
            return BenchmarkResult(
                provider=provider_name,
                operation="standardization",
                item_name=item_name,
                response_time=end_time - start_time,
                success=False,
                response="",
                error=str(e),
            )

    async def benchmark_text_generation(
        self, provider, provider_name: str, item_name: str
    ) -> BenchmarkResult:
        """Benchmark general text generation."""
        start_time = time.time()
        try:
            prompt = TEST_PROMPTS["text_generation"].format(item_name=item_name)
            result = await provider.generate_text(prompt)
            end_time = time.time()

            return BenchmarkResult(
                provider=provider_name,
                operation="text_generation",
                item_name=item_name,
                response_time=end_time - start_time,
                success=True,
                response=result,
            )
        except Exception as e:
            end_time = time.time()
            return BenchmarkResult(
                provider=provider_name,
                operation="text_generation",
                item_name=item_name,
                response_time=end_time - start_time,
                success=False,
                response="",
                error=str(e),
            )

    async def run_benchmark_suite(
        self, provider, provider_name: str
    ) -> List[BenchmarkResult]:
        """Run complete benchmark suite for a provider."""
        results = []
        operations = [
            ("categorization", self.benchmark_categorization),
            ("icon_suggestion", self.benchmark_icon_suggestion),
            ("standardization", self.benchmark_standardization),
            ("text_generation", self.benchmark_text_generation),
        ]

        print(f"\n🚀 Running benchmark suite for {provider_name}...")

        for run in range(self.runs):
            print(f"📊 Run {run + 1}/{self.runs}")

            for item in self.test_items:
                for op_name, op_func in operations:
                    try:
                        print(f"  - {op_name}: {item}")
                        result = await asyncio.wait_for(
                            op_func(provider, provider_name, item), timeout=self.timeout
                        )
                        results.append(result)

                        # Show immediate feedback
                        if result.success:
                            print(f"    ✅ {result.response_time:.2f}s")
                        else:
                            print(f"    ❌ {result.error}")

                    except asyncio.TimeoutError:
                        results.append(
                            BenchmarkResult(
                                provider=provider_name,
                                operation=op_name,
                                item_name=item,
                                response_time=self.timeout,
                                success=False,
                                response="",
                                error="Timeout",
                            )
                        )
                        print(f"    ⏰ Timeout ({self.timeout}s)")

                    # Small delay to avoid overwhelming the providers
                    await asyncio.sleep(0.1)

        return results

    def calculate_stats(
        self, results: List[BenchmarkResult], provider_name: str
    ) -> ProviderStats:
        """Calculate statistics for a provider."""
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        if successful:
            response_times = [r.response_time for r in successful]
            avg_time = statistics.mean(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            median_time = statistics.median(response_times)
        else:
            avg_time = min_time = max_time = median_time = 0.0

        return ProviderStats(
            provider=provider_name,
            total_operations=len(results),
            successful_operations=len(successful),
            failed_operations=len(failed),
            avg_response_time=avg_time,
            min_response_time=min_time,
            max_response_time=max_time,
            median_response_time=median_time,
            success_rate=len(successful) / len(results) * 100 if results else 0,
        )

    def print_results(
        self,
        gemini_results: List[BenchmarkResult],
        ollama_results: List[BenchmarkResult],
    ):
        """Print comprehensive benchmark results."""
        gemini_stats = (
            self.calculate_stats(gemini_results, "Gemini") if gemini_results else None
        )
        ollama_stats = (
            self.calculate_stats(ollama_results, "Ollama") if ollama_results else None
        )

        print_benchmark_results(
            gemini_results,
            ollama_results,
            gemini_stats,
            ollama_stats,
            self.test_items,
            settings,
        )

    def save_detailed_results(
        self,
        gemini_results: List[BenchmarkResult],
        ollama_results: List[BenchmarkResult],
    ):
        """Save detailed results to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ai_benchmark_results_{timestamp}.json"

        data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "runs": self.runs,
                "timeout": self.timeout,
                "test_items": self.test_items,
                "gemini_model": settings.GEMINI_MODEL_NAME,
                "ollama_model": settings.OLLAMA_MODEL_NAME,
                "ollama_server": settings.OLLAMA_BASE_URL,
            },
            "gemini_results": [asdict(r) for r in gemini_results],
            "ollama_results": [asdict(r) for r in ollama_results],
        }

        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

        print(f"\n💾 Detailed results saved to: {filename}")

    async def run(self):
        """Run the complete benchmark suite."""
        print("🔬 AI Provider Benchmark Suite")
        print(f"⚙️  Configuration:")
        print(f"   Runs per test: {self.runs}")
        print(f"   Timeout: {self.timeout}s")
        print(f"   Test items: {len(self.test_items)}")

        await self.setup_providers()

        gemini_results = []
        ollama_results = []

        # Run Gemini benchmarks
        if self.gemini_provider:
            gemini_results = await self.run_benchmark_suite(
                self.gemini_provider, "Gemini"
            )
        else:
            print("⚠️  Skipping Gemini benchmarks (provider not available)")

        # Run Ollama benchmarks
        if self.ollama_provider:
            ollama_results = await self.run_benchmark_suite(
                self.ollama_provider, "Ollama"
            )
        else:
            print("⚠️  Skipping Ollama benchmarks (provider not available)")

        # Print and save results
        if gemini_results or ollama_results:
            self.print_results(gemini_results, ollama_results)
            self.save_detailed_results(gemini_results, ollama_results)
        else:
            print("❌ No benchmarks could be run. Check provider configuration.")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Benchmark AI providers for FamilyCart"
    )
    parser.add_argument(
        "--runs", type=int, default=3, help="Number of runs per test (default: 3)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Timeout per operation in seconds (default: 120)",
    )

    args = parser.parse_args()

    benchmark = AIProviderBenchmark(runs=args.runs, timeout=args.timeout)
    await benchmark.run()


if __name__ == "__main__":
    asyncio.run(main())
