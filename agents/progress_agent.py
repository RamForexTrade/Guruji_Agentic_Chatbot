"""
Progress Agent
==============

Specialized agent for tracking and monitoring user progress.

Responsibilities:
    - Log practice completions
    - Record user feedback and ratings
    - Track adherence patterns
    - Calculate statistics and metrics
    - Identify obstacles and challenges
    - Analyze improvement trends
    - Generate progress insights
    - Provide motivational messages
    - Update user profile with progress data

Architecture:
    Practice Completion + Feedback → Progress Agent
                                          ↓
                                    Validation
                                          ↓
                                    Database Logging
                                          ↓
                                  Statistics Update
                                          ↓
                                  Pattern Analysis
                                          ↓
                                  Insight Generation
                                          ↓
                              Progress Response (JSON)
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import logging

from langchain_core.prompts import PromptTemplate
from langchain_core.messages import BaseMessage

from agents.base_agent import BaseAgent, AgentContext, AgentResponse
from agents.agent_types import (
    AgentType,
    PracticeType,
    EmotionalState
)

logger = logging.getLogger(__name__)


class PracticeLog:
    """
    Data class representing a single practice log entry.
    
    Records all information about a practice completion.
    """
    
    def __init__(
        self,
        log_id: str,
        user_id: str,
        practice_id: str,
        practice_name: str,
        practice_type: PracticeType,
        duration_minutes: int,
        completed: bool,
        completion_datetime: datetime,
        feedback: str = "",
        rating: Optional[int] = None,
        state_before: Optional[EmotionalState] = None,
        state_after: Optional[EmotionalState] = None,
        challenges: List[str] = None,
        benefits_experienced: List[str] = None,
        notes: str = ""
    ):
        self.log_id = log_id
        self.user_id = user_id
        self.practice_id = practice_id
        self.practice_name = practice_name
        self.practice_type = practice_type
        self.duration_minutes = duration_minutes
        self.completed = completed
        self.completion_datetime = completion_datetime
        self.feedback = feedback
        self.rating = rating  # 1-5 scale
        self.state_before = state_before
        self.state_after = state_after
        self.challenges = challenges or []
        self.benefits_experienced = benefits_experienced or []
        self.notes = notes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert log to dictionary"""
        return {
            'log_id': self.log_id,
            'user_id': self.user_id,
            'practice_id': self.practice_id,
            'practice_name': self.practice_name,
            'practice_type': self.practice_type.value if isinstance(self.practice_type, PracticeType) else self.practice_type,
            'duration_minutes': self.duration_minutes,
            'completed': self.completed,
            'completion_datetime': self.completion_datetime.isoformat(),
            'feedback': self.feedback,
            'rating': self.rating,
            'state_before': self.state_before.value if self.state_before else None,
            'state_after': self.state_after.value if self.state_after else None,
            'challenges': self.challenges,
            'benefits_experienced': self.benefits_experienced,
            'notes': self.notes
        }
    
    def __repr__(self) -> str:
        return f"PracticeLog(practice={self.practice_name}, completed={self.completed}, rating={self.rating})"


class ProgressStatistics:
    """
    Data class containing user progress statistics.
    
    Aggregates metrics about practice adherence and patterns.
    """
    
    def __init__(
        self,
        total_practices: int,
        completed_practices: int,
        adherence_rate: float,
        current_streak: int,
        longest_streak: int,
        practices_by_type: Dict[str, int],
        average_rating: float,
        average_duration: float,
        most_practiced: str,
        recent_trend: str,
        total_minutes: int
    ):
        self.total_practices = total_practices
        self.completed_practices = completed_practices
        self.adherence_rate = adherence_rate
        self.current_streak = current_streak
        self.longest_streak = longest_streak
        self.practices_by_type = practices_by_type
        self.average_rating = average_rating
        self.average_duration = average_duration
        self.most_practiced = most_practiced
        self.recent_trend = recent_trend
        self.total_minutes = total_minutes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert statistics to dictionary"""
        return {
            'total_practices': self.total_practices,
            'completed_practices': self.completed_practices,
            'adherence_rate': self.adherence_rate,
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'practices_by_type': self.practices_by_type,
            'average_rating': self.average_rating,
            'average_duration': self.average_duration,
            'most_practiced': self.most_practiced,
            'recent_trend': self.recent_trend,
            'total_minutes': self.total_minutes
        }
    
    def __repr__(self) -> str:
        return f"ProgressStatistics(completed={self.completed_practices}, adherence={self.adherence_rate:.1%}, streak={self.current_streak})"


class ProgressInsight:
    """
    Data class containing progress insights and analysis.
    
    Provides meaningful interpretation of progress data.
    """
    
    def __init__(
        self,
        key_achievements: List[str],
        areas_for_growth: List[str],
        patterns_observed: List[str],
        motivational_message: str,
        recommendations: List[str],
        confidence: float
    ):
        self.key_achievements = key_achievements
        self.areas_for_growth = areas_for_growth
        self.patterns_observed = patterns_observed
        self.motivational_message = motivational_message
        self.recommendations = recommendations
        self.confidence = confidence
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert insight to dictionary"""
        return {
            'key_achievements': self.key_achievements,
            'areas_for_growth': self.areas_for_growth,
            'patterns_observed': self.patterns_observed,
            'motivational_message': self.motivational_message,
            'recommendations': self.recommendations,
            'confidence': self.confidence
        }
    
    def __repr__(self) -> str:
        return f"ProgressInsight(achievements={len(self.key_achievements)}, confidence={self.confidence:.2f})"


