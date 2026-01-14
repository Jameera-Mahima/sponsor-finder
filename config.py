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

# Export configuration
__all__ = [
    'OPENAI_API_KEY',
    'OPENAI_MODEL_FAST',
    'OPENAI_MODEL_QUALITY',
    'USE_OPENAI',
    'AGENT_MODELS',
    'get_openai_client',
    'get_model_for_agent',
]
