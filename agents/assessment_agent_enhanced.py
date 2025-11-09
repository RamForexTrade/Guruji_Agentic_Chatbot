"""
Enhanced Assessment Agent with Empathetic Mental State Evaluation
==================================================================

Behavioral Objective:
The agent's core task is to interact with the user to gently and empathetically
uncover the user's predominant emotional state and the real-life situation
(botheration) causing mental imbalance.

Key Features:
    - Multi-turn conversational dialog for state extraction
    - Empathetic probing with open-ended questions
    - Never immediately routes to wisdom - must assess first
    - Extracts: emotion, life situation, location, age
    - Tailored recommendations based on context
    - Verbatim wisdom retrieval from Knowledge Sheets
    - 4-part solution: Pranayama, Asana, Wisdom, Activity/Joke

Architecture:
    User Input → Warm Greeting
                     ↓
              Probe Emotion (if ambiguous)
                     ↓
              Probe Situation (botheration)
                     ↓
              Probe Location/Context
                     ↓
              Extract Complete State
                     ↓
              Build Query for Wisdom Retrieval
                     ↓
              Generate 4-Part Solution
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
import logging
import json
import re

from langchain.prompts import PromptTemplate
from langchain.schema import BaseMessage

from agents.base_agent import BaseAgent, AgentContext, AgentResponse
from agents.agent_types import (
    AgentType,
    EmotionalState,
    SeverityLevel,
    ReadinessLevel,
    PracticeType,
    LifeSituation,
    UserLocation,
    ConversationState
)

logger = logging.getLogger(__name__)


@dataclass
class EnhancedAssessment:
    """
    Enhanced assessment with all required fields for empathetic guidance.

    Captures:
        - Predominant emotion
        - Life situation (botheration)
        - Physical location/context
        - User age (estimated or provided)
        - Assessment completion status
        - Conversation state for multi-turn dialog
    """
    # Core extracted states
    primary_emotion: EmotionalState
    secondary_emotions: List[EmotionalState] = field(default_factory=list)
    life_situation: LifeSituation = LifeSituation.UNKNOWN
    user_location: UserLocation = UserLocation.UNKNOWN
    user_age: Optional[int] = None

    # Additional context
    severity: SeverityLevel = SeverityLevel.MEDIUM
    physical_indicators: List[str] = field(default_factory=list)
    readiness: ReadinessLevel = ReadinessLevel.READY

    # Assessment status
    conversation_state: ConversationState = ConversationState.INITIAL_GREETING
    is_complete: bool = False
    missing_info: List[str] = field(default_factory=list)

    # Metadata
    urgency_level: int = 5  # 1-10
    confidence: float = 0.7
    reasoning: str = ""
    tone: str = "warm"  # warm, somber, playful

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'primary_emotion': self.primary_emotion.value if isinstance(self.primary_emotion, EmotionalState) else self.primary_emotion,
            'secondary_emotions': [e.value if isinstance(e, EmotionalState) else e for e in self.secondary_emotions],
            'life_situation': self.life_situation.value if isinstance(self.life_situation, LifeSituation) else self.life_situation,
            'user_location': self.user_location.value if isinstance(self.user_location, UserLocation) else self.user_location,
            'user_age': self.user_age,
            'severity': self.severity.value if isinstance(self.severity, SeverityLevel) else self.severity,
            'physical_indicators': self.physical_indicators,
            'readiness': self.readiness.value if isinstance(self.readiness, ReadinessLevel) else self.readiness,
            'conversation_state': self.conversation_state.value if isinstance(self.conversation_state, ConversationState) else self.conversation_state,
            'is_complete': self.is_complete,
            'missing_info': self.missing_info,
            'urgency_level': self.urgency_level,
            'confidence': self.confidence,
            'reasoning': self.reasoning,
            'tone': self.tone
        }

    def __repr__(self) -> str:
        return f"EnhancedAssessment(emotion={self.primary_emotion}, situation={self.life_situation}, location={self.user_location}, complete={self.is_complete})"


class EnhancedAssessmentAgent(BaseAgent):
    """
    Enhanced Assessment Agent for empathetic mental state evaluation.

    Core Responsibilities:
        1. Warm, compassionate greeting to encourage openness
        2. Gentle probing with empathetic, open-ended questions
        3. Extract predominant emotion from user
        4. Extract life situation (botheration) causing imbalance
        5. Determine user's physical location/context
        6. Estimate or extract user age
        7. Prevent premature wisdom routing
        8. Build appropriate query for wisdom retrieval
        9. Generate 4-part solution with proper tone

    Never skips direct interaction and state assessment before wisdom retrieval.
    """

    def __init__(
        self,
        llm_provider: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.7,  # Higher for more empathetic, conversational responses
        verbose: bool = False
    ):
        """Initialize the Enhanced Assessment Agent"""
        super().__init__(
            agent_type=AgentType.ASSESSMENT,
            name="enhanced_assessment",
            llm_provider=llm_provider,
            model_name=model_name,
            temperature=temperature,
            verbose=verbose
        )

        # Prompt templates for different conversation stages
        self.greeting_prompt = self._create_greeting_prompt()
        self.emotion_probe_prompt = self._create_emotion_probe_prompt()
        self.situation_probe_prompt = self._create_situation_probe_prompt()
        self.location_probe_prompt = self._create_location_probe_prompt()
        self.extraction_prompt = self._create_extraction_prompt()

        # Keyword mappings for quick detection
        self.emotion_keywords = self._initialize_emotion_keywords()
        self.situation_keywords = self._initialize_situation_keywords()
        self.location_keywords = self._initialize_location_keywords()

        logger.info("Enhanced Assessment Agent initialized successfully")

    def _create_greeting_prompt(self) -> PromptTemplate:
        """Create warm, compassionate greeting prompt"""
        template = """You are a compassionate AI companion inspired by Gurudev Sri Sri Ravishanker's teachings.

