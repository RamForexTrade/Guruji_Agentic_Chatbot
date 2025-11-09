"""
Agent Types and Enumerations
=============================

Defines all types, enums, and constants used across the agent system.
"""

from enum import Enum
from typing import Literal


class AgentType(str, Enum):
    """Types of agents in the system"""
    ORCHESTRATOR = "orchestrator"
    WISDOM = "wisdom"
    ASSESSMENT = "assessment"
    PRACTICE = "practice"
    PROGRESS = "progress"


class IntentType(str, Enum):
    """User intent classifications"""
    SEEKING_WISDOM = "seeking_wisdom"
    EXPRESSING_STATE = "expressing_state"
    PRACTICE_COMPLETION = "practice_completion"
    PRACTICE_INQUIRY = "practice_inquiry"
    GENERAL_CONVERSATION = "general_conversation"
    GREETING = "greeting"
    FAREWELL = "farewell"
    FEEDBACK = "feedback"
    UNKNOWN = "unknown"


class MessageType(str, Enum):
    """Types of messages exchanged between agents"""
    QUERY = "query"
    RESPONSE = "response"
    ERROR = "error"
    ACKNOWLEDGMENT = "acknowledgment"


class EmotionalState(str, Enum):
    """Detected emotional states - aligned with Gurudev's wisdom categories"""
    LOVE = "love"
    FEAR = "fear"
    ANGER = "anger"
    DEPRESSION = "depression"
    OVERWHELMED = "overwhelmed"
    CONFUSION = "confusion"
    HURT = "hurt"
    LONELINESS = "loneliness"
    GUILT = "guilt"  # Guilt/Remorse
    INADEQUACY = "inadequacy"
    # V3 additions for more nuanced emotional detection
    FRUSTRATION = "frustration"
    NUMBNESS = "numbness"
    HOPE = "hope"
    SADNESS = "sadness"  # Alternative to SAD
    # Legacy states for backward compatibility
    ANXIOUS = "anxious"
    STRESSED = "stressed"
    CALM = "calm"
    SEEKING = "seeking"
    HAPPY = "happy"
    SAD = "sad"
    NEUTRAL = "neutral"
    UNKNOWN = "unknown"


class SeverityLevel(str, Enum):
    """Severity levels for user states"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ReadinessLevel(str, Enum):
    """User readiness for practice"""
    READY = "ready"
    NEEDS_PREPARATION = "needs_preparation"
    NOT_READY = "not_ready"


class PracticeType(str, Enum):
    """Types of spiritual practices"""
    PRANAYAMA = "pranayama"
    MEDITATION = "meditation"
    THERAPY = "therapy"
    MOVEMENT = "movement"
    CONTEMPLATION = "contemplation"
    LIFESTYLE = "lifestyle"


class ExperienceLevel(str, Enum):
    """User experience levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class LifeSituation(str, Enum):
    """Life situation categories (botherations) causing mental imbalance"""
    FINANCE_CAREER = "finance_career"
    DECISION_MAKING = "decision_making"  # Self-doubt
    RELATIONSHIP_LOVE = "relationship_love"
    BURNOUT = "burnout"
    HEALTH = "health"
    MIND_CREATED = "mind_created"  # Not external real situation, but mental
    WORLD_PROBLEMS = "world_problems"  # Natural calamity, politics, war, etc.
    SPIRITUAL_GROWTH = "spiritual_growth"
    UNKNOWN = "unknown"


class UserLocation(str, Enum):
    """User's physical location context for tailored recommendations"""
    HOME_INDOOR = "home_indoor"
    OUTDOOR = "outdoor"
    OFFICE = "office"
    PUBLIC_PLACE = "public_place"
    VEHICLE = "vehicle"
    UNKNOWN = "unknown"


class TimeAvailable(str, Enum):
    """Time user has available for wellness break"""
    SEVEN_MIN = "7_min"
    TWELVE_MIN = "12_min"
    TWENTY_MIN = "20_min"
    UNKNOWN = "unknown"


class MealStatus(str, Enum):
    """User's meal status (important for practice safety)"""
    FULL_STOMACH = "full_stomach"
    EMPTY_STOMACH = "empty_stomach"
    UNKNOWN = "unknown"


class ConversationState(str, Enum):
    """Assessment conversation flow states"""
    INITIAL_GREETING = "initial_greeting"
    PROBING_EMOTION = "probing_emotion"
    PROBING_SITUATION = "probing_situation"
    PROBING_LOCATION = "probing_location"
    PROBING_TIME = "probing_time"  # New: asking for time available
    PROBING_MEAL = "probing_meal"  # New: asking for meal status
    ASSESSMENT_COMPLETE = "assessment_complete"
    DELIVERING_SOLUTION = "delivering_solution"


# Type aliases for better code readability
AgentName = str
UserId = str
SessionId = str
Confidence = float  # 0.0 to 1.0
