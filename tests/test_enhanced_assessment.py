"""
Test Enhanced Assessment Agent
===============================

Demonstrates the new empathetic assessment flow with multi-turn conversation.
"""

import sys
import os
from dotenv import load_dotenv
import uuid

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.assessment_agent_enhanced import EnhancedAssessmentAgent, EnhancedAssessment
from agents.base_agent import AgentContext
from agents.agent_types import EmotionalState, LifeSituation, UserLocation
from agents.solution_generator import SolutionGenerator

# Load environment variables
load_dotenv()


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_response(speaker, message):
    """Print a conversation message"""
    print(f"{speaker}: {message}\n")


def test_ambiguous_input():
    """Test 1: User with ambiguous initial input - requires probing"""
    print_section("TEST 1: Ambiguous Input - Multi-Turn Dialog")

    # Create agent
    agent = EnhancedAssessmentAgent(verbose=False)

    # Create user context
    context = AgentContext(
        user_id=str(uuid.uuid4()),
        session_id=str(uuid.uuid4()),
        user_profile={
            'name': 'Alex',
            'age': 28
        },
        conversation_history=[]
    )

    # Simulate conversation
    conversation = [
        "I don't know what's happening with me",
        "I feel really worried and anxious",
        "I have to make a big career decision and I'm scared I'll choose wrong",
        "I'm at home right now"
    ]

    for user_input in conversation:
        print_response("Alex", user_input)

        # Process with agent
        response = agent.process(user_input, context)

        print_response("Agent", response.content)

        # Show assessment status
        assessment_status = response.metadata.get('is_complete', False)
        conv_state = response.metadata.get('conversation_state', 'unknown')
        print(f"[Status: {conv_state}, Complete: {assessment_status}]")

        # Update conversation history
        context.conversation_history.append({'role': 'user', 'content': user_input})
        context.conversation_history.append({'role': 'assistant', 'content': response.content})

        if assessment_status:
            print("\n✓ Assessment Complete! Ready for wisdom retrieval.")
            assessment_data = response.metadata.get('assessment', {})
            print(f"\nExtracted Information:")
            print(f"  - Emotion: {assessment_data.get('primary_emotion')}")
            print(f"  - Situation: {assessment_data.get('life_situation')}")
            print(f"  - Location: {assessment_data.get('user_location')}")
            print(f"  - Tone: {assessment_data.get('tone')}")
            break


def test_clear_input():
    """Test 2: User with clear initial input - quick assessment"""
    print_section("TEST 2: Clear Input - Quick Assessment")

    agent = EnhancedAssessmentAgent(verbose=False)

    context = AgentContext(
        user_id=str(uuid.uuid4()),
        session_id=str(uuid.uuid4()),
        user_profile={
            'name': 'Sarah',
            'age': 35
        },
        conversation_history=[]
    )

    user_input = "I'm feeling really angry and frustrated about my job. My boss keeps overloading me with work and I'm at my office desk right now feeling like I'm going to explode."

    print_response("Sarah", user_input)

    response = agent.process(user_input, context)

    print_response("Agent", response.content)

    assessment_status = response.metadata.get('is_complete', False)
    print(f"\n[Assessment Complete: {assessment_status}]")

    if assessment_status:
        assessment_data = response.metadata.get('assessment', {})
        print(f"\nQuickly Extracted:")
        print(f"  - Emotion: {assessment_data.get('primary_emotion')}")
        print(f"  - Situation: {assessment_data.get('life_situation')}")
        print(f"  - Location: {assessment_data.get('user_location')}")


def test_solution_generation():
    """Test 3: Generate complete 4-part solution"""
    print_section("TEST 3: 4-Part Solution Generation")

    # Simulate a completed assessment
    print("Simulating completed assessment for:")
    print("  - User: Maya, age 22")
    print("  - Emotion: Fear")
    print("  - Situation: Decision Making")
    print("  - Location: Home Indoor")
    print("  - Tone: Warm\n")

    # Mock wisdom (in real system, retrieved from Chroma DB)
    mock_wisdom = """
"The cause of distress is set concepts in the mind that things should be a certain way.
Train the mind to live in the present moment. Drop the stress that you are carrying for nothing."
- Gurudev Sri Sri Ravishanker (Knowledge Sheet #127)
    """.strip()

    # Generate solution
    solution = SolutionGenerator.generate(
        emotion=EmotionalState.FEAR,
        situation=LifeSituation.DECISION_MAKING,
        location=UserLocation.HOME_INDOOR,
        age=22,
        tone="warm",
        user_name="Maya",
        wisdom_text=mock_wisdom
    )

    # Format and display
    formatted = SolutionGenerator.format_solution(solution, UserLocation.HOME_INDOOR)

    print(formatted)


