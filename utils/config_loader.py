"""
Configuration Loader - Unified YAML-based Configuration
=======================================================

Loads all configuration from config.yaml including LLM provider settings.
Replaces the old llm_provider_config.py approach.
"""

import yaml
import os
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigLoader:
    """Centralized configuration loader"""

    _config: Optional[Dict[str, Any]] = None
    _config_path: str = "config.yaml"
    _prompts: Optional[Dict[str, Any]] = None
    _prompts_path: str = "system_prompts.yaml"

    @classmethod
    def load_config(cls, config_path: str = "config.yaml") -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if cls._config is None:
            cls._config_path = config_path
            with open(config_path, 'r', encoding='utf-8') as f:
                cls._config = yaml.safe_load(f)
        return cls._config

    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Get loaded configuration (loads if not already loaded)"""
        if cls._config is None:
            cls.load_config()
        return cls._config

    @classmethod
    def get_default_provider(cls) -> str:
        """Get the default LLM provider"""
        config = cls.get_config()
        return config.get('model_provider', {}).get('default', 'openai')

    @classmethod
    def get_provider_for_agent(cls, agent_type: str) -> str:
        """
        Get the LLM provider for a specific agent.

        Args:
            agent_type: Agent type (orchestrator, assessment, wisdom, practice, progress)

        Returns:
            Provider name to use (groq, openai, or anthropic)
        """
        config = cls.get_config()
        model_provider = config.get('model_provider', {})

        # Check for agent-specific override
        agent_overrides = model_provider.get('agent_overrides') or {}
        if agent_type in agent_overrides and agent_overrides[agent_type]:
            return agent_overrides[agent_type]

        # Return default provider
        return model_provider.get('default', 'openai')

    @classmethod
    def get_model_for_provider(cls, provider: str) -> Optional[str]:
        """
        Get the model name for a provider.

        Args:
            provider: Provider name (groq, openai, anthropic)

        Returns:
            Model name or None (uses provider default)
        """
        config = cls.get_config()
        model_provider = config.get('model_provider', {})
        provider_config = model_provider.get(provider, {})
        return provider_config.get('model')

    @classmethod
    def get_temperature_for_provider(cls, provider: str) -> float:
        """
        Get the temperature for a provider.

        Args:
            provider: Provider name

        Returns:
            Temperature value (default: 0.7)
        """
        config = cls.get_config()
        model_provider = config.get('model_provider', {})
        provider_config = model_provider.get(provider, {})
        return provider_config.get('temperature', 0.7)

    @classmethod
    def get_max_tokens_for_provider(cls, provider: str) -> int:
        """
        Get the max_tokens for a provider.

        Args:
            provider: Provider name

        Returns:
            Max tokens value (default: 1500)
        """
        config = cls.get_config()
        model_provider = config.get('model_provider', {})
        provider_config = model_provider.get(provider, {})
        return provider_config.get('max_tokens', 1500)

    @classmethod
    def get_provider_config(cls, provider: str) -> Dict[str, Any]:
        """
        Get full configuration for a provider.

        Args:
            provider: Provider name

        Returns:
            Dictionary with model, temperature, max_tokens
        """
        config = cls.get_config()
        model_provider = config.get('model_provider', {})
        return model_provider.get(provider, {})

    @classmethod
    def load_prompts(cls, prompts_path: str = "system_prompts.yaml") -> Dict[str, Any]:
        """
        Load prompts from YAML file.

        Args:
            prompts_path: Path to prompts YAML file

        Returns:
            Dictionary containing all prompts
        """
        if cls._prompts is None:
            cls._prompts_path = prompts_path
            try:
                with open(prompts_path, 'r', encoding='utf-8') as f:
                    cls._prompts = yaml.safe_load(f)
            except FileNotFoundError:
                # If prompts file not found, try in parent directory
                parent_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), prompts_path)
                with open(parent_path, 'r', encoding='utf-8') as f:
                    cls._prompts = yaml.safe_load(f)
        return cls._prompts

    @classmethod
    def get_prompts(cls) -> Dict[str, Any]:
        """
        Get loaded prompts (loads if not already loaded).

        Returns:
            Dictionary containing all prompts
        """
        if cls._prompts is None:
            cls.load_prompts()
        return cls._prompts

    @classmethod
    def get_prompt(cls, agent_type: str, prompt_name: str) -> str:
        """
        Get a specific prompt for an agent.

        Args:
            agent_type: Type of agent (e.g., 'assessment_agent_v2', 'wisdom_agent', 'orchestrator_agent')
            prompt_name: Name of the prompt (e.g., 'system_prompt', 'conversation_prompt', 'extraction_prompt')

        Returns:
            The prompt string

        Raises:
            KeyError: If agent_type or prompt_name not found

        Example:
            >>> system_prompt = ConfigLoader.get_prompt('assessment_agent_v2', 'system_prompt')
            >>> conv_prompt = ConfigLoader.get_prompt('assessment_agent_v2', 'conversation_prompt')
        """
        prompts = cls.get_prompts()

        if agent_type not in prompts:
            raise KeyError(f"Agent type '{agent_type}' not found in system_prompts.yaml. Available agents: {list(prompts.keys())}")

        agent_prompts = prompts[agent_type]

        if prompt_name not in agent_prompts:
            raise KeyError(f"Prompt '{prompt_name}' not found for agent '{agent_type}'. Available prompts: {list(agent_prompts.keys())}")

        return agent_prompts[prompt_name]

    @classmethod
    def get_agent_prompts(cls, agent_type: str) -> Dict[str, str]:
        """
        Get all prompts for a specific agent.

        Args:
            agent_type: Type of agent (e.g., 'assessment_agent_v2', 'wisdom_agent')

        Returns:
            Dictionary containing all prompts for the agent

        Example:
            >>> prompts = ConfigLoader.get_agent_prompts('assessment_agent_v2')
            >>> system_prompt = prompts['system_prompt']
            >>> conversation_prompt = prompts['conversation_prompt']
        """
        prompts = cls.get_prompts()

        if agent_type not in prompts:
            raise KeyError(f"Agent type '{agent_type}' not found in system_prompts.yaml. Available agents: {list(prompts.keys())}")

        return prompts[agent_type]

    @classmethod
    def validate_configuration(cls) -> bool:
        """
        Validate the configuration and check API keys.

        Returns:
            True if configuration is valid
        """
        from dotenv import load_dotenv
        load_dotenv()

        config = cls.get_config()
        default_provider = cls.get_default_provider()

        print("=" * 70)
        print("LLM PROVIDER CONFIGURATION")
        print("=" * 70)

        print(f"\n[OK] Default Provider: {default_provider}")
        print(f"     Model: {cls.get_model_for_provider(default_provider)}")
        print(f"     Temperature: {cls.get_temperature_for_provider(default_provider)}")

        # Check API keys
        print("\n[KEY] API Key Status:")

        providers = {
            "groq": "GROQ_API_KEY",
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY"
        }

        available = []
        for provider, key_name in providers.items():
            has_key = bool(os.getenv(key_name))
            status = "[OK]" if has_key else "[X]"
            print(f"      {status} {provider.upper()}: {key_name} {'set' if has_key else 'NOT SET'}")
            if has_key:
                available.append(provider)

        # Validate default provider
        if default_provider not in available:
            print(f"\n[WARN] WARNING: Default provider '{default_provider}' has no API key!")
            if available:
                print(f"       Available providers: {', '.join(available)}")
                print(f"       Consider changing 'model_provider.default' in config.yaml")
            else:
                print(f"       Please set at least one API key in your .env file")
            return False

        print(f"\n[OK] Configuration valid!")

        # Show agent overrides if any
        agent_overrides = config.get('model_provider', {}).get('agent_overrides') or {}
        active_overrides = {k: v for k, v in agent_overrides.items() if v}
        if active_overrides:
            print(f"\n[CONFIG] Agent-Specific Overrides:")
            for agent, provider in active_overrides.items():
                print(f"         - {agent}: {provider}")

        print("=" * 70)
        return True


# Convenience functions for backward compatibility
def get_default_provider() -> str:
    """Get the default LLM provider"""
    return ConfigLoader.get_default_provider()


def get_provider_for_agent(agent_type: str) -> str:
    """Get the LLM provider for a specific agent"""
    return ConfigLoader.get_provider_for_agent(agent_type)


def get_model_for_provider(provider: str) -> Optional[str]:
    """Get the model name for a provider"""
    return ConfigLoader.get_model_for_provider(provider)


def get_temperature_for_provider(provider: str) -> float:
    """Get the temperature for a provider"""
    return ConfigLoader.get_temperature_for_provider(provider)


def get_max_tokens_for_provider(provider: str) -> int:
    """Get the max_tokens for a provider"""
    return ConfigLoader.get_max_tokens_for_provider(provider)


def validate_configuration() -> bool:
    """Validate the configuration"""
    return ConfigLoader.validate_configuration()


def get_prompt(agent_type: str, prompt_name: str) -> str:
    """Get a specific prompt for an agent"""
    return ConfigLoader.get_prompt(agent_type, prompt_name)


def get_agent_prompts(agent_type: str) -> Dict[str, str]:
    """Get all prompts for a specific agent"""
    return ConfigLoader.get_agent_prompts(agent_type)


# For testing/validation
if __name__ == "__main__":
    validate_configuration()