class ProgressAgent(BaseAgent):
    """
    Progress Agent for tracking and analyzing user practice progress.
    
    This agent:
    1. Logs practice completions with full details
    2. Records user feedback and ratings
    3. Calculates adherence and statistics
    4. Analyzes patterns and trends
    5. Identifies obstacles and challenges
    6. Generates insights and recommendations
    7. Provides motivational messages
    8. Updates user profile with progress data
    
    The agent tracks:
    - Practice completion status
    - Duration and timing
    - User ratings (1-5 scale)
    - Qualitative feedback
    - State changes (before/after)
    - Challenges encountered
    - Benefits experienced
    - Adherence patterns
    - Improvement trends
    
    Features:
        - Comprehensive logging system
        - Streak tracking (current and longest)
        - Multi-metric statistics
        - Pattern analysis via LLM
        - Personalized insights
        - Motivational messaging
        - Trend detection
        - Challenge identification
    """
    
    def __init__(
        self,
        llm_provider: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.6,
        verbose: bool = False
    ):
        """
        Initialize the Progress Agent.
        
        Args:
            llm_provider: LLM provider (groq, openai, anthropic)
            model_name: Model name
            temperature: LLM temperature
            verbose: Enable verbose logging
        """
        super().__init__(
            agent_type=AgentType.PROGRESS,
            name="progress",
            llm_provider=llm_provider,
            model_name=model_name,
            temperature=temperature,
            verbose=verbose
        )
        
        # Insight generation prompt
        self.insight_prompt = self._create_insight_prompt()
        
        # Motivational message prompt
        self.motivation_prompt = self._create_motivation_prompt()
        
        logger.info("Progress Agent initialized successfully")
    
    def _create_insight_prompt(self) -> PromptTemplate:
        """
        Create prompt template for generating progress insights.
        
        Returns:
            PromptTemplate for insight generation
        """
        template = """You are a compassionate wellness coach analyzing a user's spiritual practice journey.

**User Information:**
- Name: {user_name}
- Journey Duration: {days_practicing} days
- Experience Level: {experience_level}

**Progress Statistics:**
{statistics_summary}

**Recent Practice Logs:**
{recent_logs}

**Your Task:**
Analyze the user's progress and provide meaningful insights that:
1. Celebrate genuine achievements (be specific)
2. Identify patterns in their practice
3. Recognize areas for growth (gently)
4. Provide actionable recommendations
5. Acknowledge challenges with compassion

**Guidelines:**
- Be genuine and specific (not generic)
- Celebrate both big and small wins
- Recognize effort, not just outcomes
- Be encouraging but realistic
- Suggest practical next steps
- Honor their unique journey

**Output Format:**
Provide your analysis as a valid JSON object with this structure:

```json
{{
    "key_achievements": [
        "Specific achievement 1",
        "Specific achievement 2",
        "Specific achievement 3"
    ],
    "patterns_observed": [
        "Pattern 1",
        "Pattern 2"
    ],
    "areas_for_growth": [
        "Growth area 1 (framed positively)",
        "Growth area 2"
    ],
    "recommendations": [
        "Actionable recommendation 1",
        "Actionable recommendation 2"
    ]
}}
```

**CRITICAL:**
- Respond with ONLY the JSON object
- Do NOT include text before or after JSON
- Do NOT use markdown code blocks
- Ensure valid JSON syntax
- All fields must be present

Analysis:"""
        
        return PromptTemplate(
            template=template,
            input_variables=[
                "user_name",
                "days_practicing",
                "experience_level",
                "statistics_summary",
                "recent_logs"
            ]
        )
    
    def _create_motivation_prompt(self) -> PromptTemplate:
        """
        Create prompt template for generating motivational messages.
        
        Returns:
            PromptTemplate for motivation
        """
        template = """You are a compassionate spiritual mentor providing encouragement.

**User:** {user_name}
**Current Situation:** {situation}
**Recent Progress:** {progress_summary}

**Your Task:**
Create a warm, personalized motivational message that:
1. Acknowledges their current moment
2. Celebrates their effort and dedication
3. Provides genuine encouragement
4. Connects to deeper spiritual wisdom
5. Inspires continued practice

**Guidelines:**
- Be authentic and heartfelt (not cliché)
- Use their name naturally
- Reference specific aspects of their journey
- Keep it concise (2-3 sentences)
- End with warmth and support

**Tone:** Warm, wise, encouraging, personal

Motivational Message:"""
        
        return PromptTemplate(
            template=template,
            input_variables=[
                "user_name",
                "situation",
                "progress_summary"
            ]
        )
    
    def define_tools(self) -> List:
        """
        Define tools for the progress agent.
        
        Progress agent primarily uses database operations
        and LLM analysis.
        
        Returns:
            List of Tool objects (empty for now)
        """
        return []
    
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for the progress agent.
        
        Returns:
            System prompt string
        """
        return """You are the Progress Agent for the JAI GURU DEV AI Companion chatbot.

