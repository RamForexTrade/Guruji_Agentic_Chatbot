"""
Assessment Agent
================

Specialized agent for analyzing user state and detecting needs.

Responsibilities:
    - Detect emotional/mental state from user input
    - Classify severity or urgency
    - Identify underlying needs
    - Map to relevant knowledge domains
    - Assess readiness for practice
    - Extract physical indicators
    - Analyze patterns from conversation history

Architecture:
    User Message + Context → Assessment Agent
                                 ↓
                        State Detection (LLM)
                                 ↓
                        Severity Classification
                                 ↓
                        Physical Indicators
                                 ↓
                        Readiness Assessment
                                 ↓
                        Recommended Interventions
                                 ↓
                    Assessment Response (JSON)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
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
    PracticeType
)

logger = logging.getLogger(__name__)


class Assessment:
    """
    Data class for user state assessment results.
    
    Contains all information about the user's current state,
    severity, and recommended interventions.
    """
    
    def __init__(
        self,
        primary_state: EmotionalState,
        secondary_states: List[EmotionalState],
        severity: SeverityLevel,
        physical_indicators: List[str],
        readiness: ReadinessLevel,
        recommended_interventions: List[PracticeType],
        underlying_needs: List[str],
        urgency_level: int,
        confidence: float,
        reasoning: str = ""
    ):
        self.primary_state = primary_state
        self.secondary_states = secondary_states
        self.severity = severity
        self.physical_indicators = physical_indicators
        self.readiness = readiness
        self.recommended_interventions = recommended_interventions
        self.underlying_needs = underlying_needs
        self.urgency_level = urgency_level  # 1-10 scale
        self.confidence = confidence
        self.reasoning = reasoning
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert assessment to dictionary"""
        return {
            'primary_state': self.primary_state.value if isinstance(self.primary_state, EmotionalState) else self.primary_state,
            'secondary_states': [s.value if isinstance(s, EmotionalState) else s for s in self.secondary_states],
            'severity': self.severity.value if isinstance(self.severity, SeverityLevel) else self.severity,
            'physical_indicators': self.physical_indicators,
            'readiness': self.readiness.value if isinstance(self.readiness, ReadinessLevel) else self.readiness,
            'recommended_interventions': [i.value if isinstance(i, PracticeType) else i for i in self.recommended_interventions],
            'underlying_needs': self.underlying_needs,
            'urgency_level': self.urgency_level,
            'confidence': self.confidence,
            'reasoning': self.reasoning
        }
    
    def __repr__(self) -> str:
        return f"Assessment(state={self.primary_state}, severity={self.severity}, readiness={self.readiness})"


