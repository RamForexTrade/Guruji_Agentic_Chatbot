"""
Practice Agent
==============

Specialized agent for recommending spiritual practices and techniques.

Responsibilities:
    - Recommend specific practices based on user assessment
    - Filter practices by user level and constraints
    - Customize techniques for individual needs
    - Provide clear, step-by-step instructions
    - Offer alternative practices
    - Match duration and difficulty to user capacity
    - Optimize recommendations for time of day
    - Consider user history and preferences

Architecture:
    Assessment + User Context → Practice Agent
                                     ↓
                          Practice Database Query
                                     ↓
                          Filter by Constraints
                                     ↓
                          Rank by Effectiveness
                                     ↓
                          Customize Instructions
                                     ↓
                    Practice Recommendation (JSON)
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, time
import logging

from langchain.prompts import PromptTemplate
from langchain.schema import BaseMessage

from agents.base_agent import BaseAgent, AgentContext, AgentResponse
from agents.agent_types import (
    AgentType,
    EmotionalState,
    SeverityLevel,
    ReadinessLevel,
    PracticeType,
    ExperienceLevel
)

logger = logging.getLogger(__name__)


class Practice:
    """
    Data class representing a spiritual practice or technique.
    
    Contains all information needed to recommend and guide a practice.
    """
    
    def __init__(
        self,
        practice_id: str,
        name: str,
        practice_type: PracticeType,
        description: str,
        instructions: str,
        duration_minutes: int,
        difficulty: ExperienceLevel,
        benefits: List[str],
        contraindications: List[str],
        best_time_of_day: List[str],
        states_addressed: List[EmotionalState],
        tags: List[str],
        source_reference: str = ""
    ):
        self.practice_id = practice_id
        self.name = name
        self.practice_type = practice_type
        self.description = description
        self.instructions = instructions
        self.duration_minutes = duration_minutes
        self.difficulty = difficulty
        self.benefits = benefits
        self.contraindications = contraindications
        self.best_time_of_day = best_time_of_day
        self.states_addressed = states_addressed
        self.tags = tags
        self.source_reference = source_reference
        self.effectiveness_score = 0.0  # Calculated during ranking
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert practice to dictionary"""
        return {
            'practice_id': self.practice_id,
            'name': self.name,
            'practice_type': self.practice_type.value if isinstance(self.practice_type, PracticeType) else self.practice_type,
            'description': self.description,
            'instructions': self.instructions,
            'duration_minutes': self.duration_minutes,
            'difficulty': self.difficulty.value if isinstance(self.difficulty, ExperienceLevel) else self.difficulty,
            'benefits': self.benefits,
            'contraindications': self.contraindications,
            'best_time_of_day': self.best_time_of_day,
            'states_addressed': [
                s.value if isinstance(s, EmotionalState) else s 
                for s in self.states_addressed
            ],
            'tags': self.tags,
            'source_reference': self.source_reference,
            'effectiveness_score': self.effectiveness_score
        }
    
    def __repr__(self) -> str:
        return f"Practice(name={self.name}, type={self.practice_type}, duration={self.duration_minutes}min)"


class PracticeRecommendation:
    """
    Data class for practice recommendation result.
    
    Contains the primary recommendation plus alternatives.
    """
    
    def __init__(
        self,
        primary_practice: Practice,
        alternatives: List[Practice],
        customized_instructions: str,
        reasoning: str,
        expected_benefits: List[str],
        preparation_tips: List[str],
        contraindication_warnings: List[str],
        confidence: float
    ):
        self.primary_practice = primary_practice
        self.alternatives = alternatives
        self.customized_instructions = customized_instructions
        self.reasoning = reasoning
        self.expected_benefits = expected_benefits
        self.preparation_tips = preparation_tips
        self.contraindication_warnings = contraindication_warnings
        self.confidence = confidence
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert recommendation to dictionary"""
        return {
            'primary_practice': self.primary_practice.to_dict(),
            'alternatives': [p.to_dict() for p in self.alternatives],
            'customized_instructions': self.customized_instructions,
            'reasoning': self.reasoning,
            'expected_benefits': self.expected_benefits,
            'preparation_tips': self.preparation_tips,
            'contraindication_warnings': self.contraindication_warnings,
            'confidence': self.confidence
        }
    
    def __repr__(self) -> str:
        return f"PracticeRecommendation(practice={self.primary_practice.name}, confidence={self.confidence:.2f})"


class PracticeAgent(BaseAgent):
    """
    Practice Agent for recommending spiritual practices and techniques.
    
    This agent:
    1. Analyzes user assessment and context
    2. Queries practice database for suitable options
    3. Filters by constraints (time, level, readiness)
    4. Ranks practices by effectiveness
    5. Customizes instructions for user
    6. Provides alternatives
    7. Includes preparation tips and warnings
    
    The agent considers:
    - User's current emotional/mental state
    - Severity and urgency levels
    - Experience level and readiness
    - Time of day and available duration
    - Previous practice history
    - Health contraindications
    - Personal preferences
    
    Features:
        - Comprehensive practice database
        - Multi-criteria filtering
        - Context-aware ranking
        - Customized instructions via LLM
        - Safety considerations
        - Alternative recommendations
        - Detailed reasoning
    """
    
    def __init__(
        self,
        llm_provider: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        verbose: bool = False
    ):
        """
        Initialize the Practice Agent.
        
        Args:
            llm_provider: LLM provider (groq, openai, anthropic)
            model_name: Model name
            temperature: LLM temperature (higher for creative instructions)
            verbose: Enable verbose logging
        """
        super().__init__(
            agent_type=AgentType.PRACTICE,
            name="practice",
            llm_provider=llm_provider,
            model_name=model_name,
            temperature=temperature,
            verbose=verbose
        )
        
        # Practice database (in-memory for now, will connect to vector DB later)
        self.practice_database = self._initialize_practice_database()
        
        # Instruction customization prompt
        self.instruction_prompt = self._create_instruction_prompt()
        
        logger.info("Practice Agent initialized successfully")
        logger.info(f"Practice database loaded: {len(self.practice_database)} practices")
    
    def _initialize_practice_database(self) -> List[Practice]:
        """
        Initialize the practice database with available practices.
        
        This is a curated database of practices from Gurudev's teachings.
        In production, this would be loaded from the knowledge base / vector DB.
        
        Returns:
            List of Practice objects
        """
        practices = []
        
        # Pranayama Practices
        practices.append(Practice(
            practice_id="pranayama_001",
            name="Nadi Shodhana (Alternate Nostril Breathing)",
            practice_type=PracticeType.PRANAYAMA,
            description="A balancing breath technique that calms the mind and nervous system",
            instructions="""1. Sit comfortably with spine straight
