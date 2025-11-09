"""
Base Agent Architecture
=======================

Implements the base agent class using LangChain's agentic framework.
All specialized agents inherit from this base class.

Key Features:
    - LangChain agent integration
    - Structured input/output handling
    - Error handling and fallbacks
    - Logging and monitoring
    - Tool execution framework
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
import logging
from enum import Enum

from langchain_core.language_models import BaseChatModel
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool, StructuredTool
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain.callbacks.base import BaseCallbackHandler

from agents.agent_types import (
    AgentType, 
    MessageType, 
    IntentType,
    AgentName,
    UserId,
    SessionId,
    Confidence
)
from agents.llm_config import get_llm, get_default_provider, LLMProvider


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AgentContext:
    """Context information passed to agents"""
    user_id: UserId
    session_id: SessionId
    user_profile: Dict[str, Any]
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'user_id': self.user_id,
            'session_id': self.session_id,
            'user_profile': self.user_profile,
            'conversation_history': self.conversation_history,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }


@dataclass
class AgentResponse:
    """Structured response from an agent"""
    agent_name: AgentName
    content: str
    confidence: Confidence
    metadata: Dict[str, Any] = field(default_factory=dict)
    tools_used: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    success: bool = True
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'agent_name': self.agent_name,
            'content': self.content,
            'confidence': self.confidence,
            'metadata': self.metadata,
            'tools_used': self.tools_used,
            'processing_time': self.processing_time,
            'success': self.success,
            'error_message': self.error_message
        }


class AgentError(Exception):
    """Custom exception for agent errors"""
    def __init__(self, agent_name: str, message: str, original_error: Optional[Exception] = None):
        self.agent_name = agent_name
        self.message = message
        self.original_error = original_error
        super().__init__(f"[{agent_name}] {message}")


class AgentCallbackHandler(BaseCallbackHandler):
    """Custom callback handler for agent monitoring"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.start_time = None
        self.tools_used = []
    
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs):
        """Called when a tool starts executing"""
        tool_name = serialized.get('name', 'unknown')
        self.tools_used.append(tool_name)
        logger.info(f"[{self.agent_name}] Tool started: {tool_name}")
    
    def on_tool_end(self, output: str, **kwargs):
        """Called when a tool finishes executing"""
        logger.info(f"[{self.agent_name}] Tool completed")
    
    def on_tool_error(self, error: Union[Exception, KeyboardInterrupt], **kwargs):
        """Called when a tool encounters an error"""
        logger.error(f"[{self.agent_name}] Tool error: {error}")


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.
    
    Uses LangChain's agentic framework to provide:
    - Tool-based execution
    - Structured reasoning
    - Error handling
    - Monitoring and logging
    
    Attributes:
        agent_type (AgentType): Type of agent
        name (str): Unique name for the agent
        llm_provider (str): LLM provider (groq, openai, anthropic)
        llm (BaseChatModel): Language model for the agent
        tools (List[Tool]): Tools available to this agent
        agent_executor (AgentExecutor): LangChain agent executor
    """
    
    def __init__(
        self,
        agent_type: AgentType,
        name: Optional[str] = None,
        llm_provider: Optional[LLMProvider] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        verbose: bool = False
    ):
        """
        Initialize the base agent.
        
        Args:
            agent_type: Type of agent
            name: Optional custom name (defaults to agent_type value)
            llm_provider: LLM provider to use ("groq", "openai", "anthropic")
                        If None, automatically detects available provider
            model_name: Model name (provider-specific)
            temperature: LLM temperature
            verbose: Enable verbose logging
        """
        self.agent_type = agent_type
        self.name = name or agent_type.value
        self.verbose = verbose
        
        # Determine LLM provider
        if llm_provider is None:
            llm_provider = get_default_provider()
            logger.info(f"Auto-detected LLM provider: {llm_provider}")
        
        self.llm_provider = llm_provider
        
        # Initialize LLM using the config system
        self.llm = get_llm(
            provider=llm_provider,
            model_name=model_name,
            temperature=temperature
        )
        
        # Initialize tools (to be defined by subclasses)
        self.tools: List[Tool] = []
        
        # Agent executor (will be initialized after tools are defined)
        self.agent_executor: Optional[AgentExecutor] = None
        
        # Callback handler for monitoring
        self.callback_handler = AgentCallbackHandler(self.name)
        
        logger.info(f"Initialized {self.name} agent")
    
    @abstractmethod
    def define_tools(self) -> List[Tool]:
        """
        Define tools available to this agent.
        Must be implemented by subclasses.
        
        Returns:
            List of LangChain Tool objects
        """
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent.
        Must be implemented by subclasses.
        
        Returns:
            System prompt string
        """
        pass
    
    def initialize_agent(self):
        """
        Initialize the LangChain agent executor.
        Should be called after defining tools.
        """
        # Define tools
        self.tools = self.define_tools()
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create agent
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=self.verbose,
            handle_parsing_errors=True,
            max_iterations=3,
            callbacks=[self.callback_handler]
        )
        
        logger.info(f"{self.name} agent executor initialized with {len(self.tools)} tools")
    
    def process(
        self,
        input_text: str,
        context: AgentContext,
        chat_history: Optional[List[BaseMessage]] = None
    ) -> AgentResponse:
        """
        Main processing method for the agent.
        
        Args:
            input_text: User input or query
            context: Agent context with user info
            chat_history: Optional chat history
        
        Returns:
            AgentResponse with results
        """
        if not self.agent_executor:
            self.initialize_agent()
        
        start_time = datetime.now()
        
        try:
            # Validate input
            if not self.validate_input(input_text, context):
                raise AgentError(
                    self.name,
                    "Input validation failed"
                )
            
            # Prepare input with context
            enriched_input = self.enrich_input(input_text, context)
            
            # Execute agent
            result = self.agent_executor.invoke({
                "input": enriched_input,
                "chat_history": chat_history or []
            })
            
            # Extract response
            output_content = result.get("output", "")
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Create response
            response = AgentResponse(
                agent_name=self.name,
                content=output_content,
                confidence=self.calculate_confidence(result),
                metadata={
                    'context': context.to_dict(),
                    'raw_result': result
                },
                tools_used=self.callback_handler.tools_used,
                processing_time=processing_time,
                success=True
            )
            
            logger.info(
                f"{self.name} processed successfully in {processing_time:.2f}s "
                f"(confidence: {response.confidence:.2f})"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"{self.name} processing error: {e}")
            return self.handle_error(e, context)
    
    def validate_input(self, input_text: str, context: AgentContext) -> bool:
        """
        Validate input data.
        Can be overridden by subclasses for custom validation.
        
        Args:
            input_text: Input text to validate
            context: Agent context
        
        Returns:
            True if valid, False otherwise
        """
        # Basic validation
        if not input_text or not input_text.strip():
            logger.warning(f"{self.name}: Empty input")
            return False
        
        if not context.user_id:
            logger.warning(f"{self.name}: Missing user_id in context")
            return False
        
        return True
    
    def enrich_input(self, input_text: str, context: AgentContext) -> str:
        """
        Enrich input with context information.
        Can be overridden by subclasses for custom enrichment.
        
        Args:
            input_text: Original input text
            context: Agent context
        
        Returns:
            Enriched input string
        """
        # Default: add basic user context
        user_name = context.user_profile.get('name', 'User')
        
        enriched = f"""
User Input: {input_text}

User Context:
- Name: {user_name}
- User ID: {context.user_id}
"""
        
        # Add relevant profile info if available
        if 'emotional_state' in context.user_profile:
            enriched += f"- Current State: {context.user_profile['emotional_state']}\n"
        
        if 'experience_level' in context.user_profile:
            enriched += f"- Experience Level: {context.user_profile['experience_level']}\n"
        
        return enriched
    
    def calculate_confidence(self, result: Dict[str, Any]) -> Confidence:
        """
        Calculate confidence score for the response.
        Can be overridden by subclasses.
        
        Args:
            result: Agent execution result
        
        Returns:
            Confidence score (0.0 to 1.0)
        """
        # Default implementation: return moderate confidence
        # Subclasses should implement more sophisticated scoring
        return 0.8
    
    def handle_error(
        self, 
        error: Exception, 
        context: AgentContext
    ) -> AgentResponse:
        """
        Handle errors gracefully with fallback responses.
        
        Args:
            error: The exception that occurred
            context: Agent context
        
        Returns:
            AgentResponse with error information
        """
        logger.error(f"{self.name} error: {str(error)}")
        
        fallback_content = self.get_fallback_response(context)
        
        return AgentResponse(
            agent_name=self.name,
            content=fallback_content,
            confidence=0.3,
            metadata={'error_type': type(error).__name__},
            success=False,
            error_message=str(error)
        )
    
    def get_fallback_response(self, context: AgentContext) -> str:
        """
        Get fallback response for errors.
        Can be overridden by subclasses.
        
        Args:
            context: Agent context
        
        Returns:
            Fallback response string
        """
        user_name = context.user_profile.get('name', 'friend')
        
        return f"""I apologize, {user_name}. I'm having a moment of difficulty processing your request. 
Could you please rephrase your question or try asking in a different way? 
I'm here to help you on your journey. 🙏"""
    
    def __repr__(self) -> str:
        """String representation of the agent"""
        return f"{self.__class__.__name__}(name='{self.name}', type={self.agent_type})"
