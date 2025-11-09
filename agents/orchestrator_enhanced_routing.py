"""
Enhanced Orchestrator Routing Logic
====================================

This module provides the updated routing logic for the orchestrator to work
with the Enhanced Assessment Agent.

Key Changes:
1. Check if assessment is in progress before routing elsewhere
2. Only route to Wisdom Agent AFTER assessment is complete
3. Support multi-turn assessment conversations
4. Generate 4-part solutions after wisdom retrieval

Integration:
- Add these methods to existing OrchestratorAgent class
- Or use as a mixin/extension
"""

from typing import Dict, Any, List, Optional, Tuple
import logging

from agents.base_agent import AgentContext, AgentResponse
from agents.agent_types import IntentType, ConversationState
from agents.solution_generator import SolutionGenerator

logger = logging.getLogger(__name__)


class EnhancedOrchestratorRouting:
    """
    Enhanced routing logic for orchestrator to support
    multi-turn assessment and prevent premature wisdom routing.
    """

    def process_with_assessment_awareness(
        self,
        input_text: str,
        context: AgentContext,
        chat_history: Optional[List] = None
    ) -> AgentResponse:
        """
        Enhanced process method that respects assessment state.

        Flow:
        1. Check if assessment is in progress
        2. If in progress → continue with assessment agent
        3. If complete → proceed with normal routing (wisdom, etc.)
        4. If wisdom retrieved → generate 4-part solution

        Args:
            input_text: User input
            context: Agent context
            chat_history: Conversation history

        Returns:
            AgentResponse
        """

        # Step 1: Check for ongoing assessment
        current_assessment = context.metadata.get('current_assessment')

        if current_assessment:
            is_complete = current_assessment.get('is_complete', False)
            conv_state = current_assessment.get('conversation_state', 'initial_greeting')

            logger.info(f"Assessment state: {conv_state}, complete: {is_complete}")

            # If assessment is ongoing (not complete), continue with assessment agent
            if not is_complete:
                logger.info("Assessment in progress - routing to assessment agent")
                return self.assessment_agent.process(input_text, context, chat_history)

            # If assessment just completed, route to wisdom agent
            elif is_complete and conv_state == 'assessment_complete':
                logger.info("Assessment complete - routing to wisdom agent")
                return self._handle_completed_assessment(input_text, context, current_assessment)

        # Step 2: New conversation or no assessment context
        # Classify intent and route normally
        intent = self._classify_intent_with_llm(input_text)

        # Step 3: If expressing state, start assessment
        if intent == IntentType.EXPRESSING_STATE:
            logger.info("User expressing state - starting assessment")
            return self.assessment_agent.process(input_text, context, chat_history)

        # Step 4: Other intents - normal routing
        return self._normal_routing(input_text, context, intent, chat_history)

    def _handle_completed_assessment(
        self,
        input_text: str,
        context: AgentContext,
        assessment_data: Dict[str, Any]
    ) -> AgentResponse:
        """
        Handle a completed assessment by retrieving wisdom and generating solution.

        Steps:
        1. Build query from assessment data
        2. Retrieve wisdom from Chroma DB via Wisdom Agent
        3. Generate 4-part solution with pranayama, asana, wisdom, activity
        4. Return formatted solution

        Args:
            input_text: User input
            context: Agent context
            assessment_data: Completed assessment data

        Returns:
            AgentResponse with complete solution
        """

        # Extract assessment details
        emotion = assessment_data.get('primary_emotion', 'unknown')
        situation = assessment_data.get('life_situation', 'unknown')
        location = assessment_data.get('user_location', 'home_indoor')
        age = assessment_data.get('user_age', 25)
        tone = assessment_data.get('tone', 'warm')

        logger.info(f"Generating solution for: emotion={emotion}, situation={situation}, location={location}")

        # Step 1: Build wisdom query
        wisdom_query = self._build_wisdom_query(emotion, situation, context)

        logger.info(f"Wisdom query: {wisdom_query}")

        # Step 2: Retrieve wisdom using Wisdom Agent
        # Create a temporary context for wisdom retrieval
        wisdom_context = AgentContext(
            user_id=context.user_id,
            session_id=context.session_id,
            user_profile=context.user_profile,
            conversation_history=context.conversation_history,
            metadata={
                'assessment': assessment_data,
                'query_type': 'assessment_based'
            }
        )

        wisdom_response = self.wisdom_agent.process(wisdom_query, wisdom_context)

        # Extract verbatim wisdom from response
        wisdom_text = wisdom_response.content

        logger.info("Wisdom retrieved successfully")

        # Step 3: Generate 4-part solution
        from agents.agent_types import EmotionalState, LifeSituation, UserLocation

        solution = SolutionGenerator.generate(
            emotion=EmotionalState(emotion),
            situation=LifeSituation(situation),
            location=UserLocation(location),
            age=age,
            tone=tone,
            user_name=context.user_profile.get('name', 'friend'),
            wisdom_text=wisdom_text
        )

        # Step 4: Format solution
        formatted_solution = SolutionGenerator.format_solution(
            solution,
            UserLocation(location)
        )

        logger.info("4-part solution generated")

        # Step 5: Mark solution as delivered and clear assessment
        context.metadata['last_assessment'] = assessment_data
        context.metadata['current_assessment'] = None  # Clear for next conversation

        # Create response
        response = AgentResponse(
            agent_name="orchestrator",
            content=formatted_solution,
            confidence=0.9,
            metadata={
                'assessment': assessment_data,
                'solution_type': '4_part_holistic',
                'wisdom_source': 'chroma_db',
                'agents_used': ['assessment', 'wisdom', 'solution_generator']
            },
            tools_used=['assessment_agent', 'wisdom_agent', 'solution_generator'],
            processing_time=wisdom_response.processing_time,
            success=True
        )

        return response

    def _build_wisdom_query(
        self,
        emotion: str,
        situation: str,
        context: AgentContext
    ) -> str:
        """
        Build appropriate wisdom query from assessment data.

        Args:
            emotion: Primary emotion
            situation: Life situation
            context: User context

        Returns:
            Query string for wisdom retrieval
        """

        emotion_readable = emotion.replace('_', ' ')
        situation_readable = situation.replace('_', ' ')

        # Build contextual query
        query = f"guidance for someone experiencing {emotion_readable} related to {situation_readable}"

        return query

    def _normal_routing(
        self,
        input_text: str,
        context: AgentContext,
        intent: IntentType,
        chat_history: Optional[List] = None
    ) -> AgentResponse:
        """
        Normal routing for non-assessment queries.

        This is the original orchestrator routing logic for:
        - SEEKING_WISDOM → Wisdom Agent
        - PRACTICE_INQUIRY → Practice Agent
        - PRACTICE_COMPLETION → Progress Agent
        - GREETING/FAREWELL → Direct responses

        Args:
            input_text: User input
            context: Agent context
            intent: Classified intent
            chat_history: Conversation history

        Returns:
            AgentResponse
        """

        # Handle simple intents directly
        if intent == IntentType.GREETING:
            return self._handle_greeting(context, None)

        elif intent == IntentType.FAREWELL:
            return self._handle_farewell(context, None)

        elif intent == IntentType.GENERAL_CONVERSATION:
            return self._handle_general_conversation(input_text, context, None)

        # Route to specialized agents
        elif intent == IntentType.SEEKING_WISDOM:
            logger.info("Routing to Wisdom Agent")
            return self.wisdom_agent.process(input_text, context, chat_history)

        elif intent == IntentType.PRACTICE_INQUIRY:
            if self.practice_agent:
                logger.info("Routing to Practice Agent")
                return self.practice_agent.process(input_text, context, chat_history)
            else:
                # Fallback to wisdom agent
                return self.wisdom_agent.process(input_text, context, chat_history)

        elif intent == IntentType.PRACTICE_COMPLETION:
            if self.progress_agent:
                logger.info("Routing to Progress Agent")
                return self.progress_agent.process(input_text, context, chat_history)
            else:
                # Fallback acknowledgment
                return self._handle_practice_completion_fallback(input_text, context)

        # Unknown or other intents → default to wisdom agent
        else:
            logger.info(f"Unknown intent {intent}, defaulting to Wisdom Agent")
            return self.wisdom_agent.process(input_text, context, chat_history)

    def _handle_practice_completion_fallback(
        self,
        input_text: str,
        context: AgentContext
    ) -> AgentResponse:
        """Fallback for practice completion when progress agent not available"""
        user_name = context.user_profile.get('name', 'friend')

        return AgentResponse(
            agent_name="orchestrator",
            content=f"Wonderful, {user_name}! Thank you for sharing your practice completion. Regular practice is the key to transformation. How are you feeling now?",
            confidence=0.8,
            metadata={'intent': 'practice_completion_fallback'},
            tools_used=[],
            processing_time=0.0,
            success=True
        )

    def should_route_to_wisdom(self, context: AgentContext) -> bool:
        """
        Check if it's safe to route to wisdom agent.

        Returns False if assessment is still in progress.

        Args:
            context: Agent context

        Returns:
            True if safe to route to wisdom, False otherwise
        """
        current_assessment = context.metadata.get('current_assessment')

        if not current_assessment:
            return True  # No assessment in progress

        is_complete = current_assessment.get('is_complete', False)

        return is_complete  # Only route if complete

    def is_assessment_in_progress(self, context: AgentContext) -> bool:
        """
        Check if assessment is currently in progress.

        Args:
            context: Agent context

        Returns:
            True if assessment ongoing, False otherwise
        """
        current_assessment = context.metadata.get('current_assessment')

        if not current_assessment:
            return False

        is_complete = current_assessment.get('is_complete', False)
        conv_state = current_assessment.get('conversation_state', '')

        # In progress if not complete and in an active probing state
        return not is_complete and conv_state in [
            'initial_greeting',
            'probing_emotion',
            'probing_situation',
            'probing_location'
        ]

    def reset_assessment(self, context: AgentContext):
        """
        Reset/clear assessment state.

        Use this to start fresh assessment or after solution delivery.

        Args:
            context: Agent context
        """
        # Move current to history if exists
        if 'current_assessment' in context.metadata:
            if 'assessment_history' not in context.metadata:
                context.metadata['assessment_history'] = []

            context.metadata['assessment_history'].append(
                context.metadata['current_assessment']
            )

        # Clear current
        context.metadata['current_assessment'] = None

        logger.info("Assessment state reset")


