"""
Conversation Message Data Model
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class ConversationMessage:
    """
    Conversation message data model
    Represents a single message in the chat history
    """
    message_id: str
    user_id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Set default timestamp if not provided"""
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            'message_id': self.message_id,
            'user_id': self.user_id,
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationMessage':
        """Create ConversationMessage from dictionary"""
        # Convert string timestamp back to datetime
        if data.get('timestamp') and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        return cls(**data)
    
    def to_langchain_format(self) -> Dict[str, str]:
        """Convert to LangChain message format"""
        return {
            'role': self.role,
            'content': self.content
        }
    
    def is_user_message(self) -> bool:
        """Check if this is a user message"""
        return self.role == 'user'
    
    def is_assistant_message(self) -> bool:
        """Check if this is an assistant message"""
        return self.role == 'assistant'
    
    def get_display_time(self) -> str:
        """Get formatted display time"""
        if not self.timestamp:
            return ""
        
        now = datetime.now()
        diff = now - self.timestamp
        
        if diff.total_seconds() < 60:
            return "Just now"
        elif diff.total_seconds() < 3600:
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes} min ago"
        elif diff.total_seconds() < 86400:
            hours = int(diff.total_seconds() / 3600)
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        else:
            return self.timestamp.strftime("%b %d, %I:%M %p")
    
    def __repr__(self) -> str:
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"ConversationMessage(role='{self.role}', content='{preview}')"


@dataclass
class ConversationHistory:
    """
    Container for managing conversation history
    """
    messages: list[ConversationMessage] = field(default_factory=list)
    
    def add_message(self, message: ConversationMessage):
        """Add a message to history"""
        self.messages.append(message)
    
    def get_last_n_messages(self, n: int = 10) -> list[ConversationMessage]:
        """Get the last N messages"""
        return self.messages[-n:] if len(self.messages) >= n else self.messages
    
    def get_langchain_history(self, max_messages: int = 20) -> list[Dict[str, str]]:
        """Get conversation history in LangChain format"""
        recent_messages = self.get_last_n_messages(max_messages)
        return [msg.to_langchain_format() for msg in recent_messages]
    
    def clear(self):
        """Clear all messages"""
        self.messages = []
    
    def get_message_count(self) -> int:
        """Get total message count"""
        return len(self.messages)
    
    def get_user_message_count(self) -> int:
        """Get count of user messages"""
        return sum(1 for msg in self.messages if msg.is_user_message())
    
    def get_assistant_message_count(self) -> int:
        """Get count of assistant messages"""
        return sum(1 for msg in self.messages if msg.is_assistant_message())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert history to dictionary"""
        return {
            'messages': [msg.to_dict() for msg in self.messages],
            'total_messages': self.get_message_count(),
            'user_messages': self.get_user_message_count(),
            'assistant_messages': self.get_assistant_message_count()
        }
    
    def __len__(self) -> int:
        return len(self.messages)
    
    def __repr__(self) -> str:
        return f"ConversationHistory(messages={len(self.messages)})"
