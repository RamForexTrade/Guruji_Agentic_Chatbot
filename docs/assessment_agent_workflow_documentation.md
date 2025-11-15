# Assessment Agent Workflow - Guruji Chatbot

## Overview

The Assessment Agent is a critical component of the Guruji Chatbot system, responsible for analyzing users' emotional, mental, and physical states to provide personalized guidance and practice recommendations. The system includes both a **Base Assessment Agent** and an **Enhanced Assessment Agent V2** with multi-turn conversational capabilities.

---

## System Architecture

### 1. Entry Point: Orchestrator Agent

**Role**: Master coordinator that routes user queries to specialized agents

**Intent Classification**:
- `SEEKING_WISDOM` → Routes to Wisdom Agent
- `EXPRESSING_STATE` → Routes to Assessment Agent (+ Wisdom + Practice)
- `PRACTICE_COMPLETION` → Routes to Progress Agent
- `PRACTICE_INQUIRY` → Routes to Practice Agent
- `GREETING/FAREWELL` → Direct response

**Decision Point**: 
- Checks if an assessment is already in progress
- If yes → Continues multi-turn assessment
- If no → Initializes new assessment

---

## Assessment Agent Implementations

### A. Base Assessment Agent (`assessment_agent.py`)

**Purpose**: Single-shot LLM-based state analysis with immediate assessment

**Key Features**:
- Quick emotional state detection
- LLM-powered comprehensive analysis
- Keyword-based validation
- Urgency calculation

#### Workflow Steps:

1. **Context Preparation**
   - Extracts user profile (name, age, experience level)
   - Summarizes conversation history (last 5 messages)
   - Retrieves previous assessment states

2. **LLM Assessment**
   - Uses structured prompt template
   - Requests JSON-formatted response
   - Temperature: 0.3 (lower for consistency)

3. **Information Extracted**:
   - **Primary State**: Main emotional/mental state
   - **Secondary States**: Additional concurrent states
   - **Severity**: LOW, MEDIUM, HIGH, CRITICAL
   - **Physical Indicators**: Tension, headache, fatigue, etc.
   - **Readiness**: READY, NEEDS_PREPARATION, NOT_READY
   - **Recommended Interventions**: Pranayama, meditation, therapy, etc.
   - **Underlying Needs**: Core psychological needs
   - **Urgency Level**: 1-10 scale
   - **Confidence**: 0.0-1.0 score
   - **Reasoning**: Explanation of assessment

4. **Validation & Enhancement**
   - Cross-checks with keyword analysis
   - Adjusts low-confidence assessments
   - Validates state consistency

5. **Urgency Calculation**
   - Base urgency from LLM
   - Adjusts for severity level
   - Adjusts for readiness
   - Checks for worsening trends
   - Clamps to 1-10 range

6. **Response Formation**
   - Creates structured Assessment object
   - Formats human-readable response
   - Stores metadata for context

---

### B. Enhanced Assessment Agent V2 (`assessment_agent_enhanced_v2.py`)

**Purpose**: Multi-turn empathetic conversation for deep understanding

**Philosophy**:
- Listen first, understand deeply
- Don't rush to solutions
- Reflect feelings back with compassion
- Gentle probing for root causes
- Gurudev-inspired empathetic style

**Key Differences from Base**:
- Multi-stage conversation flow
- Age-aware tone adjustment
- Deeper contextual probing
- Additional safety checks (time, meal status)
- Enhanced empathy in responses

#### Conversation States:

```
INITIAL_GREETING
    ↓
PROBING_EMOTION (2-3 turns)
    ↓
PROBING_SITUATION (2-3 turns)
    ↓
PROBING_LOCATION (1-2 turns)
    ↓
PROBING_TIME (1 turn)
    ↓
PROBING_MEAL (1 turn)
    ↓
ASSESSMENT_COMPLETE
```

#### Stage Details:

**Stage 1: Initial Greeting**
- Ask age range (18-25, 26-35, 36-45)
- Adjust tone accordingly
- Open with: "What's on your mind?"

**Stage 2: Probing Emotion**
- Encourage emotional sharing
- Use reflective listening
- Examples: "I hear that you're feeling..."
- Ask clarifying questions
- Multiple turns allowed - don't rush

**Stage 3: Probing Situation**
- Understand root cause
- What's triggering the emotion?
- Life situation context
- Deep exploration allowed

**Stage 4: Probing Location**
- Physical context needed
- Only after understanding emotion/situation
- Options: home_indoor, outdoor, office, public_place, vehicle

**Stage 5: Probing Time** *(NEW in V2)*
- How much time available?
- Options: 7, 12, or 20 minutes
- For practice duration tailoring