# Integration Example
# ====================
# Add these methods to existing OrchestratorAgent class:

"""
class OrchestratorAgent(BaseAgent):
    # ... existing code ...

    def process(self, input_text, context, chat_history=None):
        '''
        Enhanced process method with assessment awareness
        '''
        # Add EnhancedOrchestratorRouting as mixin or delegate
        routing = EnhancedOrchestratorRouting()

        # Copy references
        routing.assessment_agent = self.assessment_agent
        routing.wisdom_agent = self.wisdom_agent
        routing.practice_agent = self.practice_agent
        routing.progress_agent = self.progress_agent
        routing.llm = self.llm
        routing._classify_intent_with_llm = self._classify_intent_with_llm
        routing._handle_greeting = self._handle_greeting
        routing._handle_farewell = self._handle_farewell
        routing._handle_general_conversation = self._handle_general_conversation

        # Delegate to enhanced routing
        return routing.process_with_assessment_awareness(
            input_text,
            context,
            chat_history
        )
"""

# Usage in main application
# ==========================

"""
from agents.orchestrator import OrchestratorAgent
from agents.assessment_agent_enhanced import EnhancedAssessmentAgent
from agents.wisdom_agent import WisdomAgent

# Create agents
orchestrator = OrchestratorAgent()
assessment_agent = EnhancedAssessmentAgent()
wisdom_agent = WisdomAgent()

# Link agents
orchestrator.assessment_agent = assessment_agent
orchestrator.wisdom_agent = wisdom_agent

# Process user input
context = AgentContext(...)

response = orchestrator.process("I'm feeling anxious", context)

# Orchestrator will:
# 1. Start assessment
# 2. Continue multi-turn dialog
# 3. Complete assessment
# 4. Retrieve wisdom
# 5. Generate 4-part solution
# 6. Return to user
"""
