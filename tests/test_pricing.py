"""
Unit tests for LLM pricing calculations

Tests accurate cost calculations for OpenAI and Claude models.
"""

import sys
sys.path.insert(0, 'logs/logging')

from pricing import calculate_cost, compare_costs, OPENAI_PRICING, CLAUDE_PRICING


def test_openai_mini_pricing():
    """Test gpt-4o-mini cost calculation"""
    # gpt-4o-mini: $0.15 per 1M input, $0.60 per 1M output
    cost = calculate_cost('gpt-4o-mini', 1000, 500)
    expected = (1000 * 0.15 / 1_000_000) + (500 * 0.60 / 1_000_000)

    assert abs(cost - expected) < 0.000001, f"Expected {expected}, got {cost}"
    print(f"✓ gpt-4o-mini pricing: 1000 input + 500 output = ${cost:.6f}")


def test_openai_full_pricing():
    """Test gpt-4o cost calculation"""
    # gpt-4o: $2.50 per 1M input, $10.00 per 1M output
    cost = calculate_cost('gpt-4o', 1000, 500)
    expected = (1000 * 2.50 / 1_000_000) + (500 * 10.00 / 1_000_000)

    assert abs(cost - expected) < 0.000001, f"Expected {expected}, got {cost}"
    print(f"✓ gpt-4o pricing: 1000 input + 500 output = ${cost:.6f}")


def test_claude_haiku_pricing():
    """Test Claude Haiku cost calculation"""
    # claude-haiku: $1.00 per 1M input, $5.00 per 1M output
    cost = calculate_cost('claude-haiku-4-5-20251001', 1000, 500)
    expected = (1000 * 1.00 / 1_000_000) + (500 * 5.00 / 1_000_000)

    assert abs(cost - expected) < 0.000001, f"Expected {expected}, got {cost}"
    print(f"✓ claude-haiku pricing: 1000 input + 500 output = ${cost:.6f}")


def test_claude_sonnet_pricing():
    """Test Claude Sonnet cost calculation"""
    # claude-sonnet: $3.00 per 1M input, $15.00 per 1M output
    cost = calculate_cost('claude-sonnet-4-5-20250929', 1000, 500)
    expected = (1000 * 3.00 / 1_000_000) + (500 * 15.00 / 1_000_000)

    assert abs(cost - expected) < 0.000001, f"Expected {expected}, got {cost}"
    print(f"✓ claude-sonnet pricing: 1000 input + 500 output = ${cost:.6f}")


def test_large_token_count():
    """Test pricing with large token counts"""
    # Real-world scenario: 50K input tokens, 5K output tokens
    cost = calculate_cost('gpt-4o-mini', 50000, 5000)
    expected = (50000 * 0.15 / 1_000_000) + (5000 * 0.60 / 1_000_000)

    assert abs(cost - expected) < 0.000001
    print(f"✓ Large tokens (50K + 5K): ${cost:.6f}")


def test_zero_tokens():
    """Test pricing with zero tokens"""
    cost = calculate_cost('gpt-4o-mini', 0, 0)
    assert cost == 0.0
    print(f"✓ Zero tokens: ${cost:.6f}")


def test_cost_comparison():
    """Test cost comparison between models"""
    comparison = compare_costs('gpt-4o-mini', 'gpt-4o', 10000, 5000)

    # gpt-4o-mini should be cheaper
    assert comparison['cheaper_model'] == 'gpt-4o-mini'
    assert comparison['savings_usd'] > 0
    assert comparison['savings_percent'] > 0

    print(f"✓ Cost comparison: gpt-4o-mini saves ${comparison['savings_usd']:.6f} ({comparison['savings_percent']:.2f}%)")


def test_cost_comparison_haiku_vs_sonnet():
    """Test cost comparison between Claude models"""
    comparison = compare_costs(
        'claude-haiku-4-5-20251001',
        'claude-sonnet-4-5-20250929',
        20000, 8000
    )

    # Haiku should be cheaper than Sonnet
    assert comparison['cheaper_model'] == 'claude-haiku-4-5-20251001'
    assert comparison['savings_usd'] > 0

    print(f"✓ Claude comparison: Haiku saves ${comparison['savings_usd']:.6f} ({comparison['savings_percent']:.2f}%)")


def test_unknown_model_fallback():
    """Test that unknown models fallback to Haiku pricing"""
    cost = calculate_cost('unknown-model-xyz', 1000, 500)

    # Should fallback to Haiku pricing
    expected = (1000 * 1.00 / 1_000_000) + (500 * 5.00 / 1_000_000)
    assert abs(cost - expected) < 0.000001

    print(f"✓ Unknown model fallback to Haiku: ${cost:.6f}")


def test_rounding_accuracy():
    """Test that costs are properly rounded to 6 decimal places"""
    cost = calculate_cost('gpt-4o-mini', 12345, 6789)

    # Should round to exactly 6 decimal places
    cost_str = f"{cost:.6f}"
    decimal_places = len(cost_str.split('.')[1])

    assert decimal_places <= 6, f"Cost has {decimal_places} decimal places"
    print(f"✓ Rounding accuracy: ${cost:.6f}")


def test_all_pricing_keys_exist():
    """Test that all expected models are in pricing dictionaries"""
    required_openai = ['gpt-4o-mini', 'gpt-4o']
    required_claude = ['claude-haiku-4-5-20251001', 'claude-sonnet-4-5-20250929']

    for model in required_openai:
        assert model in OPENAI_PRICING, f"Missing OpenAI model: {model}"
        assert 'input' in OPENAI_PRICING[model]
        assert 'output' in OPENAI_PRICING[model]

    for model in required_claude:
        assert model in CLAUDE_PRICING, f"Missing Claude model: {model}"
        assert 'input' in CLAUDE_PRICING[model]
        assert 'output' in CLAUDE_PRICING[model]

    print("✓ All required models present in pricing dictionaries")


def run_all_tests():
    """Run all pricing tests"""
    tests = [
        test_openai_mini_pricing,
        test_openai_full_pricing,
        test_claude_haiku_pricing,
        test_claude_sonnet_pricing,
        test_large_token_count,
        test_zero_tokens,
        test_cost_comparison,
        test_cost_comparison_haiku_vs_sonnet,
        test_unknown_model_fallback,
        test_rounding_accuracy,
        test_all_pricing_keys_exist,
    ]

    print("Running pricing tests...\n")

    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            return False

    print(f"\n✅ All {len(tests)} pricing tests passed!")
    return True


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
