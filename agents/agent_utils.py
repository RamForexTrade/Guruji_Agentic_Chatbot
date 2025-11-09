"""
Agent Communication Utilities
==============================

Helper functions and utilities for agent communication and coordination.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json

from agents.agent_types import MessageType, AgentName


@dataclass
class AgentMessage:
    """
    Message structure for inter-agent communication.
    """
    from_agent: AgentName
    to_agent: AgentName
    message_type: MessageType
    payload: Dict[str, Any]
    timestamp: datetime = None
    message_id: str = None
    
    def __post_init__(self):
        """Initialize computed fields"""
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.message_id is None:
            self.message_id = self._generate_message_id()
    
    def _generate_message_id(self) -> str:
        """Generate unique message ID"""
        import uuid
        return str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'from_agent': self.from_agent,
            'to_agent': self.to_agent,
            'message_type': self.message_type.value if isinstance(self.message_type, MessageType) else self.message_type,
            'payload': self.payload,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'message_id': self.message_id
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMessage':
        """Create from dictionary"""
        # Convert timestamp string to datetime if needed
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        # Convert message_type string to enum if needed
        if isinstance(data.get('message_type'), str):
            data['message_type'] = MessageType(data['message_type'])
        
        return cls(**data)


class AgentCommunicationProtocol:
    """
    Handles communication between agents.
    """
    
    def __init__(self):
        self.message_log: List[AgentMessage] = []
    
    def send_message(
        self,
        from_agent: AgentName,
        to_agent: AgentName,
        message_type: MessageType,
        payload: Dict[str, Any]
    ) -> AgentMessage:
        """
        Send a message from one agent to another.
        
        Args:
            from_agent: Sender agent name
            to_agent: Recipient agent name
            message_type: Type of message
            payload: Message payload
        
        Returns:
            AgentMessage object
        """
        message = AgentMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type,
            payload=payload
        )
        
        self.message_log.append(message)
        return message
    
    def get_message_history(
        self,
        agent_name: Optional[AgentName] = None,
        limit: int = 100
    ) -> List[AgentMessage]:
        """
        Get message history, optionally filtered by agent.
        
        Args:
            agent_name: Filter by agent (sent from or to)
            limit: Maximum number of messages to return
        
        Returns:
            List of AgentMessage objects
        """
        if agent_name:
            messages = [
                msg for msg in self.message_log
                if msg.from_agent == agent_name or msg.to_agent == agent_name
            ]
        else:
            messages = self.message_log
        
        return messages[-limit:]
    
    def clear_history(self):
        """Clear message history"""
        self.message_log = []


def format_user_context(context: Dict[str, Any]) -> str:
    """
    Format user context for agent consumption.
    
    Args:
        context: User context dictionary
    
    Returns:
        Formatted string
    """
    formatted = "User Context:\n"
    
    # Essential fields
    if 'name' in context:
        formatted += f"- Name: {context['name']}\n"
    
    if 'age' in context:
        formatted += f"- Age: {context['age']}\n"
    
    if 'emotional_state' in context:
        formatted += f"- Current State: {context['emotional_state']}\n"
    
    if 'life_aspect' in context:
        formatted += f"- Life Aspect: {context['life_aspect']}\n"
    
    if 'experience_level' in context:
        formatted += f"- Experience Level: {context['experience_level']}\n"
    
    # Additional fields
    if 'specific_situation' in context and context['specific_situation']:
        formatted += f"- Current Situation: {context['specific_situation']}\n"
    
    return formatted


def extract_intent_keywords(text: str) -> List[str]:
    """
    Extract keywords that indicate user intent.
    
    Args:
        text: User input text
    
    Returns:
        List of intent keywords
    """
    # Define intent keyword patterns
    intent_patterns = {
        'seeking_wisdom': ['why', 'what is', 'how can', 'teach me', 'explain', 'understand'],
        'expressing_state': ['feeling', 'feel', 'anxious', 'stressed', 'worried', 'happy', 'sad'],
        'practice_completion': ['completed', 'finished', 'did', 'practiced', 'done with'],
        'practice_inquiry': ['how to', 'practice', 'technique', 'meditation', 'pranayama'],
        'greeting': ['hello', 'hi', 'hey', 'good morning', 'good evening'],
        'farewell': ['bye', 'goodbye', 'see you', 'thank you']
    }
    
    text_lower = text.lower()
    found_keywords = []
    
    for intent, patterns in intent_patterns.items():
        for pattern in patterns:
            if pattern in text_lower:
                found_keywords.append(intent)
                break
    
    return found_keywords


def sanitize_agent_output(text: str) -> str:
    """
    Sanitize agent output to remove unwanted formatting.
    
    Args:
        text: Raw agent output
    
    Returns:
        Sanitized text
    """
    # Remove excessive newlines
    text = '\n'.join(line for line in text.split('\n') if line.strip())
    
    # Remove markdown artifacts if present
    text = text.replace('```', '')
    
    # Trim whitespace
    text = text.strip()
    
    return text


def merge_agent_responses(responses: List[Dict[str, Any]]) -> str:
    """
    Merge multiple agent responses into a coherent output.
    
    Args:
        responses: List of agent response dictionaries
    
    Returns:
        Merged response string
    """
    if not responses:
        return ""
    
    if len(responses) == 1:
        return responses[0].get('content', '')
    
    # Combine responses with natural transitions
    merged = []
    for i, response in enumerate(responses):
        content = response.get('content', '')
        if content:
            if i > 0:
                merged.append('\n\n')
            merged.append(content)
    
    return ''.join(merged)


def calculate_average_confidence(responses: List[Dict[str, Any]]) -> float:
    """
    Calculate average confidence across multiple agent responses.
    
    Args:
        responses: List of agent response dictionaries
    
    Returns:
        Average confidence score
    """
    if not responses:
        return 0.0
    
    confidences = [r.get('confidence', 0.0) for r in responses]
    return sum(confidences) / len(confidences)