class AssessmentAgent(BaseAgent):
    """
    Assessment Agent for analyzing user's current state and needs.
    
    This agent uses LLM-powered analysis to detect:
    - Emotional/mental states (anxious, stressed, calm, etc.)
    - Severity levels (low, medium, high, critical)
    - Physical indicators (tension, fatigue, restlessness)
    - Readiness for practice
    - Underlying needs
    - Appropriate intervention types
    
    The agent analyzes:
    - Current user message
    - Conversation history patterns
    - User profile information
    - Previous assessments
    
    Features:
        - Multi-state detection (primary + secondary states)
        - Pattern analysis from history
        - Context-aware severity assessment
        - Readiness evaluation for practices
        - Intervention recommendation mapping
        - Confidence scoring
        - Detailed reasoning for transparency
    """
    
    def __init__(
        self,
        llm_provider: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.3,  # Lower temperature for more consistent assessments
        verbose: bool = False
    ):
        """
        Initialize the Assessment Agent.
        
        Args:
            llm_provider: LLM provider (groq, openai, anthropic)
            model_name: Model name
            temperature: LLM temperature (lower for consistency)
            verbose: Enable verbose logging
        """
        super().__init__(
            agent_type=AgentType.ASSESSMENT,
            name="assessment",
            llm_provider=llm_provider,
            model_name=model_name,
            temperature=temperature,
            verbose=verbose
        )
        
        # Assessment prompt template
        self.assessment_prompt = self._create_assessment_prompt()
        
        # Pattern keywords for quick analysis
        self.state_keywords = self._initialize_state_keywords()
        
        logger.info("Assessment Agent initialized successfully")
    
    def _create_assessment_prompt(self) -> PromptTemplate:
        """
        Create the prompt template for state assessment.
        
        This prompt guides the LLM to perform comprehensive state analysis
        and return structured JSON output.
        
        Returns:
            PromptTemplate for assessment
        """
        template = """You are a compassionate wellness assessment specialist analyzing a user's mental, emotional, and physical state.

**User Information:**
- Name: {user_name}
- Age: {user_age}
- Experience Level: {experience_level}

**Current Message:**
{user_message}

**Conversation History Context:**
{history_summary}

**Previous States (if any):**
{previous_states}

**Your Task:**
Analyze the user's state comprehensively and provide a detailed assessment.

**Assessment Categories:**

1. **Emotional/Mental States** (choose primary + any secondary):
   - anxious: feeling worried, nervous, uneasy
   - stressed: overwhelmed, pressured, tense
   - calm: peaceful, relaxed, centered
   - confusion: uncertain, unclear, lost
   - seeking: searching for guidance, answers
   - happy: joyful, content, positive
   - sad: down, melancholy, grieving
   - neutral: balanced, even, stable
   - unknown: cannot determine

2. **Severity Levels:**
   - low: minor concern, manageable
   - medium: moderate impact on wellbeing
   - high: significant distress, needs attention
   - critical: urgent, severe distress

3. **Physical Indicators** (extract if mentioned):
   - tension, headache, fatigue, restlessness, insomnia, etc.

4. **Readiness for Practice:**
   - ready: open and able to engage immediately
   - needs_preparation: requires mental preparation first
   - not_ready: too distressed for practice now

5. **Recommended Interventions** (choose appropriate types):
   - pranayama: breathing exercises
   - meditation: mindfulness, contemplation
   - therapy: specific healing modalities
   - movement: yoga, dance, physical activity
   - contemplation: reflection, self-inquiry
   - lifestyle: daily routines, habits

6. **Underlying Needs** (identify core needs):
   - Examples: connection, understanding, peace, clarity, support, healing, etc.

7. **Urgency Level:** (1-10 scale)
   - 1-3: low urgency, stable
   - 4-6: moderate, needs attention soon
   - 7-9: high, needs prompt support
   - 10: critical, immediate intervention needed

**Analysis Guidelines:**
- Be empathetic and non-judgmental
- Consider both explicit statements and implicit signals
- Look for patterns across conversation history
- Assess holistically (mind, body, emotions)
- Be realistic about severity (don't over or under-diagnose)
- Consider cultural context and individual differences
- If unclear, acknowledge uncertainty

**Output Format:**
Provide your assessment as a valid JSON object with this EXACT structure:

```json
{{
    "primary_state": "anxious|stressed|calm|confusion|seeking|happy|sad|neutral|unknown",
    "secondary_states": ["state1", "state2"],
    "severity": "low|medium|high|critical",
    "physical_indicators": ["indicator1", "indicator2"],
    "readiness": "ready|needs_preparation|not_ready",
    "recommended_interventions": ["pranayama", "meditation"],
    "underlying_needs": ["need1", "need2"],
    "urgency_level": 5,
    "confidence": 0.85,
    "reasoning": "Brief explanation of your assessment"
}}
```

**CRITICAL:** 
- Respond with ONLY the JSON object
- Do NOT include any text before or after the JSON
- Do NOT use markdown code blocks (no ```json)
- Ensure valid JSON syntax
- Use double quotes for strings
- All fields must be present

Assessment:"""
        
        return PromptTemplate(
            template=template,
            input_variables=[
                "user_name",
                "user_age",
                "experience_level",
                "user_message",
                "history_summary",
                "previous_states"
            ]
        )
    
    def _initialize_state_keywords(self) -> Dict[EmotionalState, List[str]]:
        """
        Initialize keyword patterns for quick state detection.
        
        These keywords help with preliminary analysis and validation
        of LLM assessments.
        
        Returns:
            Dictionary mapping states to keyword lists
        """
        return {
            EmotionalState.ANXIOUS: [
                'anxious', 'worried', 'nervous', 'uneasy', 'fear',
                'scared', 'panic', 'tense', 'apprehensive', 'frightened'
            ],
            EmotionalState.STRESSED: [
                'stressed', 'overwhelmed', 'pressure', 'burden',
                'exhausted', 'strained', 'overworked', 'cannot cope'
            ],
            EmotionalState.CALM: [
                'calm', 'peaceful', 'relaxed', 'serene', 'tranquil',
                'centered', 'balanced', 'composed', 'settled'
            ],
            EmotionalState.CONFUSION: [
                'confused', 'uncertain', 'unclear', 'lost', 'bewildered',
                'don\'t understand', 'puzzled', 'perplexed'
            ],
            EmotionalState.SEEKING: [
                'seeking', 'searching', 'looking for', 'need guidance',
                'want to know', 'help me', 'what should i', 'how can i'
            ],
            EmotionalState.HAPPY: [
                'happy', 'joyful', 'content', 'grateful', 'blessed',
                'wonderful', 'amazing', 'great', 'fantastic', 'excellent'
            ],
            EmotionalState.SAD: [
                'sad', 'depressed', 'down', 'low', 'unhappy',
                'miserable', 'heartbroken', 'grief', 'sorrow', 'mourning'
            ],
        }
    
    def define_tools(self) -> List:
        """
        Define tools for the assessment agent.
        
        Assessment agent primarily uses LLM analysis,
        with optional tools for pattern detection.
        
        Returns:
            List of Tool objects
        """
        # Assessment is primarily LLM-based
        # Could add tools for specific analyses if needed
        return []
    
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for the assessment agent.
        
        Returns:
            System prompt string
        """
        return """You are the Assessment Agent for the JAI GURU DEV AI Companion chatbot.

