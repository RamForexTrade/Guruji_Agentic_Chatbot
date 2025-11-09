"""
User Profile Data Model
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
import json


@dataclass
class UserProfile:
    """
    User profile data model with all user context information
    """
    user_id: str
    name: str
    age: Optional[int] = None
    life_aspect: str = ""
    emotional_state: str = ""
    guidance_type: str = ""
    specific_situation: str = ""
    experience_level: str = "beginner"  # beginner, intermediate, advanced
    preferences: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_active: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user profile to dictionary"""
        return {
            'user_id': self.user_id,
            'name': self.name,
            'age': self.age,
            'life_aspect': self.life_aspect,
            'emotional_state': self.emotional_state,
            'guidance_type': self.guidance_type,
            'specific_situation': self.specific_situation,
            'experience_level': self.experience_level,
            'preferences': self.preferences,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_active': self.last_active.isoformat() if self.last_active else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """Create UserProfile from dictionary"""
        # Convert string timestamps back to datetime
        if data.get('created_at') and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at') and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        if data.get('last_active') and isinstance(data['last_active'], str):
            data['last_active'] = datetime.fromisoformat(data['last_active'])
        
        return cls(**data)
    
    def get_context_summary(self) -> str:
        """Get a summary of user context for LLM prompts"""
        context_parts = [
            f"Name: {self.name}",
        ]
        
        if self.age:
            context_parts.append(f"Age: {self.age}")
        
        if self.life_aspect:
            context_parts.append(f"Life Aspect: {self.life_aspect}")
        
        if self.emotional_state:
            context_parts.append(f"Emotional State: {self.emotional_state}")
        
        if self.guidance_type:
            context_parts.append(f"Guidance Type: {self.guidance_type}")
        
        if self.specific_situation:
            context_parts.append(f"Situation: {self.specific_situation}")
        
        context_parts.append(f"Experience Level: {self.experience_level}")
        
        return "\n".join(context_parts)
    
    def update_from_context(self, context_dict: Dict[str, str]):
        """Update user profile from UserContext"""
        if 'life_aspect' in context_dict:
            self.life_aspect = context_dict['life_aspect']
        if 'emotional_state' in context_dict:
            self.emotional_state = context_dict['emotional_state']
        if 'guidance_type' in context_dict:
            self.guidance_type = context_dict['guidance_type']
        if 'specific_situation' in context_dict:
            self.specific_situation = context_dict['specific_situation']
        
        self.updated_at = datetime.now()
    
    def is_new_user(self) -> bool:
        """Check if this is a new user (less than 24 hours)"""
        if not self.created_at:
            return True
        
        age = datetime.now() - self.created_at
        return age.total_seconds() < 86400  # 24 hours
    
    def __repr__(self) -> str:
        return f"UserProfile(user_id='{self.user_id}', name='{self.name}', level='{self.experience_level}')"