2. Use right thumb to close right nostril
3. Inhale slowly through left nostril (count 4)
4. Close left nostril with ring finger
5. Release right nostril, exhale (count 4)
6. Inhale through right nostril (count 4)
7. Close right nostril, exhale through left (count 4)
8. This completes one round
9. Continue for 5-10 rounds
10. Keep breath smooth and steady""",
            duration_minutes=5,
            difficulty=ExperienceLevel.BEGINNER,
            benefits=[
                "Calms anxiety and stress",
                "Balances left and right brain hemispheres",
                "Improves focus and concentration",
                "Reduces racing thoughts"
            ],
            contraindications=[
                "Severe nasal congestion",
                "Active nosebleeds"
            ],
            best_time_of_day=["morning", "evening", "anytime"],
            states_addressed=[EmotionalState.ANXIOUS, EmotionalState.STRESSED, EmotionalState.CONFUSION],
            tags=["breathing", "calming", "balance", "focus"],
            source_reference="Art of Living Pranayama Teachings"
        ))
        
        practices.append(Practice(
            practice_id="pranayama_002",
            name="Ujjayi Breath (Victory Breath)",
            practice_type=PracticeType.PRANAYAMA,
            description="A warming breath that creates internal focus and calms the mind",
            instructions="""1. Sit comfortably with eyes closed
2. Breathe through nose with mouth closed
3. Slightly constrict throat (like whispering)
4. Create soft ocean sound with breath
5. Inhale deeply, feeling throat vibration
6. Exhale slowly with same constriction
7. Continue for 5-10 minutes
8. Keep breath steady and rhythmic""",
            duration_minutes=10,
            difficulty=ExperienceLevel.BEGINNER,
            benefits=[
                "Reduces anxiety and stress",
                "Increases internal awareness",
                "Calms nervous system",
                "Improves concentration"
            ],
            contraindications=[
                "Severe respiratory issues"
            ],
            best_time_of_day=["morning", "evening"],
            states_addressed=[EmotionalState.ANXIOUS, EmotionalState.STRESSED],
            tags=["breathing", "calming", "focus", "grounding"],
            source_reference="Art of Living Pranayama Teachings"
        ))
        
        practices.append(Practice(
            practice_id="pranayama_003",
            name="Bhastrika (Bellows Breath)",
            practice_type=PracticeType.PRANAYAMA,
            description="An energizing breath that releases tension and increases vitality",
            instructions="""1. Sit comfortably with spine straight
2. Take deep breath in, deep breath out
3. Begin rapid, forceful breaths (in-out)
4. Use diaphragm, not shoulders
5. Keep face and shoulders relaxed
6. Do 20-30 rapid breaths (one round)
7. Take deep breath in, hold briefly
8. Exhale slowly and completely
9. Rest for 30 seconds
10. Repeat 2-3 rounds total""",
            duration_minutes=5,
            difficulty=ExperienceLevel.INTERMEDIATE,
            benefits=[
                "Releases tension and stress",
                "Increases energy and vitality",
                "Clears mental fog",
                "Improves lung capacity"
            ],
            contraindications=[
                "High blood pressure",
                "Heart conditions",
                "Pregnancy",
                "Hernia",
                "Recent surgery"
            ],
            best_time_of_day=["morning"],
            states_addressed=[EmotionalState.STRESSED, EmotionalState.SAD],
            tags=["breathing", "energizing", "releasing", "cleansing"],
            source_reference="Art of Living Pranayama Teachings"
        ))
        
        # Meditation Practices
        practices.append(Practice(
            practice_id="meditation_001",
            name="Body Scan Meditation",
            practice_type=PracticeType.MEDITATION,
            description="A relaxation meditation that releases physical and mental tension",
            instructions="""1. Lie down or sit comfortably
2. Close eyes, take 3 deep breaths
3. Bring awareness to top of head
4. Notice any sensations, tension
5. Mentally relax that area
6. Slowly move attention down body:
   - Face, jaw, neck
   - Shoulders, arms, hands
   - Chest, belly, back
   - Hips, legs, feet