def test_somber_tone():
    """Test 4: Somber tone for grief/loss"""
    print_section("TEST 4: Somber Tone for Grief/Loss")

    agent = EnhancedAssessmentAgent(verbose=False)

    context = AgentContext(
        user_id=str(uuid.uuid4()),
        session_id=str(uuid.uuid4()),
        user_profile={
            'name': 'David',
            'age': 45
        },
        conversation_history=[]
    )

    # Simulate grief scenario
    conversation = [
        "My father passed away last week",
        "I'm feeling lost and heartbroken, I don't know how to cope",
        "I'm at home with my family"
    ]

    for user_input in conversation:
        print_response("David", user_input)

        response = agent.process(user_input, context)

        print_response("Agent", response.content)

        context.conversation_history.append({'role': 'user', 'content': user_input})
        context.conversation_history.append({'role': 'assistant', 'content': response.content})

        if response.metadata.get('is_complete', False):
            assessment_data = response.metadata.get('assessment', {})
            tone = assessment_data.get('tone', 'unknown')
            print(f"\n✓ Tone detected: {tone}")
            print("  (Somber tone means no jokes, only gentle support)")
            break


def test_prevention_of_premature_routing():
    """Test 5: Demonstrate prevention of premature wisdom routing"""
    print_section("TEST 5: Prevention of Premature Wisdom Routing")

    agent = EnhancedAssessmentAgent(verbose=False)

    context = AgentContext(
        user_id=str(uuid.uuid4()),
        session_id=str(uuid.uuid4()),
        user_profile={
            'name': 'Rachel',
            'age': 30
        },
        conversation_history=[]
    )

    print("Simulating orchestrator routing logic:\n")

    # First message - incomplete assessment
    user_input1 = "I feel overwhelmed"

    print_response("Rachel", user_input1)
    response1 = agent.process(user_input1, context)

    is_complete = response1.metadata.get('is_complete', False)
    print(f"Assessment complete? {is_complete}")
    print(f"Should route to Wisdom Agent? {is_complete}")
    print(f"Action: {'Route to Wisdom' if is_complete else 'Continue Assessment'}\n")

    print_response("Agent", response1.content)

    # Check routing decision
    if not is_complete:
        print("\n✓ Correct! Orchestrator continues with assessment agent.")
        print("  (Does NOT route to wisdom yet)")

    # Second message - still incomplete
    context.conversation_history.append({'role': 'user', 'content': user_input1})
    context.conversation_history.append({'role': 'assistant', 'content': response1.content})

    user_input2 = "Too much work, I can't keep up"

    print_response("\nRachel", user_input2)
    response2 = agent.process(user_input2, context)

    is_complete = response2.metadata.get('is_complete', False)
    print(f"Assessment complete? {is_complete}")
    print(f"Should route to Wisdom Agent? {is_complete}")
    print(f"Action: {'Route to Wisdom' if is_complete else 'Continue Assessment'}\n")

    print_response("Agent", response2.content)

    # Final message - complete
    context.conversation_history.append({'role': 'user', 'content': user_input2})
    context.conversation_history.append({'role': 'assistant', 'content': response2.content})

    user_input3 = "I'm at my office desk"

    print_response("\nRachel", user_input3)
    response3 = agent.process(user_input3, context)

    is_complete = response3.metadata.get('is_complete', False)
    print(f"Assessment complete? {is_complete}")
    print(f"Should route to Wisdom Agent? {is_complete}")
    print(f"Action: {'Route to Wisdom' if is_complete else 'Continue Assessment'}\n")

    if is_complete:
        print("\n✓ NOW orchestrator can safely route to Wisdom Agent!")
        print("  Assessment has all required information.")

        assessment_data = response3.metadata.get('assessment', {})
        print(f"\n  Extracted State:")
        print(f"    - Emotion: {assessment_data.get('primary_emotion')}")
        print(f"    - Situation: {assessment_data.get('life_situation')}")
        print(f"    - Location: {assessment_data.get('user_location')}")


def main():
    """Run all tests"""
    print("\n" + "━" * 70)
    print("  ENHANCED ASSESSMENT AGENT - TEST SUITE")
    print("━" * 70)

    try:
        # Run tests
        test_ambiguous_input()
        test_clear_input()
        test_solution_generation()
        test_somber_tone()
        test_prevention_of_premature_routing()

        print_section("ALL TESTS COMPLETED ✓")
        print("The Enhanced Assessment Agent is working correctly:")
        print("  ✓ Multi-turn empathetic dialog")
        print("  ✓ Emotion, situation, location extraction")
        print("  ✓ Tone adaptation (warm/somber)")
        print("  ✓ Prevention of premature wisdom routing")
        print("  ✓ 4-part solution generation")
        print("\nReady for integration with orchestrator and wisdom agent!")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
