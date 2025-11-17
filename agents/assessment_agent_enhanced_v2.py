"""
Enhanced Assessment Agent V2 - Deeply Empathetic & Gurudev-Inspired
====================================================================

This version focuses on:
1. DEEP empathetic probing - not rushing through stages
2. Understanding ROOT cause before asking location
3. Soothing, compassionate tone like Gurudev
4. Natural conversation flow (not mechanical checklist)
5. Reflecting back what user says with warmth
6. Only completing assessment when we truly understand the pain

Key Behavioral Changes from V1:
- NO quick detection that rushes through stages
- MUST probe emotion → then situation → multiple turns if needed
- Only ask location AFTER fully understanding emotional landscape
- Use reflective listening ("I hear that you're feeling...")
- Acknowledge pain before probing deeper
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
import logging
import json
import re

from langchain_core.prompts import PromptTemplate
from langchain_core.messages import BaseMessage

from agents.base_agent import BaseAgent, AgentContext, AgentResponse
from agents.agent_types import (
    AgentType,
    EmotionalState,
    SeverityLevel,
    ReadinessLevel,
    PracticeType,
    LifeSituation,
    UserLocation,
    TimeAvailable,
    MealStatus,
    ConversationState
)
from utils.config_loader import get_prompt

logger = logging.getLogger(__name__)


@dataclass
class EnhancedAssessment:
    """Assessment state - tracks what we know about the user's situation"""

    # What we're trying to understand
    primary_emotion: EmotionalState = EmotionalState.UNKNOWN
    secondary_emotions: List[EmotionalState] = field(default_factory=list)
    life_situation: LifeSituation = LifeSituation.UNKNOWN
    user_location: UserLocation = UserLocation.UNKNOWN
    user_age: Optional[int] = None

    # NEW: Additional context for better practice recommendations
    time_available: TimeAvailable = TimeAvailable.UNKNOWN  # 7/12/20 minutes
    meal_status: MealStatus = MealStatus.UNKNOWN  # full/empty stomach

    # Detailed understanding (for better wisdom matching)
    situation_details: str = ""  # What the user actually said about their situation
    emotion_details: str = ""    # How they described their feelings

    # Assessment flow control
    conversation_state: ConversationState = ConversationState.INITIAL_GREETING
    turns_in_current_state: int = 0  # How many turns in this stage
    is_complete: bool = False

    # Tone and context
    severity: SeverityLevel = SeverityLevel.MEDIUM
    tone: str = "warm"  # warm, somber, playful
    confidence: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'primary_emotion': self.primary_emotion.value if isinstance(self.primary_emotion, EmotionalState) else self.primary_emotion,
            'secondary_emotions': [e.value if isinstance(e, EmotionalState) else e for e in self.secondary_emotions],
            'life_situation': self.life_situation.value if isinstance(self.life_situation, LifeSituation) else self.life_situation,
            'user_location': self.user_location.value if isinstance(self.user_location, UserLocation) else self.user_location,
            'user_age': self.user_age,
            'time_available': self.time_available.value if isinstance(self.time_available, TimeAvailable) else self.time_available,
            'meal_status': self.meal_status.value if isinstance(self.meal_status, MealStatus) else self.meal_status,
            'situation_details': self.situation_details,
            'emotion_details': self.emotion_details,
            'conversation_state': self.conversation_state.value if isinstance(self.conversation_state, ConversationState) else self.conversation_state,
            'turns_in_current_state': self.turns_in_current_state,
            'is_complete': self.is_complete,
            'severity': self.severity.value if isinstance(self.severity, SeverityLevel) else self.severity,
            'tone': self.tone,
            'confidence': self.confidence
        }


