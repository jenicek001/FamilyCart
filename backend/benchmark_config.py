#!/usr/bin/env python3
"""
Configuration and data structures for AI provider benchmarking.

This module contains all the configuration data, test items, prompts,
and utility functions used by the benchmark script.
"""

import statistics
from dataclasses import dataclass
from typing import List


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


# Test items covering different categories
TEST_ITEMS = [
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
]

# Test prompts for different operations
TEST_PROMPTS = {
    "categorization": "Please categorize this grocery item: {item_name}",
    "icon_suggestion": "Suggest an appropriate icon for: {item_name}",
    "standardization": "Standardize this item name: {item_name}",
    "text_generation": "Describe the shopping item '{item_name}' in one sentence.",
}

# Default configuration
DEFAULT_CONFIG = {
    "runs": 3,
    "timeout": 120,
    "operations": [
        "categorization",
        "icon_suggestion",
        "standardization",
        "text_generation",
    ],
}


def print_benchmark_results(
    gemini_results: List[BenchmarkResult],
    ollama_results: List[BenchmarkResult],
    gemini_stats,
    ollama_stats,
    test_items: List[str],
    settings,
):
    """Print comprehensive benchmark results."""
    print("\n" + "=" * 80)
    print("🎯 AI PROVIDER BENCHMARK RESULTS")
    print("=" * 80)

    # Print provider statistics
    if gemini_results:
        print(f"\n📊 GEMINI STATISTICS:")
        print(f"   Model: {settings.GEMINI_MODEL_NAME}")
        print(f"   Total Operations: {gemini_stats.total_operations}")
        print(f"   Success Rate: {gemini_stats.success_rate:.1f}%")
        print(f"   Avg Response Time: {gemini_stats.avg_response_time:.3f}s")
        print(f"   Min Response Time: {gemini_stats.min_response_time:.3f}s")
        print(f"   Max Response Time: {gemini_stats.max_response_time:.3f}s")
        print(f"   Median Response Time: {gemini_stats.median_response_time:.3f}s")

    if ollama_results:
        print(f"\n📊 OLLAMA STATISTICS:")
        print(f"   Model: {settings.OLLAMA_MODEL_NAME}")
        print(f"   Server: {settings.OLLAMA_BASE_URL}")
        print(f"   Total Operations: {ollama_stats.total_operations}")
        print(f"   Success Rate: {ollama_stats.success_rate:.1f}%")
        print(f"   Avg Response Time: {ollama_stats.avg_response_time:.3f}s")
        print(f"   Min Response Time: {ollama_stats.min_response_time:.3f}s")
        print(f"   Max Response Time: {ollama_stats.max_response_time:.3f}s")
        print(f"   Median Response Time: {ollama_stats.median_response_time:.3f}s")

    # Performance comparison
    if gemini_results and ollama_results:
        print(f"\n⚡ PERFORMANCE COMPARISON:")
        if gemini_stats.avg_response_time > 0 and ollama_stats.avg_response_time > 0:
            speed_ratio = (
                gemini_stats.avg_response_time / ollama_stats.avg_response_time
            )
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
            gemini_op = [
                r for r in gemini_results if r.operation == operation and r.success
            ]
            if gemini_op:
                avg_time = statistics.mean([r.response_time for r in gemini_op])
                success_rate = (
                    len(gemini_op)
                    / len([r for r in gemini_results if r.operation == operation])
                    * 100
                )
                print(f"     Gemini: {avg_time:.3f}s avg, {success_rate:.1f}% success")
            else:
                print(f"     Gemini: No successful operations")

        if ollama_results:
            ollama_op = [
                r for r in ollama_results if r.operation == operation and r.success
            ]
            if ollama_op:
                avg_time = statistics.mean([r.response_time for r in ollama_op])
                success_rate = (
                    len(ollama_op)
                    / len([r for r in ollama_results if r.operation == operation])
                    * 100
                )
                print(f"     Ollama: {avg_time:.3f}s avg, {success_rate:.1f}% success")
            else:
                print(f"     Ollama: No successful operations")

    # Sample responses
    print(f"\n📝 SAMPLE RESPONSES:")
    sample_item = test_items[0]  # First item

    for operation in ["categorization", "icon_suggestion", "text_generation"]:
        print(f"\n   {operation.upper()} for '{sample_item}':")

        if gemini_results:
            gemini_sample = next(
                (
                    r
                    for r in gemini_results
                    if r.operation == operation
                    and r.item_name == sample_item
                    and r.success
                ),
                None,
            )
            if gemini_sample:
                print(f"     Gemini: {gemini_sample.response[:100]}...")

        if ollama_results:
            ollama_sample = next(
                (
                    r
                    for r in ollama_results
                    if r.operation == operation
                    and r.item_name == sample_item
                    and r.success
                ),
                None,
            )
            if ollama_sample:
                print(f"     Ollama: {ollama_sample.response[:100]}...")
