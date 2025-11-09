"""
Multi-Agent System for JAI GURU DEV AI Chatbot
================================================

This module implements a sophisticated multi-agent architecture for the spiritual
guidance chatbot. Each agent specializes in specific aspects of user interaction:

Agents:
    - BaseAgent: Abstract base class for all agents
    - OrchestratorAgent: Master coordinator and router
    - WisdomAgent: Knowledge retrieval and wisdom sharing (IMPLEMENTED)
    - AssessmentAgent: User state analysis and needs identification (TODO)
    - PracticeAgent: Practice recommendations and instructions (TODO)
    - ProgressAgent: Progress monitoring and tracking (TODO)

Architecture:
    Uses LangChain's agentic framework with:
    - Tool-based agent execution
    - Chain-of-thought reasoning
    - Structured output parsing
    - Error handling and fallbacks

Integration:
    - RAG System: Wisdom Agent integrates with existing RAG for teaching retrieval
    - Vector Store: ChromaDB with semantic search and metadata filtering
    - LLM: OpenAI/Groq for contextualization and reasoning
"""

from agents.base_agent import BaseAgent, AgentResponse, AgentError, AgentContext
from agents.agent_types import AgentType, IntentType, MessageType
from agents.llm_config import get_llm, get_default_provider, get_available_providers, LLMProvider
from agents.orchestrator import OrchestratorAgent
from agents.wisdom_agent import WisdomAgent

__version__ = "1.1.0"  # Added Wisdom Agent
__all__ = [
    "BaseAgent",
    "AgentResponse",
    "AgentError",
    "AgentContext",
    "AgentType",
    "IntentType",
    "MessageType",
    "get_llm",
    "get_default_provider",
    "get_available_providers",
    "LLMProvider",
    "OrchestratorAgent",
    "WisdomAgent"
]