class EnhancedAssessmentAgentV2(BaseAgent):
    """
    Deeply empathetic assessment agent inspired by Gurudev's compassionate style.

    Philosophy:
    - We are here to LISTEN first, understand deeply
    - Not rushing to solutions - taking time to understand the pain
    - Reflecting back what we hear with compassion
    - Gentle probing to uncover root cause
    - Only after full understanding → suggest practices

    Conversation Flow:
    1. WARM GREETING - make them feel safe
    2. UNDERSTAND EMOTION - what are they feeling? (may take 2-3 turns)
    3. UNDERSTAND ROOT CAUSE - what's causing it? (may take 2-3 turns)
    4. CONTEXT (location) - only after we fully understand
    5. COMPLETE - now we can help
    """

    def __init__(
        self,
        llm_provider: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.8,  # Higher for more empathetic responses
        verbose: bool = False
    ):
        """Initialize V2 Assessment Agent"""
        super().__init__(
            agent_type=AgentType.ASSESSMENT,
            name="assessment_v2",
            llm_provider=llm_provider,
            model_name=model_name,
            temperature=temperature,
            verbose=verbose
        )

        # Create prompts
        self.conversation_prompt = self._create_conversation_prompt()
        self.extraction_prompt = self._create_extraction_prompt()

        logger.info("Enhanced Assessment Agent V2 initialized (deeply empathetic mode)")

    def define_tools(self) -> List:
        """
        Define tools for the agent.
        V2 doesn't use tools - it's pure conversational with built-in detection.
        """
        return []

    def get_system_prompt(self) -> str:
        """
        Get system prompt for the agent.
        Wisdom Companion style - deeply empathetic assessment.
        Loaded from system_prompts.yaml for easy customization.
        """
        try:
            return get_prompt('assessment_agent_v2', 'system_prompt')
        except Exception as e:
            logger.error(f"Failed to load system prompt from YAML: {e}")
            # Fallback to empty prompt if loading fails
            raise RuntimeError(f"Could not load assessment agent system prompt: {e}")

    def _create_conversation_prompt(self) -> PromptTemplate:
        """
        Wisdom Companion unified conversation prompt.
        Emphasizes deep listening and empathetic probing.
        Loaded from system_prompts.yaml for easy customization.
        """
        try:
            template = get_prompt('assessment_agent_v2', 'conversation_prompt')
            return PromptTemplate(
                template=template,
                input_variables=["time_of_day", "user_name", "user_message", "conversation_summary", "assessment_summary"]
            )
        except Exception as e:
            logger.error(f"Failed to load conversation prompt from YAML: {e}")
            raise RuntimeError(f"Could not load assessment agent conversation prompt: {e}")

    def _create_extraction_prompt(self) -> PromptTemplate:
        """
        Extract structured data from conversation.
        Loaded from system_prompts.yaml for easy customization.
        """
        try:
            template = get_prompt('assessment_agent_v2', 'extraction_prompt')
            return PromptTemplate(
                template=template,
                input_variables=["conversation"]
            )
        except Exception as e:
            logger.error(f"Failed to load extraction prompt from YAML: {e}")
            raise RuntimeError(f"Could not load assessment agent extraction prompt: {e}")

    def process(
        self,
        input_text: str,
        context: AgentContext,
        chat_history: Optional[List[BaseMessage]] = None
    ) -> AgentResponse:
        """Main processing - deeply empathetic conversation"""

        start_time = datetime.now()

        try:
            # Get or create assessment
            assessment = self._get_current_assessment(context)

            # CRITICAL: Capture the state at START of turn, before any detection
            # This prevents detection from running on the same turn as state transition
            state_at_turn_start = assessment.conversation_state

            # Track turns in current state
            assessment.turns_in_current_state += 1

            logger.info(f"🔍 Turn start: state={state_at_turn_start.value}, turns={assessment.turns_in_current_state}, input='{input_text[:50]}'")

            # STEP 1: DETECT and UPDATE assessment FIRST (before generating LLM response)
            # This ensures the LLM sees the updated assessment when generating the response

            # Detect age from user input if not already known
            # Age is asked FIRST, so detect it when we haven't stored it yet
            if assessment.user_age is None:
                detected_age = self._detect_age(input_text)
                if detected_age is not None:
                    assessment.user_age = detected_age
                    context.user_profile['age'] = detected_age  # Also store in user profile
                    logger.info(f"✓ Age SET to: {detected_age}")

            # Detect location from user input
            # ONLY detect when in PROBING_LOCATION state (prevents false positives from emotional talk)
            if state_at_turn_start == ConversationState.PROBING_LOCATION:
                detected_location = self._quick_detect_location(input_text)
                logger.info(f"📍 Location detection (in PROBING_LOCATION state): input='{input_text}' -> detected={detected_location.value}")

                if detected_location != UserLocation.UNKNOWN:
                    assessment.user_location = detected_location
                    logger.info(f"✅ Location SET to: {detected_location.value}")
                else:
                    logger.info(f"Current location status: {assessment.user_location.value}")

                    # CRITICAL SAFEGUARD: If we've been in PROBING_LOCATION state for 3+ turns
                    # and still can't detect location, assume HOME_INDOOR to prevent infinite loop
                    if (assessment.turns_in_current_state >= 3 and
                        assessment.user_location == UserLocation.UNKNOWN):
                        logger.warning(f"⚠️ Location asked {assessment.turns_in_current_state} times without detection. Assuming HOME_INDOOR to prevent loop.")
                        assessment.user_location = UserLocation.HOME_INDOOR
            else:
                logger.info(f"Location detection skipped (not in PROBING_LOCATION state): current_state={state_at_turn_start.value}")
    
            # Detect time available from user input
            # ONLY detect when in PROBING_TIME state (prevents false positives from emotional talk)
            if state_at_turn_start == ConversationState.PROBING_TIME:
                detected_time = self._detect_time_available(input_text)
                logger.info(f"⏰ Time detection (in PROBING_TIME state): input='{input_text}' -> detected={detected_time.value}")

                if detected_time != TimeAvailable.UNKNOWN:
                    assessment.time_available = detected_time
                    logger.info(f"✅ Time SET to: {detected_time.value}")
                else:
                    logger.info(f"Current time status: {assessment.time_available.value}")

                    # SAFEGUARD: If we've been in PROBING_TIME state for 3+ turns, default to 12 min
                    if (assessment.turns_in_current_state >= 3 and
                        assessment.time_available == TimeAvailable.UNKNOWN):
                        logger.warning(f"⚠️ Time asked {assessment.turns_in_current_state} times without detection. Defaulting to 12_MIN.")
                        assessment.time_available = TimeAvailable.TWELVE_MIN
            else:
                logger.info(f"Time detection skipped (not in PROBING_TIME state): current_state={state_at_turn_start.value}")
    
            # Detect meal status from user input
            # ONLY detect when in PROBING_MEAL state (prevents false positives from emotional talk)
            if state_at_turn_start == ConversationState.PROBING_MEAL:
                detected_meal = self._detect_meal_status(input_text)
                logger.info(f"🍽️ Meal detection (in PROBING_MEAL state): input='{input_text}' -> detected={detected_meal.value}")

                if detected_meal != MealStatus.UNKNOWN:
                    assessment.meal_status = detected_meal
                    logger.info(f"✅ Meal status SET to: {detected_meal.value}")
                else:
                    logger.info(f"Current meal status: {assessment.meal_status.value}")

                    # SAFEGUARD: If we've been in PROBING_MEAL state for 3+ turns, default to EMPTY_STOMACH (safer for practices)
                    if (assessment.turns_in_current_state >= 3 and
                        assessment.meal_status == MealStatus.UNKNOWN):
                        logger.warning(f"⚠️ Meal status asked {assessment.turns_in_current_state} times without detection. Defaulting to EMPTY_STOMACH (safer).")
                        assessment.meal_status = MealStatus.EMPTY_STOMACH
            else:
                logger.info(f"Meal detection skipped (not in PROBING_MEAL state): current_state={state_at_turn_start.value}")
    
            # STEP 2: GENERATE LLM response based on UPDATED assessment
            # Build conversation summary
            conversation_summary = self._build_conversation_summary(context)
            assessment_summary = self._build_assessment_summary(assessment)  # Uses UPDATED assessment!

            # Generate empathetic response using LLM
            user_name = context.user_profile.get('name', 'friend')

            # Get time-based greeting (only for first message)
            time_of_day = self._get_time_of_day()

            # Check if this is the first message
            is_first_message = len(context.conversation_history) == 0

            # RULE-BASED SHORTCUT: If user just gave a simple answer, acknowledge and ask next question directly
            # This prevents LLM from getting confused and repeating questions
            simple_response = self._generate_simple_transition_response(
                state_at_turn_start, assessment, input_text, user_name
            )

            if simple_response:
                # Use the simple rule-based response instead of calling LLM
                logger.info(f"Using simple rule-based response for state transition from {state_at_turn_start.value}")
                response_text = simple_response
            else:
                # Update conversation summary to indicate if greeting needed
                if is_first_message:
                    conversation_summary = "This is the start of the conversation. Use time-based greeting."
                elif conversation_summary == "This is the start of the conversation.":
                    conversation_summary = "Continuing conversation (already greeted - don't repeat greeting)."

                prompt_input = {
                    'user_name': user_name,
                    'user_message': input_text,
                    'conversation_summary': conversation_summary,
                    'assessment_summary': assessment_summary,
                    'time_of_day': time_of_day
                }

                formatted_prompt = self.conversation_prompt.format(**prompt_input)
                response = self.llm.invoke(formatted_prompt)
                response_text = response.content.strip()
    
            # Try to extract structured data (emotion, situation, tone)
            extracted = self._try_extraction(context.conversation_history + [
                {'role': 'user', 'content': input_text},
                {'role': 'assistant', 'content': response_text}
            ])
    
            if extracted:
                assessment.primary_emotion = extracted.get('primary_emotion', assessment.primary_emotion)
                assessment.life_situation = extracted.get('life_situation', assessment.life_situation)
                assessment.tone = extracted.get('tone', assessment.tone)
                assessment.confidence = extracted.get('confidence', assessment.confidence)
                assessment.emotion_details = extracted.get('emotion_details', assessment.emotion_details)
                assessment.situation_details = extracted.get('situation_details', assessment.situation_details)

                # DEBUG: Log extracted emotion and situation for testing
                logger.info(f"📊 EXTRACTION DEBUG:")
                logger.info(f"  → Emotion extracted: {assessment.primary_emotion.value}")
                logger.info(f"  → Life Situation extracted: {assessment.life_situation.value}")
                if assessment.emotion_details:
                    logger.info(f"  → Emotion details: {assessment.emotion_details}")
                if assessment.situation_details:
                    logger.info(f"  → Situation details: {assessment.situation_details}")
    
            # Determine if assessment is complete
            # Complete ONLY if: emotion + situation + location + time + meal status known
            # We MUST have all five - never skip any
            has_emotion = assessment.primary_emotion != EmotionalState.UNKNOWN
            has_situation = assessment.life_situation != LifeSituation.UNKNOWN
            has_location = assessment.user_location != UserLocation.UNKNOWN
            has_time = assessment.time_available != TimeAvailable.UNKNOWN
            has_meal = assessment.meal_status != MealStatus.UNKNOWN
    
            logger.info(f"Completion check: emotion={has_emotion} ({assessment.primary_emotion.value}), "
                       f"situation={has_situation} ({assessment.life_situation.value}), "
                       f"location={has_location} ({assessment.user_location.value}), "
                       f"time={has_time} ({assessment.time_available.value}), "
                       f"meal={has_meal} ({assessment.meal_status.value})")
    
            if has_emotion and has_situation and has_location and has_time and has_meal:
                # Only complete when we have ALL FIVE pieces
                assessment.is_complete = True
                assessment.conversation_state = ConversationState.ASSESSMENT_COMPLETE
                logger.info("✓✓✓ ASSESSMENT COMPLETE!")

                # DEBUG: Log final assessment summary for testing
                logger.info(f"📋 FINAL ASSESSMENT SUMMARY:")
                logger.info(f"  → Age: {assessment.user_age} years")
                logger.info(f"  → Emotion: {assessment.primary_emotion.value}")
                logger.info(f"  → Life Situation: {assessment.life_situation.value}")
                logger.info(f"  → Location: {assessment.user_location.value}")
                logger.info(f"  → Time Available: {assessment.time_available.value}")
                logger.info(f"  → Meal Status: {assessment.meal_status.value}")
    
                # CRITICAL: Set response_text to empty string
                # The SolutionGenerator already includes the personalized intro
                # The orchestrator will combine: response.content + "\n\n" + solution
                # So we just return empty string to avoid duplication
                response_text = ""
                logger.info("Assessment complete - returning empty response (solution will include intro)")
            else:
                # Update conversation state based on what we know
                # CRITICAL: Reset turn counter when state changes to prevent inherited counts
                old_state = assessment.conversation_state
    
                if not has_emotion:
                    new_state = ConversationState.PROBING_EMOTION
                elif not has_situation:
                    new_state = ConversationState.PROBING_SITUATION
                elif not has_location:
                    new_state = ConversationState.PROBING_LOCATION
                elif not has_time:
                    new_state = ConversationState.PROBING_TIME
                elif not has_meal:
                    new_state = ConversationState.PROBING_MEAL
                else:
                    new_state = old_state
    
                # Reset turn counter when transitioning to a new state
                if new_state != old_state:
                    logger.info(f"State transition: {old_state.value} → {new_state.value}, resetting turn counter")
                    assessment.turns_in_current_state = 0
    
                assessment.conversation_state = new_state
    
            # Save assessment
            context.metadata['current_assessment'] = assessment.to_dict()

            # Build response
            processing_time = (datetime.now() - start_time).total_seconds()

            return AgentResponse(
                agent_name="assessment_v2",
                content=response_text,
                confidence=assessment.confidence,
                metadata={
                    'assessment': assessment.to_dict(),
                    'is_complete': assessment.is_complete,
                    'conversation_state': assessment.conversation_state.value,
                    'suggested_next_action': "continue_assessment" if not assessment.is_complete else "generate_solution"
                },
                processing_time=processing_time,
                tools_used=[],
                success=True
            )

        except Exception as e:
            logger.error(f"❌ Assessment Agent V2 error: {e}", exc_info=True)

            # Get user name for personalized fallback
            user_name = context.user_profile.get('name', 'friend')
            time_of_day = self._get_time_of_day()

            # Wisdom Companion style fallback - warm and inviting
            is_first_message = len(context.conversation_history) == 0

            if is_first_message:
                fallback_response = f"Good {time_of_day}, {user_name}. I'm here to listen and support you. What's been on your mind?"
            else:
                fallback_response = f"I'm here with you, {user_name}. Can you share a bit more about what you're feeling or going through?"

            processing_time = (datetime.now() - start_time).total_seconds()

            return AgentResponse(
                agent_name="assessment_v2",
                content=fallback_response,
                confidence=0.3,
                metadata={
                    'error': str(e),
                    'is_complete': False,
                    'conversation_state': 'initial_greeting'
                },
                processing_time=processing_time,
                tools_used=[],
                success=False
            )

    def _get_current_assessment(self, context: AgentContext) -> EnhancedAssessment:
        """Get current assessment from context or create new one"""
        assessment_data = context.metadata.get('current_assessment')

        if not assessment_data:
            # Create new assessment
            age = context.user_profile.get('age')
            return EnhancedAssessment(user_age=age)

        # Reconstruct from stored data
        assessment = EnhancedAssessment()

        # Restore enum values
        emotion_str = assessment_data.get('primary_emotion', 'unknown')
        try:
            assessment.primary_emotion = EmotionalState(emotion_str)
        except ValueError:
            assessment.primary_emotion = EmotionalState.UNKNOWN

        situation_str = assessment_data.get('life_situation', 'unknown')
        try:
            assessment.life_situation = LifeSituation(situation_str)
        except ValueError:
            assessment.life_situation = LifeSituation.UNKNOWN

        location_str = assessment_data.get('user_location', 'unknown')
        try:
            assessment.user_location = UserLocation(location_str)
        except ValueError:
            assessment.user_location = UserLocation.UNKNOWN

        state_str = assessment_data.get('conversation_state', 'initial_greeting')
        try:
            assessment.conversation_state = ConversationState(state_str)
        except ValueError:
            assessment.conversation_state = ConversationState.INITIAL_GREETING

        # Restore time_available
        time_str = assessment_data.get('time_available', 'unknown')
        try:
            assessment.time_available = TimeAvailable(time_str)
        except ValueError:
            assessment.time_available = TimeAvailable.UNKNOWN

        # Restore meal_status
        meal_str = assessment_data.get('meal_status', 'unknown')
        try:
            assessment.meal_status = MealStatus(meal_str)
        except ValueError:
            assessment.meal_status = MealStatus.UNKNOWN

        # Restore other fields
        assessment.user_age = assessment_data.get('user_age')
        assessment.situation_details = assessment_data.get('situation_details', '')
        assessment.emotion_details = assessment_data.get('emotion_details', '')
        assessment.turns_in_current_state = assessment_data.get('turns_in_current_state', 0)
        assessment.is_complete = assessment_data.get('is_complete', False)
        assessment.tone = assessment_data.get('tone', 'warm')
        assessment.confidence = assessment_data.get('confidence', 0.5)

        return assessment

    def _build_conversation_summary(self, context: AgentContext) -> str:
        """Build a summary of conversation so far"""
        history = context.conversation_history[-6:]  # Last 3 exchanges

        if not history:
            return "This is the start of the conversation."

        summary = []
        for msg in history:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')[:100]  # Truncate long messages
            if role == 'user':
                summary.append(f"User said: {content}")
            else:
                summary.append(f"You said: {content}")

        return "\n".join(summary)

    def _get_time_of_day(self) -> str:
        """Get time-appropriate greeting based on current hour"""
        current_hour = datetime.now().hour

        if 5 <= current_hour < 12:
            return "morning"
        elif 12 <= current_hour < 17:
            return "afternoon"
        elif 17 <= current_hour < 21:
            return "evening"
        else:
            return "evening"  # Late night also gets "evening"

    def _build_assessment_summary(self, assessment: EnhancedAssessment) -> str:
        """Build summary of what we know"""
        parts = []

        # CRITICAL: Include age first so LLM knows not to ask again!
        if assessment.user_age is not None:
            parts.append(f"- Age: {assessment.user_age} years old (✓ ALREADY KNOWN - DO NOT ASK AGAIN!)")
        else:
            parts.append("- Age: NOT YET ASKED")

        if assessment.primary_emotion != EmotionalState.UNKNOWN:
            parts.append(f"- Emotion: {assessment.primary_emotion.value} (✓ ALREADY KNOWN - DO NOT ASK AGAIN!)")
            if assessment.emotion_details:
                parts.append(f"  Details: {assessment.emotion_details}")
        else:
            parts.append("- Emotion: NOT YET UNDERSTOOD")

        if assessment.life_situation != LifeSituation.UNKNOWN:
            parts.append(f"- Situation: {assessment.life_situation.value.replace('_', ' ')} (✓ ALREADY KNOWN - DO NOT ASK AGAIN!)")
            if assessment.situation_details:
                parts.append(f"  Details: {assessment.situation_details}")
        else:
            parts.append("- Situation/Cause: NOT YET UNDERSTOOD")

        if assessment.user_location != UserLocation.UNKNOWN:
            parts.append(f"- Location: {assessment.user_location.value.replace('_', ' ')} (✓ ALREADY KNOWN - DO NOT ASK AGAIN!)")
        else:
            parts.append("- Location: NOT YET ASKED")

        if assessment.time_available != TimeAvailable.UNKNOWN:
            parts.append(f"- Time Available: {assessment.time_available.value.replace('_', ' ')} (✓ ALREADY KNOWN - DO NOT ASK AGAIN!)")
        else:
            parts.append("- Time Available: NOT YET ASKED")

        if assessment.meal_status != MealStatus.UNKNOWN:
            parts.append(f"- Meal Status: {assessment.meal_status.value.replace('_', ' ')} (✓ ALREADY KNOWN - DO NOT ASK AGAIN!)")
        else:
            parts.append("- Meal Status: NOT YET ASKED")

        if not parts:
            return "We don't know anything about their situation yet."

        return "\n".join(parts)

    def _quick_detect_location(self, text: str) -> UserLocation:
        """
        Intelligently detect location from user input with leniency.
        CRITICAL: This prevents infinite loop when user mentions location.
        Uses keywords + LLM to understand context and handle typos/variations.
        """
        logger.info(f"📍 Location detection: analyzing input='{text}'")

        text_lower = text.lower().strip()

        # STEP 1: Keyword-based detection (fast and reliable)
        # Location-specific phrases to avoid false positives
        home_keywords = ['home', 'house', 'at home', 'in home', 'from home', 'im home', "i'm home",
                        'home indoor', 'inside home', 'in my house', 'at my house',
                        'my home', 'my house', 'home right now', 'at the house', 'apartment', 'flat']

        office_keywords = ['work', 'office', 'at work', 'in office', 'at office', 'in my office',
                          'at the office', 'in the office', 'at my desk', 'at desk',
                          'in my cubicle', 'at workplace', 'office right now', 'workplace']

        outdoor_keywords = ['outside', 'outdoor', 'in park', 'at park', 'walking outside',
                           'in nature', 'in garden', 'at beach', 'outdoors', 'out in nature', 'garden']

        public_keywords = ['cafe', 'coffee shop', 'restaurant', 'at cafe', 'in cafe', 'at restaurant', 'in restaurant',
                          'at mall', 'in mall', 'at store', 'in store', 'at library', 'in library',
                          'at gym', 'in gym', 'public place', 'shopping center', 'mall', 'gym']

        vehicle_keywords = ['car', 'driving', 'vehicle', 'in car', 'in my car', 'in bus', 'in train', 'in vehicle',
                           'commuting', 'on the road', 'in transit', 'in the car', 'bus', 'train']

        # Check keywords (handles most cases quickly)
        if any(keyword in text_lower for keyword in home_keywords):
            logger.info(f"✅ Location detection: keyword match → HOME")
            print(f"\n{'='*60}")
            print(f"📍 LOCATION DETECTION")
            print(f"{'='*60}")
            print(f"User said: '{text}'")
            print(f"Detected: HOME (keyword match)")
            print(f"{'='*60}\n")
            return UserLocation.HOME_INDOOR

        if any(keyword in text_lower for keyword in office_keywords):
            logger.info(f"✅ Location detection: keyword match → OFFICE")
            print(f"\n{'='*60}")
            print(f"📍 LOCATION DETECTION")
            print(f"{'='*60}")
            print(f"User said: '{text}'")
            print(f"Detected: OFFICE (keyword match)")
            print(f"{'='*60}\n")
            return UserLocation.OFFICE

        if any(keyword in text_lower for keyword in outdoor_keywords):
            logger.info(f"✅ Location detection: keyword match → OUTDOOR")
            print(f"\n{'='*60}")
            print(f"📍 LOCATION DETECTION")
            print(f"{'='*60}")
            print(f"User said: '{text}'")
            print(f"Detected: OUTDOOR (keyword match)")
            print(f"{'='*60}\n")
            return UserLocation.OUTDOOR

        if any(keyword in text_lower for keyword in public_keywords):
            logger.info(f"✅ Location detection: keyword match → PUBLIC_PLACE")
            print(f"\n{'='*60}")
            print(f"📍 LOCATION DETECTION")
            print(f"{'='*60}")
            print(f"User said: '{text}'")
            print(f"Detected: PUBLIC PLACE (keyword match)")
            print(f"{'='*60}\n")
            return UserLocation.PUBLIC_PLACE

        if any(keyword in text_lower for keyword in vehicle_keywords):
            logger.info(f"✅ Location detection: keyword match → VEHICLE")
            print(f"\n{'='*60}")
            print(f"📍 LOCATION DETECTION")
            print(f"{'='*60}")
            print(f"User said: '{text}'")
            print(f"Detected: VEHICLE (keyword match)")
            print(f"{'='*60}\n")
            return UserLocation.VEHICLE

        # STEP 2: LLM fallback for complex/short answers
        try:
            logger.info(f"📍 Location detection: using LLM fallback")
            location_prompt = f"""The user was asked where they are physically located.
They responded: "{text}"

Based on this response, what is their location? Choose ONE:
- home_indoor (at home, in house, inside, apartment, flat)
- office (at work, workplace, office, desk)
- outdoor (outside, park, nature, beach, garden)
- public_place (cafe, restaurant, mall, library, gym, store)
- vehicle (in car, bus, train, driving, commuting)
- unknown (ONLY if completely unclear)

Be LENIENT - even short answers like "home" or "work" should be detected. Handle typos (e.g., "homw" = "home_indoor", "wrk" = "office").

Respond with ONLY the location category (e.g., "home_indoor")."""

            response = self.llm.invoke(location_prompt)
            detected = response.content.strip().lower()

            logger.info(f"📍 Location detection: LLM response='{detected}'")

            # Map LLM response to enum
            location_map = {
                'home_indoor': UserLocation.HOME_INDOOR,
                'home': UserLocation.HOME_INDOOR,
                'office': UserLocation.OFFICE,
                'work': UserLocation.OFFICE,
                'outdoor': UserLocation.OUTDOOR,
                'public_place': UserLocation.PUBLIC_PLACE,
                'vehicle': UserLocation.VEHICLE,
                'unknown': UserLocation.UNKNOWN
            }

            detected_location = location_map.get(detected, UserLocation.HOME_INDOOR)  # Default to HOME if unclear

            if detected_location != UserLocation.UNKNOWN:
                logger.info(f"✅ Location detection: LLM mapped to {detected_location.value}")
            else:
                logger.info(f"⚠️ Location detection: unclear → defaulting to HOME")
                detected_location = UserLocation.HOME_INDOOR  # Default to HOME (safer)

            return detected_location

        except Exception as e:
            logger.error(f"LLM location detection failed: {e}")
            # Default to HOME for safety
            return UserLocation.HOME_INDOOR

    def _detect_time_available(self, text: str) -> TimeAvailable:
        """
        Intelligently detect time available from user input.
        Uses mathematical mapping to find closest valid slot (7, 12, or 20 minutes).
        """
        logger.info(f"⏰ Time detection: analyzing input='{text}'")

        try:
            # STEP 1: Try to extract numbers from user input
            numbers = re.findall(r'\b(\d+)\s*(?:min|minute|minutes)?\b', text.lower())

            if numbers:
                # Get the first number mentioned (usually the time they have)
                user_time = int(numbers[0])
                logger.info(f"⏰ Time detection: extracted number '{user_time}' from input")

                # Valid time slots
                valid_slots = [7, 12, 20]

                # Find closest valid slot using mathematical distance
                closest_slot = min(valid_slots, key=lambda x: abs(x - user_time))

                # Calculate how close it is
                distance = abs(closest_slot - user_time)

                # Log the mapping with visual feedback
                if distance == 0:
                    logger.info(f"✅ Time mapping: {user_time} → {closest_slot} min (exact match)")
                else:
                    logger.info(f"🔄 Time mapping: {user_time} → {closest_slot} min (distance: {distance} min)")

                # Also print to console for visibility
                print(f"\n{'='*60}")
                print(f"⏰ TIME MAPPING TOOL ACTIVATED")
                print(f"{'='*60}")
                print(f"User said: '{text}'")
                print(f"Extracted: {user_time} minutes")
                print(f"Mapped to: {closest_slot} minutes (closest valid slot)")
                print(f"Distance: {distance} minutes")
                print(f"{'='*60}\n")

                # Map to enum
                if closest_slot == 7:
                    return TimeAvailable.SEVEN_MIN
                elif closest_slot == 12:
                    return TimeAvailable.TWELVE_MIN
                elif closest_slot == 20:
                    return TimeAvailable.TWENTY_MIN

            # STEP 2: Fallback to LLM if no number found
            logger.info(f"⏰ Time detection: no number found, using LLM fallback")
            time_prompt = f"""The user was asked: "How much time do you have right now—7, 12, or about 20 minutes?"

They responded: "{text}"

Based on their response, which time option did they choose?
- If they said 7 (or seven, or short time, or quick): return "7"
- If they said 12 (or twelve, or medium time): return "12"
- If they said 20 (or twenty, or long time): return "20"
- If unclear or they didn't answer the question: return "unknown"

Respond with ONLY one word: "7", "12", "20", or "unknown"."""

            response = self.llm.invoke(time_prompt)
            detected = response.content.strip().lower()

            logger.info(f"⏰ Time detection: LLM response='{detected}'")

            # Map LLM response to enum
            if '7' in detected or 'seven' in detected:
                logger.info("✅ Time detection: mapped to SEVEN_MIN")
                return TimeAvailable.SEVEN_MIN
            elif '12' in detected or 'twelve' in detected:
                logger.info("✅ Time detection: mapped to TWELVE_MIN")
                return TimeAvailable.TWELVE_MIN
            elif '20' in detected or 'twenty' in detected:
                logger.info("✅ Time detection: mapped to TWENTY_MIN")
                return TimeAvailable.TWENTY_MIN
            else:
                logger.info("❌ Time detection: no clear match → UNKNOWN")
                return TimeAvailable.UNKNOWN

        except Exception as e:
            logger.error(f"LLM time detection failed: {e}")
            return TimeAvailable.UNKNOWN

    def _detect_meal_status(self, text: str) -> MealStatus:
        """
        Intelligently detect meal status from user input with leniency.
        Important for practice safety - some breathing practices shouldn't be done on full stomach.
        """
        logger.info(f"🍽️ Meal detection: analyzing input='{text}'")

        text_lower = text.lower().strip()

        # STEP 1: Keyword-based detection (fast and reliable)
        # Full stomach indicators
        full_keywords = ['yes', 'yeah', 'yep', 'ate', 'eaten', 'full', 'just ate', 'recently', 'had meal', 'had food', 'finished eating', 'fed']

        # Empty stomach indicators
        empty_keywords = ['no', 'nope', 'nah', 'not', "haven't", 'havent', 'empty', 'hungry', 'starving', 'didnt eat', "didn't eat", 'no food']

        # Light meal indicators (map to EMPTY for safety - breathing practices are safer)
        light_keywords = ['slightly', 'a bit', 'little bit', 'small snack', 'light', 'just a little', 'barely', 'tiny bit']

        # Check keywords first
        if any(keyword in text_lower for keyword in full_keywords):
            logger.info(f"✅ Meal detection: keyword match → FULL_STOMACH")
            print(f"\n{'='*60}")
            print(f"🍽️ MEAL DETECTION")
            print(f"{'='*60}")
            print(f"User said: '{text}'")
            print(f"Detected: FULL STOMACH (keyword match)")
            print(f"{'='*60}\n")
            return MealStatus.FULL_STOMACH

        if any(keyword in text_lower for keyword in empty_keywords):
            logger.info(f"✅ Meal detection: keyword match → EMPTY_STOMACH")
            print(f"\n{'='*60}")
            print(f"🍽️ MEAL DETECTION")
            print(f"{'='*60}")
            print(f"User said: '{text}'")
            print(f"Detected: EMPTY STOMACH (keyword match)")
            print(f"{'='*60}\n")
            return MealStatus.EMPTY_STOMACH

        if any(keyword in text_lower for keyword in light_keywords):
            logger.info(f"✅ Meal detection: light meal → EMPTY_STOMACH (safer for practices)")
            print(f"\n{'='*60}")
            print(f"🍽️ MEAL DETECTION")
            print(f"{'='*60}")
            print(f"User said: '{text}'")
            print(f"Detected: LIGHT MEAL → Mapped to EMPTY STOMACH")
            print(f"Reason: Safer for breathing practices")
            print(f"{'='*60}\n")
            return MealStatus.EMPTY_STOMACH

        # STEP 2: LLM fallback for complex answers
        try:
            logger.info(f"🍽️ Meal detection: using LLM fallback")
            meal_prompt = f"""The user was asked: "Have you eaten recently?" or "Have you had a meal in the past 2-3 hours?"

They responded: "{text}"

Based on their response, have they eaten recently (full stomach) or not (empty stomach)?
- If they said YES, or they ATE RECENTLY, or they're FULL, or had a FULL MEAL: return "full"
- If they said NO, or HAVEN'T EATEN, or HUNGRY, or EMPTY STOMACH: return "empty"
- If they had a LIGHT SNACK, SLIGHTLY ate, A BIT, SMALL AMOUNT: return "empty" (safer for breathing practices)
- Only if COMPLETELY UNCLEAR: return "unknown"

Be LENIENT - if there's any indication of eating or not eating, choose full or empty. Only return unknown if truly impossible to determine.

Respond with ONLY one word: "full", "empty", or "unknown"."""

            response = self.llm.invoke(meal_prompt)
            detected = response.content.strip().lower()

            logger.info(f"🍽️ Meal detection: LLM response='{detected}'")

            # Map LLM response to enum
            if 'full' in detected:
                logger.info("✅ Meal detection: mapped to FULL_STOMACH")
                return MealStatus.FULL_STOMACH
            elif 'empty' in detected:
                logger.info("✅ Meal detection: mapped to EMPTY_STOMACH")
                return MealStatus.EMPTY_STOMACH
            else:
                # Be lenient - default to EMPTY if unclear (safer for practices)
                logger.info("⚠️ Meal detection: unclear → defaulting to EMPTY_STOMACH (safer)")
                return MealStatus.EMPTY_STOMACH

        except Exception as e:
            logger.error(f"LLM meal detection failed: {e}")
            # Default to EMPTY for safety
            return MealStatus.EMPTY_STOMACH

    def _detect_age(self, text: str) -> Optional[int]:
        """
        Detect age from user input.
        User answers age question in various ways: "18", "I'm 25", "26-35", etc.
        """
        logger.info(f"Age detection: analyzing input='{text}'")

        text_lower = text.lower().strip()

        # Try to extract a number between 18-45
        import re
        numbers = re.findall(r'\b(\d{1,2})\b', text)

        for num_str in numbers:
            try:
                age = int(num_str)
                if 18 <= age <= 45:
                    logger.info(f"Age detection: found valid age {age}")
                    return age
            except ValueError:
                continue

        # Check for range responses like "18-25"
        if '18' in text or '25' in text or '18-25' in text:
            logger.info("Age detection: user said 18-25 range, using midpoint 21")
            return 21
        elif '26' in text or '35' in text or '26-35' in text:
            logger.info("Age detection: user said 26-35 range, using midpoint 30")
            return 30
        elif '36' in text or '45' in text or '36-45' in text:
            logger.info("Age detection: user said 36-45 range, using midpoint 40")
            return 40

        logger.info("Age detection: no valid age found")
        return None

    def _generate_simple_transition_response(
        self,
        state_at_turn_start: ConversationState,
        assessment: 'EnhancedAssessment',
        user_input: str,
        user_name: str
    ) -> Optional[str]:
        """
        Generate simple rule-based response for state transitions.
        Returns None if we should use the LLM instead.

        This handles cases where user gives a direct simple answer (e.g., "home", "7", "yes")
        and we just need to acknowledge and ask the next question.
        """
        # Only use this for short, direct answers (but be more lenient)
        if len(user_input.split()) > 8:
            return None  # Let LLM handle very long responses

        # SITUATION → LOCATION transition (FIX FOR LOOPING!)
        if (state_at_turn_start == ConversationState.PROBING_SITUATION and
            assessment.life_situation != LifeSituation.UNKNOWN and
            assessment.user_location == UserLocation.UNKNOWN):
            logger.info("Simple transition: Situation detected, moving to LOCATION")
            return f"Got it. {user_name}, so I can suggest something practical—where are you right now? At work, home, or somewhere else?"

        # SITUATION → TIME transition (alternate path if location already known)
        if (state_at_turn_start == ConversationState.PROBING_SITUATION and
            assessment.life_situation != LifeSituation.UNKNOWN and
            assessment.user_location != UserLocation.UNKNOWN and
            assessment.time_available == TimeAvailable.UNKNOWN):
            logger.info("Simple transition: Situation detected (location known), moving to TIME")
            return f"Thanks for sharing that. Let me help you with something that fits your schedule. How much time do you have right now—7, 12, or about 20 minutes?"

        # LOCATION → TIME transition
        if (state_at_turn_start == ConversationState.PROBING_LOCATION and
            assessment.user_location != UserLocation.UNKNOWN):
            logger.info("Simple transition: Location detected, moving to TIME")
            return f"Got it. How much time do you have right now—7, 12, or 20 minutes?"

        # TIME → MEAL transition
        if (state_at_turn_start == ConversationState.PROBING_TIME and
            assessment.time_available != TimeAvailable.UNKNOWN):
            logger.info("Simple transition: Time detected, moving to MEAL")
            return f"Perfect. One last thing—have you eaten in the past 2-3 hours? Just helps me tailor the right practice for you."

        # MEAL → COMPLETE (will be handled by solution generator)
        if (state_at_turn_start == ConversationState.PROBING_MEAL and
            assessment.meal_status != MealStatus.UNKNOWN):
            logger.info("Simple transition: Meal detected, assessment complete")
            # Return empty - the solution generator will take over
            return ""

        # Not a simple transition - use LLM
        return None

    def _try_extraction(self, conversation: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        """Try to extract structured data from conversation"""

        # Need at least 2 exchanges to extract
        if len(conversation) < 4:
            return None

        # Build conversation text
        conv_text = "\n".join([
            f"{msg.get('role', 'unknown')}: {msg.get('content', '')}"
            for msg in conversation[-8:]  # Last 4 exchanges
        ])

        try:
            formatted_prompt = self.extraction_prompt.format(conversation=conv_text)
            response = self.llm.invoke(formatted_prompt)

            # Parse JSON
            json_text = response.content.strip()
            # Extract JSON from markdown code blocks if present
            if '```json' in json_text:
                json_text = json_text.split('```json')[1].split('```')[0].strip()
            elif '```' in json_text:
                json_text = json_text.split('```')[1].split('```')[0].strip()

            data = json.loads(json_text)

            # Convert string values to enums
            emotion_str = data.get('primary_emotion', 'unknown')
            try:
                data['primary_emotion'] = EmotionalState(emotion_str)
            except ValueError:
                data['primary_emotion'] = EmotionalState.UNKNOWN

            situation_str = data.get('life_situation', 'unknown')
            try:
                data['life_situation'] = LifeSituation(situation_str)
            except ValueError:
                data['life_situation'] = LifeSituation.UNKNOWN

            return data

        except Exception as e:
            logger.warning(f"Extraction failed: {e}")
            return None
