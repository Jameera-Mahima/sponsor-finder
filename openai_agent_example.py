"""
Example: Using OpenAI with Sponsor Finder Agents

This script demonstrates how to use OpenAI models with the agent system.
"""

from config import get_openai_client, get_model_for_agent, USE_OPENAI

def call_openai_agent(agent_type, prompt):
    """
    Call an OpenAI model configured for a specific agent type

    Args:
        agent_type: Type of agent (e.g., 'keyword-extractor', 'web-researcher')
        prompt: The prompt to send to the model

    Returns:
        Response from OpenAI model
    """
    if not USE_OPENAI:
        print("OpenAI is not enabled. Set USE_OPENAI=true in .env")
        return None

    # Get OpenAI client and appropriate model
    client = get_openai_client()
    model = get_model_for_agent(agent_type)

    print(f"Using {model} for {agent_type}")

    # Make API call
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": f"You are a {agent_type} agent for sponsor research."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content

# Example usage
if __name__ == "__main__":
    # Example 1: Keyword Extraction
    print("=" * 60)
    print("EXAMPLE 1: Keyword Extraction")
    print("=" * 60)

    prompt = """Extract keywords for sponsor search:
    "Find sponsors for arts education programs supporting students with disabilities in NYC"

    Return JSON with primary, secondary, location, and sector keywords."""

    result = call_openai_agent('keyword-extractor', prompt)
    print(result)
    print()

    # Example 2: Web Research (demonstration only)
    print("=" * 60)
    print("EXAMPLE 2: Web Research")
    print("=" * 60)

    prompt = """Find 3 potential sponsors for arts education in NYC.
    Return: name, type, website, relevance score."""

    result = call_openai_agent('web-researcher', prompt)
    print(result)
    print()

    # Show model configuration
    print("=" * 60)
    print("MODEL CONFIGURATION")
    print("=" * 60)
    from config import AGENT_MODELS
    for agent, model in AGENT_MODELS.items():
        print(f"{agent:30} -> {model}")
