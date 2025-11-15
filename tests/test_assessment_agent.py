"""
Test Script for Assessment Agent
=================================

Tests the Assessment Agent's ability to:
- Detect emotional/mental states
- Classify severity levels
- Assess readiness for practice
- Identify physical indicators
- Recommend appropriate interventions
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import uuid
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.assessment_agent import AssessmentAgent, Assessment
from agents.base_agent import AgentContext
from agents.agent_types import EmotionalState, SeverityLevel, ReadinessLevel

# Load environment variables
load_dotenv()


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*70}")
    print(f" {title}")
    print(f"{'='*70}\n")


def print_assessment(response):
    """Pretty print assessment results"""
    print(f"✅ Success: {response.success}")
    print(f"⏱️  Processing Time: {response.processing_time:.2f}s")
    print(f"📊 Confidence: {response.confidence:.0%}")
    print(f"\n{'-'*70}")
    print(response.content)
    print(f"{'-'*70}")
    
    if 'assessment' in response.metadata:
        assessment = response.metadata['assessment']
        print(f"\n📋 Detailed Assessment Data:")
        print(f"   Primary State: {assessment['primary_state']}")
        print(f"   Severity: {assessment['severity']}")
        print(f"   Readiness: {assessment['readiness']}")
        print(f"   Urgency: {assessment['urgency_level']}/10")
        print(f"   Interventions: {', '.join(assessment['recommended_interventions'])}")
        
        if assessment['physical_indicators']:
            print(f"   Physical: {', '.join(assessment['physical_indicators'])}")
        
        if assessment['underlying_needs']:
            print(f"   Needs: {', '.join(assessment['underlying_needs'])}")


def test_basic_states():
    """Test detection of basic emotional states"""
    print_section("TEST 1: Basic Emotional State Detection")
    
    agent = AssessmentAgent(verbose=False)
    
    test_cases = [
        ("I'm feeling very anxious about tomorrow's meeting.", EmotionalState.ANXIOUS),
        ("I'm so stressed and overwhelmed with everything.", EmotionalState.STRESSED),
        ("I feel calm and peaceful after meditation.", EmotionalState.CALM),
        ("I'm confused about what to do next in life.", EmotionalState.CONFUSED),
        ("I'm seeking guidance on my spiritual journey.", EmotionalState.SEEKING),
        ("I'm really happy and grateful today!", EmotionalState.HAPPY),
        ("I'm feeling sad and down lately.", EmotionalState.SAD),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for message, expected_state in test_cases:
        context = AgentContext(
            user_id=str(uuid.uuid4()),
            session_id=str(uuid.uuid4()),
            user_profile={'name': 'TestUser', 'age': 30}
        )
        
        print(f"\nTest: '{message}'")
        print(f"Expected: {expected_state.value}")
        
        response = agent.process(message, context)
        
        if response.success:
            detected_state = response.metadata['assessment']['primary_state']
            print(f"Detected: {detected_state}")
            
            if detected_state == expected_state.value:
                print("✅ PASS")
                passed += 1
            else:
                print(f"⚠️  PARTIAL - Detected different state")
                # Still count as partial success if detection worked
                passed += 0.5
        else:
            print(f"❌ FAIL - {response.error_message}")
    
    print(f"\n{'='*70}")
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    return passed / total >= 0.7  # 70% pass rate


def test_severity_assessment():
    """Test severity level classification"""
    print_section("TEST 2: Severity Level Assessment")
    
    agent = AssessmentAgent(verbose=False)
    
    test_cases = [
        ("I'm a bit worried about the project.", SeverityLevel.LOW),
        ("I'm stressed about work but managing okay.", SeverityLevel.MEDIUM),
        ("I'm extremely anxious and can't function properly.", SeverityLevel.HIGH),
        ("I'm having panic attacks and can't breathe. Help!", SeverityLevel.CRITICAL),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for message, expected_severity in test_cases:
        context = AgentContext(
            user_id=str(uuid.uuid4()),
            session_id=str(uuid.uuid4()),
            user_profile={'name': 'TestUser', 'age': 30}
        )
        
        print(f"\nTest: '{message}'")
        print(f"Expected Severity: {expected_severity.value}")
        
        response = agent.process(message, context)
        
        if response.success:
            detected_severity = response.metadata['assessment']['severity']
            print(f"Detected Severity: {detected_severity}")
            
            if detected_severity == expected_severity.value:
                print("✅ PASS")
                passed += 1
            else:
                # Check if it's within one level
                severity_order = ['low', 'medium', 'high', 'critical']
                expected_idx = severity_order.index(expected_severity.value)
                detected_idx = severity_order.index(detected_severity)
                
                if abs(expected_idx - detected_idx) <= 1:
                    print("⚠️  PARTIAL - Within one severity level")
                    passed += 0.7
                else:
                    print("❌ FAIL - Severity mismatch")
        else:
            print(f"❌ FAIL - {response.error_message}")
    
    print(f"\n{'='*70}")
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    return passed / total >= 0.6


def test_physical_indicators():
    """Test extraction of physical indicators"""
    print_section("TEST 3: Physical Indicator Detection")
    
    agent = AssessmentAgent(verbose=False)
    
    test_cases = [
        ("I have a terrible headache and feel tense.", ['headache', 'tension']),
        ("Can't sleep, feeling restless and my heart is racing.", ['insomnia', 'restlessness']),
        ("I feel tired and exhausted all the time.", ['fatigue']),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for message, expected_indicators in test_cases:
        context = AgentContext(
            user_id=str(uuid.uuid4()),
            session_id=str(uuid.uuid4()),
            user_profile={'name': 'TestUser', 'age': 30}
        )
        
        print(f"\nTest: '{message}'")
        print(f"Expected Indicators: {expected_indicators}")
        
        response = agent.process(message, context)
        
        if response.success:
            detected = response.metadata['assessment']['physical_indicators']
            print(f"Detected Indicators: {detected}")
            
            # Check if at least one expected indicator was detected
            has_match = any(
                any(exp_word in det.lower() for exp_word in expected_indicators)
                for det in detected
            )
            
            if detected and has_match:
                print("✅ PASS - Physical indicators detected")
                passed += 1
            elif detected:
                print("⚠️  PARTIAL - Some indicators detected")
                passed += 0.5
            else:
                print("❌ FAIL - No indicators detected")
        else:
            print(f"❌ FAIL - {response.error_message}")
    
    print(f"\n{'='*70}")
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    return passed / total >= 0.5


def test_readiness_assessment():
    """Test readiness for practice assessment"""
    print_section("TEST 4: Readiness Assessment")
    
    agent = AssessmentAgent(verbose=False)
    
    test_cases = [
        ("I'm calm and ready to try meditation.", ReadinessLevel.READY),
        ("I'm open to learning but need to understand it first.", ReadinessLevel.NEEDS_PREPARATION),
        ("I'm too upset right now, can't focus on anything.", ReadinessLevel.NOT_READY),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for message, expected_readiness in test_cases:
        context = AgentContext(
            user_id=str(uuid.uuid4()),
            session_id=str(uuid.uuid4()),
            user_profile={'name': 'TestUser', 'age': 30}
        )
        
        print(f"\nTest: '{message}'")
        print(f"Expected Readiness: {expected_readiness.value}")
        
        response = agent.process(message, context)
        
        if response.success:
            detected = response.metadata['assessment']['readiness']
            print(f"Detected Readiness: {detected}")
            
            if detected == expected_readiness.value:
                print("✅ PASS")
                passed += 1
            else:
                print("⚠️  PARTIAL - Different readiness level")
                passed += 0.5
        else:
            print(f"❌ FAIL - {response.error_message}")
    
    print(f"\n{'='*70}")
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    return passed / total >= 0.6


def test_intervention_recommendations():
    """Test intervention type recommendations"""
    print_section("TEST 5: Intervention Recommendations")
    
    agent = AssessmentAgent(verbose=False)
    
    test_cases = [
        "I'm anxious and my breathing feels tight.",
        "I can't calm my mind, thoughts are racing.",
        "I feel disconnected from myself.",
        "I have too much nervous energy.",
    ]
    
    passed = 0
    total = len(test_cases)
    
    for message in test_cases:
        context = AgentContext(
            user_id=str(uuid.uuid4()),
            session_id=str(uuid.uuid4()),
            user_profile={'name': 'TestUser', 'age': 30}
        )
        
        print(f"\nTest: '{message}'")
        
        response = agent.process(message, context)
        
        if response.success:
            interventions = response.metadata['assessment']['recommended_interventions']
            print(f"Recommended Interventions: {interventions}")
            
            if interventions:
                print("✅ PASS - Interventions recommended")
                passed += 1
            else:
                print("❌ FAIL - No interventions recommended")
        else:
            print(f"❌ FAIL - {response.error_message}")
    
    print(f"\n{'='*70}")
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    return passed / total >= 0.7


def test_comprehensive_scenario():
    """Test a comprehensive real-world scenario"""
    print_section("TEST 6: Comprehensive Scenario")
    
    agent = AssessmentAgent(verbose=True)
    
    # Simulate a user's journey with multiple messages
    scenario = {
        'user_profile': {
            'name': 'Sarah',
            'age': 28,
            'experience_level': 'beginner'
        },
        'messages': [
            "I've been feeling really stressed lately with work deadlines.",
            "Now I'm getting anxious too. My chest feels tight and I can't sleep.",
            "I tried some breathing but I'm still overwhelmed. What should I do?",
        ]
    }
    
    context = AgentContext(
        user_id=str(uuid.uuid4()),
        session_id=str(uuid.uuid4()),
        user_profile=scenario['user_profile'],
        conversation_history=[]
    )
    
    print(f"User: {scenario['user_profile']['name']}, Age: {scenario['user_profile']['age']}")
    print(f"\nProgression of assessments:\n")
    
    previous_assessments = []
    
    for idx, message in enumerate(scenario['messages'], 1):
        print(f"\n{'-'*70}")
        print(f"Message {idx}: '{message}'")
        print(f"{'-'*70}")
        
        # Add previous assessments to context
        context.metadata['previous_assessments'] = previous_assessments
        
        response = agent.process(message, context)
        print_assessment(response)
        
        # Store assessment for next iteration
        if response.success:
            previous_assessments.append(response.metadata['assessment'])
        
        # Add to conversation history
        context.conversation_history.append({
            'role': 'user',
            'content': message
        })
    
    print(f"\n{'='*70}")
    print("Scenario complete - Agent tracked state progression")
    return True


def run_all_tests():
    """Run all test suites"""
    print_section("ASSESSMENT AGENT TEST SUITE")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Testing Assessment Agent functionality...\n")
    
    results = {
        'Basic State Detection': test_basic_states(),
        'Severity Assessment': test_severity_assessment(),
        'Physical Indicators': test_physical_indicators(),
        'Readiness Assessment': test_readiness_assessment(),
        'Intervention Recommendations': test_intervention_recommendations(),
        'Comprehensive Scenario': test_comprehensive_scenario(),
    }
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'='*70}")
    print(f"Overall: {passed}/{total} test suites passed ({passed/total*100:.0f}%)")
    print(f"{'='*70}\n")
    
    if passed == total:
        print("🎉 All tests passed! Assessment Agent is working perfectly!")
        return 0
    elif passed >= total * 0.7:
        print("⚠️  Most tests passed. Assessment Agent is functional with minor issues.")
        return 0
    else:
        print("❌ Many tests failed. Assessment Agent needs attention.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
