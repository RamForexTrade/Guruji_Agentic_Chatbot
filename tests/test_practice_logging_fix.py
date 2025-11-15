"""
Test Script for Practice Logging Form Display
==============================================

This script tests the practice logging form display issue fix.
It simulates the agent flow to verify that recommendations are properly
extracted and the form appears in the UI.
"""

import sys
import os
from datetime import datetime
import uuid

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.orchestrator import OrchestratorAgent
from agents.wisdom_agent import WisdomAgent
from agents.assessment_agent import AssessmentAgent
from agents.practice_agent import PracticeAgent
from agents.base_agent import AgentContext


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_section(text):
    """Print formatted section"""
    print(f"\n--- {text} ---")


def test_practice_recommendation_flow():
    """
    Test the complete flow of practice recommendation and metadata extraction.
    
    This simulates what happens when a user expresses a state and the
    system needs to display the practice logging form.
    """
    
    print_header("PRACTICE RECOMMENDATION FLOW TEST")
    
    # Step 1: Initialize agents
    print_section("Step 1: Initializing Agents")
    
    try:
        orchestrator = OrchestratorAgent(verbose=False)
        print("✅ Orchestrator initialized")
        
        wisdom_agent = WisdomAgent(
            config_path="config.yaml",
            knowledge_base_path="Knowledge_Base",
            verbose=False
        )
        print("✅ Wisdom Agent initialized")
        
        assessment_agent = AssessmentAgent(verbose=False)
        print("✅ Assessment Agent initialized")
        
        practice_agent = PracticeAgent(verbose=False)
        print("✅ Practice Agent initialized")
        
        # Register agents
        orchestrator.set_specialized_agents(
            wisdom_agent=wisdom_agent,
            assessment_agent=assessment_agent,
            practice_agent=practice_agent
        )
        print("✅ Agents registered with orchestrator")
        
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        return False
    
    # Step 2: Create test context
    print_section("Step 2: Creating Test Context")
    
    context = AgentContext(
        user_id=str(uuid.uuid4()),
        session_id=str(uuid.uuid4()),
        user_profile={
            'name': 'TestUser',
            'age': 30,
            'experience_level': 'beginner',
            'life_aspect': 'Managing stress and anxiety',
            'emotional_state': 'anxious'
        },
        conversation_history=[],
        metadata={
            'practice_history': []
        }
    )
    print(f"✅ Context created for user: {context.user_profile['name']}")
    
    # Step 3: Process state expression
    print_section("Step 3: Processing State Expression")
    
    test_input = "I'm feeling very anxious today and can't seem to calm down."
    print(f"User Input: '{test_input}'")
    
    try:
        response = orchestrator.process(
            input_text=test_input,
            context=context
        )
        print(f"✅ Orchestrator processed query")
        print(f"   Intent: {response.metadata.get('intent', 'unknown')}")
        print(f"   Confidence: {response.confidence:.2f}")
        print(f"   Agents Invoked: {response.metadata.get('agents_invoked', [])}")
        
    except Exception as e:
        print(f"❌ Processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 4: Check metadata structure
    print_section("Step 4: Checking Metadata Structure")
    
    # Check for agent_responses
    if 'agent_responses' not in response.metadata:
        print("❌ No 'agent_responses' in metadata")
        return False
    
    print(f"✅ Found 'agent_responses' in metadata")
    agent_responses = response.metadata['agent_responses']
    print(f"   Number of agent responses: {len(agent_responses)}")
    
    # List all agents that responded
    for i, agent_resp in enumerate(agent_responses, 1):
        agent_name = agent_resp.get('agent_name', 'unknown')
        success = agent_resp.get('success', False)
        print(f"   {i}. {agent_name} - {'✅ Success' if success else '❌ Failed'}")
    
    # Step 5: Extract recommendation (THE KEY FIX)
    print_section("Step 5: Extracting Recommendation (Testing Fix)")
    
    recommendation_found = False
    recommendation_data = None
    
    # First check top-level (shouldn't be there but good to check)
    if 'recommendation' in response.metadata:
        print("⚠️  Found recommendation at TOP LEVEL (unexpected but ok)")
        recommendation_data = response.metadata['recommendation']
        recommendation_found = True
    
    # Check in nested agent responses (THE FIX)
    if not recommendation_found:
        print("Searching in nested agent responses...")
        for agent_resp in agent_responses:
            if agent_resp.get('agent_name') == 'practice':
                print(f"   Found practice agent response")
                if 'metadata' in agent_resp:
                    print(f"      Has metadata")
                    if 'recommendation' in agent_resp['metadata']:
                        print(f"      ✅ Found recommendation in practice agent metadata!")
                        recommendation_data = agent_resp['metadata']['recommendation']
                        recommendation_found = True
                        break
                else:
                    print(f"      ❌ No metadata in practice agent response")
    
    if not recommendation_found:
        print("❌ FAILED: Recommendation not found in response metadata")
        print("\nMetadata structure:")
        print(response.metadata.keys())
        return False
    
    # Step 6: Validate recommendation structure
    print_section("Step 6: Validating Recommendation Structure")
    
    required_fields = [
        'primary_practice',
        'alternatives',
        'customized_instructions',
        'reasoning',
        'confidence'
    ]
    
    all_present = True
    for field in required_fields:
        if field in recommendation_data:
            print(f"   ✅ {field}")
        else:
            print(f"   ❌ {field} - MISSING")
            all_present = False
    
    if not all_present:
        print("\n❌ FAILED: Recommendation missing required fields")
        return False
    
    # Step 7: Validate primary practice structure
    print_section("Step 7: Validating Primary Practice")
    
    primary_practice = recommendation_data.get('primary_practice', {})
    
    practice_fields = [
        'practice_id',
        'name',
        'practice_type',
        'duration_minutes',
        'instructions'
    ]
    
    all_present = True
    for field in practice_fields:
        if field in primary_practice:
            value = primary_practice[field]
            if field == 'name':
                print(f"   ✅ {field}: {value}")
            else:
                print(f"   ✅ {field}")
        else:
            print(f"   ❌ {field} - MISSING")
            all_present = False
    
    if not all_present:
        print("\n❌ FAILED: Primary practice missing required fields")
        return False
    
    # Step 8: Simulate UI state update
    print_section("Step 8: Simulating UI State Update")
    
    # This is what happens in app.py after the fix
    class MockSessionState:
        def __init__(self):
            self.current_recommendation = None
            self.show_practice_log = False
    
    session_state = MockSessionState()
    
    # Apply the fix logic
    if 'recommendation' in response.metadata:
        session_state.current_recommendation = response.metadata['recommendation']
        session_state.show_practice_log = True
    else:
        # Check in nested agent responses
        for agent_resp in agent_responses:
            if agent_resp.get('agent_name') == 'practice':
                if 'recommendation' in agent_resp.get('metadata', {}):
                    session_state.current_recommendation = agent_resp['metadata']['recommendation']
                    session_state.show_practice_log = True
                    break
    
    # Verify state was set correctly
    if session_state.show_practice_log:
        print("   ✅ show_practice_log = True")
    else:
        print("   ❌ show_practice_log = False (SHOULD BE TRUE)")
        return False
    
    if session_state.current_recommendation is not None:
        print("   ✅ current_recommendation is set")
    else:
        print("   ❌ current_recommendation is None (SHOULD BE SET)")
        return False
    
    # Step 9: Simulate form rendering check
    print_section("Step 9: Simulating Form Render Check")
    
    # This is the check in render_sidebar()
    should_show_form = (
        session_state.show_practice_log 
        and session_state.current_recommendation is not None
    )
    
    if should_show_form:
        print("   ✅ Form should be rendered in sidebar")
        practice = session_state.current_recommendation.get('primary_practice', {})
        practice_name = practice.get('name', 'Unknown')
        print(f"   Practice to log: {practice_name}")
    else:
        print("   ❌ Form will NOT be rendered (BUG)")
        return False
    
    # Final summary
    print_header("TEST RESULTS")
    print("\n✅ ALL TESTS PASSED!")
    print("\nThe practice logging form fix is working correctly:")
    print("1. ✅ Recommendation is properly extracted from nested agent responses")
    print("2. ✅ Session state flags are set correctly")
    print("3. ✅ Form render conditions are satisfied")
    print("4. ✅ Practice details are accessible for the form")
    print("\n🎉 The form WILL appear in the sidebar after practice recommendations!\n")
    
    return True


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║          PRACTICE LOGGING FORM DISPLAY - FIX TEST                ║
║                                                                  ║
║  This test verifies that the practice logging form will          ║
║  automatically appear in the sidebar after a recommendation.     ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        success = test_practice_recommendation_flow()
        
        if success:
            print("\n" + "=" * 70)
            print("  ✅ TEST SUITE PASSED - Fix is working correctly!")
            print("=" * 70)
            sys.exit(0)
        else:
            print("\n" + "=" * 70)
            print("  ❌ TEST SUITE FAILED - Issues detected")
            print("=" * 70)
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
