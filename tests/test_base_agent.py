"""
Test Base Agent Architecture
=============================

Tests to verify the base agent implementation works correctly.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent, AgentContext, AgentResponse
from agents.agent_types import AgentType
from langchain.tools import Tool
from typing import List
import uuid


class TestAgent(BaseAgent):
    """
    Simple test agent implementation to verify base class functionality.
    """
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.WISDOM,
            name="test_agent",
            verbose=True
        )
    
    def define_tools(self) -> List[Tool]:
        """Define simple test tools"""
        
        def greet_user(name: str) -> str:
            """Greet the user by name"""
            return f"Hello, {name}! Welcome to Gurudev's wisdom."
        
        def get_wisdom_quote() -> str:
            """Get a wisdom quote"""
            return "The quality of your life depends on the quality of your mind."
        
        tools = [
            Tool(
                name="greet_user",
                func=greet_user,
                description="Greet the user by name. Input should be the user's name."
            ),
            Tool(
                name="get_wisdom_quote",
                func=get_wisdom_quote,
                description="Get a wisdom quote from Gurudev's teachings."
            )
        ]
        
        return tools
    
    def get_system_prompt(self) -> str:
        """Get test agent system prompt"""
        return """You are a test agent for the Gurudev AI Companion chatbot.
        
Your role is to:
1. Greet users warmly
2. Share wisdom quotes when appropriate
3. Be compassionate and helpful

Available tools:
- greet_user: Greet the user by name
- get_wisdom_quote: Share a wisdom quote

Always be warm and supportive in your responses."""


def test_agent_initialization():
    """Test 1: Agent initialization"""
    print("\n" + "="*60)
    print("TEST 1: Agent Initialization")
    print("="*60)
    
    try:
        agent = TestAgent()
        print(f"✅ Agent created: {agent}")
        print(f"   - Name: {agent.name}")
        print(f"   - Type: {agent.agent_type}")
        print(f"   - LLM: {agent.llm.model_name}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_agent_tools():
    """Test 2: Tool definition"""
    print("\n" + "="*60)
    print("TEST 2: Tool Definition")
    print("="*60)
    
    try:
        agent = TestAgent()
        tools = agent.define_tools()
        print(f"✅ Tools defined: {len(tools)} tools")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_agent_executor():
    """Test 3: Agent executor initialization"""
    print("\n" + "="*60)
    print("TEST 3: Agent Executor Initialization")
    print("="*60)
    
    try:
        agent = TestAgent()
        agent.initialize_agent()
        print(f"✅ Agent executor initialized")
        print(f"   - Tools: {len(agent.tools)}")
        print(f"   - Executor: {type(agent.agent_executor).__name__}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_context_creation():
    """Test 4: Context creation"""
    print("\n" + "="*60)
    print("TEST 4: Context Creation")
    print("="*60)
    
    try:
        context = AgentContext(
            user_id=str(uuid.uuid4()),
            session_id=str(uuid.uuid4()),
            user_profile={
                'name': 'Test User',
                'age': 30,
                'emotional_state': 'curious'
            }
        )
        print(f"✅ Context created:")
        print(f"   - User ID: {context.user_id[:8]}...")
        print(f"   - Session ID: {context.session_id[:8]}...")
        print(f"   - User: {context.user_profile['name']}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_agent_processing():
    """Test 5: Agent processing (requires OpenAI API)"""
    print("\n" + "="*60)
    print("TEST 5: Agent Processing")
    print("="*60)
    
    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Skipped: OPENAI_API_KEY not set")
        print("   Set your API key in .env to test agent processing")
        return None
    
    try:
        # Create agent and context
        agent = TestAgent()
        context = AgentContext(
            user_id=str(uuid.uuid4()),
            session_id=str(uuid.uuid4()),
            user_profile={
                'name': 'Alice',
                'age': 28,
                'emotional_state': 'seeking guidance'
            }
        )
        
        # Process a simple query
        print("\n   Processing query: 'Hello, I need some guidance'")
        response = agent.process(
            input_text="Hello, I need some guidance",
            context=context
        )
        
        print(f"\n✅ Agent processed successfully:")
        print(f"   - Success: {response.success}")
        print(f"   - Confidence: {response.confidence:.2f}")
        print(f"   - Processing time: {response.processing_time:.2f}s")
        print(f"   - Tools used: {response.tools_used}")
        print(f"\n   Response:")
        print(f"   {response.content[:200]}...")
        
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling():
    """Test 6: Error handling"""
    print("\n" + "="*60)
    print("TEST 6: Error Handling")
    print("="*60)
    
    try:
        agent = TestAgent()
        
        # Create invalid context (missing user_id)
        context = AgentContext(
            user_id="",  # Invalid
            session_id=str(uuid.uuid4()),
            user_profile={'name': 'Test'}
        )
        
        response = agent.process(
            input_text="Test query",
            context=context
        )
        
        print(f"✅ Error handled gracefully:")
        print(f"   - Success: {response.success}")
        print(f"   - Error message: {response.error_message}")
        print(f"   - Fallback response provided: {bool(response.content)}")
        
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 BASE AGENT ARCHITECTURE TESTS")
    print("="*60)
    
    tests = [
        ("Agent Initialization", test_agent_initialization),
        ("Tool Definition", test_agent_tools),
        ("Agent Executor", test_agent_executor),
        ("Context Creation", test_context_creation),
        ("Agent Processing", test_agent_processing),
        ("Error Handling", test_error_handling)
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
    from dotenv import load_dotenv
    load_dotenv()
    
    success = run_all_tests()
    sys.exit(0 if success else 1)