7. Spend 30 seconds on each area
8. Release tension with each breath
9. End with full body awareness
10. Rest for 2-3 minutes""",
            duration_minutes=15,
            difficulty=ExperienceLevel.BEGINNER,
            benefits=[
                "Deep physical relaxation",
                "Reduces stress and anxiety",
                "Improves body awareness",
                "Better sleep quality"
            ],
            contraindications=[],
            best_time_of_day=["evening", "night", "anytime"],
            states_addressed=[EmotionalState.STRESSED, EmotionalState.ANXIOUS],
            tags=["meditation", "relaxation", "body-awareness", "sleep"],
            source_reference="Art of Living Meditation Practices"
        ))
        
        practices.append(Practice(
            practice_id="meditation_002",
            name="Breath Awareness Meditation",
            practice_type=PracticeType.MEDITATION,
            description="Simple meditation focusing on natural breath rhythm",
            instructions="""1. Sit comfortably with spine straight
2. Close eyes gently
3. Take 3 deep, slow breaths
4. Let breath return to natural rhythm
5. Observe breath without changing it
6. Notice: inhale, pause, exhale, pause
7. If mind wanders, gently return to breath
8. No judgment, just observation
9. Continue for 10-20 minutes
10. Slowly open eyes when ready""",
            duration_minutes=15,
            difficulty=ExperienceLevel.BEGINNER,
            benefits=[
                "Calms racing thoughts",
                "Reduces anxiety",
                "Improves focus",
                "Increases present-moment awareness"
            ],
            contraindications=[],
            best_time_of_day=["morning", "afternoon", "evening", "anytime"],
            states_addressed=[EmotionalState.ANXIOUS, EmotionalState.STRESSED, EmotionalState.CONFUSION],
            tags=["meditation", "mindfulness", "calming", "beginner-friendly"],
            source_reference="Art of Living Meditation Practices"
        ))
        
        practices.append(Practice(
            practice_id="meditation_003",
            name="Loving-Kindness Meditation (Metta)",
            practice_type=PracticeType.MEDITATION,
            description="Cultivation of compassion and loving-kindness towards self and others",
            instructions="""1. Sit comfortably with eyes closed
2. Take few deep, calming breaths
3. Bring yourself to mind with warmth
4. Silently repeat: "May I be happy, may I be healthy, may I be at peace"
5. Feel genuine care for yourself (2 minutes)
6. Bring loved one to mind
7. Repeat: "May you be happy, may you be healthy, may you be at peace"
8. Feel love and care (2 minutes)
9. Extend to neutral person, then difficult person
10. Finally, extend to all beings everywhere
11. Rest in feeling of universal love""",
            duration_minutes=15,
            difficulty=ExperienceLevel.INTERMEDIATE,
            benefits=[
                "Reduces anger and resentment",
                "Increases compassion and empathy",
                "Improves relationships",
                "Reduces depression and sadness",
                "Increases positive emotions"
            ],
            contraindications=[],
            best_time_of_day=["morning", "evening"],
            states_addressed=[EmotionalState.SAD, EmotionalState.CONFUSION, EmotionalState.SEEKING],
            tags=["meditation", "compassion", "love", "healing", "relationships"],
            source_reference="Buddhist Meditation adapted for Art of Living"
        ))
        
        # Contemplation Practices
        practices.append(Practice(
            practice_id="contemplation_001",
            name="Self-Inquiry Meditation",
            practice_type=PracticeType.CONTEMPLATION,
            description="Guided reflection to gain clarity and insight",
            instructions="""1. Sit quietly in contemplative space
2. Close eyes, take calming breaths
3. Ask yourself gently: "Who am I?"
4. Don't answer with thoughts
5. Feel into the question
6. Notice the awareness behind thoughts
7. Rest in that observing presence
8. If thoughts arise, return to inquiry
9. Sit with question for 10-15 minutes
10. Notice any insights without grasping""",
            duration_minutes=15,
            difficulty=ExperienceLevel.ADVANCED,
            benefits=[
                "Deep self-understanding",
                "Clarity on life direction",
                "Reduced identification with thoughts",
                "Increased wisdom"
            ],
            contraindications=[
                "Severe mental health crisis (need professional support first)"
            ],
            best_time_of_day=["morning", "evening"],
            states_addressed=[EmotionalState.CONFUSION, EmotionalState.SEEKING],
            tags=["contemplation", "self-inquiry", "wisdom", "clarity"],
            source_reference="Vedantic Teachings - Gurudev's Wisdom"
        ))
        
        # Movement Practices
        practices.append(Practice(
            practice_id="movement_001",
            name="Gentle Yoga Flow",
            practice_type=PracticeType.MOVEMENT,
            description="Simple yoga sequence to release physical and mental tension",
            instructions="""1. Start in standing position
2. Raise arms overhead, stretch up
3. Forward fold, hang loose
4. Slow roll up to standing
5. Side stretches (left and right)
6. Gentle twists (both sides)
7. Cat-cow stretches (on hands and knees)
8. Child's pose rest
9. Gentle hip openers
10. Final resting pose (5 minutes)
Move slowly, breathe deeply throughout""",
            duration_minutes=20,
            difficulty=ExperienceLevel.BEGINNER,
            benefits=[
                "Releases physical tension",
                "Calms nervous system",
                "Improves flexibility",
                "Reduces stress"
            ],
            contraindications=[
                "Recent injury (consult doctor)",
                "Severe pain (stop and rest)"
            ],
            best_time_of_day=["morning", "afternoon"],
            states_addressed=[EmotionalState.STRESSED, EmotionalState.ANXIOUS],
            tags=["yoga", "movement", "stretching", "physical-release"],
            source_reference="Art of Living Yoga Practices"
        ))
        
        # Simple calming practice
        practices.append(Practice(
            practice_id="simple_001",
            name="Three-Minute Breathing Space",
            practice_type=PracticeType.PRANAYAMA,
            description="Quick practice for immediate calm and centering",
            instructions="""MINUTE 1: Awareness
