# Enhanced Assessment Agent - Integration Guide

## Overview

The Enhanced Assessment Agent implements empathetic mental state evaluation with multi-turn conversational dialog. It **NEVER** routes to wisdom retrieval until complete assessment is finished.

## Key Features Implemented

### 1. Multi-Turn Conversational Flow

**Conversation States:**
- `INITIAL_GREETING` - Warm welcome, initial assessment
- `PROBING_EMOTION` - Gentle probing to identify predominant emotion
- `PROBING_SITUATION` - Understanding the life situation (botheration)
- `PROBING_LOCATION` - Determining physical context for recommendations
- `ASSESSMENT_COMPLETE` - All required information collected

### 2. Required Information Extraction

The agent extracts:
1. **Predominant Emotion** (from 10 core emotions)
   - Love, Fear, Anger, Depression, Overwhelmed, Confusion, Hurt, Loneliness, Guilt, Inadequacy

2. **Life Situation (Botheration)**
   - Finance/Career, Decision Making, Relationship/Love, Burnout, Health, Mind-created, World Problems, Spiritual Growth

3. **User Location**
   - Home Indoor, Outdoor, Office, Public Place, Vehicle

4. **User Age** (estimated or provided)

### 3. Empathetic Probing System

- **Open-ended questions** - Never yes/no questions
- **One question at a time** - Not overwhelming
- **Warm, compassionate language** - Youth-friendly by default
- **Tone adaptation** - Somber for grief/loss, playful for lighthearted situations

### 4. Prevention of Premature Wisdom Routing

The agent tracks `is_complete` status in the assessment:

```python
assessment.is_complete = (
    assessment.primary_emotion != EmotionalState.UNKNOWN and
    assessment.life_situation != LifeSituation.UNKNOWN and
    assessment.user_location != UserLocation.UNKNOWN
)
```

**Only when `is_complete == True` should the orchestrator route to Wisdom Agent.**

## Integration with Orchestrator

### Current Flow

```
User Input
    ↓
Orchestrator
    ↓
Route to Enhanced Assessment Agent
    ↓
[Multi-turn dialog until assessment complete]
    ↓
ONLY WHEN assessment.is_complete == True:
    ↓
Route to Wisdom Agent
    ↓
Generate 4-Part Solution
```

### Orchestrator Changes Needed

The orchestrator must:

1. **Check assessment status before routing:**

```python
# In orchestrator.py
def route_message(self, user_input: str, context: AgentContext):
    # Check if we're in middle of assessment
    current_assessment = context.metadata.get('current_assessment')

    if current_assessment and not current_assessment.get('is_complete', False):
        # Continue with assessment agent - don't route elsewhere
        return self.assessment_agent.process(user_input, context)

    # Only after assessment is complete, check for wisdom routing
    if current_assessment and current_assessment.get('is_complete', True):
        # Now safe to route to wisdom agent
        return self.wisdom_agent.process(user_input, context)
```

2. **Maintain conversation context:**

The assessment state is stored in `context.metadata['current_assessment']` and persists across turns.

3. **Detect new conversation vs continuation:**

```python
def is_new_conversation(context: AgentContext) -> bool:
    """Check if this is a new conversation or continuation"""
    return 'current_assessment' not in context.metadata or \
           context.metadata['current_assessment'].get('is_complete', False)
```

## 4-Part Solution Generation

### After Assessment is Complete

Once `assessment.is_complete == True`:

1. **Build wisdom query** from extracted state:
```python
query = f"{emotion} related to {situation}"
```

2. **Retrieve wisdom** from Chroma DB (via Wisdom Agent)

3. **Generate holistic solution** using `SolutionGenerator`:

```python
from agents.solution_generator import SolutionGenerator

# After wisdom retrieval
solution = SolutionGenerator.generate(
    emotion=assessment.primary_emotion,
    situation=assessment.life_situation,
    location=assessment.user_location,
    age=assessment.user_age,
    tone=assessment.tone,
    user_name=context.user_profile.get('name'),
    wisdom_text=retrieved_wisdom_verbatim
)

# Format for delivery
formatted_solution = SolutionGenerator.format_solution(
    solution,
    assessment.user_location
)
```

## Solution Structure

The 4-part solution includes:

### Part 1: Pranayama (Breathing)
- Specific pranayama for the emotion
- Adapted to user's location
- Clear instructions
- Duration and benefits

### Part 2: Asana (Yoga)
- Specific yoga pose for the emotion
- Adapted to user's location
- Modifications for beginners
- Duration and benefits

### Part 3: Wisdom Byte
- **Verbatim** text from Gurudev's Knowledge Sheets
- Retrieved via Wisdom Agent from Chroma DB
- Never invented or paraphrased

### Part 4: Activity/Joke
- Age-appropriate
- Tone-appropriate (warm/playful/somber)
- Helps practice the wisdom
- Engaging and memorable

## Example Conversation Flow

