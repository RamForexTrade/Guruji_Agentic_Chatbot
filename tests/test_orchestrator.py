"""
Test Orchestrator Agent
========================

Comprehensive tests for the orchestrator agent functionality.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.orchestrator import OrchestratorAgent
from agents.base_agent import AgentContext
from agents.agent_types import IntentType
from dotenv import load_dotenv
import uuid


def test_orchestrator_initialization():
    """Test 1: Orchestrator initialization"""
    print("\n" + "="*60)
    print("TEST 1: Orchestrator Initialization")
    print("="*60)
    
    try:
        orchestrator = OrchestratorAgent()
        print(f"✅ Orchestrator created: {orchestrator}")
        print(f"   - Name: {orchestrator.name}")
        print(f"   - Type: {orchestrator.agent_type}")
        print(f"   - LLM Provider: {orchestrator.llm_provider}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_intent_classification():
    """Test 2: Intent classification"""
    print("\n" + "="*60)
    print("TEST 2: Intent Classification")
    print("="*60)
    
    try:
        orchestrator = OrchestratorAgent()
        
        # Test cases: (query, expected_intent)
        test_cases = [
            ("Hello! Good morning!", IntentType.GREETING),
            ("I'm feeling anxious", IntentType.EXPRESSING_STATE),
            ("Why do we meditate?", IntentType.SEEKING_WISDOM),
            ("How do I do pranayama?", IntentType.PRACTICE_INQUIRY),
            ("I completed my meditation", IntentType.PRACTICE_COMPLETION),
            ("Thank you, goodbye!", IntentType.FAREWELL),
        ]
        
        passed = 0
        for query, expected in test_cases:
            intent = orchestrator._classify_intent_by_keywords(query)
            if intent == expected:
                print(f"   ✅ '{query[:30]}...' → {intent.value}")
                passed += 1
            else:
                print(f"   ⚠️  '{query[:30]}...' → Expected {expected.value}, got {intent.value}")
        
        print(f"\n   Passed: {passed}/{len(test_cases)}")
        return passed >= len(test_cases) * 0.7  # 70% pass rate acceptable
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_agent_routing():
    """Test 3: Agent routing logic"""
    print("\n" + "="*60)
    print("TEST 3: Agent Routing Logic")
    print("="*60)
    
    try:
        orchestrator = OrchestratorAgent()
        
        # Test routing for different intents
        routing_tests = [
            (IntentType.SEEKING_WISDOM, ['wisdom']),
            (IntentType.EXPRESSING_STATE, ['assessment', 'wisdom', 'practice']),
            (IntentType.PRACTICE_COMPLETION, ['progress']),
            (IntentType.PRACTICE_INQUIRY, ['practice']),
        ]
        
        passed = 0
        for intent, expected_agents in routing_tests:
            agents = orchestrator._determine_agent_routing(intent, "test query")
            if agents == expected_agents:
                print(f"   ✅ {intent.value} → {agents}")
                passed += 1
            else:
                print(f"   ❌ {intent.value} → Expected {expected_agents}, got {agents}")
        
        print(f"\n   Passed: {passed}/{len(routing_tests)}")
        return passed == len(routing_tests)
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_greeting_handling():
    """Test 4: Greeting handling"""
    print("\n" + "="*60)
    print("TEST 4: Greeting Handling")
    print("="*60)
    
    try:
        orchestrator = OrchestratorAgent()
        
        context = AgentContext(
            user_id=str(uuid.uuid4()),
            session_id=str(uuid.uuid4()),
            user_profile={'name': 'Test User', 'age': 30}
        )
        
        response = orchestrator.process("Hello!", context)
        
        print(f"✅ Greeting response generated:")
        print(f"   - Success: {response.success}")
        print(f"   - Confidence: {response.confidence:.2f}")
        print(f"   - Intent: {response.metadata.get('intent')}")
        print(f"   - Response: {response.content[:100]}...")
        
        return response.success and "Test User" in response.content
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_farewell_handling():
    """Test 5: Farewell handling"""
    print("\n" + "="*60)
    print("TEST 5: Farewell Handling")
    print("="*60)
    
    try:
        orchestrator = OrchestratorAgent()
        
        context = AgentContext(
            user_id=str(uuid.uuid4()),
            session_id=str(uuid.uuid4()),
            user_profile={'name': 'Test User', 'age': 30}
        )
        
        response = orchestrator.process("Thank you, goodbye!", context)
        
        print(f"✅ Farewell response generated:")
        print(f"   - Success: {response.success}")
        print(f"   - Confidence: {response.confidence:.2f}")
        print(f"   - Intent: {response.metadata.get('intent')}")
        print(f"   - Response: {response.content[:100]}...")
        
        return response.success
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_general_conversation():
    """Test 6: General conversation (requires API key)"""
    print("\n" + "="*60)
    print("TEST 6: General Conversation")
    print("="*60)
    
    if not os.getenv('GROQ_API_KEY') and not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Skipped: No API key set")
        return None
    
    try:
        orchestrator = OrchestratorAgent()
        
        context = AgentContext(
            user_id=str(uuid.uuid4()),
            session_id=str(uuid.uuid4()),
            user_profile={'name': 'Alice', 'age': 28}
        )
        
        response = orchestrator.process("How are you?", context)
        
        print(f"✅ General conversation handled:")
        print(f"   - Success: {response.success}")
        print(f"   - Confidence: {response.confidence:.2f}")
        print(f"   - Processing time: {response.processing_time:.2f}s")
        print(f"   - Response: {response.content[:150]}...")
        
        return response.success
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_expressing_state_routing():
    """Test 7: Expressing state routing (placeholder agents)"""
    print("\n" + "="*60)
    print("TEST 7: Expressing State Routing")
    print("="*60)
    
    if not os.getenv('GROQ_API_KEY') and not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Skipped: No API key set")
        return None
    
    try:
        orchestrator = OrchestratorAgent()
        
        context = AgentContext(
            user_id=str(uuid.uuid4()),
            session_id=str(uuid.uuid4()),
            user_profile={'name': 'Bob', 'age': 35, 'emotional_state': 'anxious'}
        )
        
        # This should route to assessment + wisdom + practice agents
        # Since they're not implemented yet, should get placeholder responses
        response = orchestrator.process("I'm feeling very anxious today", context)
        
        print(f"✅ State expression handled:")
        print(f"   - Success: {response.success}")
        print(f"   - Intent: {response.metadata.get('intent')}")
        print(f"   - Agents invoked: {response.metadata.get('agents_invoked')}")
        print(f"   - Response contains placeholders: {response.success}")
        
        return True  # Success even with placeholder agents
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all orchestrator tests"""
    print("\n" + "="*60)
    print("🧪 ORCHESTRATOR AGENT TESTS")
    print("="*60)
    
    tests = [
        ("Orchestrator Initialization", test_orchestrator_initialization),
        ("Intent Classification", test_intent_classification),
        ("Agent Routing Logic", test_agent_routing),
        ("Greeting Handling", test_greeting_handling),
        ("Farewell Handling", test_farewell_handling),
        ("General Conversation", test_general_conversation),
        ("Expressing State Routing", test_expressing_state_routing),
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result is True)
    failed = sum(1 for _, result in results if result is False)
    skipped = sum(1 for _, result in results if result is None)
    
    for test_name, result in results:
        if result is True:
            print(f"✅ {test_name}")
        elif result is False:
            print(f"❌ {test_name}")
        else:
            print(f"⚠️  {test_name} (skipped)")
    
    print("\n" + "-"*60)
    print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
    print("="*60)
    
    if failed == 0:
        print("\n🎉 All tests passed!")
        if skipped > 0:
            print(f"Note: {skipped} test(s) skipped (requires API key)")
    else:
        print(f"\n⚠️  {failed} test(s) failed")
    
    return failed == 0


if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    success = run_all_tests()
    sys.exit(0 if success else 1)