Your sacred responsibility is to honor and track each user's spiritual practice journey with care and wisdom.

## Your Capabilities:

1. **Practice Logging**: Record every completion with full details
2. **Statistics Tracking**: Calculate meaningful progress metrics
3. **Pattern Analysis**: Identify trends and behaviors
4. **Insight Generation**: Provide deep understanding of progress
5. **Motivation**: Encourage continued practice
6. **Recommendations**: Suggest next steps

## Core Principles:

**Honor Every Step**:
- Every practice attempt is valuable
- Effort matters more than perfection
- Small consistent steps > sporadic intensity
- Progress isn't always linear

**Data with Compassion**:
- Numbers tell part of the story
- Context and experience matter more
- Celebrate qualitative growth
- Recognize invisible progress (patience, awareness, peace)

**Realistic Encouragement**:
- Acknowledge actual achievements
- Be honest about patterns
- Gentle with areas for growth
- Practical in recommendations

**Personalized Insight**:
- Each journey is unique
- Compare user to their past self only
- Consider life circumstances
- Honor individual pace

## Tracking Framework:

**What to Log:**
- Practice name and type
- Duration and completion status
- User rating (1-5)
- Qualitative feedback
- State before/after
- Challenges encountered
- Benefits experienced

**What to Calculate:**
- Adherence rate (% completed)
- Current practice streak
- Longest streak achieved
- Practices by type
- Average rating
- Total practice time
- Trends (improving/stable/declining)

**What to Analyze:**
- Consistency patterns (time of day, day of week)
- Practice preferences (what they enjoy most)
- Challenge patterns (recurring obstacles)
- State improvements (emotional shifts)
- Growth trajectory (getting better/stuck)

**What to Share:**
- Specific achievements (not generic)
- Meaningful patterns
- Gentle growth opportunities
- Actionable recommendations
- Genuine encouragement

## Quality Indicators:

- Logs are complete and accurate
- Statistics are meaningful
- Insights are specific and helpful
- Recommendations are actionable
- Motivation feels genuine
- User feels seen and supported

