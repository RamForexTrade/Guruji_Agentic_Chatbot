"""
LLM Provider Configuration
==========================

Utilities for initializing different LLM providers (Groq, OpenAI, etc.)
Makes the agent system LLM-agnostic and flexible.
"""

import os
from typing import Optional, Union, Literal
from langchain_core.language_models import BaseChatModel
import logging

logger = logging.getLogger(__name__)

# Type for LLM providers
LLMProvider = Literal["groq", "openai", "anthropic"]


def get_llm(
    provider: LLMProvider = "groq",
    model_name: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    **kwargs
) -> BaseChatModel:
    """
    Initialize and return an LLM based on the specified provider.
    
    Args:
        provider: LLM provider to use ("groq", "openai", "anthropic")
        model_name: Model name (provider-specific)
        temperature: Sampling temperature (0.0 to 1.0)
        max_tokens: Maximum tokens to generate
        **kwargs: Additional provider-specific arguments
    
    Returns:
        Initialized LangChain chat model
    
    Raises:
        ValueError: If provider is not supported or API key is missing
        ImportError: If required package is not installed
    
    Examples:
        >>> # Using Groq (fast and free)
        >>> llm = get_llm(provider="groq")
        
        >>> # Using OpenAI
        >>> llm = get_llm(provider="openai", model_name="gpt-4-turbo-preview")
        
        >>> # Custom configuration
        >>> llm = get_llm(provider="groq", temperature=0.5, max_tokens=2000)
    """
    
    provider = provider.lower()
    
    if provider == "groq":
        return _init_groq(model_name, temperature, max_tokens, **kwargs)
    
    elif provider == "openai":
        return _init_openai(model_name, temperature, max_tokens, **kwargs)
    
    elif provider == "anthropic":
        return _init_anthropic(model_name, temperature, max_tokens, **kwargs)
    
    else:
        raise ValueError(
            f"Unsupported provider: {provider}. "
            f"Supported providers: groq, openai, anthropic"
        )


def _init_groq(
    model_name: Optional[str],
    temperature: float,
    max_tokens: Optional[int],
    **kwargs
) -> BaseChatModel:
    """Initialize Groq LLM"""
    
    try:
        from langchain_groq import ChatGroq
    except ImportError:
        raise ImportError(
            "langchain-groq is not installed. "
            "Install it with: pip install langchain-groq"
        )
    
    # Check for API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found in environment variables. "
            "Please set it in your .env file."
        )
    
    # Default model for Groq
    if model_name is None:
        model_name = "openai/gpt-oss-120b" # "llama-3.3-70b-versatile"  # Fast and capable
        # Alternatives: "mixtral-8x7b-32768", "llama-3.1-70b-versatile"
    
    # Default max_tokens for Groq
    if max_tokens is None:
        max_tokens = 8000
    
    logger.info(f"Initializing Groq with model: {model_name}")
    
    return ChatGroq(
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        groq_api_key=api_key,
        **kwargs
    )


def _init_openai(
    model_name: Optional[str],
    temperature: float,
    max_tokens: Optional[int],
    **kwargs
) -> BaseChatModel:
    """Initialize OpenAI LLM"""
    
    try:
        from langchain_openai import ChatOpenAI
    except ImportError:
        raise ImportError(
            "langchain-openai is not installed. "
            "Install it with: pip install langchain-openai"
        )
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found in environment variables. "
            "Please set it in your .env file."
        )
    
    # Default model for OpenAI
    if model_name is None:
        model_name = "gpt-4-turbo-preview"
        # Alternatives: "gpt-4", "gpt-3.5-turbo"
    
    # Default max_tokens for OpenAI
    if max_tokens is None:
        max_tokens = 4000
    
    logger.info(f"Initializing OpenAI with model: {model_name}")
    
    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        openai_api_key=api_key,
        **kwargs
    )


