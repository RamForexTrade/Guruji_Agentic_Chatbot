"""
Orchestrator Agent
==================

The master coordinator agent that routes queries to specialized agents
and synthesizes their responses into coherent outputs.

Responsibilities:
    - Classify user intent from input
    - Route queries to appropriate specialized agents
    - Coordinate multi-agent collaboration
    - Synthesize responses from multiple agents
    - Maintain conversation flow and coherence
    - Handle edge cases and fallbacks

Architecture:
    User Input → Orchestrator
                    ↓
    ┌───────────────┴───────────────┐
    │                               │
    Wisdom Agent              Assessment Agent
    Practice Agent            Progress Agent
                    ↓
    Orchestrator (Synthesize) → Final Response
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from langchain.tools import Tool
from langchain.schema import BaseMessage

from agents.base_agent import BaseAgent, AgentContext, AgentResponse
from agents.agent_types import AgentType, IntentType
from agents.agent_utils import merge_agent_responses, calculate_average_confidence

logger = logging.getLogger(__name__)


class OrchestratorAgent(BaseAgent):
    """
    Master orchestrator agent that coordinates all specialized agents.
    
    The orchestrator is responsible for:
    1. Analyzing user input to determine intent
    2. Routing queries to appropriate specialized agents
    3. Coordinating multiple agents when needed
    4. Synthesizing responses into coherent output
    5. Maintaining conversation flow
    
    Intent Classification:
        - SEEKING_WISDOM: User asking for teachings, guidance, insights
        - EXPRESSING_STATE: User sharing emotional/physical state
        - PRACTICE_COMPLETION: User reporting practice completion
        - PRACTICE_INQUIRY: User asking about practices/techniques
        - GENERAL_CONVERSATION: Greetings, casual chat
        - GREETING: Hello, hi, good morning, etc.
        - FAREWELL: Goodbye, bye, thank you, see you
        - FEEDBACK: User providing feedback on practices
    
    Routing Logic:
        SEEKING_WISDOM → WisdomAgent
        EXPRESSING_STATE → AssessmentAgent + WisdomAgent + PracticeAgent
        PRACTICE_COMPLETION → ProgressAgent
        PRACTICE_INQUIRY → PracticeAgent
        GENERAL_CONVERSATION → WisdomAgent (light mode)
        GREETING → Direct response
        FAREWELL → Direct response
    """
    
    def __init__(
        self,
        llm_provider: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        verbose: bool = False
    ):
        """
        Initialize the Orchestrator Agent.
        
        Args:
            llm_provider: LLM provider (groq, openai, anthropic)
            model_name: Model name
            temperature: LLM temperature for reasoning
            verbose: Enable verbose logging
        """
        super().__init__(
            agent_type=AgentType.ORCHESTRATOR,
            name="orchestrator",
            llm_provider=llm_provider,
            model_name=model_name,
            temperature=temperature,
            verbose=verbose
        )
        
        # Store references to specialized agents (will be set later)
        self.wisdom_agent = None
        self.assessment_agent = None
        self.practice_agent = None
        self.progress_agent = None
        
        logger.info("Orchestrator Agent initialized")
    
    def define_tools(self) -> List[Tool]:
        """
        Define tools for the orchestrator agent.
        
        Tools:
            - classify_intent: Classify user intent
            - route_to_agents: Determine which agents to invoke
            - synthesize_responses: Combine multiple agent responses
        
        Returns:
            List of Tool objects
        """
        
        def classify_intent_tool(user_input: str) -> str:
            """
            Classify the user's intent from their input.
            
            Args:
                user_input: The user's message
            
            Returns:
                Intent type as string
            """
            # Use LLM to classify intent
            intent = self._classify_intent_with_llm(user_input)
            return intent.value
        
        def determine_routing_tool(intent: str, user_input: str) -> str:
            """
            Determine which agents should handle this query.
            
            Args:
                intent: Classified intent type
                user_input: Original user input
            
            Returns:
                Comma-separated list of agent names
            """
            # Convert string back to enum
            try:
                intent_enum = IntentType(intent)
            except ValueError:
                intent_enum = IntentType.UNKNOWN
            
            agents = self._determine_agent_routing(intent_enum, user_input)
            return ", ".join(agents)
        
        tools = [
            Tool(
                name="classify_intent",
                func=classify_intent_tool,
                description=(
                    "Classify the user's intent from their input. "
                    "Returns one of: seeking_wisdom, expressing_state, "
                    "practice_completion, practice_inquiry, general_conversation, "
                    "greeting, farewell, feedback, unknown"
                )
            ),
            Tool(
                name="determine_routing",
                func=determine_routing_tool,
                description=(
                    "Determine which specialized agents should handle this query. "
                    "Input should be the classified intent and user input. "
                    "Returns a comma-separated list of agent names."
                )
            )
        ]
        
        return tools
    
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for the orchestrator.
        
        Returns:
            System prompt string
        """
        return """You are the Orchestrator Agent for the JAI GURU DEV AI Companion chatbot.

Your role is to be the master coordinator that ensures users receive comprehensive, 
compassionate, and contextually appropriate responses.

## Your Responsibilities:

1. **Analyze User Intent**: Understand what the user truly needs
   - Are they seeking spiritual wisdom?
   - Are they expressing an emotional or physical state?
   - Are they reporting practice completion?
   - Are they asking about practices?
   - Are they making casual conversation?

2. **Route to Specialists**: Direct queries to the right specialized agents
   - WisdomAgent: For teachings, guidance, insights
   - AssessmentAgent: For analyzing user state and needs
   - PracticeAgent: For practice recommendations
   - ProgressAgent: For tracking practice completion

3. **Synthesize Responses**: Combine multiple agent outputs into coherent responses

4. **Maintain Flow**: Ensure natural, compassionate conversation

## Intent Classification Guidelines:

**SEEKING_WISDOM**: Questions about life, teachings, meaning
- "Why do I feel this way?"
- "What is the purpose of meditation?"
- "How can I find peace?"

**EXPRESSING_STATE**: Sharing emotional or physical condition
- "I'm feeling anxious today"
- "I'm stressed about work"
- "I have a headache"

**PRACTICE_COMPLETION**: Reporting practice done
- "I completed Sudarshan Kriya"
- "I finished my meditation"
- "I did the breathing exercise"

**PRACTICE_INQUIRY**: Asking about techniques
- "How do I do pranayama?"
- "What meditation should I try?"
- "Can you teach me a breathing technique?"

**GREETING**: Opening conversations
- "Hello", "Hi", "Good morning"

**FAREWELL**: Closing conversations
- "Goodbye", "Thanks", "See you"

**GENERAL_CONVERSATION**: Casual chat
- "How are you?"
- "Tell me about yourself"

## Routing Logic:

- SEEKING_WISDOM → WisdomAgent only
- EXPRESSING_STATE → AssessmentAgent + WisdomAgent + PracticeAgent (comprehensive support)
- PRACTICE_COMPLETION → ProgressAgent only
- PRACTICE_INQUIRY → PracticeAgent only
- GREETING/FAREWELL/GENERAL → Handle directly (no agents needed)

## Communication Style:

- Be warm and compassionate
- Acknowledge user feelings
- Provide clear guidance
- Maintain spiritual context
- Be natural and conversational

Available tools:
- classify_intent: Classify user's intent
- determine_routing: Decide which agents to invoke

Always think step by step and ensure the user receives complete, helpful guidance."""
    
    def process(
        self,
        input_text: str,
        context: AgentContext,
        chat_history: Optional[List[BaseMessage]] = None
    ) -> AgentResponse:
        """
        Process user input by routing to appropriate agents.

        ENHANCED: Now supports multi-turn assessment conversations

        This is the main orchestration logic that:
        1. Checks if assessment is in progress (multi-turn)
        2. Classifies intent
        3. Routes to appropriate agents
        4. Synthesizes responses

        Args:
            input_text: User's input message
            context: User context and profile
            chat_history: Conversation history

        Returns:
            AgentResponse with orchestrated output
        """
        start_time = datetime.now()

        try:
            logger.info(f"Orchestrator processing: '{input_text[:50]}...'")

            # ENHANCED: Check if assessment is in progress
            current_assessment = context.metadata.get('current_assessment')

            if current_assessment:
                is_complete = current_assessment.get('is_complete', False)
                conv_state = current_assessment.get('conversation_state', 'initial_greeting')

                logger.info(f"Assessment state: {conv_state}, complete: {is_complete}")

                # If assessment ongoing, continue with assessment agent
                if not is_complete:
                    logger.info("Assessment in progress - continuing with assessment agent")

                    if self.assessment_agent:
                        response = self.assessment_agent.process(input_text, context, chat_history)

                        # ENHANCED: Check if assessment just completed in THIS response
                        response_assessment = response.metadata.get('assessment', {})
                        just_completed = response_assessment.get('is_complete', False)

                        if just_completed:
                            logger.info("✓✓✓ Assessment just completed! Generating 4-part solution immediately...")
                            logger.info(f"Assessment data: emotion={response_assessment.get('primary_emotion')}, "
                                      f"situation={response_assessment.get('life_situation')}, "
                                      f"location={response_assessment.get('user_location')}")

                            # Generate solution and append to the response
                            logger.info("Calling _handle_completed_assessment()...")
                            solution_response = self._handle_completed_assessment(
                                input_text,
                                context,
                                response_assessment,
                                start_time
                            )
                            logger.info(f"Solution response received: {len(solution_response.content)} chars")

                            # Combine the completion message with the solution
                            # If assessment response is empty (to avoid duplication), just use solution
                            if response.content.strip():
                                combined_content = response.content + "\n\n" + solution_response.content
                            else:
                                combined_content = solution_response.content

                            # Update response
                            response.content = combined_content
                            response.metadata.update(solution_response.metadata)
                            response.processing_time = (datetime.now() - start_time).total_seconds()

                            logger.info("✓ Combined assessment completion + 4-part solution delivered")

                        logger.info(f"Assessment agent completed in {response.processing_time:.2f}s")
                        return response
                    else:
                        logger.warning("Assessment agent not available")

                # If assessment just completed, generate 4-part solution
                elif is_complete and conv_state == 'assessment_complete':
                    logger.info("Assessment complete - generating 4-part solution")
                    return self._handle_completed_assessment(input_text, context, current_assessment, start_time)

            # Step 1: Classify intent
            intent = self._classify_intent_with_llm(input_text)
            logger.info(f"Classified intent: {intent.value}")

            # Step 2: Handle simple cases directly
            if intent == IntentType.GREETING:
                return self._handle_greeting(context, start_time)

            elif intent == IntentType.FAREWELL:
                return self._handle_farewell(context, start_time)

            elif intent == IntentType.GENERAL_CONVERSATION:
                return self._handle_general_conversation(input_text, context, start_time)

            # ENHANCED: If expressing state, start assessment
            if intent == IntentType.EXPRESSING_STATE and self.assessment_agent:
                logger.info("User expressing state - starting assessment")
                response = self.assessment_agent.process(input_text, context, chat_history)

                processing_time = (datetime.now() - start_time).total_seconds()
                response.processing_time = processing_time

                return response

            # Step 3: Determine agent routing for complex queries
            agent_names = self._determine_agent_routing(intent, input_text)
            logger.info(f"Routing to agents: {agent_names}")

            # Step 4: Invoke specialized agents
            agent_responses = self._invoke_agents(
                agent_names,
                input_text,
                context,
                intent
            )

            # Step 5: Synthesize responses
            final_response = self._synthesize_responses(
                agent_responses,
                intent,
                context
            )

            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()

            # Create orchestrator response
            response = AgentResponse(
                agent_name=self.name,
                content=final_response,
                confidence=calculate_average_confidence(agent_responses),
                metadata={
                    'intent': intent.value,
                    'agents_invoked': agent_names,
                    'agent_responses': agent_responses
                },
tools_used=['classify_intent', 'determine_routing', 'synthesize_responses'],
                processing_time=processing_time,
                success=True
            )

            logger.info(f"Orchestrator completed in {processing_time:.2f}s")
            return response

        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            return self.handle_error(e, context)
    
    def _classify_intent_with_llm(self, user_input: str) -> IntentType:
        """
        Use LLM to classify user intent.
        
        Args:
            user_input: User's message
        
        Returns:
            IntentType enum
        """
        # Create classification prompt
        prompt = f"""Classify the following user message into ONE of these intents:

EXPRESSING_STATE - User sharing their emotional, mental, or physical state, feelings, confusion, stress, anxiety, sadness, pain, or any personal struggle. Examples: "I'm feeling anxious", "I don't know what's happening with me", "I'm stressed", "I feel lost", "Something is bothering me"

SEEKING_WISDOM - User asking for general teachings, philosophical insights, or explanations about life concepts (NOT about their current emotional state). Examples: "What is the meaning of life?", "Tell me about karma", "What does Gurudev say about relationships?"

PRACTICE_COMPLETION - User reporting they completed a practice
PRACTICE_INQUIRY - User asking about practices, techniques, or how to do them
GENERAL_CONVERSATION - Casual conversation, questions about the chatbot
GREETING - Hello, hi, good morning, etc.
FAREWELL - Goodbye, thanks, see you later, etc.
FEEDBACK - User providing feedback on their experience
UNKNOWN - Cannot determine intent

IMPORTANT: If the user is expressing any personal feeling, confusion, or emotional state, ALWAYS classify as EXPRESSING_STATE, even if they're asking for help.

User message: "{user_input}"

Respond with ONLY the intent name (e.g., "EXPRESSING_STATE").
"""
        
        try:
            # Invoke LLM for classification
            response = self.llm.invoke(prompt)
            intent_str = response.content.strip().upper()
            
            # Try to match to IntentType
            for intent_type in IntentType:
                if intent_type.value.upper() == intent_str:
                    return intent_type
            
            # Fallback: keyword matching
            return self._classify_intent_by_keywords(user_input)
            
        except Exception as e:
            logger.warning(f"LLM classification failed: {e}, using keyword fallback")
            return self._classify_intent_by_keywords(user_input)
    
    def _classify_intent_by_keywords(self, user_input: str) -> IntentType:
        """
        Fallback keyword-based intent classification.
        
        Args:
            user_input: User's message
        
        Returns:
            IntentType enum
        """
        text = user_input.lower()
        
        # Greeting patterns
        if any(word in text for word in ['hello', 'hi', 'hey', 'good morning', 'good evening', 'namaste']):
            return IntentType.GREETING
        
        # Farewell patterns
        if any(word in text for word in ['bye', 'goodbye', 'see you', 'thank you', 'thanks']):
            return IntentType.FAREWELL
        
        # Practice completion patterns
        if any(phrase in text for phrase in ['completed', 'finished', 'did the', 'practiced', 'done with']):
            return IntentType.PRACTICE_COMPLETION
        
        # Expressing state patterns (EXPANDED for better detection)
        expressing_keywords = [
            'feeling', 'feel', 'anxious', 'stressed', 'worried', 'sad', 'happy', 'pain',
            "don't know what", "don't know why", 'confused', 'overwhelmed', 'upset',
            'depressed', 'lonely', 'angry', 'frustrated', 'lost', 'stuck', 'hurt',
            'struggling', 'bothering me', 'happening with me', 'happening to me',
            'wrong with me', 'matter with me'
        ]
        if any(phrase in text for phrase in expressing_keywords):
            return IntentType.EXPRESSING_STATE
        
        # Practice inquiry patterns
        if any(phrase in text for phrase in ['how to', 'how do i', 'teach me', 'show me', 'practice', 'technique']):
            return IntentType.PRACTICE_INQUIRY
        
        # Seeking wisdom patterns
        if any(word in text for word in ['why', 'what is', 'meaning', 'purpose', 'wisdom', 'teach', 'guidance']):
            return IntentType.SEEKING_WISDOM
        
        # Default to general conversation
        return IntentType.GENERAL_CONVERSATION
    
    def _determine_agent_routing(self, intent: IntentType, user_input: str) -> List[str]:
        """
        Determine which agents should handle this query.
        
        Args:
            intent: Classified intent
            user_input: Original user input
        
        Returns:
            List of agent names to invoke
        """
        routing_map = {
            IntentType.SEEKING_WISDOM: ['wisdom'],
            IntentType.EXPRESSING_STATE: ['assessment', 'wisdom', 'practice'],
            IntentType.PRACTICE_COMPLETION: ['progress'],
            IntentType.PRACTICE_INQUIRY: ['practice'],
            IntentType.FEEDBACK: ['progress'],
            IntentType.UNKNOWN: ['wisdom']
        }
        
        return routing_map.get(intent, [])
    
    def _invoke_agents(
        self,
        agent_names: List[str],
        input_text: str,
        context: AgentContext,
        intent: IntentType
    ) -> List[Dict[str, Any]]:
        """
        Invoke specified specialized agents.
        
        Args:
            agent_names: List of agent names to invoke
            input_text: User input
            context: User context
            intent: Classified intent
        
        Returns:
            List of agent response dictionaries
        """
        responses = []
        
        for agent_name in agent_names:
            try:
                # Get agent reference
                agent = self._get_agent(agent_name)
                
                if agent is None:
                    logger.warning(f"Agent '{agent_name}' not available, creating placeholder response")
                    # Create placeholder response
                    responses.append({
                        'agent_name': agent_name,
                        'content': f"[{agent_name} agent not yet implemented]",
                        'confidence': 0.5,
                        'success': False
                    })
                    continue
                
                # Invoke agent
                logger.info(f"Invoking {agent_name} agent...")
                response = agent.process(input_text, context)
                responses.append(response.to_dict())
                
            except Exception as e:
                logger.error(f"Error invoking {agent_name} agent: {e}")
                responses.append({
                    'agent_name': agent_name,
                    'content': f"Error from {agent_name}",
                    'confidence': 0.0,
                    'success': False,
                    'error': str(e)
                })
        
        return responses
    
    def _get_agent(self, agent_name: str):
        """Get reference to specialized agent"""
        agent_map = {
            'wisdom': self.wisdom_agent,
            'assessment': self.assessment_agent,
            'practice': self.practice_agent,
            'progress': self.progress_agent
        }
        return agent_map.get(agent_name)
    
    def _synthesize_responses(
        self,
        agent_responses: List[Dict[str, Any]],
        intent: IntentType,
        context: AgentContext
    ) -> str:
        """
        Synthesize multiple agent responses into coherent output.
        
        Args:
            agent_responses: List of responses from agents
            intent: Original intent
            context: User context
        
        Returns:
            Synthesized response string
        """
        if not agent_responses:
            return self.get_fallback_response(context)
        
        # For single agent response, return as-is
        if len(agent_responses) == 1:
            return agent_responses[0].get('content', '')
        
        # For multiple agents, synthesize
        user_name = context.user_profile.get('name', 'friend')
        
        # Build synthesis prompt
        responses_text = "\n\n".join([
            f"{resp.get('agent_name', 'Agent')}: {resp.get('content', '')}"
            for resp in agent_responses
            if resp.get('success', False)
        ])
        
        synthesis_prompt = f"""You are synthesizing responses from multiple specialized agents for a user.

User: {user_name}
Intent: {intent.value}

Agent Responses:
{responses_text}

Create a single, coherent, compassionate response that:
1. Flows naturally as one message
2. Acknowledges the user's state/question
3. Provides wisdom and guidance
4. Recommends practices if applicable
5. Maintains a warm, supportive tone

Do not mention agents or system components. Respond as a caring guide.

Synthesized Response:"""
        
        try:
            # Use LLM to synthesize
            response = self.llm.invoke(synthesis_prompt)
            return response.content.strip()
        except Exception as e:
            logger.error(f"Synthesis failed: {e}, using fallback")
            # Fallback: concatenate responses
            return merge_agent_responses(agent_responses)
    
    def _handle_greeting(self, context: AgentContext, start_time: datetime) -> AgentResponse:
        """Handle greeting intent directly"""
        user_name = context.user_profile.get('name', 'dear friend')
        
        greetings = [
            f"🙏 Namaste, {user_name}! Welcome to your spiritual journey. How may I guide you today?",
            f"Hello, {user_name}! 🙏 I'm here to support you with wisdom and guidance. What's on your mind?",
            f"Greetings, {user_name}! May your day be filled with peace and clarity. How can I help you today?",
        ]
        
        import random
        greeting = random.choice(greetings)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return AgentResponse(
            agent_name=self.name,
            content=greeting,
            confidence=1.0,
            metadata={'intent': 'greeting', 'direct_response': True},
            processing_time=processing_time,
            success=True
        )
    
    def _handle_farewell(self, context: AgentContext, start_time: datetime) -> AgentResponse:
        """Handle farewell intent directly"""
        user_name = context.user_profile.get('name', 'dear friend')
        
        farewells = [
            f"🙏 May peace and wisdom be with you, {user_name}. Until we meet again!",
            f"Take care, {user_name}! Remember, I'm always here when you need guidance. 🙏",
            f"Blessings on your journey, {user_name}. May you find clarity and joy in each moment. 🙏",
        ]
        
        import random
        farewell = random.choice(farewells)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return AgentResponse(
            agent_name=self.name,
            content=farewell,
            confidence=1.0,
            metadata={'intent': 'farewell', 'direct_response': True},
            processing_time=processing_time,
            success=True
        )
    
    def _handle_general_conversation(
        self,
        input_text: str,
        context: AgentContext,
        start_time: datetime
    ) -> AgentResponse:
        """Handle general conversation intent"""
        user_name = context.user_profile.get('name', 'friend')
        
        prompt = f"""You are the JAI GURU DEV AI Companion, a compassionate spiritual guide.

User ({user_name}) said: "{input_text}"

Respond warmly and naturally to their message. Keep it conversational and supportive.
If they're asking about you, explain you're an AI spiritual companion based on Sri Sri Ravi Shankar's teachings.

Response:"""
        
        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip()
        except Exception as e:
            logger.error(f"General conversation handling failed: {e}")
            content = f"Hello {user_name}! I'm here to support you on your spiritual journey. How may I help you today? 🙏"
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return AgentResponse(
            agent_name=self.name,
            content=content,
            confidence=0.8,
            metadata={'intent': 'general_conversation', 'direct_response': True},
            processing_time=processing_time,
            success=True
        )

    def _handle_completed_assessment(
        self,
        input_text: str,
        context: AgentContext,
        assessment_data: Dict[str, Any],
        start_time: datetime
    ) -> AgentResponse:
        """
        Handle completed assessment by generating 4-part solution.

        Steps:
        1. Build wisdom query from assessment
        2. Retrieve wisdom from Wisdom Agent
        3. Generate 4-part solution (Pranayama, Asana, Wisdom, Activity)
        4. Return formatted solution

        Args:
            input_text: User input
            context: Agent context
            assessment_data: Completed assessment data
            start_time: Processing start time

        Returns:
            AgentResponse with 4-part solution
        """
        try:
            # Extract assessment details
            emotion = assessment_data.get('primary_emotion', 'unknown')
            situation = assessment_data.get('life_situation', 'unknown')
            location = assessment_data.get('user_location', 'home_indoor')
            age = assessment_data.get('user_age', context.user_profile.get('age', 25))
            tone = assessment_data.get('tone', 'warm')

            logger.info(f"Generating 4-part solution: emotion={emotion}, situation={situation}, location={location}")

            # Step 1: Build wisdom query
            emotion_readable = emotion.replace('_', ' ')
            situation_readable = situation.replace('_', ' ')
            wisdom_query = f"guidance for someone experiencing {emotion_readable} related to {situation_readable}"

            logger.info(f"Wisdom query: {wisdom_query}")

            # Step 2: Retrieve wisdom using Wisdom Agent
            if self.wisdom_agent:
                logger.info("Calling wisdom agent to retrieve teachings...")
                wisdom_context = AgentContext(
                    user_id=context.user_id,
                    session_id=context.session_id,
                    user_profile=context.user_profile,
                    conversation_history=context.conversation_history,
                    metadata={'assessment': assessment_data, 'query_type': 'assessment_based'}
                )

                try:
                    wisdom_response = self.wisdom_agent.process(wisdom_query, wisdom_context)
                    wisdom_text = wisdom_response.content
                    logger.info(f"✓ Wisdom retrieved successfully: {len(wisdom_text)} chars")
                except Exception as e:
                    logger.error(f"❌ Wisdom agent failed: {e}")
                    import traceback
                    traceback.print_exc()
                    wisdom_text = "Take a moment to breathe and center yourself. All things pass in time."
            else:
                wisdom_text = "Take a moment to breathe and center yourself. All things pass in time."
                logger.warning("⚠ Wisdom agent not available, using fallback wisdom")

            # Step 3: Retrieve pranayama practice using Practice Agent
            pranayama_text = None
            if self.practice_agent:
                logger.info("Calling practice agent to retrieve pranayama recommendation...")
                practice_context = AgentContext(
                    user_id=context.user_id,
                    session_id=context.session_id,
                    user_profile=context.user_profile,
                    conversation_history=context.conversation_history,
                    metadata={'assessment': assessment_data, 'practice_type': 'pranayama'}
                )

                try:
                    pranayama_response = self.practice_agent.process(
                        f"Recommend pranayama for {emotion_readable}",
                        practice_context
                    )

                    # Check if Practice Agent returned a valid recommendation
                    confidence = pranayama_response.metadata.get('confidence', 1.0)
                    logger.info(f"Practice Agent pranayama response confidence: {confidence}")

                    # Check if it's a fallback: low confidence OR contains "Breath Awareness Meditation"
                    is_fallback = (confidence < 0.7 or
                                  "Breath Awareness Meditation" in pranayama_response.content)

                    if is_fallback:
                        logger.warning(f"⚠ Practice Agent returned fallback for pranayama (confidence={confidence}), using hardcoded instead")
                        pranayama_text = None
                    else:
                        pranayama_text = pranayama_response.content
                        logger.info(f"✓ Pranayama retrieved from Practice Agent: {len(pranayama_text)} chars")
                except Exception as e:
                    logger.error(f"❌ Practice agent failed for pranayama: {e}")
                    import traceback
                    traceback.print_exc()
                    pranayama_text = None
            else:
                logger.warning("⚠ Practice agent not available for pranayama")
                pranayama_text = None

            # Step 4: Retrieve asana practice using Practice Agent
            asana_text = None
            if self.practice_agent:
                logger.info("Calling practice agent to retrieve asana recommendation...")
                practice_context = AgentContext(
                    user_id=context.user_id,
                    session_id=context.session_id,
                    user_profile=context.user_profile,
                    conversation_history=context.conversation_history,
                    metadata={'assessment': assessment_data, 'practice_type': 'asana'}
                )

                try:
                    asana_response = self.practice_agent.process(
                        f"Recommend yoga asana for {emotion_readable}",
                        practice_context
                    )

                    # Check if Practice Agent returned a valid recommendation
                    confidence = asana_response.metadata.get('confidence', 1.0)
                    logger.info(f"Practice Agent asana response confidence: {confidence}")

                    # Check if it's a fallback: low confidence OR contains "Breath Awareness Meditation"
                    is_fallback = (confidence < 0.7 or
                                  "Breath Awareness Meditation" in asana_response.content)

                    if is_fallback:
                        logger.warning(f"⚠ Practice Agent returned fallback for asana (confidence={confidence}), using hardcoded instead")
                        asana_text = None
                    else:
                        asana_text = asana_response.content
                        logger.info(f"✓ Asana retrieved from Practice Agent: {len(asana_text)} chars")
                except Exception as e:
                    logger.error(f"❌ Practice agent failed for asana: {e}")
                    import traceback
                    traceback.print_exc()
                    asana_text = None
            else:
                logger.warning("⚠ Practice agent not available for asana")
                asana_text = None

            # Step 5: Generate 4-part solution
            from agents.solution_generator import SolutionGenerator
            from agents.agent_types import EmotionalState, LifeSituation, UserLocation

            try:
                logger.info("Generating 4-part solution (Pranayama, Asana, Wisdom, Activity)...")
                solution = SolutionGenerator.generate(
                    emotion=EmotionalState(emotion),
                    situation=LifeSituation(situation),
                    location=UserLocation(location),
                    age=age,
                    tone=tone,
                    user_name=context.user_profile.get('name', 'friend'),
                    wisdom_text=wisdom_text,
                    pranayama_text=pranayama_text,  # From Practice Agent
                    asana_text=asana_text  # From Practice Agent
                )

                # Step 6: Format solution
                logger.info("Formatting 4-part solution...")
                formatted_solution = SolutionGenerator.format_solution(solution, UserLocation(location))

                logger.info("✓ 4-part solution generated successfully")

            except Exception as e:
                logger.error(f"❌ Solution generation failed: {e}, using wisdom only")
                import traceback
                traceback.print_exc()
                formatted_solution = wisdom_text

            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()

            # Clear assessment from context (solution delivered)
            context.metadata['last_assessment'] = assessment_data
            context.metadata['current_assessment'] = None

            # Create response
            response = AgentResponse(
                agent_name=self.name,
                content=formatted_solution,
                confidence=0.9,
                metadata={
                    'assessment': assessment_data,
                    'solution_type': '4_part_holistic',
                    'wisdom_source': 'wisdom_agent',
                    'agents_used': ['assessment', 'wisdom', 'solution_generator']
                },
                tools_used=['assessment_agent', 'wisdom_agent', 'solution_generator'],
                processing_time=processing_time,
                success=True
            )

            logger.info(f"4-part solution delivered in {processing_time:.2f}s")
            return response

        except Exception as e:
            logger.error(f"Error handling completed assessment: {e}")
            import traceback
            traceback.print_exc()

            # Fallback: return wisdom only
            processing_time = (datetime.now() - start_time).total_seconds()

            return AgentResponse(
                agent_name=self.name,
                content="I understand your situation. Let me offer you some guidance and practices to help you find balance.",
                confidence=0.5,
                metadata={'error': str(e)},
                processing_time=processing_time,
                success=False
            )

    def set_specialized_agents(
        self,
        wisdom_agent=None,
        assessment_agent=None,
        practice_agent=None,
        progress_agent=None
    ):
        """
        Set references to specialized agents.
        
        Args:
            wisdom_agent: WisdomAgent instance
            assessment_agent: AssessmentAgent instance
            practice_agent: PracticeAgent instance
            progress_agent: ProgressAgent instance
        """
        if wisdom_agent:
            self.wisdom_agent = wisdom_agent
            logger.info("Wisdom agent registered with orchestrator")
        
        if assessment_agent:
            self.assessment_agent = assessment_agent
            logger.info("Assessment agent registered with orchestrator")
        
        if practice_agent:
            self.practice_agent = practice_agent
            logger.info("Practice agent registered with orchestrator")
        
        if progress_agent:
            self.progress_agent = progress_agent
            logger.info("Progress agent registered with orchestrator")


# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    import uuid
    
    load_dotenv()
    
    print("=" * 60)
    print("Orchestrator Agent Test")
    print("=" * 60)
    
    # Create orchestrator
    orchestrator = OrchestratorAgent(verbose=True)
    
    # Create test context
    context = AgentContext(
        user_id=str(uuid.uuid4()),
        session_id=str(uuid.uuid4()),
        user_profile={
            'name': 'Alice',
            'age': 28,
            'emotional_state': 'curious'
        }
    )
    
    # Test different intents
    test_queries = [
        "Hello! Good morning!",
        "I'm feeling very anxious today",
        "Why do we meditate?",
        "How do I do Sudarshan Kriya?",
        "I completed my meditation practice",
        "Thank you, goodbye!",
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"User: {query}")
        print("-" * 60)
        
        response = orchestrator.process(query, context)
        
        print(f"Intent: {response.metadata.get('intent', 'unknown')}")
        print(f"Confidence: {response.confidence:.2f}")
        print(f"Processing Time: {response.processing_time:.2f}s")
        print(f"\nResponse:\n{response.content}")
    
    print("\n" + "=" * 60)
    print("✅ Orchestrator Agent Test Complete!")
    print("=" * 60)