**User Profile:**
- Name: {user_name}
- Previous interaction: {has_history}

**User Message:**
{user_message}

**Your Task:**
Provide a warm, compassionate greeting that:
1. Acknowledges their presence with genuine care
2. Encourages openness and self-reflection
3. Invites them to share what's on their mind
4. Uses simple, warm language (avoid jargon)
5. Keeps tone youth-friendly yet respectful

**Guidelines:**
- Be genuine and empathetic
- Don't be overly formal or religious
- Make them feel safe to share
- Use their name if appropriate
- Keep it brief (2-3 sentences)

**CRITICAL:**
- Do NOT ask multiple questions at once
- Do NOT probe for specific details yet
- Just create a warm, open invitation to share

Compassionate Greeting:"""

        return PromptTemplate(
            template=template,
            input_variables=["user_name", "has_history", "user_message"]
        )

    def _create_emotion_probe_prompt(self) -> PromptTemplate:
        """Create empathetic emotion probing prompt"""
        template = """You are a compassionate guide helping someone understand their emotions.

**User Profile:**
- Name: {user_name}
- Age: {user_age}
- What they said: {user_message}

**Detected Possible Emotions:**
{detected_emotions}

**Your Task:**
The user's emotional state is not yet clear. Ask ONE warm, open-ended question to help them identify their predominant feeling.