def _init_anthropic(
    model_name: Optional[str],
    temperature: float,
    max_tokens: Optional[int],
    **kwargs
) -> BaseChatModel:
    """Initialize Anthropic (Claude) LLM"""
    
    try:
        from langchain_anthropic import ChatAnthropic
    except ImportError:
        raise ImportError(
            "langchain-anthropic is not installed. "
            "Install it with: pip install langchain-anthropic"
        )
    
    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY not found in environment variables. "
            "Please set it in your .env file."
        )
    
    # Default model for Anthropic
    if model_name is None:
        model_name = "claude-3-sonnet-20240229"
        # Alternatives: "claude-3-opus-20240229", "claude-3-haiku-20240307"
    
    # Default max_tokens for Anthropic
    if max_tokens is None:
        max_tokens = 4000
    
    logger.info(f"Initializing Anthropic with model: {model_name}")
    
    return ChatAnthropic(
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        anthropic_api_key=api_key,
        **kwargs
    )


def get_available_providers() -> list[str]:
    """
    Check which LLM providers are available (have API keys set).
    
    Returns:
        List of available provider names
    """
    available = []
    
    if os.getenv("GROQ_API_KEY"):
        available.append("groq")
    
    if os.getenv("OPENAI_API_KEY"):
        available.append("openai")
    
    if os.getenv("ANTHROPIC_API_KEY"):
        available.append("anthropic")
    
    return available


def get_default_provider() -> str:
    """
    Get the default provider based on available API keys.
    
    Priority: Groq > OpenAI > Anthropic
    
    Returns:
        Default provider name
    
    Raises:
        ValueError: If no providers are available
    """
    available = get_available_providers()
    
    if not available:
        raise ValueError(
            "No LLM providers available. Please set at least one API key:\n"
            "- GROQ_API_KEY (recommended)\n"
            "- OPENAI_API_KEY\n"
            "- ANTHROPIC_API_KEY"
        )
    
    # Priority order
    if "groq" in available:
        return "groq"
    elif "openai" in available:
        return "openai"
    elif "anthropic" in available:
        return "anthropic"
    else:
        return available[0]


# Provider-specific model recommendations
RECOMMENDED_MODELS = {
    "groq": {
        "default": "llama-3.3-70b-versatile",
        "fast": "llama-3.1-8b-instant",
        "powerful": "llama-3.1-70b-versatile",
        "alternatives": [
            "mixtral-8x7b-32768",
            "llama-3.3-70b-specdec",
            "gemma2-9b-it"
        ]
    },
    "openai": {
        "default": "gpt-4-turbo-preview",
        "fast": "gpt-3.5-turbo",
        "powerful": "gpt-4",
        "alternatives": [
            "gpt-4-1106-preview",
            "gpt-3.5-turbo-16k"
        ]
    },
    "anthropic": {
        "default": "claude-3-sonnet-20240229",
        "fast": "claude-3-haiku-20240307",
        "powerful": "claude-3-opus-20240229",
        "alternatives": []
    }
}


def get_recommended_model(
    provider: LLMProvider,
    priority: Literal["default", "fast", "powerful"] = "default"
) -> str:
    """
    Get recommended model for a provider.
    
    Args:
        provider: LLM provider
        priority: Model priority (default, fast, or powerful)
    
    Returns:
        Recommended model name
    """
    return RECOMMENDED_MODELS.get(provider, {}).get(priority, "default")


# Example usage and testing
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print("=" * 60)
    print("LLM Provider Configuration Test")
    print("=" * 60)
    
    # Check available providers
    print("\n1. Checking available providers...")
    available = get_available_providers()
    print(f"   Available: {', '.join(available) if available else 'None'}")
    
    if not available:
        print("\n❌ No API keys found!")
        print("\nPlease set at least one API key in your .env file:")
        print("  GROQ_API_KEY=your_key_here")
        print("  OPENAI_API_KEY=your_key_here")
        print("  ANTHROPIC_API_KEY=your_key_here")
    else:
        # Get default provider
        print("\n2. Getting default provider...")
        default = get_default_provider()
        print(f"   Default: {default}")
        
        # Initialize LLM
        print(f"\n3. Initializing {default} LLM...")
        try:
            llm = get_llm(provider=default)
            print(f"   ✅ Success: {type(llm).__name__}")
            print(f"   Model: {llm.model_name if hasattr(llm, 'model_name') else llm.model}")
            
            # Test invocation
            print("\n4. Testing LLM invocation...")
            response = llm.invoke("Say 'Hello from JAI GURU DEV AI!' in one sentence.")
            print(f"   Response: {response.content}")
            
            print("\n✅ All tests passed!")
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    print("\n" + "=" * 60)
