"""Test life situation extraction with the updated prompt"""
import json
from utils.config_loader import get_prompt
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# Test conversations that were previously failing
test_cases = [
    {
        "name": "Social isolation case",
        "conversation": """User: I don't know what is happening with me
Bot: Good evening, Muthu. Can I ask your age range so I can support you better? 18–25, 26–35, or 36–45?
User: 25
Bot: Thanks for sharing that, Muthu. That sounds tough — totally normal to feel lost when things aren't clicking. What's been making you feel this way?
User: nobody speaking to me""",
        "expected_situation": "relationship_love",
        "expected_emotion": "loneliness"
    },
    {
        "name": "Boss importance case",
        "conversation": """User: My boss is not giving importance to me""",
        "expected_situation": "finance_career",
        "expected_emotion": "frustration"
    },
    {
        "name": "Feeling lost case",
        "conversation": """User: nothing working out, I feel I am lost""",
        "expected_situation": "decision_making",
        "expected_emotion": "confusion"
    }
]

def test_extraction():
    """Test the extraction prompt with various cases"""
    print("=== TESTING LIFE SITUATION EXTRACTION ===\n")

    # Load extraction prompt
    extraction_template = get_prompt('assessment_agent_v2', 'extraction_prompt')
    extraction_prompt = PromptTemplate(
        template=extraction_template,
        input_variables=["conversation"]
    )

    # Initialize LLM (using gpt-4o-mini for testing)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

    passed = 0
    failed = 0

    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['name']}")
        print(f"Conversation: {test_case['conversation'][:100]}...")

        # Format and invoke
        formatted_prompt = extraction_prompt.format(conversation=test_case['conversation'])
        response = llm.invoke(formatted_prompt)

        try:
            # Parse JSON response
            result = json.loads(response.content)

            print(f"✓ Extracted situation: {result.get('life_situation')}")
            print(f"✓ Extracted emotion: {result.get('primary_emotion')}")
            print(f"✓ Confidence: {result.get('confidence')}")
            print(f"✓ Situation details: {result.get('situation_details')}")

            # Check if matches expected
            situation_match = result.get('life_situation') == test_case['expected_situation']
            emotion_match = result.get('primary_emotion') == test_case['expected_emotion']

            if situation_match:
                print(f"✅ PASS - Situation correctly extracted as '{test_case['expected_situation']}'")
                passed += 1
            else:
                print(f"❌ FAIL - Expected '{test_case['expected_situation']}' but got '{result.get('life_situation')}'")
                failed += 1

        except json.JSONDecodeError as e:
            print(f"❌ FAIL - Could not parse JSON: {e}")
            print(f"Response: {response.content}")
            failed += 1

        print("-" * 80)
        print()

    print(f"\n=== RESULTS ===")
    print(f"✅ Passed: {passed}/{len(test_cases)}")
    print(f"❌ Failed: {failed}/{len(test_cases)}")

    if failed == 0:
        print("\n🎉 All tests passed! Life situation extraction is working correctly.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Review extraction prompt or test expectations.")

if __name__ == "__main__":
    test_extraction()