- Notice your current experience
- What thoughts, feelings, sensations?
- Just observe, don't judge

MINUTE 2: Focus on Breath
- Bring attention to breathing
- Feel the breath at nostrils or belly
- Notice each inhale and exhale

MINUTE 3: Expand Awareness
- Expand awareness to whole body
- Feel yourself breathing
- Sense body as breathing space
- Notice increased calm""",
            duration_minutes=3,
            difficulty=ExperienceLevel.BEGINNER,
            benefits=[
                "Quick stress relief",
                "Immediate grounding",
                "Breaks negative thought cycles",
                "Can be done anywhere"
            ],
            contraindications=[],
            best_time_of_day=["morning", "afternoon", "evening", "anytime"],
            states_addressed=[EmotionalState.ANXIOUS, EmotionalState.STRESSED],
            tags=["breathing", "quick", "emergency", "grounding"],
            source_reference="Mindfulness-Based Stress Reduction"
        ))
        
        return practices
    
    def _create_instruction_prompt(self) -> PromptTemplate:
        """
        Create prompt template for customizing practice instructions.
        
        This prompt helps the LLM tailor instructions to the user's
        specific needs and context.
        
        Returns:
            PromptTemplate for instruction customization
        """
        template = """You are a compassionate spiritual practice guide helping someone learn a technique.

**User Context:**
- Name: {user_name}
- Age: {user_age}
- Experience Level: {experience_level}
- Current State: {current_state}
- Readiness: {readiness}

**Practice to Teach:**
Name: {practice_name}
Type: {practice_type}
Standard Instructions:
{standard_instructions}

**Assessment Context:**
{assessment_summary}

**Your Task:**
Customize the practice instructions for this specific user. Make the instructions:
1. **Personalized**: Address them by name, acknowledge their state
2. **Appropriate**: Match their experience level
3. **Encouraging**: Supportive and motivating tone
4. **Clear**: Simple, step-by-step guidance
5. **Safe**: Include relevant modifications or cautions

**Guidelines:**
- Keep the core technique intact
- Add personal touches and encouragement
- Suggest modifications if needed for their level
- Address any hesitation based on readiness
- Use warm, compassionate language
- Keep instructions practical and doable

**Format:**
Provide customized instructions in a clear, easy-to-follow format.
Start with a brief personalized introduction, then give the step-by-step instructions.

