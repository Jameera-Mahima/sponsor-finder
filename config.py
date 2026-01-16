"""
Configuration for Sponsor Finder System
Loads OpenAI API keys and model settings from environment variables
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL_FAST = os.getenv('OPENAI_MODEL_FAST', 'gpt-4o-mini')
OPENAI_MODEL_QUALITY = os.getenv('OPENAI_MODEL_QUALITY', 'gpt-4o')
USE_OPENAI = os.getenv('USE_OPENAI', 'true').lower() == 'true'

# Claude API Configuration (fallback)
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
USE_CLAUDE_FALLBACK = os.getenv('USE_CLAUDE_FALLBACK', 'true').lower() == 'true'

# Claude model mappings for fallback
CLAUDE_MODEL_FAST = 'claude-haiku-4-5-20251001'
CLAUDE_MODEL_QUALITY = 'claude-sonnet-4-5-20250929'

# Fallback mapping: OpenAI -> Claude
FALLBACK_MODEL_MAP = {
    'gpt-4o-mini': CLAUDE_MODEL_FAST,
    'gpt-4o': CLAUDE_MODEL_QUALITY
}

# Validate configuration
if USE_OPENAI and not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY not found in environment variables. "
        "Please create a .env file with your OpenAI API key."
    )

# Agent Model Mapping
# Maps agent types to their preferred models
AGENT_MODELS = {
    'keyword-extractor': OPENAI_MODEL_FAST,
    'web-researcher': OPENAI_MODEL_FAST,
    'categorizer': OPENAI_MODEL_FAST,
    'validator': OPENAI_MODEL_QUALITY,
    'salesforce-integration': OPENAI_MODEL_FAST,
    'engagement-tracking': OPENAI_MODEL_QUALITY,
    'event-coordination': OPENAI_MODEL_FAST,
    'campaign-orchestrator': OPENAI_MODEL_QUALITY,
}

def get_openai_client():
    """
    Returns configured OpenAI client
    """
    if not USE_OPENAI:
        raise RuntimeError("OpenAI is not enabled. Set USE_OPENAI=true in .env")

    try:
        from openai import OpenAI
        return OpenAI(api_key=OPENAI_API_KEY)
    except ImportError:
        raise ImportError(
            "openai package not installed. Install with: pip install openai"
        )

def get_model_for_agent(agent_type):
    """
    Get the appropriate OpenAI model for a given agent type

    Args:
        agent_type: Type of agent (keyword-extractor, web-researcher, etc.)

    Returns:
        Model name string (gpt-4o-mini or gpt-4o)
    """
    return AGENT_MODELS.get(agent_type, OPENAI_MODEL_FAST)

def get_claude_client():
    """
    Returns configured Anthropic client for fallback

    Raises:
        RuntimeError: If ANTHROPIC_API_KEY not configured
        ImportError: If anthropic package not installed
    """
    if not ANTHROPIC_API_KEY:
        raise RuntimeError(
            "ANTHROPIC_API_KEY not found in environment variables. "
            "Set ANTHROPIC_API_KEY in .env for fallback support."
        )

    try:
        from anthropic import Anthropic
        return Anthropic(api_key=ANTHROPIC_API_KEY)
    except ImportError:
        raise ImportError(
            "anthropic package not installed. "
            "Install with: pip install anthropic"
        )

def get_fallback_model(openai_model):
    """
    Get Claude fallback model for a given OpenAI model

    Args:
        openai_model: OpenAI model name (e.g., 'gpt-4o-mini')

    Returns:
        Claude model name (e.g., 'claude-haiku-4-5-20251001')
    """
    return FALLBACK_MODEL_MAP.get(openai_model, CLAUDE_MODEL_FAST)

def call_llm(agent_type, messages, temperature=0.7, max_tokens=4000):
    """
    Call LLM with automatic Claude fallback if OpenAI fails

    Args:
        agent_type: Type of agent (determines model selection)
        messages: List of message dicts [{"role": "user", "content": "..."}]
        temperature: Sampling temperature (0.0-2.0)
        max_tokens: Maximum tokens in response

    Returns:
        Dict with:
            - content: Response text
            - model_used: Which model was used
            - tokens_input: Input tokens
            - tokens_output: Output tokens
            - provider: 'openai' or 'claude'

    Raises:
        RuntimeError: If both OpenAI and Claude fail
    """
    import logging
    logger = logging.getLogger(__name__)

    openai_model = get_model_for_agent(agent_type)

    # Try OpenAI first
    if USE_OPENAI:
        try:
            client = get_openai_client()
            response = client.chat.completions.create(
                model=openai_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            return {
                'content': response.choices[0].message.content,
                'model_used': openai_model,
                'tokens_input': response.usage.prompt_tokens,
                'tokens_output': response.usage.completion_tokens,
                'provider': 'openai'
            }

        except Exception as e:
            if USE_CLAUDE_FALLBACK:
                logger.warning(
                    f"OpenAI API failed for {agent_type}: {str(e)[:100]}. "
                    f"Falling back to Claude."
                )
            else:
                raise

    # Fallback to Claude
    if USE_CLAUDE_FALLBACK:
        claude_model = get_fallback_model(openai_model)
        logger.info(
            f"Using Claude fallback: {claude_model} for agent {agent_type}"
        )

        try:
            client = get_claude_client()

            # Convert messages format (OpenAI format -> Claude format)
            system_msg = None
            user_msgs = []
            for msg in messages:
                if msg['role'] == 'system':
                    system_msg = msg['content']
                else:
                    user_msgs.append(msg)

            response = client.messages.create(
                model=claude_model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_msg,
                messages=user_msgs
            )

            return {
                'content': response.content[0].text,
                'model_used': claude_model,
                'tokens_input': response.usage.input_tokens,
                'tokens_output': response.usage.output_tokens,
                'provider': 'claude'
            }

        except Exception as e:
            logger.error(f"Claude fallback also failed: {str(e)[:100]}")
            raise RuntimeError(
                f"Both OpenAI and Claude failed. "
                f"OpenAI: {str(e)[:100]}"
            )

    raise RuntimeError("No LLM provider available. Check USE_OPENAI and USE_CLAUDE_FALLBACK settings.")

# Export configuration
__all__ = [
    'OPENAI_API_KEY',
    'OPENAI_MODEL_FAST',
    'OPENAI_MODEL_QUALITY',
    'USE_OPENAI',
    'ANTHROPIC_API_KEY',
    'USE_CLAUDE_FALLBACK',
    'CLAUDE_MODEL_FAST',
    'CLAUDE_MODEL_QUALITY',
    'FALLBACK_MODEL_MAP',
    'AGENT_MODELS',
    'get_openai_client',
    'get_claude_client',
    'get_model_for_agent',
    'get_fallback_model',
    'call_llm',
]