**Emotion Categories to Help Identify:**
- Love (warmth, connection, compassion)
- Fear (worried, nervous, anxious, scared)
- Anger (frustrated, irritated, mad)
- Depression (down, hopeless, heavy)
- Overwhelmed (too much, can't cope, drowning)
- Confusion (uncertain, lost, unclear)
- Hurt (pain, wounded, rejected)
- Loneliness (isolated, alone, disconnected)
- Guilt/Remorse (regret, shame, self-blame)
- Inadequacy (not enough, failing, incompetent)

**Guidelines:**
- Ask only ONE question
- Use empathetic, non-judgmental language
- Offer emotion words as gentle suggestions if helpful
- Match their tone (serious, casual, etc.)
- Keep it conversational, not clinical
- If grief/loss detected, use somber, supportive tone

**Examples:**
- "Could you tell me a bit more about what you're feeling?"
- "It sounds like there's something weighing on you. Would you say it feels more like worry, sadness, or something else?"
- "I hear you. Are you feeling frustrated, anxious, or is it a different kind of feeling?"

Empathetic Question:"""

        return PromptTemplate(
            template=template,
            input_variables=["user_name", "user_age", "user_message", "detected_emotions"]
        )

    def _create_situation_probe_prompt(self) -> PromptTemplate:
        """Create empathetic situation/botheration probing prompt"""
        template = """You are helping someone identify what's causing their emotional state.

**User Profile:**
- Name: {user_name}
- Emotion: {emotion}
- What they said: {user_message}

**Life Situation Categories (Botherations):**
- Finance/Career concerns
- Decision making or self-doubt
- Relationship and love issues
- Burnout or exhaustion
- Health concerns
- Mind-created (worry without external cause)
- Big world problems (politics, calamity, war)
- Spiritual growth questions

**Your Task:**
Ask ONE warm, open-ended question to understand what real-life situation is causing their {emotion}.

**Guidelines:**
- Focus on "what's happening" not "why do you feel this way"
- Keep it simple and conversational
- Don't list all categories - let them describe naturally
- Be gentle - they might not want to share everything yet
- Show you're listening and care

**Examples:**
- "What's going on that's making you feel this way?"
- "Is there something specific happening in your life right now that's brought this up?"
- "Would you like to share what's been on your mind lately?"

Caring Question:"""

        return PromptTemplate(
            template=template,
            input_variables=["user_name", "emotion", "user_message"]
        )

    def _create_location_probe_prompt(self) -> PromptTemplate:
        """Create location context probing prompt"""
        template = """You are about to suggest practices like breathing or yoga to help someone.

**User Profile:**
- Name: {user_name}
- Emotion: {emotion}
- Situation: {situation}

**Your Task:**
Ask ONE quick question about where they are physically, so you can tailor your recommendations.

**Why This Matters:**
- Home/indoor → can suggest longer practices, lying down, etc.
- Outdoor → suggest walking meditation, outdoor breathing
- Office/public → suggest discrete practices, quick exercises
- Vehicle → suggest audio practices, breathing only

**Guidelines:**
- Make it casual and practical, not interrogative
- Explain briefly why you're asking (to help better)
- Keep it short - just one simple question

**Examples:**
- "Just so I can suggest the most practical practices for you - are you at home right now, or somewhere outside?"
- "To give you practices you can actually do right now - are you indoors or outdoors?"
- "Quick question: are you in a private space at home, or are you at work/outside somewhere?"

Location Question:"""

        return PromptTemplate(
            template=template,
            input_variables=["user_name", "emotion", "situation"]
        )

    def _create_extraction_prompt(self) -> PromptTemplate:
        """Create comprehensive state extraction prompt"""
        template = """You are an expert at understanding human emotional and life situations.

**User Profile:**
- Name: {user_name}
- Age: {user_age}

**Full Conversation:**
{conversation_text}

**Your Task:**
Analyze the conversation and extract the user's complete state as JSON.

**Emotion Categories:**
- love, fear, anger, depression, overwhelmed, confusion, hurt, loneliness, guilt, inadequacy
- (Also: anxious, stressed, calm, seeking, happy, sad if clearer fit)

**Life Situation Categories:**
- finance_career, decision_making, relationship_love, burnout, health, mind_created, world_problems, spiritual_growth, unknown

**Location Categories:**
- home_indoor, outdoor, office, public_place, vehicle, unknown

**Severity Levels:**
- low, medium, high, critical

**Readiness:**
- ready, needs_preparation, not_ready

**Tone to Use:**
- "warm" - default, youth-friendly, encouraging
- "somber" - for grief, loss, bereavement, serious trauma
- "playful" - if user is light-hearted, young, receptive to humor

**Output Format (JSON ONLY):**
```json
{{
    "primary_emotion": "fear",
    "secondary_emotions": ["overwhelmed", "confusion"],
    "life_situation": "decision_making",
    "user_location": "home_indoor",
    "user_age": 25,
    "severity": "medium",
    "physical_indicators": ["restlessness", "can't sleep"],
    "readiness": "ready",
    "urgency_level": 6,
    "confidence": 0.85,
    "tone": "warm",
    "reasoning": "User is experiencing fear and confusion about career decision, at home, ready for guidance"
}}
```

**CRITICAL:**
- Respond with ONLY valid JSON
- All fields must be present
- Use exact enum values from categories above
- Estimate age from context if not explicitly stated (default: 25 if unknown)

Extraction:"""

        return PromptTemplate(
            template=template,
            input_variables=["user_name", "user_age", "conversation_text"]
        )

    def _initialize_emotion_keywords(self) -> Dict[EmotionalState, List[str]]:
        """Initialize emotion keyword mappings"""
        return {
            EmotionalState.LOVE: ['love', 'loving', 'compassion', 'warmth', 'caring', 'affection'],
            EmotionalState.FEAR: ['fear', 'afraid', 'scared', 'frightened', 'anxious', 'nervous', 'worried', 'panic'],
            EmotionalState.ANGER: ['anger', 'angry', 'mad', 'furious', 'frustrated', 'irritated', 'rage'],
            EmotionalState.DEPRESSION: ['depressed', 'depression', 'hopeless', 'worthless', 'empty', 'numb', 'heavy'],
            EmotionalState.OVERWHELMED: ['overwhelmed', 'too much', 'can\'t cope', 'drowning', 'overloaded', 'swamped'],
            EmotionalState.CONFUSION: ['confused', 'confusion', 'uncertain', 'unclear', 'lost', 'don\'t know', 'bewildered'],
            EmotionalState.HURT: ['hurt', 'pain', 'wounded', 'rejected', 'betrayed', 'heartbroken'],
            EmotionalState.LONELINESS: ['lonely', 'loneliness', 'alone', 'isolated', 'disconnected', 'nobody'],
            EmotionalState.GUILT: ['guilt', 'guilty', 'shame', 'ashamed', 'regret', 'remorse', 'my fault'],
            EmotionalState.INADEQUACY: ['inadequate', 'not enough', 'failing', 'incompetent', 'useless', 'can\'t do'],
        }

    def _initialize_situation_keywords(self) -> Dict[LifeSituation, List[str]]:
        """Initialize life situation keyword mappings"""
        return {
            LifeSituation.FINANCE_CAREER: ['money', 'job', 'work', 'career', 'finance', 'salary', 'unemployed', 'business'],
            LifeSituation.DECISION_MAKING: ['decision', 'choice', 'should i', 'don\'t know what', 'uncertain', 'doubt'],
            LifeSituation.RELATIONSHIP_LOVE: ['relationship', 'partner', 'spouse', 'boyfriend', 'girlfriend', 'marriage', 'divorce', 'breakup'],
            LifeSituation.BURNOUT: ['burnout', 'exhausted', 'tired', 'drained', 'overworked', 'no energy'],
            LifeSituation.HEALTH: ['health', 'sick', 'illness', 'disease', 'pain', 'medical', 'doctor'],
            LifeSituation.MIND_CREATED: ['overthinking', 'in my head', 'thoughts', 'imagining', 'what if', 'nothing happened but'],
            LifeSituation.WORLD_PROBLEMS: ['war', 'politics', 'climate', 'disaster', 'pandemic', 'world', 'country'],
            LifeSituation.SPIRITUAL_GROWTH: ['spiritual', 'meditation', 'purpose', 'meaning', 'enlightenment', 'growth'],
        }

    def _initialize_location_keywords(self) -> Dict[UserLocation, List[str]]:
        """Initialize location keyword mappings"""
        return {
            UserLocation.HOME_INDOOR: ['home', 'house', 'apartment', 'room', 'indoors', 'inside'],
            UserLocation.OUTDOOR: ['outside', 'outdoors', 'park', 'garden', 'walking', 'nature'],
            UserLocation.OFFICE: ['office', 'work', 'workplace', 'desk', 'cubicle'],
            UserLocation.PUBLIC_PLACE: ['cafe', 'restaurant', 'mall', 'public', 'store', 'shop'],
            UserLocation.VEHICLE: ['car', 'bus', 'train', 'driving', 'commute', 'vehicle'],
        }

    def define_tools(self) -> List:
        """Define tools for the enhanced assessment agent"""
        # Primarily conversational, minimal tools needed
        return []

    def get_system_prompt(self) -> str:
        """Get system prompt for the enhanced assessment agent"""
        return """You are the Enhanced Assessment Agent for JAI GURU DEV AI Companion.

Your sacred responsibility is to gently and empathetically uncover the user's emotional state, life situation, and context through compassionate dialog.

## Core Principles:

**Never Rush to Wisdom:**
- NEVER immediately provide wisdom teachings
- NEVER route to other agents before complete assessment
- ALWAYS engage in dialog to understand first

**Empathetic Probing:**
- Ask open-ended, caring questions
- One question at a time
- Listen deeply to their responses
- Validate their feelings without judgment
- Use warm, conversational language

**Tone Adaptation:**
- Youth-friendly and lightly humorous by default
- Somber and supportive for grief/loss/bereavement
- Respectful for all age groups
- Avoid jargon and overly spiritual language early on

**Required Information:**
1. Predominant emotion
2. Life situation (botheration)
3. Physical location/context
4. Age (estimate if not stated)

**Only After Complete Assessment:**
- Build query for wisdom retrieval
- Generate tailored 4-part solution
- Recommend practices suited to their context

You are a bridge between confusion and clarity, pain and peace."""

    def process(
        self,
        input_text: str,
        context: AgentContext,
        chat_history: Optional[List[BaseMessage]] = None
    ) -> AgentResponse:
        """
        Process user input with multi-turn conversational assessment.

        Flow:
        1. Check current conversation state
        2. If beginning → warm greeting
        3. If emotion unclear → empathetic probing
        4. If situation unclear → situation probing
        5. If location unclear → location probing
        6. If complete → extract full assessment
        7. Return appropriate response with assessment metadata
        """
        start_time = datetime.now()

        try:
            logger.info(f"Enhanced Assessment processing: '{input_text[:50]}...'")

            # Get or create current assessment from context
            current_assessment = self._get_current_assessment(context)

            # Determine conversation stage and respond
            if current_assessment.conversation_state == ConversationState.INITIAL_GREETING:
                response_content, updated_assessment = self._handle_greeting_stage(
                    input_text, context, current_assessment
                )

            elif current_assessment.conversation_state == ConversationState.PROBING_EMOTION:
                response_content, updated_assessment = self._handle_emotion_probing(
                    input_text, context, current_assessment
                )

            elif current_assessment.conversation_state == ConversationState.PROBING_SITUATION:
                response_content, updated_assessment = self._handle_situation_probing(
                    input_text, context, current_assessment
                )

            elif current_assessment.conversation_state == ConversationState.PROBING_LOCATION:
                response_content, updated_assessment = self._handle_location_probing(
                    input_text, context, current_assessment
                )

            else:
                # Fallback - re-extract
                response_content, updated_assessment = self._handle_extraction(
                    input_text, context, current_assessment
                )

            # Check if assessment is now complete
            if self._is_assessment_complete(updated_assessment):
                updated_assessment.is_complete = True
                updated_assessment.conversation_state = ConversationState.ASSESSMENT_COMPLETE
                # Add completion message
                response_content += "\n\n✓ I understand your situation now. Let me find the wisdom and practices that will help you most..."

            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()

            # Store updated assessment in context for next turn
            context.metadata['current_assessment'] = updated_assessment.to_dict()

            # Create response
            response = AgentResponse(
                agent_name=self.name,
                content=response_content,
                confidence=updated_assessment.confidence,
                metadata={
                    'assessment': updated_assessment.to_dict(),
                    'conversation_state': updated_assessment.conversation_state.value,
                    'is_complete': updated_assessment.is_complete
                },
                tools_used=['conversational_extraction'],
                processing_time=processing_time,
                success=True
            )

            logger.info(
                f"Assessment stage: {updated_assessment.conversation_state.value}, "
                f"complete: {updated_assessment.is_complete}"
            )

            return response

        except Exception as e:
            logger.error(f"Enhanced Assessment error: {e}", exc_info=True)
            return self.handle_error(e, context)

    def _get_current_assessment(self, context: AgentContext) -> EnhancedAssessment:
        """Get or create current assessment from context"""
        assessment_data = context.metadata.get('current_assessment')

        if not assessment_data:
            # New conversation - create fresh assessment
            return EnhancedAssessment(
                primary_emotion=EmotionalState.UNKNOWN,
                conversation_state=ConversationState.INITIAL_GREETING,
                is_complete=False
            )

        # Reconstruct assessment from stored data
        return EnhancedAssessment(
            primary_emotion=EmotionalState(assessment_data.get('primary_emotion', 'unknown')),
            secondary_emotions=[EmotionalState(e) for e in assessment_data.get('secondary_emotions', [])],
            life_situation=LifeSituation(assessment_data.get('life_situation', 'unknown')),
            user_location=UserLocation(assessment_data.get('user_location', 'unknown')),
            user_age=assessment_data.get('user_age'),
            severity=SeverityLevel(assessment_data.get('severity', 'medium')),
            physical_indicators=assessment_data.get('physical_indicators', []),
            readiness=ReadinessLevel(assessment_data.get('readiness', 'ready')),
            conversation_state=ConversationState(assessment_data.get('conversation_state', 'initial_greeting')),
            is_complete=assessment_data.get('is_complete', False),
            missing_info=assessment_data.get('missing_info', []),
            urgency_level=assessment_data.get('urgency_level', 5),
            confidence=assessment_data.get('confidence', 0.7),
            reasoning=assessment_data.get('reasoning', ''),
            tone=assessment_data.get('tone', 'warm')
        )

    def _handle_greeting_stage(
        self,
        user_input: str,
        context: AgentContext,
        assessment: EnhancedAssessment
    ) -> Tuple[str, EnhancedAssessment]:
        """Handle initial greeting and set next stage"""

        user_name = context.user_profile.get('name', 'friend')
        has_history = len(context.conversation_history) > 0

        # Generate warm greeting
        prompt_input = {
            'user_name': user_name,
            'has_history': 'yes' if has_history else 'no',
            'user_message': user_input
        }

        formatted_prompt = self.greeting_prompt.format(**prompt_input)
        response = self.llm.invoke(formatted_prompt)
        greeting_text = response.content.strip()

        # Quick analysis of user input to decide next stage
        detected_emotion = self._quick_detect_emotion(user_input)
        detected_situation = self._quick_detect_situation(user_input)
        detected_location = self._quick_detect_location(user_input)

        # Update assessment
        if detected_emotion != EmotionalState.UNKNOWN:
            assessment.primary_emotion = detected_emotion
        if detected_situation != LifeSituation.UNKNOWN:
            assessment.life_situation = detected_situation
        if detected_location != UserLocation.UNKNOWN:
            assessment.user_location = detected_location

        # Determine next stage
        if assessment.primary_emotion == EmotionalState.UNKNOWN:
            assessment.conversation_state = ConversationState.PROBING_EMOTION
        elif assessment.life_situation == LifeSituation.UNKNOWN:
            assessment.conversation_state = ConversationState.PROBING_SITUATION
        elif assessment.user_location == UserLocation.UNKNOWN:
            assessment.conversation_state = ConversationState.PROBING_LOCATION
        else:
            assessment.conversation_state = ConversationState.ASSESSMENT_COMPLETE

        return greeting_text, assessment

    def _handle_emotion_probing(
        self,
        user_input: str,
        context: AgentContext,
        assessment: EnhancedAssessment
    ) -> Tuple[str, EnhancedAssessment]:
        """Handle emotion probing stage"""

        user_name = context.user_profile.get('name', 'friend')
        user_age = context.user_profile.get('age', 'not specified')

        # Detect emotion from response
        detected_emotion = self._quick_detect_emotion(user_input)
        if detected_emotion != EmotionalState.UNKNOWN:
            assessment.primary_emotion = detected_emotion

        detected_emotions_text = str(detected_emotion.value) if detected_emotion != EmotionalState.UNKNOWN else "unclear"

        # If still unclear, probe with LLM
        if assessment.primary_emotion == EmotionalState.UNKNOWN:
            prompt_input = {
                'user_name': user_name,
                'user_age': user_age,
                'user_message': user_input,
                'detected_emotions': detected_emotions_text
            }

            formatted_prompt = self.emotion_probe_prompt.format(**prompt_input)
            response = self.llm.invoke(formatted_prompt)
            probe_text = response.content.strip()

            return probe_text, assessment

        # Emotion detected, move to next stage
        assessment.conversation_state = ConversationState.PROBING_SITUATION

        # Generate transition
        transition = f"I hear you. It sounds like you're experiencing {assessment.primary_emotion.value}. "

        return transition, assessment

    def _handle_situation_probing(
        self,
        user_input: str,
        context: AgentContext,
        assessment: EnhancedAssessment
    ) -> Tuple[str, EnhancedAssessment]:
        """Handle situation probing stage"""

        user_name = context.user_profile.get('name', 'friend')
        emotion_text = assessment.primary_emotion.value

        # Detect situation from response
        detected_situation = self._quick_detect_situation(user_input)
        if detected_situation != LifeSituation.UNKNOWN:
            assessment.life_situation = detected_situation

        # If still unclear, probe
        if assessment.life_situation == LifeSituation.UNKNOWN:
            prompt_input = {
                'user_name': user_name,
                'emotion': emotion_text,
                'user_message': user_input
            }

            formatted_prompt = self.situation_probe_prompt.format(**prompt_input)
            response = self.llm.invoke(formatted_prompt)
            probe_text = response.content.strip()

            return probe_text, assessment

        # Situation detected, move to location probing
        assessment.conversation_state = ConversationState.PROBING_LOCATION

        transition = "Thank you for sharing that. "

        return transition, assessment

    def _handle_location_probing(
        self,
        user_input: str,
        context: AgentContext,
        assessment: EnhancedAssessment
    ) -> Tuple[str, EnhancedAssessment]:
        """Handle location probing stage"""

        user_name = context.user_profile.get('name', 'friend')
        emotion_text = assessment.primary_emotion.value
        situation_text = assessment.life_situation.value.replace('_', ' ')

        # Detect location
        detected_location = self._quick_detect_location(user_input)
        if detected_location != UserLocation.UNKNOWN:
            assessment.user_location = detected_location

        # If still unclear, probe
        if assessment.user_location == UserLocation.UNKNOWN:
            prompt_input = {
                'user_name': user_name,
                'emotion': emotion_text,
                'situation': situation_text
            }

            formatted_prompt = self.location_probe_prompt.format(**prompt_input)
            response = self.llm.invoke(formatted_prompt)
            probe_text = response.content.strip()

            return probe_text, assessment

        # Location detected, assessment complete
        assessment.conversation_state = ConversationState.ASSESSMENT_COMPLETE
        assessment.is_complete = True

        acknowledgment = "Got it. "

        return acknowledgment, assessment

    def _handle_extraction(
        self,
        user_input: str,
        context: AgentContext,
        assessment: EnhancedAssessment
    ) -> Tuple[str, EnhancedAssessment]:
        """Perform full extraction from conversation history"""

        user_name = context.user_profile.get('name', 'friend')
        user_age = context.user_profile.get('age', 25)

        # Build conversation text from history
        conversation_text = self._build_conversation_text(context.conversation_history, user_input)

        # Extract using LLM
        prompt_input = {
            'user_name': user_name,
            'user_age': user_age,
            'conversation_text': conversation_text
        }

        formatted_prompt = self.extraction_prompt.format(**prompt_input)
        response = self.llm.invoke(formatted_prompt)
        extraction_json = response.content.strip()

        # Parse extraction
        try:
            extraction_data = self._parse_extraction_json(extraction_json)

            # Update assessment
            assessment.primary_emotion = EmotionalState(extraction_data.get('primary_emotion', 'unknown'))
            assessment.secondary_emotions = [EmotionalState(e) for e in extraction_data.get('secondary_emotions', [])]
            assessment.life_situation = LifeSituation(extraction_data.get('life_situation', 'unknown'))
            assessment.user_location = UserLocation(extraction_data.get('user_location', 'unknown'))
            assessment.user_age = extraction_data.get('user_age')
            assessment.severity = SeverityLevel(extraction_data.get('severity', 'medium'))
            assessment.physical_indicators = extraction_data.get('physical_indicators', [])
            assessment.readiness = ReadinessLevel(extraction_data.get('readiness', 'ready'))
            assessment.urgency_level = extraction_data.get('urgency_level', 5)
            assessment.confidence = extraction_data.get('confidence', 0.7)
            assessment.tone = extraction_data.get('tone', 'warm')
            assessment.reasoning = extraction_data.get('reasoning', '')

        except Exception as e:
            logger.error(f"Extraction parsing failed: {e}")

        return "I'm understanding your situation better now...", assessment

    def _quick_detect_emotion(self, text: str) -> EmotionalState:
        """Quick emotion detection using keywords"""
        text_lower = text.lower()
        scores = {}

        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[emotion] = score

        if scores:
            return max(scores, key=scores.get)
        return EmotionalState.UNKNOWN

    def _quick_detect_situation(self, text: str) -> LifeSituation:
        """Quick situation detection using keywords"""
        text_lower = text.lower()
        scores = {}

        for situation, keywords in self.situation_keywords.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[situation] = score

        if scores:
            return max(scores, key=scores.get)
        return LifeSituation.UNKNOWN

    def _quick_detect_location(self, text: str) -> UserLocation:
        """Quick location detection using keywords"""
        text_lower = text.lower()
        scores = {}

        for location, keywords in self.location_keywords.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[location] = score

        if scores:
            return max(scores, key=scores.get)
        return UserLocation.UNKNOWN

    def _parse_extraction_json(self, json_text: str) -> Dict[str, Any]:
        """Parse extraction JSON from LLM response"""
        try:
            # Clean up
            cleaned = json_text.strip()
            cleaned = re.sub(r'^```json\s*', '', cleaned)
            cleaned = re.sub(r'^```\s*', '', cleaned)
            cleaned = re.sub(r'\s*```$', '', cleaned)

            # Parse
            return json.loads(cleaned)

        except json.JSONDecodeError:
            logger.error(f"Failed to parse extraction JSON")
            return {}

    def _build_conversation_text(self, history: List[Dict[str, Any]], current_input: str) -> str:
        """Build conversation text from history"""
        lines = []
        for msg in history[-5:]:  # Last 5 messages
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            lines.append(f"{role}: {content}")

        lines.append(f"user: {current_input}")
        return "\n".join(lines)

    def _is_assessment_complete(self, assessment: EnhancedAssessment) -> bool:
        """Check if assessment has all required information"""
        return (
            assessment.primary_emotion != EmotionalState.UNKNOWN and
            assessment.life_situation != LifeSituation.UNKNOWN and
            assessment.user_location != UserLocation.UNKNOWN
        )

    def get_fallback_response(self, context: AgentContext) -> str:
        """Fallback response for errors"""
        user_name = context.user_profile.get('name', 'friend')
        return f"""I'm here with you, {user_name}. I want to understand what you're going through.

Could you share with me:
- How you're feeling right now
- What's on your mind

Take your time. I'm listening."""


# For testing
if __name__ == "__main__":
    print("Enhanced Assessment Agent - Ready for empathetic mental state evaluation")