Customized Instructions:"""
        
        return PromptTemplate(
            template=template,
            input_variables=[
                "user_name",
                "user_age",
                "experience_level",
                "current_state",
                "readiness",
                "practice_name",
                "practice_type",
                "standard_instructions",
                "assessment_summary"
            ]
        )
    
    def define_tools(self) -> List:
        """
        Define tools for the practice agent.
        
        Practice agent uses internal database and LLM customization.
        
        Returns:
            List of Tool objects (empty for now)
        """
        return []
    
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for the practice agent.
        
        Returns:
            System prompt string
        """
        return """You are the Practice Agent for the JAI GURU DEV AI Companion chatbot.

Your sacred responsibility is to recommend and guide spiritual practices that genuinely help users on their wellness journey.

## Your Capabilities:

1. **Practice Recommendation**: Select most appropriate practice from knowledge base
2. **Constraint Filtering**: Consider time, level, readiness, health
3. **Effectiveness Ranking**: Prioritize what will help most
4. **Instruction Customization**: Tailor guidance to individual
5. **Alternative Suggestions**: Provide backup options
6. **Safety Considerations**: Warn about contraindications

## Core Principles:

**User-Centered Approach**:
- Match practices to actual capability (not ideal)
- Consider emotional state and readiness
- Provide realistic duration and difficulty
- Honor where they are right now

**Safety First**:
- Check contraindications
- Provide modifications when needed
- Start simple, build gradually
- Never push beyond capacity

**Practical Wisdom**:
- Simple is often better than complex
- Short daily practice beats long occasional
- What they'll actually do > theoretically perfect
- Meet them where they are

**Encouragement & Support**:
- Acknowledge their state with compassion
- Build confidence through small wins
- Celebrate willingness to try
- Be patient with learning process

## Recommendation Framework:

**Step 1: Analyze Assessment**
- What is primary state?
- What is severity/urgency?
- What is readiness level?
- What interventions recommended?

**Step 2: Filter Practice Database**
- Match to recommended intervention types
- Filter by experience level
- Consider time constraints
- Check contraindications

**Step 3: Rank Options**
- Effectiveness for this state
- Match to user history
- Time of day optimization
- Success probability

**Step 4: Select & Customize**
- Choose best fit
- Customize instructions for user
- Prepare alternatives
- Add relevant tips

**Step 5: Present Recommendation**
- Clear rationale
- Personalized instructions
- Expected benefits
- Preparation tips
- Alternatives if needed

## Quality Indicators:

- Practice truly matches need
- Instructions are clear and doable
- User feels supported and capable
- Safety considerations addressed
- Realistic about commitment
- Provides alternatives

Remember: The best practice is the one they'll actually do. Better a simple 3-minute breathing exercise completed than a perfect 30-minute meditation skipped."""
    
    def process(
        self,
        input_text: str,
        context: AgentContext,
        chat_history: Optional[List[BaseMessage]] = None
    ) -> AgentResponse:
        """
        Process practice recommendation request.
        
        Main method that:
        1. Extracts assessment from context
        2. Identifies user constraints
        3. Filters practice database
        4. Ranks practices by effectiveness
        5. Selects best practice
        6. Customizes instructions via LLM
        7. Prepares alternatives
        8. Returns comprehensive recommendation
        
        Args:
            input_text: Request for practice (usually from orchestrator)
            context: User context with assessment
            chat_history: Conversation history
        
        Returns:
            AgentResponse with practice recommendation
        """
        start_time = datetime.now()
        
        try:
            logger.info("Practice Agent generating recommendation...")
            
            # Step 1: Extract assessment from context
            assessment = self._extract_assessment(context)
            if not assessment:
                logger.warning("No assessment found in context")
                return self._fallback_recommendation(context)
            
            # Step 2: Identify user constraints
            constraints = self._identify_constraints(context, assessment)
            
            # Step 3: Filter practice database
            suitable_practices = self._filter_practices(
                assessment=assessment,
                constraints=constraints
            )
            
            if not suitable_practices:
                logger.warning("No suitable practices found after filtering")
                return self._fallback_recommendation(context)
            
            # Step 4: Rank practices by effectiveness
            ranked_practices = self._rank_practices(
                practices=suitable_practices,
                assessment=assessment,
                context=context
            )
            
            # Step 5: Select primary and alternatives
            primary_practice = ranked_practices[0]
            alternatives = ranked_practices[1:3] if len(ranked_practices) > 1 else []
            
            # Step 6: Customize instructions via LLM
            customized_instructions = self._customize_instructions(
                practice=primary_practice,
                context=context,
                assessment=assessment
            )
            
            # Step 7: Prepare recommendation
            recommendation = self._prepare_recommendation(
                primary_practice=primary_practice,
                alternatives=alternatives,
                customized_instructions=customized_instructions,
                assessment=assessment,
                context=context
            )
            
            # Step 8: Format response
            response_content = self._format_recommendation_response(recommendation)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Create response
            response = AgentResponse(
                agent_name=self.name,
                content=response_content,
                confidence=recommendation.confidence,
                metadata={
                    'recommendation': recommendation.to_dict(),
                    'practices_considered': len(suitable_practices),
                    'filtering_applied': constraints
                },
                tools_used=['practice_database', 'llm_customization', 'ranking_algorithm'],
                processing_time=processing_time,
                success=True
            )
            
            logger.info(
                f"Practice recommendation completed: {primary_practice.name}, "
                f"confidence={recommendation.confidence:.2f}"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Practice Agent error: {e}", exc_info=True)
            return self.handle_error(e, context)
    
    def _extract_assessment(self, context: AgentContext) -> Optional[Dict[str, Any]]:
        """
        Extract assessment data from context.
        
        Args:
            context: Agent context
        
        Returns:
            Assessment dictionary or None
        """
        return context.metadata.get('assessment', None)
    
    def _identify_constraints(
        self,
        context: AgentContext,
        assessment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Identify user constraints for practice selection.
        
        Considers:
        - Available time
        - Experience level
        - Readiness
        - Health contraindications
        - Time of day
        - Location/privacy
        
        Args:
            context: User context
            assessment: Assessment data
        
        Returns:
            Dictionary of constraints
        """
        profile = context.user_profile
        
        # Get time of day
        current_hour = datetime.now().hour
        if 5 <= current_hour < 12:
            time_of_day = "morning"
        elif 12 <= current_hour < 17:
            time_of_day = "afternoon"
        elif 17 <= current_hour < 21:
            time_of_day = "evening"
        else:
            time_of_day = "night"
        
        # Get experience level
        experience_level = profile.get('experience_level', 'beginner')
        
        # Get readiness
        readiness = assessment.get('readiness', 'ready')
        
        # Get available time (default to moderate if not specified)
        available_minutes = profile.get('available_time_minutes', 15)
        
        # Get health contraindications
        health_issues = profile.get('health_issues', [])
        if not isinstance(health_issues, list):
            health_issues = []
        
        # Get severity (affects practice intensity)
        severity = assessment.get('severity', 'medium')
        
        constraints = {
            'time_of_day': time_of_day,
            'experience_level': experience_level,
            'readiness': readiness,
            'available_minutes': available_minutes,
            'health_contraindications': health_issues,
            'severity': severity,
            'max_difficulty': self._get_max_difficulty(experience_level),
            'urgency': assessment.get('urgency_level', 5)
        }
        
        logger.info(f"Identified constraints: {constraints}")
        return constraints
    
    def _get_max_difficulty(self, experience_level: str) -> ExperienceLevel:
        """
        Get maximum practice difficulty for experience level.
        
        Args:
            experience_level: User's experience level
        
        Returns:
            Maximum difficulty level
        """
        level_map = {
            'beginner': ExperienceLevel.BEGINNER,
            'intermediate': ExperienceLevel.INTERMEDIATE,
            'advanced': ExperienceLevel.ADVANCED
        }
        return level_map.get(experience_level, ExperienceLevel.BEGINNER)
    
    def _filter_practices(
        self,
        assessment: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> List[Practice]:
        """
        Filter practice database by constraints.
        
        Args:
            assessment: Assessment data
            constraints: User constraints
        
        Returns:
            List of suitable practices
        """
        suitable = []
        
        primary_state = assessment.get('primary_state', 'unknown')
        try:
            primary_state_enum = EmotionalState(primary_state)
        except:
            primary_state_enum = EmotionalState.UNKNOWN
        
        recommended_interventions = assessment.get('recommended_interventions', [])
        try:
            intervention_enums = [PracticeType(i) for i in recommended_interventions]
        except:
            intervention_enums = [PracticeType.MEDITATION]
        
        max_difficulty = constraints['max_difficulty']
        available_minutes = constraints['available_minutes']
        time_of_day = constraints['time_of_day']
        health_issues = constraints['health_contraindications']
        
        for practice in self.practice_database:
            # Filter 1: Check if practice type matches recommended interventions
            if practice.practice_type not in intervention_enums:
                continue
            
            # Filter 2: Check difficulty level
            difficulty_order = {
                ExperienceLevel.BEGINNER: 1,
                ExperienceLevel.INTERMEDIATE: 2,
                ExperienceLevel.ADVANCED: 3
            }
            if difficulty_order[practice.difficulty] > difficulty_order[max_difficulty]:
                continue
            
            # Filter 3: Check duration
            if practice.duration_minutes > available_minutes + 5:  # Allow 5 min buffer
                continue
            
            # Filter 4: Check if addresses user's state
            if primary_state_enum != EmotionalState.UNKNOWN:
                if primary_state_enum not in practice.states_addressed:
                    # Still include if it's a general calming practice
                    if not any(s in [EmotionalState.CALM, EmotionalState.NEUTRAL] 
                              for s in practice.states_addressed):
                        continue
            
            # Filter 5: Check time of day (not strict, just preference)
            # We don't filter out, just note for ranking
            
            # Filter 6: Check contraindications
            has_contraindication = False
            for issue in health_issues:
                if any(issue.lower() in c.lower() for c in practice.contraindications):
                    has_contraindication = True
                    break
            if has_contraindication:
                continue
            
            # Practice passed all filters
            suitable.append(practice)
        
        logger.info(f"Filtered to {len(suitable)} suitable practices")
        return suitable
    
    def _rank_practices(
        self,
        practices: List[Practice],
        assessment: Dict[str, Any],
        context: AgentContext
    ) -> List[Practice]:
        """
        Rank practices by effectiveness for this user.
        
        Scoring criteria:
        - State match (40%)
        - Time of day fit (20%)
        - Experience level match (15%)
        - Previous success with similar (15%)
        - Urgency appropriateness (10%)
        
        Args:
            practices: List of practices to rank
            assessment: Assessment data
            context: User context
        
        Returns:
            Ranked list of practices (best first)
        """
        primary_state = assessment.get('primary_state', 'unknown')
        try:
            primary_state_enum = EmotionalState(primary_state)
        except:
            primary_state_enum = EmotionalState.UNKNOWN
        
        current_hour = datetime.now().hour
        if 5 <= current_hour < 12:
            time_of_day = "morning"
        elif 12 <= current_hour < 17:
            time_of_day = "afternoon"
        elif 17 <= current_hour < 21:
            time_of_day = "evening"
        else:
            time_of_day = "night"
        
        experience_level = context.user_profile.get('experience_level', 'beginner')
        
        # Get practice history
        practice_history = context.metadata.get('practice_history', [])
        
        urgency = assessment.get('urgency_level', 5)
        
        # Score each practice
        for practice in practices:
            score = 0.0
            
            # 1. State match (40 points max)
            if primary_state_enum in practice.states_addressed:
                score += 40
            elif EmotionalState.CALM in practice.states_addressed:
                score += 20  # General calming practices get partial credit
            
            # 2. Time of day fit (20 points max)
            if time_of_day in practice.best_time_of_day or "anytime" in practice.best_time_of_day:
                score += 20
            elif len(practice.best_time_of_day) > 2:  # Flexible practices
                score += 10
            
            # 3. Experience level match (15 points max)
            if practice.difficulty.value == experience_level:
                score += 15
            elif practice.difficulty == ExperienceLevel.BEGINNER:
                score += 10  # Beginner practices always acceptable
            
            # 4. Previous success (15 points max)
            similar_practices = [
                p for p in practice_history 
                if p.get('practice_type') == practice.practice_type.value
                and p.get('rating', 0) >= 4
            ]
            if len(similar_practices) > 0:
                score += min(15, len(similar_practices) * 5)
            
            # 5. Urgency appropriateness (10 points max)
            if urgency >= 7:  # High urgency - prefer quick practices
                if practice.duration_minutes <= 10:
                    score += 10
                elif practice.duration_minutes <= 15:
                    score += 5
            else:  # Normal urgency - any duration fine
                score += 7
            
            practice.effectiveness_score = score
        
        # Sort by score (descending)
        ranked = sorted(practices, key=lambda p: p.effectiveness_score, reverse=True)
        
        logger.info(
            f"Ranked practices: {[(p.name, p.effectiveness_score) for p in ranked[:3]]}"
        )
        
        return ranked
    
    def _customize_instructions(
        self,
        practice: Practice,
        context: AgentContext,
        assessment: Dict[str, Any]
    ) -> str:
        """
        Customize practice instructions via LLM.
        
        Args:
            practice: Practice to customize
            context: User context
            assessment: Assessment data
        
        Returns:
            Customized instruction text
        """
        try:
            profile = context.user_profile
            
            # Prepare assessment summary
            assessment_summary = f"""Current State: {assessment.get('primary_state', 'unknown')}
Severity: {assessment.get('severity', 'medium')}
Readiness: {assessment.get('readiness', 'ready')}
Underlying Needs: {', '.join(assessment.get('underlying_needs', []))}
Reasoning: {assessment.get('reasoning', '')}"""
            
            # Format prompt
            prompt_input = {
                'user_name': profile.get('name', 'friend'),
                'user_age': profile.get('age', 'unknown'),
                'experience_level': profile.get('experience_level', 'beginner'),
                'current_state': assessment.get('primary_state', 'unknown'),
                'readiness': assessment.get('readiness', 'ready'),
                'practice_name': practice.name,
                'practice_type': practice.practice_type.value,
                'standard_instructions': practice.instructions,
                'assessment_summary': assessment_summary
            }
            
            formatted_prompt = self.instruction_prompt.format(**prompt_input)
            
            # Invoke LLM
            response = self.llm.invoke(formatted_prompt)
            customized = response.content.strip()
            
            return customized
            
        except Exception as e:
            logger.error(f"Instruction customization failed: {e}")
            # Fallback to standard instructions with simple personalization
            user_name = context.user_profile.get('name', 'friend')
            return f"Dear {user_name},\n\n{practice.instructions}"
    
    def _prepare_recommendation(
        self,
        primary_practice: Practice,
        alternatives: List[Practice],
        customized_instructions: str,
        assessment: Dict[str, Any],
        context: AgentContext
    ) -> PracticeRecommendation:
        """
        Prepare comprehensive practice recommendation.
        
        Args:
            primary_practice: Primary recommended practice
            alternatives: Alternative practices
            customized_instructions: Customized instructions
            assessment: Assessment data
            context: User context
        
        Returns:
            PracticeRecommendation object
        """
        # Generate reasoning
        reasoning = self._generate_reasoning(
            primary_practice,
            assessment,
            context
        )
        
        # Expected benefits
        expected_benefits = primary_practice.benefits.copy()
        
        # Preparation tips
        preparation_tips = self._generate_preparation_tips(
            primary_practice,
            assessment
        )
        
        # Contraindication warnings
        warnings = []
        if primary_practice.contraindications:
            warnings = [
                f"⚠️ Please note: {c}" 
                for c in primary_practice.contraindications
            ]
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            primary_practice,
            assessment,
            context
        )
        
        return PracticeRecommendation(
            primary_practice=primary_practice,
            alternatives=alternatives,
            customized_instructions=customized_instructions,
            reasoning=reasoning,
            expected_benefits=expected_benefits,
            preparation_tips=preparation_tips,
            contraindication_warnings=warnings,
            confidence=confidence
        )
    
    def _generate_reasoning(
        self,
        practice: Practice,
        assessment: Dict[str, Any],
        context: AgentContext
    ) -> str:
        """
        Generate explanation for why this practice was recommended.
        
        Args:
            practice: Recommended practice
            assessment: Assessment data
            context: User context
        
        Returns:
            Reasoning text
        """
        state = assessment.get('primary_state', 'your current state')
        severity = assessment.get('severity', 'medium')
        
        reasoning = f"I'm recommending {practice.name} because:\n\n"
        reasoning += f"1. **State Match**: This practice is particularly effective for {state}"
        
        if severity in ['high', 'critical']:
            reasoning += f", especially when intensity is {severity}"
        
        reasoning += ".\n\n"
        reasoning += f"2. **Experience Level**: This is suitable for your {context.user_profile.get('experience_level', 'beginner')} level.\n\n"
        reasoning += f"3. **Duration**: At {practice.duration_minutes} minutes, it fits your available time.\n\n"
        reasoning += f"4. **Proven Benefits**: This practice is known to help with "
        reasoning += f"{', '.join(practice.benefits[:2])}."
        
        return reasoning
    
    def _generate_preparation_tips(
        self,
        practice: Practice,
        assessment: Dict[str, Any]
    ) -> List[str]:
        """
        Generate preparation tips for the practice.
        
        Args:
            practice: Practice to prepare for
            assessment: Assessment data
        
        Returns:
            List of preparation tips
        """
        tips = []
        
        # General tips
        tips.append("Find a quiet, comfortable space where you won't be disturbed")
        
        # Based on practice type
        if practice.practice_type == PracticeType.PRANAYAMA:
            tips.append("Sit with spine straight but comfortable")
            tips.append("Empty stomach is best (or 2 hours after eating)")
        elif practice.practice_type == PracticeType.MEDITATION:
            tips.append("You can sit on a chair or cushion, whatever feels comfortable")
            tips.append("Set a gentle timer if you'd like")
        elif practice.practice_type == PracticeType.MOVEMENT:
            tips.append("Wear comfortable, loose clothing")
            tips.append("Use a yoga mat or soft surface")
        
        # Based on readiness
        readiness = assessment.get('readiness', 'ready')
        if readiness == 'needs_preparation':
            tips.append("Take a few deep breaths before starting to center yourself")
        elif readiness == 'not_ready':
            tips.append("It's okay if this feels difficult - start with just 2-3 minutes")
            tips.append("Be gentle with yourself, any effort is valuable")
        
        # Based on severity
        severity = assessment.get('severity', 'medium')
        if severity in ['high', 'critical']:
            tips.append("Go slowly and be very gentle with yourself")
            tips.append("If emotions arise, that's okay - let them flow")
        
        return tips
    
    def _calculate_confidence(
        self,
        practice: Practice,
        assessment: Dict[str, Any],
        context: AgentContext
    ) -> float:
        """
        Calculate confidence in recommendation.
        
        Based on:
        - Effectiveness score
        - Assessment confidence
        - State match clarity
        
        Args:
            practice: Recommended practice
            assessment: Assessment data
            context: User context
        
        Returns:
            Confidence score (0-1)
        """
        # Start with effectiveness score (0-100) normalized
        base_confidence = practice.effectiveness_score / 100.0
        
        # Factor in assessment confidence
        assessment_confidence = assessment.get('confidence', 0.7)
        
        # Combined confidence (weighted average)
        confidence = (base_confidence * 0.6) + (assessment_confidence * 0.4)
        
        # Clamp to reasonable range
        return max(0.5, min(0.95, confidence))
    
    def _format_recommendation_response(
        self,
        recommendation: PracticeRecommendation
    ) -> str:
        """
        Format recommendation as readable response.
        
        Args:
            recommendation: Recommendation to format
        
        Returns:
            Formatted response string
        """
        practice = recommendation.primary_practice
        
        response = f"""## 🌟 Recommended Practice: {practice.name}

**Type:** {practice.practice_type.value.title()}
**Duration:** {practice.duration_minutes} minutes
**Level:** {practice.difficulty.value.title()}

### Why This Practice?

{recommendation.reasoning}

### Preparation Tips

"""
        for i, tip in enumerate(recommendation.preparation_tips, 1):
            response += f"{i}. {tip}\n"
        
        response += f"\n### How to Practice\n\n{recommendation.customized_instructions}\n"
        
        if recommendation.contraindication_warnings:
            response += "\n### Important Safety Notes\n\n"
            for warning in recommendation.contraindication_warnings:
                response += f"{warning}\n"
        
        response += f"\n### Expected Benefits\n\n"
        for benefit in recommendation.expected_benefits:
            response += f"• {benefit}\n"
        
        if recommendation.alternatives:
            response += "\n### Alternative Practices\n\n"
            response += "If this doesn't feel right, you can also try:\n\n"
            for i, alt in enumerate(recommendation.alternatives, 1):
                response += f"{i}. **{alt.name}** ({alt.duration_minutes} min) - {alt.description}\n"
        
        response += f"\n---\n*Recommendation Confidence: {recommendation.confidence:.0%}*"
        
        return response
    
    def _fallback_recommendation(self, context: AgentContext) -> AgentResponse:
        """
        Provide fallback recommendation when normal process fails.
        
        Args:
            context: User context
        
        Returns:
            AgentResponse with simple recommendation
        """
        # Default to simple breath awareness
        fallback_practice = None
        for practice in self.practice_database:
            if practice.practice_id == "meditation_002":  # Breath Awareness
                fallback_practice = practice
                break
        
        if not fallback_practice:
            fallback_practice = self.practice_database[0]  # First practice
        
        user_name = context.user_profile.get('name', 'friend')
        
        recommendation = PracticeRecommendation(
            primary_practice=fallback_practice,
            alternatives=[],
            customized_instructions=f"Dear {user_name},\n\n{fallback_practice.instructions}",
            reasoning="This is a gentle, universal practice suitable for most situations.",
            expected_benefits=fallback_practice.benefits,
            preparation_tips=[
                "Find a quiet space",
                "Sit comfortably",
                "Be patient with yourself"
            ],
            contraindication_warnings=[],
            confidence=0.6
        )
        
        response_content = self._format_recommendation_response(recommendation)
        
        return AgentResponse(
            agent_name=self.name,
            content=response_content,
            confidence=0.6,
            metadata={'recommendation': recommendation.to_dict(), 'fallback': True},
            tools_used=['fallback_database'],
            processing_time=0.1,
            success=True
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
        
        return f"""I'm having difficulty generating a specific practice recommendation right now, {user_name}.

However, here's a simple practice that's always helpful:

**Three-Minute Breathing Space**

1. Find a quiet moment
2. Close your eyes gently
3. Take three slow, deep breaths
4. Notice how you feel
5. Rest in the present moment

This simple practice can bring immediate calm and centering.

Would you like me to suggest something more specific? Feel free to share more about what you're looking for. 🙏"""


# Example usage and testing
if __name__ == "__main__":
    from dotenv import load_dotenv
    import uuid
    
    load_dotenv()
    
    print("=" * 60)
    print("Practice Agent Test")
    print("=" * 60)
    
    try:
        # Create practice agent
        practice_agent = PracticeAgent(verbose=True)
        
        # Test context with assessment
        context = AgentContext(
            user_id=str(uuid.uuid4()),
            session_id=str(uuid.uuid4()),
            user_profile={
                'name': 'Sarah',
                'age': 32,
                'experience_level': 'beginner',
                'available_time_minutes': 15
            },
            conversation_history=[],
            metadata={
                'assessment': {
                    'primary_state': 'anxious',
                    'secondary_states': ['stressed'],
                    'severity': 'high',
                    'physical_indicators': ['tension', 'racing heart'],
                    'readiness': 'ready',
                    'recommended_interventions': ['pranayama', 'meditation'],
                    'underlying_needs': ['calm', 'peace'],
                    'urgency_level': 7,
                    'confidence': 0.85,
                    'reasoning': 'User experiencing anxiety with high urgency'
                }
            }
        )
        
        # Test recommendation
        response = practice_agent.process(
            "Please recommend a practice",
            context
        )
        
        print(f"\nConfidence: {response.confidence:.2f}")
        print(f"Processing Time: {response.processing_time:.2f}s")
        print(f"\nRecommendation:\n{response.content}")
        
        print("\n" + "=" * 60)
        print("✅ Practice Agent Test Complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