Your sacred responsibility is to understand and assess the user's current state with compassion and wisdom.

## Your Capabilities:

1. **State Detection**: Identify emotional, mental, and physical states
2. **Severity Assessment**: Evaluate urgency and intensity of needs
3. **Pattern Recognition**: Detect recurring themes from history
4. **Holistic Analysis**: Consider mind, body, emotions together
5. **Readiness Evaluation**: Assess capacity for practices
6. **Intervention Mapping**: Recommend appropriate practice types

## Core Principles:

**Compassionate Analysis**:
- Be empathetic and non-judgmental
- Recognize that all states are valid
- See the person beyond the symptoms
- Honor their experience

**Holistic Perspective**:
- Consider physical, mental, emotional aspects
- Look for connections between different signals
- Understand context and background
- Recognize complexity

**Practical Wisdom**:
- Assess realistically (no over/under-diagnosis)
- Consider readiness for intervention
- Prioritize what's most helpful now
- Balance urgency with capability

**Cultural Sensitivity**:
- Respect individual differences
- Consider cultural context
- Avoid assumptions
- Be inclusive

## Assessment Framework:

**Primary State Detection**:
- What is the dominant emotional/mental state?
- Is it explicitly stated or implicit?
- What signals indicate this state?

**Severity Evaluation**:
- How intense is the distress/experience?
- Is it manageable or overwhelming?
- Does it require immediate attention?

**Physical Dimension**:
- Are there physical symptoms mentioned?
- How do they relate to emotional state?
- Do they indicate urgency?

**Readiness Assessment**:
- Is the person open to practice?
- Do they have capacity to engage?
- Do they need preparation first?

**Intervention Mapping**:
- What type of practice would help most?
- Multiple options for flexibility
- Match to current capacity

**Underlying Needs**:
- What does the person truly need?
- Beyond surface symptoms
- Core desires and requirements

## Quality Indicators:

- Accurate state identification
- Appropriate severity level
- Realistic readiness assessment
- Helpful intervention recommendations
- Empathetic understanding
- Clear reasoning

