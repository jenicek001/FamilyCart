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

import asyncio
import json
import time
import statistics
import argparse
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict
import os
import sys
import httpx
from datetime import datetime

# Add the backend app directory to Python path
sys.path.append('/home/honzik/GitHub/FamilyCart/FamilyCart/backend')

from app.core.config import settings
from app.services.ai_factory import get_ai_provider
from app.services.gemini_provider import GeminiProvider
from app.services.ollama_provider import OllamaProvider


@dataclass
class BenchmarkResult:
    """Container for benchmark results of a single operation."""
    provider: str
    operation: str
    item_name: str
    response_time: float  # in seconds
    success: bool
    response: str
    error: str = ""
    

@dataclass
class ProviderStats:
    """Statistics for a provider across all operations."""
    provider: str
    total_operations: int
    successful_operations: int
    failed_operations: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    median_response_time: float
    success_rate: float


class AIProviderBenchmark:
    """Benchmark runner for AI providers."""
    
    def __init__(self, runs: int = 10, timeout: int = 120):
        self.runs = runs
        self.timeout = timeout
        self.results: List[BenchmarkResult] = []
        
        # Test items covering different categories
        self.test_items = [
            "organic apples",
            "whole milk",
            "chicken breast", 
            "sourdough bread",
            "frozen pizza",
            "olive oil",
            "orange juice",
            "shampoo",
            "paper towels",
            "greek yogurt",
            "salmon fillet",
            "avocados",
            "ice cream",
            "pasta sauce",
            "toilet paper"
        ]
        
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
                response = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=5)
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
                    print(f"❌ Ollama server not available (status: {response.status_code})")
        except Exception as e:
            print(f"❌ Failed to initialize Ollama provider: {e}")
            
    async def benchmark_categorization(self, provider, provider_name: str, item_name: str) -> BenchmarkResult:
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
                response=category
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
                error=str(e)
            )
            
    async def benchmark_icon_suggestion(self, provider, provider_name: str, item_name: str) -> BenchmarkResult:
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
                response=icon
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
                error=str(e)
            )
            
    async def benchmark_standardization(self, provider, provider_name: str, item_name: str) -> BenchmarkResult:
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
                response=json.dumps(result, indent=2)
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
                error=str(e)
            )
            
    async def benchmark_text_generation(self, provider, provider_name: str, item_name: str) -> BenchmarkResult:
        """Benchmark general text generation."""
        start_time = time.time()
        try:
            prompt = f"Describe the shopping item '{item_name}' in one sentence."
            result = await provider.generate_text(prompt)
            end_time = time.time()
            
            return BenchmarkResult(
                provider=provider_name,
                operation="text_generation",
                item_name=item_name,
                response_time=end_time - start_time,
                success=True,
                response=result
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
                error=str(e)
            )
            
    async def run_benchmark_suite(self, provider, provider_name: str) -> List[BenchmarkResult]:
        """Run complete benchmark suite for a provider."""
        results = []
        operations = [
            ("categorization", self.benchmark_categorization),
            ("icon_suggestion", self.benchmark_icon_suggestion), 
            ("standardization", self.benchmark_standardization),
            ("text_generation", self.benchmark_text_generation)
        ]
        
        print(f"\n🚀 Running benchmark suite for {provider_name}...")
        
        for run in range(self.runs):
            print(f"📊 Run {run + 1}/{self.runs}")
            
            for item in self.test_items:
                for op_name, op_func in operations:
                    try:
                        print(f"  - {op_name}: {item}")
                        result = await asyncio.wait_for(
                            op_func(provider, provider_name, item),
                            timeout=self.timeout
                        )
                        results.append(result)
                        
                        # Show immediate feedback
                        if result.success:
                            print(f"    ✅ {result.response_time:.2f}s")
                        else:
                            print(f"    ❌ {result.error}")
                            
                    except asyncio.TimeoutError:
                        results.append(BenchmarkResult(
                            provider=provider_name,
                            operation=op_name,
                            item_name=item,
                            response_time=self.timeout,
                            success=False,
                            response="",
                            error="Timeout"
                        ))
                        print(f"    ⏰ Timeout ({self.timeout}s)")
                        
                    # Small delay to avoid overwhelming the providers
                    await asyncio.sleep(0.1)
                    
        return results
        
    def calculate_stats(self, results: List[BenchmarkResult], provider_name: str) -> ProviderStats:
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
            success_rate=len(successful) / len(results) * 100 if results else 0
        )
        
    def print_results(self, gemini_results: List[BenchmarkResult], ollama_results: List[BenchmarkResult]):
        """Print comprehensive benchmark results."""
        print("\n" + "="*80)
        print("🎯 AI PROVIDER BENCHMARK RESULTS")
        print("="*80)
        
        # Calculate stats for each provider
        if gemini_results:
            gemini_stats = self.calculate_stats(gemini_results, "Gemini")
            print(f"\n📊 GEMINI STATISTICS:")
            print(f"   Model: {settings.GEMINI_MODEL_NAME}")
            print(f"   Total Operations: {gemini_stats.total_operations}")
            print(f"   Success Rate: {gemini_stats.success_rate:.1f}%")
            print(f"   Avg Response Time: {gemini_stats.avg_response_time:.3f}s")
            print(f"   Min Response Time: {gemini_stats.min_response_time:.3f}s") 
            print(f"   Max Response Time: {gemini_stats.max_response_time:.3f}s")
            print(f"   Median Response Time: {gemini_stats.median_response_time:.3f}s")
            
        if ollama_results:
            ollama_stats = self.calculate_stats(ollama_results, "Ollama")
            print(f"\n📊 OLLAMA STATISTICS:")
            print(f"   Model: {settings.OLLAMA_MODEL_NAME}")
            print(f"   Server: {settings.OLLAMA_BASE_URL}")
            print(f"   Total Operations: {ollama_stats.total_operations}")
            print(f"   Success Rate: {ollama_stats.success_rate:.1f}%")
            print(f"   Avg Response Time: {ollama_stats.avg_response_time:.3f}s")
            print(f"   Min Response Time: {ollama_stats.min_response_time:.3f}s")
            print(f"   Max Response Time: {ollama_stats.max_response_time:.3f}s")
            print(f"   Median Response Time: {ollama_stats.median_response_time:.3f}s")
            
        # Comparison
        if gemini_results and ollama_results:
            print(f"\n⚡ PERFORMANCE COMPARISON:")
            if gemini_stats.avg_response_time > 0 and ollama_stats.avg_response_time > 0:
                speed_ratio = gemini_stats.avg_response_time / ollama_stats.avg_response_time
                if speed_ratio > 1:
                    print(f"   Ollama is {speed_ratio:.1f}x faster than Gemini")
                else:
                    print(f"   Gemini is {1/speed_ratio:.1f}x faster than Ollama")
                    
            print(f"   Gemini Success Rate: {gemini_stats.success_rate:.1f}%")
            print(f"   Ollama Success Rate: {ollama_stats.success_rate:.1f}%")
            
        # Operation breakdown
        print(f"\n📋 OPERATION BREAKDOWN:")
        all_results = (gemini_results or []) + (ollama_results or [])
        operations = set(r.operation for r in all_results)
        
        for operation in sorted(operations):
            print(f"\n   {operation.upper()}:")
            
            if gemini_results:
                gemini_op = [r for r in gemini_results if r.operation == operation and r.success]
                if gemini_op:
                    avg_time = statistics.mean([r.response_time for r in gemini_op])
                    success_rate = len(gemini_op) / len([r for r in gemini_results if r.operation == operation]) * 100
                    print(f"     Gemini: {avg_time:.3f}s avg, {success_rate:.1f}% success")
                else:
                    print(f"     Gemini: No successful operations")
                    
            if ollama_results:
                ollama_op = [r for r in ollama_results if r.operation == operation and r.success]
                if ollama_op:
                    avg_time = statistics.mean([r.response_time for r in ollama_op])
                    success_rate = len(ollama_op) / len([r for r in ollama_results if r.operation == operation]) * 100
                    print(f"     Ollama: {avg_time:.3f}s avg, {success_rate:.1f}% success")
                else:
                    print(f"     Ollama: No successful operations")
                    
        # Sample responses
        print(f"\n📝 SAMPLE RESPONSES:")
        sample_item = self.test_items[0]  # "organic apples"
        
        for operation in ["categorization", "icon_suggestion", "text_generation"]:
            print(f"\n   {operation.upper()} for '{sample_item}':")
            
            if gemini_results:
                gemini_sample = next((r for r in gemini_results 
                                    if r.operation == operation and r.item_name == sample_item and r.success), None)
                if gemini_sample:
                    print(f"     Gemini: {gemini_sample.response[:100]}...")
                    
            if ollama_results:
                ollama_sample = next((r for r in ollama_results 
                                    if r.operation == operation and r.item_name == sample_item and r.success), None)
                if ollama_sample:
                    print(f"     Ollama: {ollama_sample.response[:100]}...")
                    
    def save_detailed_results(self, gemini_results: List[BenchmarkResult], ollama_results: List[BenchmarkResult]):
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
                "ollama_server": settings.OLLAMA_BASE_URL
            },
            "gemini_results": [asdict(r) for r in gemini_results],
            "ollama_results": [asdict(r) for r in ollama_results]
        }
        
        with open(filename, 'w') as f:
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
            gemini_results = await self.run_benchmark_suite(self.gemini_provider, "Gemini")
        else:
            print("⚠️  Skipping Gemini benchmarks (provider not available)")
            
        # Run Ollama benchmarks  
        if self.ollama_provider:
            ollama_results = await self.run_benchmark_suite(self.ollama_provider, "Ollama")
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
    parser = argparse.ArgumentParser(description="Benchmark AI providers for FamilyCart")
    parser.add_argument("--runs", type=int, default=3, help="Number of runs per test (default: 3)")
    parser.add_argument("--timeout", type=int, default=120, help="Timeout per operation in seconds (default: 120)")
    
    args = parser.parse_args()
    
    benchmark = AIProviderBenchmark(runs=args.runs, timeout=args.timeout)
    await benchmark.run()


if __name__ == "__main__":
    asyncio.run(main())