Remember: You're not just tracking data - you're witnessing and honoring a sacred journey of growth and transformation."""
    
    def process(
        self,
        input_text: str,
        context: AgentContext,
        chat_history: Optional[List[BaseMessage]] = None
    ) -> AgentResponse:
        """
        Process progress tracking request.
        
        Main method that handles different progress operations:
        - Log practice completion
        - Calculate statistics
        - Generate insights
        - Provide motivational messages
        
        Args:
            input_text: Request (logging, stats, insights)
            context: User context
            chat_history: Conversation history
        
        Returns:
            AgentResponse with progress information
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Progress Agent processing: '{input_text[:50]}...'")
            
            # Determine operation type
            operation = self._classify_operation(input_text, context)
            
            if operation == 'log_practice':
                response = self._handle_log_practice(input_text, context)
            elif operation == 'view_stats':
                response = self._handle_view_stats(context)
            elif operation == 'generate_insights':
                response = self._handle_generate_insights(context)
            else:
                response = self._handle_general_progress(context)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            response.processing_time = processing_time
            
            logger.info(f"Progress Agent completed: {operation}")
            
            return response
            
        except Exception as e:
            logger.error(f"Progress Agent error: {e}", exc_info=True)
            return self.handle_error(e, context)
    
    def _classify_operation(
        self,
        input_text: str,
        context: AgentContext
    ) -> str:
        """
        Classify what progress operation to perform.
        
        Args:
            input_text: Request text
            context: User context
        
        Returns:
            Operation type string
        """
        text_lower = input_text.lower()
        
        # Check for logging keywords
        log_keywords = ['completed', 'finished', 'did', 'practiced', 'done with']
        if any(keyword in text_lower for keyword in log_keywords):
            return 'log_practice'
        
        # Check for stats keywords
        stats_keywords = ['progress', 'statistics', 'stats', 'how am i doing', 'my journey']
        if any(keyword in text_lower for keyword in stats_keywords):
            # If recent logs exist, generate insights; otherwise show stats
            practice_history = context.metadata.get('practice_history', [])
            if len(practice_history) >= 3:
                return 'generate_insights'
            else:
                return 'view_stats'
        
        # Check for insight keywords
        insight_keywords = ['insights', 'analysis', 'patterns', 'feedback', 'how am i doing']
        if any(keyword in text_lower for keyword in insight_keywords):
            return 'generate_insights'
        
        # Default to general progress
        return 'general_progress'
    
    def _handle_log_practice(
        self,
        input_text: str,
        context: AgentContext
    ) -> AgentResponse:
        """
        Handle logging a practice completion.
        
        Args:
            input_text: Log information
            context: User context
        
        Returns:
            AgentResponse with confirmation and encouragement
        """
        # Extract practice information from context or text
        practice_data = self._extract_practice_data(input_text, context)
        
        # Create practice log
        practice_log = self._create_practice_log(
            practice_data,
            context
        )
        
        # Save to practice history (in context for now, would save to DB)
        practice_history = context.metadata.get('practice_history', [])
        practice_history.append(practice_log.to_dict())
        context.metadata['practice_history'] = practice_history
        
        # Update statistics
        stats = self._calculate_statistics(context)
        
        # Generate motivational message
        motivation = self._generate_motivation(
            practice_log,
            stats,
            context
        )
        
        # Format response
        response_content = self._format_log_response(
            practice_log,
            stats,
            motivation
        )
        
        return AgentResponse(
            agent_name=self.name,
            content=response_content,
            confidence=1.0,
            metadata={
                'operation': 'log_practice',
                'log': practice_log.to_dict(),
                'updated_stats': stats.to_dict()
            },
            tools_used=['logging', 'statistics', 'motivation'],
            processing_time=0.0,  # Will be set by process()
            success=True
        )
    
    def _extract_practice_data(
        self,
        input_text: str,
        context: AgentContext
    ) -> Dict[str, Any]:
        """
        Extract practice information from text and context.
        
        Args:
            input_text: User's message
            context: User context
        
        Returns:
            Dictionary with practice data
        """
        # Check if practice info is in metadata (from Practice Agent)
        recommended_practice = context.metadata.get('recommended_practice', {})
        
        if recommended_practice:
            practice_data = {
                'practice_id': recommended_practice.get('practice_id', 'unknown'),
                'practice_name': recommended_practice.get('name', 'Unknown Practice'),
                'practice_type': recommended_practice.get('practice_type', 'meditation'),
                'duration_minutes': recommended_practice.get('duration_minutes', 15)
            }
        else:
            # Parse from text (simple extraction)
            practice_data = {
                'practice_id': 'manual_entry',
                'practice_name': 'Practice Session',
                'practice_type': 'meditation',
                'duration_minutes': 15
            }
        
        # Extract rating if mentioned
        rating = None
        text_lower = input_text.lower()
        for i in range(1, 6):
            if f"{i}/5" in text_lower or f"{i} out of 5" in text_lower:
                rating = i
                break
        
        practice_data['rating'] = rating
        
        # Extract feedback
        practice_data['feedback'] = input_text
        
        # Check for completion status
        completed = True
        if any(word in text_lower for word in ['partial', 'incomplete', 'stopped']):
            completed = False
        
        practice_data['completed'] = completed
        
        return practice_data
    
    def _create_practice_log(
        self,
        practice_data: Dict[str, Any],
        context: AgentContext
    ) -> PracticeLog:
        """
        Create a PracticeLog object from data.
        
        Args:
            practice_data: Extracted practice data
            context: User context
        
        Returns:
            PracticeLog object
        """
        import uuid
        
        # Get state before/after if in context
        assessment = context.metadata.get('assessment', {})
        state_before_str = assessment.get('primary_state')
        state_before = None
        if state_before_str:
            try:
                state_before = EmotionalState(state_before_str)
            except:
                pass
        
        # State after could be extracted from feedback sentiment
        # For now, leave as None (could be enhanced)
        
        try:
            practice_type_enum = PracticeType(practice_data.get('practice_type', 'meditation'))
        except:
            practice_type_enum = PracticeType.MEDITATION
        
        return PracticeLog(
            log_id=str(uuid.uuid4()),
            user_id=context.user_id,
            practice_id=practice_data.get('practice_id', 'unknown'),
            practice_name=practice_data.get('practice_name', 'Practice'),
            practice_type=practice_type_enum,
            duration_minutes=practice_data.get('duration_minutes', 15),
            completed=practice_data.get('completed', True),
            completion_datetime=datetime.now(),
            feedback=practice_data.get('feedback', ''),
            rating=practice_data.get('rating'),
            state_before=state_before,
            state_after=None,  # Could be enhanced
            challenges=[],  # Could extract from feedback
            benefits_experienced=[],  # Could extract from feedback
            notes=""
        )
    
    def _calculate_statistics(
        self,
        context: AgentContext
    ) -> ProgressStatistics:
        """
        Calculate user progress statistics.
        
        Args:
            context: User context with practice history
        
        Returns:
            ProgressStatistics object
        """
        practice_history = context.metadata.get('practice_history', [])
        
        if not practice_history:
            return self._empty_statistics()
        
        # Total practices
        total_practices = len(practice_history)
        
        # Completed practices
        completed_practices = sum(
            1 for log in practice_history if log.get('completed', True)
        )
        
        # Adherence rate
        adherence_rate = completed_practices / total_practices if total_practices > 0 else 0.0
        
        # Calculate streaks
        current_streak, longest_streak = self._calculate_streaks(practice_history)
        
        # Practices by type
        practices_by_type = defaultdict(int)
        for log in practice_history:
            practice_type = log.get('practice_type', 'unknown')
            practices_by_type[practice_type] += 1
        
        # Average rating
        ratings = [log.get('rating') for log in practice_history if log.get('rating') is not None]
        average_rating = sum(ratings) / len(ratings) if ratings else 0.0
        
        # Average duration
        durations = [log.get('duration_minutes', 0) for log in practice_history]
        average_duration = sum(durations) / len(durations) if durations else 0.0
        
        # Most practiced
        if practices_by_type:
            most_practiced = max(practices_by_type.items(), key=lambda x: x[1])[0]
        else:
            most_practiced = "None yet"
        
        # Recent trend (last 5 vs previous 5)
        recent_trend = self._calculate_trend(practice_history)
        
        # Total minutes
        total_minutes = sum(durations)
        
        return ProgressStatistics(
            total_practices=total_practices,
            completed_practices=completed_practices,
            adherence_rate=adherence_rate,
            current_streak=current_streak,
            longest_streak=longest_streak,
            practices_by_type=dict(practices_by_type),
            average_rating=average_rating,
            average_duration=average_duration,
            most_practiced=most_practiced,
            recent_trend=recent_trend,
            total_minutes=total_minutes
        )
    
    def _empty_statistics(self) -> ProgressStatistics:
        """
        Return empty statistics for new users.
        
        Returns:
            Empty ProgressStatistics
        """
        return ProgressStatistics(
            total_practices=0,
            completed_practices=0,
            adherence_rate=0.0,
            current_streak=0,
            longest_streak=0,
            practices_by_type={},
            average_rating=0.0,
            average_duration=0.0,
            most_practiced="None yet",
            recent_trend="Just starting",
            total_minutes=0
        )
    
    def _calculate_streaks(
        self,
        practice_history: List[Dict[str, Any]]
    ) -> Tuple[int, int]:
        """
        Calculate current and longest practice streaks.
        
        A streak is consecutive days with at least one practice.
        
        Args:
            practice_history: List of practice logs
        
        Returns:
            Tuple of (current_streak, longest_streak)
        """
        if not practice_history:
            return (0, 0)
        
        # Get completion dates
        dates = []
        for log in practice_history:
            if log.get('completed', True):
                date_str = log.get('completion_datetime', '')
                if date_str:
                    try:
                        dt = datetime.fromisoformat(date_str)
                        dates.append(dt.date())
                    except:
                        pass
        
        if not dates:
            return (0, 0)
        
        # Sort dates
        dates = sorted(set(dates))  # Unique dates only
        
        # Calculate current streak (from today backwards)
        today = datetime.now().date()
        current_streak = 0
        
        check_date = today
        while check_date in dates:
            current_streak += 1
            check_date -= timedelta(days=1)
        
        # Calculate longest streak
        longest_streak = 1
        current_sequence = 1
        
        for i in range(1, len(dates)):
            if (dates[i] - dates[i-1]).days == 1:
                current_sequence += 1
                longest_streak = max(longest_streak, current_sequence)
            else:
                current_sequence = 1
        
        return (current_streak, longest_streak)
    
    def _calculate_trend(
        self,
        practice_history: List[Dict[str, Any]]
    ) -> str:
        """
        Calculate recent trend (improving, stable, declining).
        
        Args:
            practice_history: List of practice logs
        
        Returns:
            Trend string
        """
        if len(practice_history) < 5:
            return "Building momentum"
        
        # Compare last 5 to previous 5
        recent = practice_history[-5:]
        previous = practice_history[-10:-5] if len(practice_history) >= 10 else []
        
        if not previous:
            return "Establishing pattern"
        
        # Calculate completion rate for each period
        recent_completion_rate = sum(
            1 for log in recent if log.get('completed', True)
        ) / len(recent)
        
        previous_completion_rate = sum(
            1 for log in previous if log.get('completed', True)
        ) / len(previous)
        
        # Compare
        if recent_completion_rate > previous_completion_rate + 0.2:
            return "Improving"
        elif recent_completion_rate < previous_completion_rate - 0.2:
            return "Needs attention"
        else:
            return "Consistent"
    
    def _generate_motivation(
        self,
        practice_log: PracticeLog,
        stats: ProgressStatistics,
        context: AgentContext
    ) -> str:
        """
        Generate personalized motivational message.
        
        Args:
            practice_log: The log that was just created
            stats: Current statistics
            context: User context
        
        Returns:
            Motivational message
        """
        try:
            user_name = context.user_profile.get('name', 'friend')
            
            # Describe situation
            situation = f"Just completed {practice_log.practice_name}"
            if practice_log.rating:
                situation += f" (rated {practice_log.rating}/5)"
            
            # Progress summary
            progress_summary = f"{stats.completed_practices} practices completed"
            if stats.current_streak > 0:
                progress_summary += f", {stats.current_streak}-day streak"
            
            # Format prompt
            prompt_input = {
                'user_name': user_name,
                'situation': situation,
                'progress_summary': progress_summary
            }
            
            formatted_prompt = self.motivation_prompt.format(**prompt_input)
            
            # Invoke LLM
            response = self.llm.invoke(formatted_prompt)
            motivation = response.content.strip()
            
            return motivation
            
        except Exception as e:
            logger.error(f"Motivation generation failed: {e}")
            # Fallback motivation
            return self._fallback_motivation(practice_log, stats, context)
    
    def _fallback_motivation(
        self,
        practice_log: PracticeLog,
        stats: ProgressStatistics,
        context: AgentContext
    ) -> str:
        """
        Generate fallback motivational message.
        
        Args:
            practice_log: Practice log
            stats: Statistics
            context: User context
        
        Returns:
            Simple motivational message
        """
        user_name = context.user_profile.get('name', 'friend')
        
        messages = [
            f"Beautiful work, {user_name}! Every practice deepens your journey. 🙏",
            f"Wonderful dedication, {user_name}! Your commitment inspires. ✨",
            f"Well done, {user_name}! Each practice is a gift to yourself. 💫",
            f"Amazing consistency, {user_name}! You're building something special. 🌟"
        ]
        
        # Select based on streak
        if stats.current_streak >= 7:
            return messages[3]
        elif stats.current_streak >= 3:
            return messages[1]
        else:
            return messages[0]
    
    def _format_log_response(
        self,
        practice_log: PracticeLog,
        stats: ProgressStatistics,
        motivation: str
    ) -> str:
        """
        Format practice log confirmation response.
        
        Args:
            practice_log: The logged practice
            stats: Current statistics
            motivation: Motivational message
        
        Returns:
            Formatted response string
        """
        response = f"""## ✅ Practice Logged Successfully!

**Practice:** {practice_log.practice_name}
**Duration:** {practice_log.duration_minutes} minutes
**Date:** {practice_log.completion_datetime.strftime('%B %d, %Y at %I:%M %p')}
"""
        
        if practice_log.rating:
            response += f"**Rating:** {'⭐' * practice_log.rating} ({practice_log.rating}/5)\n"
        
        if practice_log.feedback:
            response += f"**Feedback:** {practice_log.feedback}\n"
        
        response += f"\n### 📊 Your Progress\n\n"
        response += f"- **Total Practices:** {stats.completed_practices}\n"
        response += f"- **Current Streak:** {stats.current_streak} days 🔥\n"
        response += f"- **Adherence Rate:** {stats.adherence_rate:.0%}\n"
        response += f"- **Total Practice Time:** {stats.total_minutes} minutes\n"
        
        if stats.current_streak > stats.longest_streak - 1:
            response += f"\n🎉 **New record! This is your longest streak!**\n"
        
        response += f"\n### 💫 {motivation}\n"
        
        return response
    
    def _handle_view_stats(self, context: AgentContext) -> AgentResponse:
        """
        Handle viewing progress statistics.
        
        Args:
            context: User context
        
        Returns:
            AgentResponse with statistics
        """
        stats = self._calculate_statistics(context)
        response_content = self._format_stats_response(stats, context)
        
        return AgentResponse(
            agent_name=self.name,
            content=response_content,
            confidence=1.0,
            metadata={
                'operation': 'view_stats',
                'statistics': stats.to_dict()
            },
            tools_used=['statistics'],
            processing_time=0.0,
            success=True
        )
    
    def _format_stats_response(
        self,
        stats: ProgressStatistics,
        context: AgentContext
    ) -> str:
        """
        Format statistics response.
        
        Args:
            stats: Statistics to format
            context: User context
        
        Returns:
            Formatted response string
        """
        user_name = context.user_profile.get('name', 'friend')
        
        if stats.total_practices == 0:
            return f"""Hi {user_name}! 👋

You're just getting started on your journey. Your first practice awaits!

Every journey of a thousand miles begins with a single step. 🌟"""
        
        response = f"""## 📊 Your Progress Journey, {user_name}

### Overview

- **Total Practices:** {stats.completed_practices}
- **Adherence Rate:** {stats.adherence_rate:.0%}
- **Current Streak:** {stats.current_streak} days 🔥
- **Longest Streak:** {stats.longest_streak} days
- **Total Time Practicing:** {stats.total_minutes} minutes ({stats.total_minutes / 60:.1f} hours)

### Practice Breakdown

"""
        
        if stats.practices_by_type:
            for practice_type, count in sorted(
                stats.practices_by_type.items(),
                key=lambda x: x[1],
                reverse=True
            ):
                response += f"- **{practice_type.title()}:** {count} sessions\n"
        
        response += f"\n### Quality Metrics\n\n"
        
        if stats.average_rating > 0:
            response += f"- **Average Rating:** {'⭐' * int(stats.average_rating)} ({stats.average_rating:.1f}/5)\n"
        
        response += f"- **Average Duration:** {stats.average_duration:.1f} minutes\n"
        response += f"- **Most Practiced:** {stats.most_practiced}\n"
        response += f"- **Recent Trend:** {stats.recent_trend}\n"
        
        response += "\n---\n\n"
        response += "*Keep up the wonderful work! Each practice is a step toward greater peace and wisdom.* 🙏"
        
        return response
    
    def _handle_generate_insights(self, context: AgentContext) -> AgentResponse:
        """
        Handle generating progress insights.
        
        Args:
            context: User context
        
        Returns:
            AgentResponse with insights
        """
        stats = self._calculate_statistics(context)
        insights = self._generate_insights(stats, context)
        response_content = self._format_insights_response(insights, stats, context)
        
        return AgentResponse(
            agent_name=self.name,
            content=response_content,
            confidence=insights.confidence,
            metadata={
                'operation': 'generate_insights',
                'insights': insights.to_dict(),
                'statistics': stats.to_dict()
            },
            tools_used=['statistics', 'llm_analysis'],
            processing_time=0.0,
            success=True
        )
    
    def _generate_insights(
        self,
        stats: ProgressStatistics,
        context: AgentContext
    ) -> ProgressInsight:
        """
        Generate progress insights via LLM analysis.
        
        Args:
            stats: Progress statistics
            context: User context
        
        Returns:
            ProgressInsight object
        """
        try:
            profile = context.user_profile
            practice_history = context.metadata.get('practice_history', [])
            
            # Calculate days practicing
            if practice_history:
                first_practice_date = datetime.fromisoformat(
                    practice_history[0].get('completion_datetime', datetime.now().isoformat())
                )
                days_practicing = (datetime.now() - first_practice_date).days + 1
            else:
                days_practicing = 0
            
            # Format statistics summary
            stats_summary = f"""- Total Practices: {stats.completed_practices}
- Adherence Rate: {stats.adherence_rate:.0%}
- Current Streak: {stats.current_streak} days
- Longest Streak: {stats.longest_streak} days
- Average Rating: {stats.average_rating:.1f}/5
- Most Practiced: {stats.most_practiced}
- Recent Trend: {stats.recent_trend}"""
            
            # Format recent logs
            recent_logs = self._format_recent_logs(practice_history[-10:])
            
            # Format prompt
            prompt_input = {
                'user_name': profile.get('name', 'User'),
                'days_practicing': days_practicing,
                'experience_level': profile.get('experience_level', 'beginner'),
                'statistics_summary': stats_summary,
                'recent_logs': recent_logs
            }
            
            formatted_prompt = self.insight_prompt.format(**prompt_input)
            
            # Invoke LLM
            response = self.llm.invoke(formatted_prompt)
            response_text = response.content.strip()
            
            # Parse JSON
            import json
            import re
            
            # Clean response
            cleaned = re.sub(r'^```json\s*', '', response_text)
            cleaned = re.sub(r'^```\s*', '', cleaned)
            cleaned = re.sub(r'\s*```$', '', cleaned)
            
            insight_data = json.loads(cleaned)
            
            # Generate motivational message
            motivation = self._generate_general_motivation(stats, context)
            
            return ProgressInsight(
                key_achievements=insight_data.get('key_achievements', []),
                areas_for_growth=insight_data.get('areas_for_growth', []),
                patterns_observed=insight_data.get('patterns_observed', []),
                motivational_message=motivation,
                recommendations=insight_data.get('recommendations', []),
                confidence=0.85
            )
            
        except Exception as e:
            logger.error(f"Insight generation failed: {e}")
            return self._fallback_insights(stats, context)
    
    def _format_recent_logs(self, logs: List[Dict[str, Any]]) -> str:
        """
        Format recent practice logs for LLM context.
        
        Args:
            logs: List of practice logs
        
        Returns:
            Formatted string
        """
        if not logs:
            return "No recent practices logged."
        
        formatted = []
        for log in logs:
            practice_name = log.get('practice_name', 'Practice')
            completed = log.get('completed', True)
            rating = log.get('rating')
            feedback = log.get('feedback', '')
            
            log_str = f"- {practice_name}"
            if not completed:
                log_str += " (incomplete)"
            if rating:
                log_str += f" - Rating: {rating}/5"
            if feedback and len(feedback) > 0 and feedback != practice_name:
                log_str += f" - Feedback: {feedback[:100]}"
            
            formatted.append(log_str)
        
        return "\n".join(formatted)
    
    def _generate_general_motivation(
        self,
        stats: ProgressStatistics,
        context: AgentContext
    ) -> str:
        """
        Generate general motivational message for insights.
        
        Args:
            stats: Statistics
            context: User context
        
        Returns:
            Motivational message
        """
        try:
            user_name = context.user_profile.get('name', 'friend')
            
            situation = f"Reviewing your journey of {stats.completed_practices} practices"
            progress_summary = f"{stats.adherence_rate:.0%} adherence, {stats.current_streak}-day streak"
            
            prompt_input = {
                'user_name': user_name,
                'situation': situation,
                'progress_summary': progress_summary
            }
            
            formatted_prompt = self.motivation_prompt.format(**prompt_input)
            response = self.llm.invoke(formatted_prompt)
            
            return response.content.strip()
            
        except:
            return f"Your dedication shines through in every practice, {context.user_profile.get('name', 'friend')}. Keep walking this beautiful path! 🙏"
    
    def _fallback_insights(
        self,
        stats: ProgressStatistics,
        context: AgentContext
    ) -> ProgressInsight:
        """
        Generate fallback insights when LLM fails.
        
        Args:
            stats: Statistics
            context: User context
        
        Returns:
            Basic ProgressInsight
        """
        achievements = []
        if stats.completed_practices > 0:
            achievements.append(f"Completed {stats.completed_practices} practices")
        if stats.current_streak > 0:
            achievements.append(f"Maintained {stats.current_streak}-day streak")
        if stats.adherence_rate >= 0.8:
            achievements.append("Strong adherence to practice")
        
        patterns = []
        if stats.most_practiced != "None yet":
            patterns.append(f"Preference for {stats.most_practiced} practices")
        patterns.append(f"Recent trend: {stats.recent_trend}")
        
        growth = ["Continue building consistency"]
        
        recommendations = [
            "Keep up your regular practice schedule",
            "Try varying practice types for well-rounded growth"
        ]
        
        return ProgressInsight(
            key_achievements=achievements if achievements else ["Just getting started!"],
            areas_for_growth=growth,
            patterns_observed=patterns if patterns else ["Building your pattern"],
            motivational_message="Every practice is a step forward on your journey! 🙏",
            recommendations=recommendations,
            confidence=0.6
        )
    
    def _format_insights_response(
        self,
        insights: ProgressInsight,
        stats: ProgressStatistics,
        context: AgentContext
    ) -> str:
        """
        Format insights response.
        
        Args:
            insights: Progress insights
            stats: Statistics
            context: User context
        
        Returns:
            Formatted response string
        """
        user_name = context.user_profile.get('name', 'friend')
        
        response = f"""## 🌟 Your Progress Insights, {user_name}

### 🎉 Key Achievements

"""
        for achievement in insights.key_achievements:
            response += f"• {achievement}\n"
        
        if insights.patterns_observed:
            response += "\n### 📈 Patterns Observed\n\n"
            for pattern in insights.patterns_observed:
                response += f"• {pattern}\n"
        
        if insights.areas_for_growth:
            response += "\n### 🌱 Areas for Growth\n\n"
            for area in insights.areas_for_growth:
                response += f"• {area}\n"
        
        if insights.recommendations:
            response += "\n### 💡 Recommendations\n\n"
            for i, rec in enumerate(insights.recommendations, 1):
                response += f"{i}. {rec}\n"
        
        response += f"\n### 💫 {insights.motivational_message}\n"
        
        response += "\n---\n\n"
        response += f"*Based on {stats.completed_practices} practices | {stats.adherence_rate:.0%} adherence*"
        
        return response
    
    def _handle_general_progress(self, context: AgentContext) -> AgentResponse:
        """
        Handle general progress query.
        
        Args:
            context: User context
        
        Returns:
            AgentResponse with overview
        """
        stats = self._calculate_statistics(context)
        
        if stats.total_practices == 0:
            content = f"""Welcome to your progress tracking! 🌟

I'm here to help you track your spiritual practice journey. After each practice, let me know how it went, and I'll keep track of your progress.

Ready to start your first practice?"""
        elif stats.total_practices < 3:
            content = self._format_stats_response(stats, context)
        else:
            # Show insights for established users
            insights = self._generate_insights(stats, context)
            content = self._format_insights_response(insights, stats, context)
        
        return AgentResponse(
            agent_name=self.name,
            content=content,
            confidence=0.9,
            metadata={
                'operation': 'general_progress',
                'statistics': stats.to_dict()
            },
            tools_used=['statistics'],
            processing_time=0.0,
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
        
        return f"""I'm having difficulty processing your progress tracking right now, {user_name}.

However, I want you to know that every practice you complete is valuable, and I'm here to support your journey!

Could you try sharing your practice completion again? I'm here to help. 🙏"""


# Example usage and testing
if __name__ == "__main__":
    from dotenv import load_dotenv
    import uuid
    
    load_dotenv()
    
    print("=" * 60)
    print("Progress Agent Test")
    print("=" * 60)
    
    try:
        # Create progress agent
        progress_agent = ProgressAgent(verbose=True)
        
        # Create test context
        context = AgentContext(
            user_id=str(uuid.uuid4()),
            session_id=str(uuid.uuid4()),
            user_profile={
                'name': 'Alex',
                'age': 28,
                'experience_level': 'beginner'
            },
            conversation_history=[],
            metadata={
                'recommended_practice': {
                    'practice_id': 'meditation_002',
                    'name': 'Breath Awareness Meditation',
                    'practice_type': 'meditation',
                    'duration_minutes': 15
                },
                'practice_history': []
            }
        )
        
        # Test 1: Log a practice
        print("\n" + "=" * 60)
        print("Test 1: Logging Practice Completion")
        print("=" * 60)
        
        response = progress_agent.process(
            "I completed the breath awareness meditation! It was really calming. Rating: 5/5",
            context
        )
        
        print(f"\nResponse:\n{response.content}")
        
        # Test 2: View stats (after adding a few more practices)
        print("\n" + "=" * 60)
        print("Test 2: Adding More Practices and Viewing Stats")
        print("=" * 60)
        
        # Simulate a few more practices
        for i in range(3):
            context.metadata['practice_history'].append({
                'practice_id': f'practice_{i}',
                'practice_name': f'Practice {i+1}',
                'practice_type': 'pranayama',
                'duration_minutes': 10,
                'completed': True,
                'completion_datetime': datetime.now().isoformat(),
                'rating': 4
            })
        
        response = progress_agent.process(
            "Show me my progress",
            context
        )
        
        print(f"\nResponse:\n{response.content}")
        
        print("\n" + "=" * 60)
        print("✅ Progress Agent Test Complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
