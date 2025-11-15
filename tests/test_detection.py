"""Test detection methods"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.assessment_agent_enhanced_v2 import AssessmentAgentEnhancedV2
from agents.agent_types import UserLocation, TimeAvailable, MealStatus

# Create agent instance (minimal initialization)
class MockContext:
    def __init__(self):
        self.user_profile = {'name': 'test'}
        self.conversation_history = []
        self.metadata = {}

agent = AssessmentAgentEnhancedV2(
    llm_provider="openai",
    model_name="gpt-4o-mini",
    temperature=0.7
)

print("=" * 70)
print("TESTING DETECTION METHODS")
print("=" * 70)

# Test location detection
print("\n[TEST 1] Location Detection:")
test_inputs = ["home", "at home", "work", "office", "at work", "outside"]
for input_text in test_inputs:
    result = agent._quick_detect_location(input_text)
    print(f"  Input: '{input_text}' -> {result.value}")

# Test time detection
print("\n[TEST 2] Time Detection:")
test_inputs = ["7", "12", "20", "seven minutes", "12 min", "about 20"]
for input_text in test_inputs:
    result = agent._detect_time_available(input_text)
    print(f"  Input: '{input_text}' -> {result.value}")

# Test meal detection
print("\n[TEST 3] Meal Detection:")
test_inputs = ["yes", "no", "I ate", "haven't eaten", "empty stomach", "just ate"]
for input_text in test_inputs:
    result = agent._detect_meal_status(input_text)
    print(f"  Input: '{input_text}' -> {result.value}")

print("\n" + "=" * 70)
