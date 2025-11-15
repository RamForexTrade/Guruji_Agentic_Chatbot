"""
Test Wisdom Agent
=================

Comprehensive testing for the Wisdom Agent that retrieves
and contextualizes wisdom from Gurudev's teachings.
"""

import sys
import os
from dotenv import load_dotenv
import uuid
from datetime import datetime

# Ensure we import from the current directory, not parent
# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.wisdom_agent import WisdomAgent
from agents.base_agent import AgentContext

load_dotenv()


def print_separator(title="", char="="):
    """Print a formatted separator"""
    width = 70
    if title:
        print(f"\n{char * width}")
        print(f"{title.center(width)}")
        print(f"{char * width}")
    else:
        print(f"\n{char * width}")


def test_wisdom_agent_initialization():
    """Test 1: Wisdom Agent Initialization"""
    print_separator("TEST 1: Wisdom Agent Initialization")
    
    try:
        wisdom_agent = WisdomAgent(
            config_path="config.yaml",
            knowledge_base_path="Knowledge_Base",
            top_k_results=3,
            verbose=True
        )
        
        print("✅ Wisdom Agent initialized successfully")
        print(f"   - Agent Type: {wisdom_agent.agent_type.value}")
        print(f"   - Agent Name: {wisdom_agent.name}")
        print(f"   - Top K Results: {wisdom_agent.top_k_results}")
        print(f"   - RAG System: {'Initialized' if wisdom_agent.rag_system else 'Not Initialized'}")
        print(f"   - Vector Store: {'Available' if wisdom_agent.rag_system and wisdom_agent.rag_system.vectorstore else 'Not Available'}")
        
        return True, wisdom_agent
        
    except Exception as e:
        print(f"❌ Failed to initialize Wisdom Agent: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_wisdom_retrieval(wisdom_agent):
    """Test 2: Wisdom Retrieval"""
    print_separator("TEST 2: Wisdom Retrieval")
    
    if not wisdom_agent:
        print("⏭️  Skipping (agent not initialized)")
        return False
    
    try:
        # Create test context
        context = AgentContext(
            user_id=str(uuid.uuid4()),
            session_id=str(uuid.uuid4()),
            user_profile={
                'name': 'Alice',
                'age': 28,
                'emotional_state': 'anxious',
                'life_situation': 'work stress'
            }
        )
        
        query = "I'm feeling very anxious about work. What should I do?"
        
        print(f"\nTest Query: '{query}'")
        print(f"User Context: {context.user_profile}")
        print("\nProcessing...")
        
        response = wisdom_agent.process(query, context)
        
        print(f"\n✅ Wisdom retrieval successful")
        print(f"   - Confidence: {response.confidence:.2f}")
        print(f"   - Teachings Retrieved: {response.metadata.get('teachings_retrieved', 0)}")
        print(f"   - Processing Time: {response.processing_time:.2f}s")
        print(f"   - Success: {response.success}")
        
        print(f"\n📚 Wisdom Response:")
        print("-" * 70)
        print(response.content)
        print("-" * 70)
        
        if 'sources' in response.metadata:
            print(f"\n📖 Sources:")
            for source in response.metadata['sources']:
                print(f"   - Teaching #{source['teaching_number']}: {source.get('title', 'Untitled')}")
                if source.get('date'):
                    print(f"     Date: {source['date']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Wisdom retrieval failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_queries(wisdom_agent):
    """Test 3: Multiple Query Types"""
    print_separator("TEST 3: Multiple Query Types")
    
    if not wisdom_agent:
        print("⏭️  Skipping (agent not initialized)")
        return False
    
    context = AgentContext(
        user_id=str(uuid.uuid4()),
        session_id=str(uuid.uuid4()),
        user_profile={
            'name': 'Bob',
            'age': 35,
            'emotional_state': 'seeking guidance',
            'life_situation': 'personal growth'
        }
    )
    
    test_queries = [
        {
            'query': "Why do we meditate?",
            'type': "Philosophical Question"
        },
        {
            'query': "How can I find inner peace?",
            'type': "Guidance Seeking"
        },
        {
            'query': "What is the purpose of suffering?",
            'type': "Existential Question"
        }
    ]
    
    all_passed = True
    
    for idx, test_case in enumerate(test_queries, 1):
        print(f"\n{'-' * 70}")
        print(f"Query {idx} ({test_case['type']}): {test_case['query']}")
        print("-" * 70)
        
        try:
            response = wisdom_agent.process(test_case['query'], context)
            
            print(f"✅ Success - Confidence: {response.confidence:.2f}, " 
                  f"Time: {response.processing_time:.2f}s, "
                  f"Teachings: {response.metadata.get('teachings_retrieved', 0)}")
            
            # Show brief excerpt
            excerpt = response.content[:200] + "..." if len(response.content) > 200 else response.content
            print(f"\nExcerpt: {excerpt}")
            
        except Exception as e:
            print(f"❌ Failed: {e}")
            all_passed = False
    
    return all_passed


def test_context_enhancement(wisdom_agent):
    """Test 4: Context Enhancement"""
    print_separator("TEST 4: Context Enhancement")
    
    if not wisdom_agent:
        print("⏭️  Skipping (agent not initialized)")
        return False
    
    try:
        # Test with different emotional states
        contexts = [
            {
                'emotional_state': 'anxious',
                'life_situation': 'work stress',
                'expected': 'anxiety management'
            },
            {
                'emotional_state': 'peaceful',
                'life_situation': 'meditation practice',
                'expected': 'deepening practice'
            },
            {
                'emotional_state': 'confused',
                'life_situation': 'life decisions',
                'expected': 'clarity and guidance'
            }
        ]
        
        query = "What guidance do you have for me?"
        
        for idx, ctx in enumerate(contexts, 1):
            context = AgentContext(
                user_id=str(uuid.uuid4()),
                session_id=str(uuid.uuid4()),
                user_profile={
                    'name': f'User{idx}',
                    'emotional_state': ctx['emotional_state'],
                    'life_situation': ctx['life_situation']
                }
            )
            
            print(f"\n{'-' * 70}")
            print(f"Context {idx}:")
            print(f"  State: {ctx['emotional_state']}, Situation: {ctx['life_situation']}")
            print(f"  Expected Focus: {ctx['expected']}")
            
            response = wisdom_agent.process(query, context)
            
            print(f"✅ Retrieved {response.metadata.get('teachings_retrieved', 0)} teachings")
            print(f"   Confidence: {response.confidence:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Context enhancement test failed: {e}")
        return False


def test_metadata_search(wisdom_agent):
    """Test 5: Metadata-based Search"""
    print_separator("TEST 5: Metadata-based Search")
    
    if not wisdom_agent:
        print("⏭️  Skipping (agent not initialized)")
        return False
    
    try:
        print("\nTesting metadata filters...")
        
        # Test topic filter
        print("\n1. Search by Topic: 'meditation'")
        results = wisdom_agent.search_by_metadata(topic="meditation", top_k=3)
        print(f"   ✅ Found {len(results)} teachings on meditation")
        
        # Test emotional state filter
        print("\n2. Search by Emotional State: 'anxious'")
        results = wisdom_agent.search_by_metadata(emotional_state="anxious", top_k=3)
        print(f"   ✅ Found {len(results)} teachings for anxiety")
        
        # Test combined filters
        print("\n3. Search by Multiple Filters: emotion='stressed' + topic='work'")
        results = wisdom_agent.search_by_metadata(
            emotional_state="stressed",
            topic="work",
            top_k=3
        )
        print(f"   ✅ Found {len(results)} teachings for work stress")
        
        return True
        
    except Exception as e:
        print(f"❌ Metadata search test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling(wisdom_agent):
    """Test 6: Error Handling"""
    print_separator("TEST 6: Error Handling")
    
    if not wisdom_agent:
        print("⏭️  Skipping (agent not initialized)")
        return False
    
    try:
        context = AgentContext(
            user_id=str(uuid.uuid4()),
            session_id=str(uuid.uuid4()),
            user_profile={'name': 'TestUser'}
        )
        
        # Test with very obscure query that likely won't match
        query = "xyzabc12345 qwertyuiop"
        
        print(f"\nTesting with nonsense query: '{query}'")
        response = wisdom_agent.process(query, context)
        
        print(f"✅ Error handled gracefully")
        print(f"   - Success: {response.success}")
        print(f"   - Fallback: {response.metadata.get('fallback', False)}")
        print(f"   - Confidence: {response.confidence:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


def run_all_tests():
    """Run all tests and report results"""
    print_separator("WISDOM AGENT TEST SUITE", "=")
    print("\nTesting the Wisdom Agent component...")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Test 1: Initialization
    passed, wisdom_agent = test_wisdom_agent_initialization()
    results['initialization'] = passed
    
    if not wisdom_agent:
        print_separator("TESTS ABORTED - Agent Not Initialized", "!")
        return
    
    # Test 2: Wisdom Retrieval
    results['wisdom_retrieval'] = test_wisdom_retrieval(wisdom_agent)
    
    # Test 3: Multiple Queries
    results['multiple_queries'] = test_multiple_queries(wisdom_agent)
    
    # Test 4: Context Enhancement
    results['context_enhancement'] = test_context_enhancement(wisdom_agent)
    
    # Test 5: Metadata Search
    results['metadata_search'] = test_metadata_search(wisdom_agent)
    
    # Test 6: Error Handling
    results['error_handling'] = test_error_handling(wisdom_agent)
    
    # Print summary
    print_separator("TEST SUMMARY", "=")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)
    
    print(f"\nTests Run: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"\nSuccess Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\nDetailed Results:")
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {test_name.replace('_', ' ').title()}")
    
    print_separator("", "=")
    
    if all(results.values()):
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("\n✅ Wisdom Agent is ready for integration!")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("\nPlease review the failures above and fix issues.")
    
    print_separator("", "=")


if __name__ == "__main__":
    run_all_tests()
