"""
Integration Test Suite for JAI GURU DEV AI Agents
=================================================

This test suite validates that all agents work together correctly
and that the complete user journey flows properly.

Test Scenarios:
1. Wisdom Query Flow
2. State Expression → Assessment → Practice Flow
3. Practice Completion → Progress Logging Flow
4. Complete End-to-End Journey
5. Error Handling and Fallbacks
6. Multi-Agent Coordination

Run this file to validate agent integration before deployment.
"""

import sys
import os
from datetime import datetime
import uuid

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from agents.orchestrator import OrchestratorAgent
from agents.wisdom_agent import WisdomAgent
from agents.assessment_agent import AssessmentAgent
from agents.practice_agent import PracticeAgent
from agents.progress_agent import ProgressAgent
from agents.base_agent import AgentContext


class Colors:
    """Terminal colors for pretty output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}")
    print(f"{text:^70}")
    print(f"{'='*70}{Colors.ENDC}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


def print_test_result(test_name, passed, details=""):
    """Print test result"""
    if passed:
        print_success(f"{test_name}")
        if details:
            print(f"   {details}")
    else:
        print_error(f"{test_name}")
        if details:
            print(f"   {details}")


def create_test_context():
    """Create a test user context"""
    return AgentContext(
        user_id=str(uuid.uuid4()),
        session_id=str(uuid.uuid4()),
        user_profile={
            'name': 'TestUser',
            'age': 30,
            'experience_level': 'beginner',
            'available_time_minutes': 15
        },
        conversation_history=[],
        metadata={}
    )


# ============================================================================
# Test Suite 1: Individual Agent Tests
# ============================================================================

def test_wisdom_agent():
    """Test Wisdom Agent individually"""
    print_header("TEST 1: WISDOM AGENT")
    
    try:
        agent = WisdomAgent(verbose=False)
        context = create_test_context()
        
        # Test query
        response = agent.process(
            "What is the meaning of inner peace?",
            context
        )
        
        # Validate response
        passed = (
            response.success and
            len(response.content) > 0 and
            response.confidence > 0.5
        )
        
        print_test_result(
            "Wisdom Agent - Basic Query",
            passed,
            f"Response length: {len(response.content)}, Confidence: {response.confidence:.2f}"
        )
        
        return passed
        
    except Exception as e:
        print_error(f"Wisdom Agent test failed: {e}")
        return False


def test_assessment_agent():
    """Test Assessment Agent individually"""
    print_header("TEST 2: ASSESSMENT AGENT")
    
    try:
        agent = AssessmentAgent(verbose=False)
        context = create_test_context()
        
        # Test query
        response = agent.process(
            "I'm feeling really anxious about work. My heart is racing and I can't sleep.",
            context
        )
        
        # Validate response
        assessment = response.metadata.get('assessment', {})
        passed = (
            response.success and
            assessment.get('primary_state') in ['anxious', 'stressed'] and
            response.confidence > 0.5
        )
        
        print_test_result(
            "Assessment Agent - State Detection",
            passed,
            f"State: {assessment.get('primary_state')}, Severity: {assessment.get('severity')}"
        )
        
        return passed
        
    except Exception as e:
        print_error(f"Assessment Agent test failed: {e}")
        return False


def test_practice_agent():
    """Test Practice Agent individually"""
    print_header("TEST 3: PRACTICE AGENT")
    
    try:
        agent = PracticeAgent(verbose=False)
        context = create_test_context()
        
        # Add assessment to context
        context.metadata['assessment'] = {
            'primary_state': 'anxious',
            'severity': 'high',
            'readiness': 'ready',
            'recommended_interventions': ['pranayama', 'meditation'],
            'underlying_needs': ['calm', 'peace'],
            'urgency_level': 7,
            'confidence': 0.85
        }
        
        # Test query
        response = agent.process(
            "Please recommend a practice",
            context
        )
        
        # Validate response
        recommendation = response.metadata.get('recommendation', {})
        passed = (
            response.success and
            recommendation.get('primary_practice') is not None and
            response.confidence > 0.5
        )
        
        print_test_result(
            "Practice Agent - Recommendation",
            passed,
            f"Practice: {recommendation.get('primary_practice', {}).get('name', 'N/A')}"
        )
        
        return passed
        
    except Exception as e:
        print_error(f"Practice Agent test failed: {e}")
        return False


def test_progress_agent():
    """Test Progress Agent individually"""
    print_header("TEST 4: PROGRESS AGENT")
    
    try:
        agent = ProgressAgent(verbose=False)
        context = create_test_context()
        
        # Add practice to context
        context.metadata['recommended_practice'] = {
            'practice_id': 'test_001',
            'name': 'Test Practice',
            'practice_type': 'meditation',
            'duration_minutes': 10
        }
        
        # Test logging
        response = agent.process(
            "I completed the practice! It was really helpful. 5/5",
            context
        )
        
        # Validate response
        passed = (
            response.success and
            'log' in response.metadata and
            len(context.metadata.get('practice_history', [])) > 0
        )
        
        print_test_result(
            "Progress Agent - Practice Logging",
            passed,
            f"Logged: {response.metadata.get('log', {}).get('practice_name', 'N/A')}"
        )
        
        return passed
        
    except Exception as e:
        print_error(f"Progress Agent test failed: {e}")
        return False


# ============================================================================
# Test Suite 2: Agent Integration Tests
# ============================================================================

def test_assessment_to_practice_flow():
    """Test Assessment Agent → Practice Agent flow"""
    print_header("TEST 5: ASSESSMENT → PRACTICE FLOW")
    
    try:
        assessment_agent = AssessmentAgent(verbose=False)
        practice_agent = PracticeAgent(verbose=False)
        context = create_test_context()
        
        # Step 1: Assessment
        print_info("Step 1: Running assessment...")
        assessment_response = assessment_agent.process(
            "I'm stressed and overwhelmed with work",
            context
        )
        
        # Step 2: Transfer assessment to context
        assessment = assessment_response.metadata.get('assessment')
        context.metadata['assessment'] = assessment
        
        # Step 3: Get practice recommendation
        print_info("Step 2: Getting practice recommendation...")
        practice_response = practice_agent.process(
            "Recommend a practice",
            context
        )
        
        # Validate flow
        passed = (
            assessment_response.success and
            practice_response.success and
            assessment is not None and
            practice_response.metadata.get('recommendation') is not None
        )
        
        print_test_result(
            "Assessment → Practice Integration",
            passed,
            f"State: {assessment.get('primary_state')} → Practice: {practice_response.metadata.get('recommendation', {}).get('primary_practice', {}).get('name', 'N/A')}"
        )
        
        return passed
        
    except Exception as e:
        print_error(f"Assessment → Practice flow test failed: {e}")
        return False


def test_practice_to_progress_flow():
    """Test Practice Agent → Progress Agent flow"""
    print_header("TEST 6: PRACTICE → PROGRESS FLOW")
    
    try:
        practice_agent = PracticeAgent(verbose=False)
        progress_agent = ProgressAgent(verbose=False)
        context = create_test_context()
        
        # Setup assessment
        context.metadata['assessment'] = {
            'primary_state': 'calm',
            'severity': 'low',
            'readiness': 'ready',
            'recommended_interventions': ['meditation'],
            'underlying_needs': ['peace'],
            'urgency_level': 3,
            'confidence': 0.8
        }
        
        # Step 1: Get practice recommendation
        print_info("Step 1: Getting practice recommendation...")
        practice_response = practice_agent.process(
            "Recommend a practice",
            context
        )
        
        # Step 2: Transfer practice to context
        recommendation = practice_response.metadata.get('recommendation', {})
        primary_practice = recommendation.get('primary_practice', {})
        
        context.metadata['recommended_practice'] = {
            'practice_id': primary_practice.get('practice_id'),
            'name': primary_practice.get('name'),
            'practice_type': primary_practice.get('practice_type'),
            'duration_minutes': primary_practice.get('duration_minutes')
        }
        
        # Step 3: Log practice completion
        print_info("Step 2: Logging practice completion...")
        progress_response = progress_agent.process(
            "Completed the practice! Feeling much better. 5/5",
            context
        )
        
        # Validate flow
        passed = (
            practice_response.success and
            progress_response.success and
            len(context.metadata.get('practice_history', [])) > 0
        )
        
        print_test_result(
            "Practice → Progress Integration",
            passed,
            f"Practice logged: {progress_response.metadata.get('log', {}).get('practice_name', 'N/A')}"
        )
        
        return passed
        
    except Exception as e:
        print_error(f"Practice → Progress flow test failed: {e}")
        return False


# ============================================================================
# Test Suite 3: End-to-End Journey Test
# ============================================================================

def test_complete_user_journey():
    """Test complete end-to-end user journey"""
    print_header("TEST 7: COMPLETE END-TO-END JOURNEY")
    
    try:
        # Initialize all agents
        assessment_agent = AssessmentAgent(verbose=False)
        practice_agent = PracticeAgent(verbose=False)
        progress_agent = ProgressAgent(verbose=False)
        context = create_test_context()
        
        print_info("Simulating complete user journey...")
        
        # Journey Step 1: User expresses state
        print_info("\n  Journey Step 1: User expresses anxiety")
        assessment_response = assessment_agent.process(
            "I'm feeling very anxious about an upcoming presentation. My heart is racing.",
            context
        )
        
        if not assessment_response.success:
            print_error("  Assessment failed")
            return False
        
        assessment = assessment_response.metadata.get('assessment')
        context.metadata['assessment'] = assessment
        print_success(f"  Assessment complete: {assessment.get('primary_state')}")
        
        # Journey Step 2: Get practice recommendation
        print_info("\n  Journey Step 2: Get practice recommendation")
        practice_response = practice_agent.process(
            "What practice should I do?",
            context
        )
        
        if not practice_response.success:
            print_error("  Practice recommendation failed")
            return False
        
        recommendation = practice_response.metadata.get('recommendation', {})
        primary_practice = recommendation.get('primary_practice', {})
        
        context.metadata['recommended_practice'] = {
            'practice_id': primary_practice.get('practice_id'),
            'name': primary_practice.get('name'),
            'practice_type': primary_practice.get('practice_type'),
            'duration_minutes': primary_practice.get('duration_minutes')
        }
        print_success(f"  Recommendation: {primary_practice.get('name')}")
        
        # Journey Step 3: Complete practice and log
        print_info("\n  Journey Step 3: Complete practice and log")
        progress_response = progress_agent.process(
            "Just finished the practice! Feeling much calmer now. 5/5",
            context
        )
        
        if not progress_response.success:
            print_error("  Progress logging failed")
            return False
        
        print_success("  Practice logged successfully")
        
        # Journey Step 4: View progress
        print_info("\n  Journey Step 4: View progress")
        stats_response = progress_agent.process(
            "Show me my progress",
            context
        )
        
        if not stats_response.success:
            print_error("  Progress stats failed")
            return False
        
        print_success("  Progress stats generated")
        
        # Final validation
        passed = (
            assessment_response.success and
            practice_response.success and
            progress_response.success and
            stats_response.success and
            len(context.metadata.get('practice_history', [])) > 0
        )
        
        print_test_result(
            "\nComplete Journey: State → Assessment → Practice → Logging → Stats",
            passed,
            "All steps completed successfully"
        )
        
        return passed
        
    except Exception as e:
        print_error(f"Complete journey test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# Test Runner
# ============================================================================

def run_all_tests():
    """Run all integration tests"""
    print_header("JAI GURU DEV AI - AGENT INTEGRATION TEST SUITE")
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = []
    
    # Individual agent tests
    results.append(("Wisdom Agent", test_wisdom_agent()))
    results.append(("Assessment Agent", test_assessment_agent()))
    results.append(("Practice Agent", test_practice_agent()))
    results.append(("Progress Agent", test_progress_agent()))
    
    # Integration tests
    results.append(("Assessment → Practice Flow", test_assessment_to_practice_flow()))
    results.append(("Practice → Progress Flow", test_practice_to_progress_flow()))
    results.append(("Complete User Journey", test_complete_user_journey()))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    print(f"\n{Colors.BOLD}Test Results:{Colors.ENDC}")
    print(f"  Total Tests: {total_count}")
    print(f"  Passed: {Colors.OKGREEN}{passed_count}{Colors.ENDC}")
    print(f"  Failed: {Colors.FAIL}{total_count - passed_count}{Colors.ENDC}")
    
    if passed_count == total_count:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! 🎉{Colors.ENDC}")
        print(f"\n{Colors.OKGREEN}The agent system is fully integrated and ready for deployment!{Colors.ENDC}")
    else:
        print(f"\n{Colors.WARNING}{Colors.BOLD}⚠️  SOME TESTS FAILED{Colors.ENDC}")
        print(f"\n{Colors.WARNING}Failed tests:{Colors.ENDC}")
        for name, passed in results:
            if not passed:
                print(f"  - {name}")
    
    print("\n" + "="*70 + "\n")
    
    return passed_count == total_count


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Tests interrupted by user{Colors.ENDC}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{Colors.FAIL}Test suite error: {e}{Colors.ENDC}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
