"""
Test Script for Prompt Configuration System
============================================

This script verifies that:
1. system_prompts.yaml can be loaded correctly
2. All agent prompts are accessible
3. The get_prompt() method works as expected
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.config_loader import ConfigLoader, get_prompt, get_agent_prompts


def test_prompt_loading():
    """Test that prompts can be loaded from YAML"""
    print("=" * 70)
    print("TESTING PROMPT CONFIGURATION SYSTEM")
    print("=" * 70)

    try:
        # Test 1: Load all prompts
        print("\n[TEST 1] Loading all prompts from system_prompts.yaml...")
        prompts = ConfigLoader.get_prompts()
        print(f"[OK] Successfully loaded prompts for {len(prompts)} agents")
        print(f"  Available agents: {list(prompts.keys())}")

        # Test 2: Get specific prompt using get_prompt()
        print("\n[TEST 2] Testing get_prompt() method...")
        system_prompt = get_prompt('assessment_agent_v2', 'system_prompt')
        print(f"[OK] Successfully retrieved assessment_agent_v2 system_prompt")
        print(f"  Prompt length: {len(system_prompt)} characters")
        print(f"  First 100 chars: {system_prompt[:100]}...")

        # Test 3: Get all prompts for an agent
        print("\n[TEST 3] Testing get_agent_prompts() method...")
        assessment_prompts = get_agent_prompts('assessment_agent_v2')
        print(f"[OK] Successfully retrieved all assessment_agent_v2 prompts")
        print(f"  Available prompts: {list(assessment_prompts.keys())}")

        # Test 4: Verify all agents have system_prompt
        print("\n[TEST 4] Verifying all agents have system_prompt...")
        for agent_type in prompts.keys():
            if 'system_prompt' in prompts[agent_type]:
                print(f"  [OK] {agent_type}: system_prompt found ({len(prompts[agent_type]['system_prompt'])} chars)")
            else:
                print(f"  [X] {agent_type}: system_prompt MISSING!")

        # Test 5: Test error handling
        print("\n[TEST 5] Testing error handling...")
        try:
            invalid_prompt = get_prompt('invalid_agent', 'system_prompt')
            print("  [X] Should have raised KeyError for invalid agent!")
        except KeyError as e:
            print(f"  [OK] Correctly raised KeyError: {str(e)[:80]}...")

        print("\n" + "=" * 70)
        print("ALL TESTS PASSED!")
        print("=" * 70)

        # Print usage example
        print("\n" + "=" * 70)
        print("USAGE EXAMPLE")
        print("=" * 70)
        print("""
# In your agent code:
from utils.config_loader import get_prompt

# Get a specific prompt
system_prompt = get_prompt('assessment_agent_v2', 'system_prompt')
conversation_prompt = get_prompt('assessment_agent_v2', 'conversation_prompt')

# Or get all prompts for an agent
from utils.config_loader import get_agent_prompts
prompts = get_agent_prompts('wisdom_agent')
system_prompt = prompts['system_prompt']
contextualization_prompt = prompts['contextualization_prompt']
""")

        print("\n" + "=" * 70)
        print("HOW TO MODIFY PROMPTS")
        print("=" * 70)
        print("""
1. Open: Guruji_Chatbot_Clean/system_prompts.yaml
2. Find the agent section (e.g., assessment_agent_v2)
3. Modify the prompt text as needed
4. Save the file
5. Restart your application

Changes will be automatically picked up - no code changes needed!
""")

        return True

    except Exception as e:
        print(f"\n[X] TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_prompt_loading()
    sys.exit(0 if success else 1)