```
User: "I don't know what's happening with me"
Agent: [Warm greeting] "I'm here to listen. Can you tell me a bit more about what you're feeling?"

User: "I feel really worried about everything"
Agent: [Emotion detected: FEAR] "I hear you. What's been going on that's making you feel worried?"

User: "I have to make a big decision about changing jobs and I'm scared"
Agent: [Situation detected: DECISION_MAKING] "Thank you for sharing that. Just so I can suggest practices you can do right now - are you at home, or somewhere else?"

User: "I'm at home"
Agent: [Location detected: HOME_INDOOR]
      [Assessment COMPLETE ✓]
      "I understand your situation now. Let me find the wisdom and practices that will help you most..."

      [Routes to Wisdom Agent]
      [Generates 4-Part Solution]
```

## File Structure

```
agents/
├── agent_types.py                      # Updated with new enums
├── assessment_agent_enhanced.py        # New enhanced agent
├── solution_generator.py               # 4-part solution generator
├── wisdom_agent.py                     # Existing (retrieves from Chroma)
└── orchestrator.py                     # Needs updates for routing logic
```

## Testing

### Test Scenarios

1. **Ambiguous initial input:**
   - User: "I'm not feeling good"
   - Agent should probe empathetically

2. **Clear initial input:**
   - User: "I'm anxious about my presentation tomorrow. I'm at home."
   - Agent should extract quickly and move to solution

3. **Grief/Loss scenario:**
   - Tone should automatically shift to somber
   - No jokes in Part 4, only gentle reflection

4. **Youth vs Senior:**
   - Language adaptation
   - Activity complexity
   - Joke style

### Validation Tests

```python
# Test assessment completion
def test_assessment_completion():
    assessment = EnhancedAssessment(
        primary_emotion=EmotionalState.FEAR,
        life_situation=LifeSituation.DECISION_MAKING,
        user_location=UserLocation.HOME_INDOOR
    )

    assert assessment.is_complete == False  # Age not set

    assessment.user_age = 30
    # Re-check via _is_assessment_complete()
    assert is_complete(assessment) == True

# Test premature routing prevention
def test_no_premature_routing():
    assessment = EnhancedAssessment(
        primary_emotion=EmotionalState.UNKNOWN,
        conversation_state=ConversationState.PROBING_EMOTION
    )

    # Orchestrator should NOT route to Wisdom Agent yet
    assert should_route_to_wisdom(assessment) == False
```

## Migration Path

### For Existing Systems

1. **Keep old assessment_agent.py** as fallback
2. **Import enhanced version** for new conversations
3. **Gradual rollout:**
   - Start with new users
   - Migrate existing users session by session

### Backward Compatibility

The old EmotionalState enum values are preserved:
- `anxious`, `stressed`, `calm`, `seeking`, `happy`, `sad`, `neutral`

These can still be used and will map to appropriate solutions.

## Configuration

### Agent Initialization

```python
from agents.assessment_agent_enhanced import EnhancedAssessmentAgent

# Create agent
assessment_agent = EnhancedAssessmentAgent(
    llm_provider="groq",  # or "openai", "anthropic"
    model_name=None,      # Uses default for provider
    temperature=0.7,      # Higher for more empathetic responses
    verbose=False
)
```

### LLM Provider Support

Works with:
- Groq (fast, economical)
- OpenAI (GPT-4/GPT-3.5)
- Anthropic Claude (highly empathetic)

## Best Practices

### 1. Conversation Management
- Always check `is_complete` before routing
- Persist assessment state in context
- Handle interruptions gracefully

### 2. Error Handling
- Fallback to simpler probing if LLM fails
- Keyword detection as backup
- Graceful degradation

### 3. User Experience
- Never overwhelm with multiple questions
- Validate their feelings before moving on
- Explain why you're asking (for location, etc.)

### 4. Wisdom Integration
- **NEVER generate fake wisdom**
- Always retrieve verbatim from Chroma DB
- If no wisdom found, acknowledge and provide general support

## Monitoring & Metrics

Track:
- Average turns to complete assessment
- Completion rate (% reaching `ASSESSMENT_COMPLETE`)
- User satisfaction post-solution
- Wisdom retrieval success rate

## Future Enhancements

Potential additions:
- Voice tone analysis (if audio input available)
- Multi-language support
- Cultural context adaptation
- Progressive disclosure of assessment (don't ask location if they said "I'm at my desk")
- Learning from user feedback on solutions

---

## Quick Reference

**Prevent Wisdom Routing:**
```python
if not assessment.is_complete:
    continue_assessment()
else:
    route_to_wisdom()
```

**Generate Solution:**
```python
solution = SolutionGenerator.generate(...)
formatted = SolutionGenerator.format_solution(solution, location)
```

**Check Tone:**
```python
if "death" in user_input or "died" in user_input:
    assessment.tone = "somber"
```

---

**Questions or Issues?**
Check the inline documentation in:
- `assessment_agent_enhanced.py`
- `solution_generator.py`
- `agent_types.py`