**Stage 6: Probing Meal Status** *(NEW in V2)*
- Full or empty stomach?
- Important for practice safety
- Some breathing exercises require empty stomach

**Stage 7: Assessment Complete**
- All information gathered
- Ready for wisdom matching and practice recommendation

#### Enhanced Assessment Object:

```python
@dataclass
class EnhancedAssessment:
    primary_emotion: EmotionalState
    secondary_emotions: List[EmotionalState]
    life_situation: LifeSituation
    user_location: UserLocation
    user_age: Optional[int]
    time_available: TimeAvailable       # NEW
    meal_status: MealStatus             # NEW
    situation_details: str              # What user said
    emotion_details: str                # How they described feelings
    conversation_state: ConversationState
    turns_in_current_state: int
    is_complete: bool
    severity: SeverityLevel
    tone: str
    confidence: float
```

---

## Data Structures & Enums

### EmotionalState
```python
LOVE, FEAR, ANGER, DEPRESSION, OVERWHELMED,
CONFUSION, HURT, LONELINESS, GUILT, INADEQUACY,
ANXIOUS, STRESSED, CALM, SEEKING, HAPPY, SAD,
NEUTRAL, UNKNOWN
```

### SeverityLevel
```python
LOW, MEDIUM, HIGH, CRITICAL
```

### ReadinessLevel
```python
READY, NEEDS_PREPARATION, NOT_READY
```

### LifeSituation
```python
FINANCE_CAREER, DECISION_MAKING, RELATIONSHIP_LOVE,
BURNOUT, HEALTH, MIND_CREATED, WORLD_PROBLEMS,
SPIRITUAL_GROWTH, UNKNOWN
```

### UserLocation
```python
HOME_INDOOR, OUTDOOR, OFFICE, PUBLIC_PLACE,
VEHICLE, UNKNOWN
```

### TimeAvailable *(NEW)*
```python
SEVEN_MIN, TWELVE_MIN, TWENTY_MIN, UNKNOWN
```

### MealStatus *(NEW)*
```python
FULL_STOMACH, EMPTY_STOMACH, UNKNOWN
```

### ConversationState
```python
INITIAL_GREETING, PROBING_EMOTION, PROBING_SITUATION,
PROBING_LOCATION, PROBING_TIME, PROBING_MEAL,
ASSESSMENT_COMPLETE, DELIVERING_SOLUTION
```

---

## Integration Flow

### Multi-Agent Collaboration

When a user expresses emotional state:

1. **Assessment Agent**
   - Analyzes current state
   - Determines severity and urgency
   - Identifies underlying needs

2. **Wisdom Agent**
   - Provides relevant spiritual teachings
   - Offers perspective and understanding
   - Shares insights from Patanjali Yoga Sutras

3. **Practice Agent**
   - Recommends specific techniques
   - Tailors practices to:
     - User's location
     - Time available
     - Meal status
     - Emotional state
     - Experience level

4. **Orchestrator**
   - Synthesizes all responses
   - Creates coherent, compassionate output
   - Maintains conversation flow

---

## Key Processing Methods

### Base Agent Methods:

1. **`_perform_llm_assessment()`**
   - Formats prompt with user context
   - Invokes LLM with structured template
   - Parses JSON response

2. **`_validate_assessment()`**
   - Cross-checks with keyword patterns
   - Adjusts low-confidence results
   - Ensures consistency

3. **`_calculate_urgency()`**
   - Base urgency from LLM
   - Severity adjustments
   - Readiness adjustments
   - Trend analysis

4. **`_detect_states_by_keywords()`**
   - Pattern matching for states
   - Backup validation method
   - Scores keyword matches

### Enhanced V2 Methods:

1. **`_determine_next_state()`**
   - Analyzes current state
   - Checks if information is sufficient
   - Transitions to next stage

2. **`_generate_response_for_state()`**
   - Creates empathetic, contextual response
   - Adjusts tone based on age and situation
   - Uses reflective listening

3. **`_extract_information_from_response()`**
   - Parses user responses
   - Extracts emotions, situations, locations
   - Updates assessment state

4. **`_check_completion()`**
   - Validates all required info gathered
   - Ensures quality of understanding
   - Marks assessment as complete

---

## Error Handling

### Fallback Mechanisms:

1. **LLM Failure**
   - Falls back to keyword-based detection
   - Returns conservative default assessment
   - Maintains conversation flow

2. **JSON Parsing Errors**
   - Attempts multiple parsing strategies
   - Extracts partial information
   - Creates valid default structure

