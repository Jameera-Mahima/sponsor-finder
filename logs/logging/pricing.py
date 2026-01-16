"""
LLM Pricing Information - Updated January 2025

Centralized pricing data for accurate cost calculations.
Supports both OpenAI and Claude models.
"""

# OpenAI Pricing (as of January 2025)
OPENAI_PRICING = {
    'gpt-4o-mini': {
        'input': 0.15 / 1_000_000,   # $0.15 per 1M input tokens
        'output': 0.60 / 1_000_000,  # $0.60 per 1M output tokens
    },
    'gpt-4o': {
        'input': 2.50 / 1_000_000,   # $2.50 per 1M input tokens
        'output': 10.00 / 1_000_000, # $10.00 per 1M output tokens
    }
}

# Claude Pricing (as of January 2025)
CLAUDE_PRICING = {
    'claude-haiku-4-5-20251001': {
        'input': 1.00 / 1_000_000,   # $1.00 per 1M input tokens
        'output': 5.00 / 1_000_000,  # $5.00 per 1M output tokens
    },
    'claude-sonnet-4-5-20250929': {
        'input': 3.00 / 1_000_000,   # $3.00 per 1M input tokens
        'output': 15.00 / 1_000_000, # $15.00 per 1M output tokens
    }
}


def calculate_cost(model_name, tokens_input, tokens_output):
    """
    Calculate cost for a model execution

    Args:
        model_name: Model identifier (e.g., 'gpt-4o-mini', 'claude-haiku-4-5-20251001')
        tokens_input: Number of input tokens
        tokens_output: Number of output tokens

    Returns:
        Cost in USD (rounded to 6 decimal places)
    """
    # Try OpenAI pricing
    if model_name in OPENAI_PRICING:
        pricing = OPENAI_PRICING[model_name]
        cost = (tokens_input * pricing['input']) + (tokens_output * pricing['output'])
        return round(cost, 6)

    # Try Claude pricing
    if model_name in CLAUDE_PRICING:
        pricing = CLAUDE_PRICING[model_name]
        cost = (tokens_input * pricing['input']) + (tokens_output * pricing['output'])
        return round(cost, 6)

    # Fallback: assume Haiku-level pricing if model unknown
    pricing = CLAUDE_PRICING['claude-haiku-4-5-20251001']
    cost = (tokens_input * pricing['input']) + (tokens_output * pricing['output'])
    return round(cost, 6)


def get_pricing_info(model_name):
    """
    Get pricing information for a model

    Args:
        model_name: Model identifier

    Returns:
        Dict with 'input' and 'output' prices per token
    """
    if model_name in OPENAI_PRICING:
        return OPENAI_PRICING[model_name]
    if model_name in CLAUDE_PRICING:
        return CLAUDE_PRICING[model_name]
    return CLAUDE_PRICING['claude-haiku-4-5-20251001']


def compare_costs(model1, model2, tokens_input, tokens_output):
    """
    Compare costs between two models

    Args:
        model1: First model identifier
        model2: Second model identifier
        tokens_input: Number of input tokens
        tokens_output: Number of output tokens

    Returns:
        Dict with cost for each model and savings percentage
    """
    cost1 = calculate_cost(model1, tokens_input, tokens_output)
    cost2 = calculate_cost(model2, tokens_input, tokens_output)

    max_cost = max(cost1, cost2)
    savings = abs(cost1 - cost2)
    savings_pct = (savings / max_cost * 100) if max_cost > 0 else 0

    return {
        'model1': model1,
        'cost1': cost1,
        'model2': model2,
        'cost2': cost2,
        'cheaper_model': model1 if cost1 < cost2 else model2,
        'savings_usd': round(savings, 6),
        'savings_percent': round(savings_pct, 2)
    }


# Export public functions
__all__ = [
    'OPENAI_PRICING',
    'CLAUDE_PRICING',
    'calculate_cost',
    'get_pricing_info',
    'compare_costs'
]