Your assessments guide the other agents in providing optimal support."""
    
    def process(
        self,
        input_text: str,
        context: AgentContext,
        chat_history: Optional[List[BaseMessage]] = None
    ) -> AgentResponse:
        """
        Process user state assessment.
        
        Main method that:
        1. Analyzes user message and context
        2. Detects emotional/mental state
        3. Evaluates severity and urgency
        4. Assesses readiness for practice
        5. Identifies physical indicators
        6. Recommends intervention types
        7. Returns structured assessment
        
        Args:
            input_text: User's message
            context: User context (profile, state, history)
            chat_history: Conversation history
        
        Returns:
            AgentResponse with assessment results
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Assessment Agent analyzing: '{input_text[:50]}...'")
            
            # Step 1: Prepare context summaries
            history_summary = self._summarize_history(
                context.conversation_history
            )
            previous_states = self._extract_previous_states(context)
            
            # Step 2: Perform LLM-based assessment
            assessment = self._perform_llm_assessment(
                user_message=input_text,
                context=context,
                history_summary=history_summary,
                previous_states=previous_states
            )
            
            # Step 3: Validate and enrich assessment
            validated_assessment = self._validate_assessment(
                assessment,
                input_text
            )
            
            # Step 4: Determine urgency and priority
            self._calculate_urgency(validated_assessment, context)
            
            # Step 5: Format response content
            response_content = self._format_assessment_response(
                validated_assessment
            )
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Create response
            response = AgentResponse(
                agent_name=self.name,
                content=response_content,
                confidence=validated_assessment.confidence,
                metadata={
                    'assessment': validated_assessment.to_dict(),
                    'analysis_method': 'llm_with_validation',
                    'history_length': len(context.conversation_history)
                },
                tools_used=['llm_analysis', 'pattern_detection', 'validation'],
                processing_time=processing_time,
                success=True
            )
            
            logger.info(
                f"Assessment completed: {validated_assessment.primary_state.value}, "
                f"severity={validated_assessment.severity.value}, "
                f"confidence={validated_assessment.confidence:.2f}"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Assessment Agent error: {e}", exc_info=True)
            return self.handle_error(e, context)
    
    def _summarize_history(
        self,
        history: List[Dict[str, Any]]
    ) -> str:
        """
        Summarize conversation history for context.
        
        Extracts key themes and patterns from recent messages.
        
        Args:
            history: Conversation history
        
        Returns:
            Summary string
        """
        if not history or len(history) == 0:
            return "No previous conversation history."
        
        # Take last 5 messages for context
        recent_history = history[-5:] if len(history) > 5 else history
        
        summary_parts = []
        for msg in recent_history:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')[:100]  # Truncate long messages
            summary_parts.append(f"{role}: {content}")
        
        return "\n".join(summary_parts)
    
    def _extract_previous_states(self, context: AgentContext) -> str:
        """
        Extract previous emotional states from context.
        
        Args:
            context: Agent context
        
        Returns:
            Summary of previous states
        """
        previous_states = context.metadata.get('previous_assessments', [])
        
        if not previous_states:
            return "No previous assessments available."
        
        # Format recent assessments
        recent = previous_states[-3:] if len(previous_states) > 3 else previous_states
        
        state_summary = []
        for assessment in recent:
            state = assessment.get('primary_state', 'unknown')
            severity = assessment.get('severity', 'unknown')
            state_summary.append(f"- {state} ({severity})")
        
        return "\n".join(state_summary)
    
    def _perform_llm_assessment(
        self,
        user_message: str,
        context: AgentContext,
        history_summary: str,
        previous_states: str
    ) -> Assessment:
        """
        Perform LLM-based state assessment.
        
        Uses the LLM to analyze the user's state and return
        structured assessment data.
        
        Args:
            user_message: User's current message
            context: User context
            history_summary: Summary of conversation history
            previous_states: Previous assessment states
        
        Returns:
            Assessment object
        """
        try:
            # Extract user information
            profile = context.user_profile
            user_name = profile.get('name', 'User')
            user_age = profile.get('age', 'Not specified')
            experience_level = profile.get('experience_level', 'beginner')
            
            # Format prompt
            prompt_input = {
                'user_name': user_name,
                'user_age': user_age,
                'experience_level': experience_level,
                'user_message': user_message,
                'history_summary': history_summary,
                'previous_states': previous_states
            }
            
            formatted_prompt = self.assessment_prompt.format(**prompt_input)
            
            # Invoke LLM
            response = self.llm.invoke(formatted_prompt)
            response_text = response.content.strip()
            
            # Parse JSON response
            assessment_data = self._parse_assessment_json(response_text)
            
            # Create Assessment object
            assessment = Assessment(
                primary_state=EmotionalState(assessment_data.get('primary_state', 'unknown')),
                secondary_states=[
                    EmotionalState(s) for s in assessment_data.get('secondary_states', [])
                ],
                severity=SeverityLevel(assessment_data.get('severity', 'medium')),
                physical_indicators=assessment_data.get('physical_indicators', []),
                readiness=ReadinessLevel(assessment_data.get('readiness', 'ready')),
                recommended_interventions=[
                    PracticeType(i) for i in assessment_data.get('recommended_interventions', [])
                ],
                underlying_needs=assessment_data.get('underlying_needs', []),
                urgency_level=assessment_data.get('urgency_level', 5),
                confidence=assessment_data.get('confidence', 0.7),
                reasoning=assessment_data.get('reasoning', '')
            )
            
            return assessment
            
        except Exception as e:
            logger.error(f"LLM assessment failed: {e}")
            # Return fallback assessment
            return self._create_fallback_assessment(user_message, context)
    
    def _parse_assessment_json(self, response_text: str) -> Dict[str, Any]:
        """
        Parse JSON assessment from LLM response.
        
        Handles various response formats and extracts JSON.
        
        Args:
            response_text: LLM response text
        
        Returns:
            Parsed assessment dictionary
        """
        try:
            # Remove markdown code blocks if present
            cleaned = response_text.strip()
            cleaned = re.sub(r'^```json\s*', '', cleaned)
            cleaned = re.sub(r'^```\s*', '', cleaned)
            cleaned = re.sub(r'\s*```$', '', cleaned)
            
            # Parse JSON
            assessment_data = json.loads(cleaned)
            return assessment_data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            logger.debug(f"Response text: {response_text}")
            
            # Try to extract JSON from text
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            
            # Return default structure
            return {
                'primary_state': 'unknown',
                'secondary_states': [],
                'severity': 'medium',
                'physical_indicators': [],
                'readiness': 'ready',
                'recommended_interventions': ['meditation'],
                'underlying_needs': ['support'],
                'urgency_level': 5,
                'confidence': 0.5,
                'reasoning': 'Unable to parse LLM response'
            }
    
    def _validate_assessment(
        self,
        assessment: Assessment,
        user_message: str
    ) -> Assessment:
        """
        Validate and enhance assessment using keyword analysis.
        
        Cross-checks LLM assessment with keyword patterns
        to improve accuracy.
        
        Args:
            assessment: Initial assessment from LLM
            user_message: Original user message
        
        Returns:
            Validated Assessment
        """
        # Perform keyword analysis
        detected_states = self._detect_states_by_keywords(user_message)
        
        # If keyword analysis strongly suggests a different state
        # and LLM confidence is low, adjust
        if detected_states and assessment.confidence < 0.7:
            keyword_state = detected_states[0]
            if keyword_state != assessment.primary_state:
                logger.info(
                    f"Adjusting state from {assessment.primary_state} "
                    f"to {keyword_state} based on keyword analysis"
                )
                assessment.primary_state = keyword_state
                assessment.confidence = min(assessment.confidence + 0.1, 0.9)
        
        return assessment
    
    def _detect_states_by_keywords(
        self,
        text: str
    ) -> List[EmotionalState]:
        """
        Detect emotional states using keyword matching.
        
        Args:
            text: Text to analyze
        
        Returns:
            List of detected states (ordered by relevance)
        """
        text_lower = text.lower()
        state_scores = {}
        
        for state, keywords in self.state_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                state_scores[state] = score
        
        # Sort by score
        sorted_states = sorted(
            state_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [state for state, score in sorted_states]
    
    def _calculate_urgency(
        self,
        assessment: Assessment,
        context: AgentContext
    ) -> None:
        """
        Calculate and adjust urgency level.
        
        Considers severity, readiness, and history patterns.
        Modifies assessment in place.
        
        Args:
            assessment: Assessment to update
            context: User context
        """
        # Base urgency from LLM
        urgency = assessment.urgency_level
        
        # Adjust based on severity
        severity_adjustment = {
            SeverityLevel.LOW: -1,
            SeverityLevel.MEDIUM: 0,
            SeverityLevel.HIGH: 2,
            SeverityLevel.CRITICAL: 4
        }
        urgency += severity_adjustment.get(assessment.severity, 0)
        
        # Adjust based on readiness
        if assessment.readiness == ReadinessLevel.NOT_READY:
            urgency += 1  # More urgent if not ready (needs support)
        
        # Check for recurring patterns
        previous_assessments = context.metadata.get('previous_assessments', [])
        if len(previous_assessments) >= 3:
            # Check if state is worsening
            recent_severities = [
                a.get('severity') for a in previous_assessments[-3:]
            ]
            if self._is_worsening_trend(recent_severities):
                urgency += 1
        
        # Clamp to 1-10 range
        assessment.urgency_level = max(1, min(10, urgency))
    
    def _is_worsening_trend(self, severity_list: List[str]) -> bool:
        """
        Check if severity is trending worse.
        
        Args:
            severity_list: List of recent severity levels
        
        Returns:
            True if worsening trend detected
        """
        severity_scores = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'critical': 4
        }
        
        scores = [severity_scores.get(s, 2) for s in severity_list]
        
        # Check if each severity is worse than or equal to previous
        for i in range(1, len(scores)):
            if scores[i] < scores[i-1]:
                return False
        
        return scores[-1] > scores[0]  # Overall increase
    
    def _format_assessment_response(
        self,
        assessment: Assessment
    ) -> str:
        """
        Format assessment as readable response.
        
        Creates a human-readable summary of the assessment
        for logging and orchestrator communication.
        
        Args:
            assessment: Assessment to format
        
        Returns:
            Formatted response string
        """
        response = f"""Assessment Complete:

**Primary State:** {assessment.primary_state.value}
**Severity:** {assessment.severity.value}
**Readiness:** {assessment.readiness.value}
**Urgency Level:** {assessment.urgency_level}/10

**Recommended Interventions:**
{', '.join([i.value for i in assessment.recommended_interventions])}

**Underlying Needs:**
{', '.join(assessment.underlying_needs)}

**Reasoning:** {assessment.reasoning}

**Confidence:** {assessment.confidence:.0%}"""
        
        if assessment.physical_indicators:
            response += f"\n\n**Physical Indicators:** {', '.join(assessment.physical_indicators)}"
        
        if assessment.secondary_states:
            states = ', '.join([s.value for s in assessment.secondary_states])
            response += f"\n\n**Secondary States:** {states}"
        
        return response
    
    def _create_fallback_assessment(
        self,
        user_message: str,
        context: AgentContext
    ) -> Assessment:
        """
        Create fallback assessment when LLM analysis fails.
        
        Uses keyword-based detection and conservative defaults.
        
        Args:
            user_message: User's message
            context: User context
        
        Returns:
            Fallback Assessment
        """
        # Try keyword detection
        detected_states = self._detect_states_by_keywords(user_message)
        
        primary_state = (
            detected_states[0] if detected_states 
            else EmotionalState.UNKNOWN
        )
        
        return Assessment(
            primary_state=primary_state,
            secondary_states=[],
            severity=SeverityLevel.MEDIUM,
            physical_indicators=[],
            readiness=ReadinessLevel.READY,
            recommended_interventions=[PracticeType.MEDITATION],
            underlying_needs=['support', 'guidance'],
            urgency_level=5,
            confidence=0.5,
            reasoning='Fallback assessment due to analysis error'
        )
    
    def get_fallback_response(self, context: AgentContext) -> str:
        """
        Get fallback response for errors.
        
        Args:
            context: Agent context
        
        Returns:
            Fallback response string
        """
        user_name = context.user_profile.get('name', 'friend')
        
        return f"""I'm having difficulty assessing your current state precisely, {user_name}. 

However, I'm here to support you. To help me understand better, could you share:
- How you're feeling right now
- What's weighing on your mind
- What brought you here today

Every step on this journey is valuable. 🙏"""


# Example usage and testing
if __name__ == "__main__":
    from dotenv import load_dotenv
    import uuid
    
    load_dotenv()
    
    print("=" * 60)
    print("Assessment Agent Test")
    print("=" * 60)
    
    try:
        # Create assessment agent
        assessment_agent = AssessmentAgent(verbose=True)
        
        # Create test context
        context = AgentContext(
            user_id=str(uuid.uuid4()),
            session_id=str(uuid.uuid4()),
            user_profile={
                'name': 'Bob',
                'age': 35,
                'experience_level': 'intermediate',
                'emotional_state': 'unknown'
            },
            conversation_history=[
                {'role': 'user', 'content': 'Hello'},
                {'role': 'assistant', 'content': 'Welcome! How can I help you today?'}
            ]
        )
        
        # Test messages with different states
        test_messages = [
            "I'm feeling really anxious about my presentation tomorrow. My heart is racing and I can't sleep.",
            "I'm so stressed with work. Everything is overwhelming and I don't know what to do.",
            "I feel peaceful today after my morning meditation. Everything seems clear.",
            "I'm confused about my life direction. Should I change careers?",
            "I'm looking for guidance on how to manage my emotions better.",
        ]
        
        for message in test_messages:
            print(f"\n{'='*60}")
            print(f"User Message: {message}")
            print("-" * 60)
            
            response = assessment_agent.process(message, context)
            
            print(f"Confidence: {response.confidence:.2f}")
            print(f"Processing Time: {response.processing_time:.2f}s")
            print(f"\nAssessment:\n{response.content}")
            
            if 'assessment' in response.metadata:
                assessment = response.metadata['assessment']
                print(f"\n📊 Detailed Assessment:")
                print(f"   State: {assessment['primary_state']}")
                print(f"   Severity: {assessment['severity']}")
                print(f"   Urgency: {assessment['urgency_level']}/10")
                print(f"   Interventions: {', '.join(assessment['recommended_interventions'])}")
        
        print("\n" + "=" * 60)
        print("✅ Assessment Agent Test Complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