3. **Missing Information**
   - Continues conversation naturally
   - Asks clarifying questions
   - Never forces premature completion

---

## Quality Indicators

### Base Agent:
- Accurate state identification
- Appropriate severity classification
- Realistic readiness assessment
- Helpful intervention mapping
- Clear reasoning provided

### Enhanced V2:
- Deep emotional understanding
- Natural conversation flow
- Non-rushed assessment
- Age-appropriate tone
- Safety-conscious (meal status check)
- Time-aware recommendations

---

## Performance Metrics

### Measured Values:
- **Processing Time**: Seconds per assessment
- **Confidence Score**: 0.0-1.0 (LLM self-assessment)
- **Turns in State**: Number of conversation turns per stage
- **Completion Rate**: Successful vs. incomplete assessments
- **Agent Routing**: Which agents were invoked

### Storage:
All assessments stored in `context.metadata`:
- Current assessment state
- Assessment history
- Previous emotional states
- Conversation flow tracking

---

## Example Flows

### Example 1: Base Assessment (Single-shot)

**User**: "I'm feeling really anxious about my presentation tomorrow. My heart is racing and I can't sleep."

**Process**:
1. Orchestrator classifies as `EXPRESSING_STATE`
2. Base Assessment Agent analyzes:
   - Primary State: ANXIOUS
   - Severity: HIGH
   - Physical: ["racing heart", "insomnia"]
   - Readiness: NEEDS_PREPARATION
   - Interventions: [PRANAYAMA, MEDITATION]
   - Urgency: 7/10

3. Routes to Wisdom + Practice Agents
4. Returns comprehensive response

---

### Example 2: Enhanced V2 (Multi-turn)

**Turn 1**:
- **User**: "Hi"
- **Agent**: "Welcome! Could you share your age range? (18-25, 26-35, 36-45)"
- **State**: INITIAL_GREETING

**Turn 2**:
- **User**: "I'm 28"
- **Agent**: "Thank you. What's been on your mind lately?"
- **State**: PROBING_EMOTION

**Turn 3**:
- **User**: "I've been feeling really stressed"
- **Agent**: "I hear that you're feeling stressed. That sounds difficult. Can you tell me more about what's weighing on you?"
- **State**: PROBING_EMOTION (continuing)

**Turn 4**:
- **User**: "Work has been overwhelming, my boss keeps piling on tasks"
- **Agent**: "It sounds like work pressure is really affecting you. I understand how overwhelming that can feel. Are you at home right now?"
- **State**: PROBING_LOCATION

**Turn 5**:
- **User**: "Yes, I'm at home"
- **Agent**: "Great. Do you have about 7, 12, or 20 minutes for a quick practice?"
- **State**: PROBING_TIME

**Turn 6**:
- **User**: "I have 12 minutes"
- **Agent**: "Perfect. One last question for safety - have you eaten recently or is your stomach empty?"
- **State**: PROBING_MEAL

**Turn 7**:
- **User**: "I haven't eaten yet"
- **Agent**: [Assessment complete, routes to Practice Agent for recommendation]
- **State**: ASSESSMENT_COMPLETE

---

## Configuration

### LLM Settings:

**Base Agent**:
- Temperature: 0.3 (consistency)
- Provider: groq/openai/anthropic
- Model: Configurable via `llm_config.py`

**Enhanced V2**:
- Temperature: 0.8 (empathy & variety)
- Provider: groq/openai/anthropic
- Model: Configurable via `llm_config.py`

### Conversation Settings:
- Max turns per state: 5 (prevents infinite loops)
- History length: 5 messages (for context)
- Confidence threshold: 0.7 (for state transitions)

---

## Future Enhancements

### Planned Features:
1. Voice tone analysis integration
2. Multi-language support
3. Cultural context awareness
4. Biometric data integration
5. Long-term pattern tracking
6. Personalized intervention learning

---

## Testing

### Test Files:
- `test_assessment_agent.py`: Base agent tests
- `test_enhanced_assessment.py`: V2 agent tests

### Test Coverage:
- State detection accuracy
- Conversation flow integrity
- Edge case handling
- Fallback mechanisms
- Multi-turn conversation logic

---

## Summary

The Assessment Agent system provides two complementary approaches:

**Base Agent**: Fast, single-shot analysis for quick assessments
**Enhanced V2**: Deep, empathetic multi-turn conversations for thorough understanding

Both work together with the Orchestrator to ensure users receive compassionate, personalized support tailored to their emotional state, life situation, and practical constraints (location, time, meal status).

The system embodies the wisdom and compassion of Gurudev's teachings while leveraging modern AI capabilities for personalized mental wellness support.
