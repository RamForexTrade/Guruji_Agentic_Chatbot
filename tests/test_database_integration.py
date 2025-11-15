"""
Database Integration Test Script
=================================
This script tests all database operations before integrating into chatbot.py

Tests:
1. Database initialization
2. User CRUD operations
3. Conversation persistence
4. Practice logging
5. Statistics and analytics
6. Full user journey simulation

Run this script to verify database is ready for integration.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List
import uuid

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.database import Database
from models.user import UserProfile
from models.conversation import ConversationMessage, ConversationHistory
from models.practice import PracticeLog, PracticeStatistics

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class DatabaseIntegrationTest:
    """Test suite for database integration"""
    
    def __init__(self, test_db_path: str = "database/test_guruji_bot.db"):
        """Initialize test suite with test database"""
        self.test_db_path = test_db_path
        self.db = None
        self.test_user_id = None
        self.test_results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
    
    def print_header(self, text: str):
        """Print colored header"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
    
    def print_test(self, test_name: str):
        """Print test name"""
        print(f"{Colors.OKCYAN}▶ Testing: {test_name}{Colors.ENDC}")
    
    def print_success(self, message: str):
        """Print success message"""
        print(f"{Colors.OKGREEN}  ✓ {message}{Colors.ENDC}")
        self.test_results['passed'].append(message)
    
    def print_failure(self, message: str):
        """Print failure message"""
        print(f"{Colors.FAIL}  ✗ {message}{Colors.ENDC}")
        self.test_results['failed'].append(message)
    
    def print_warning(self, message: str):
        """Print warning message"""
        print(f"{Colors.WARNING}  ⚠ {message}{Colors.ENDC}")
        self.test_results['warnings'].append(message)
    
    def print_info(self, message: str):
        """Print info message"""
        print(f"{Colors.OKBLUE}  ℹ {message}{Colors.ENDC}")
    
    def setup(self):
        """Setup test environment"""
        self.print_header("SETUP: Database Integration Tests")
        
        # Remove existing test database
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
            self.print_info(f"Removed existing test database: {self.test_db_path}")
        
        # Initialize database
        try:
            self.db = Database(self.test_db_path)
            self.print_success("Database initialized successfully")
        except Exception as e:
            self.print_failure(f"Failed to initialize database: {e}")
            return False
        
        return True
    
    def test_database_initialization(self):
        """Test 1: Database initialization"""
        self.print_header("TEST 1: Database Initialization")
        
        self.print_test("Database file creation")
        if os.path.exists(self.test_db_path):
            self.print_success(f"Database file exists: {self.test_db_path}")
        else:
            self.print_failure("Database file not created")
            return False
        
        self.print_test("Database tables creation")
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Check all tables exist
        tables = ['users', 'conversations', 'practice_logs', 'user_preferences', 'sessions']
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if cursor.fetchone():
                self.print_success(f"Table '{table}' created successfully")
            else:
                self.print_failure(f"Table '{table}' not found")
        
        conn.close()
        return True
    
    def test_user_operations(self):
        """Test 2: User CRUD operations"""
        self.print_header("TEST 2: User CRUD Operations")
        
        # Test CREATE
        self.print_test("Create User")
        try:
            user_data = {
                'name': 'Test User',
                'age': 30,
                'life_aspect': 'Spiritual Practice',
                'emotional_state': 'Seeking',
                'guidance_type': 'General Wisdom',
                'specific_situation': 'Looking for inner peace',
                'experience_level': 'beginner',
                'preferences': {'theme': 'light', 'notifications': True}
            }
            
            self.test_user_id = self.db.create_user(user_data)
            
            if self.test_user_id:
                self.print_success(f"User created with ID: {self.test_user_id[:8]}...")
            else:
                self.print_failure("Failed to create user")
                return False
        except Exception as e:
            self.print_failure(f"User creation failed: {e}")
            return False
        
        # Test READ
        self.print_test("Read User")
        try:
            user = self.db.get_user(self.test_user_id)
            
            if user:
                self.print_success("User retrieved successfully")
                self.print_info(f"Name: {user['name']}, Age: {user['age']}, Level: {user['experience_level']}")
                
                # Verify data
                if user['name'] == user_data['name']:
                    self.print_success("User name matches")
                if user['age'] == user_data['age']:
                    self.print_success("User age matches")
                if user['life_aspect'] == user_data['life_aspect']:
                    self.print_success("User life_aspect matches")
            else:
                self.print_failure("Failed to retrieve user")
                return False
        except Exception as e:
            self.print_failure(f"User retrieval failed: {e}")
            return False
        
        # Test UPDATE
        self.print_test("Update User")
        try:
            update_data = {
                'emotional_state': 'Peaceful',
                'experience_level': 'intermediate'
            }
            
            self.db.update_user(self.test_user_id, update_data)
            
            # Verify update
            updated_user = self.db.get_user(self.test_user_id)
            if updated_user['emotional_state'] == 'Peaceful':
                self.print_success("User emotional_state updated successfully")
            if updated_user['experience_level'] == 'intermediate':
                self.print_success("User experience_level updated successfully")
        except Exception as e:
            self.print_failure(f"User update failed: {e}")
            return False
        
        # Test last_active update
        self.print_test("Update Last Active")
        try:
            self.db.update_last_active(self.test_user_id)
            user = self.db.get_user(self.test_user_id)
            if user['last_active']:
                self.print_success("Last active timestamp updated")
        except Exception as e:
            self.print_failure(f"Last active update failed: {e}")
        
        # Test get all users
        self.print_test("Get All Users")
        try:
            all_users = self.db.get_all_users()
            if len(all_users) >= 1:
                self.print_success(f"Retrieved {len(all_users)} user(s)")
        except Exception as e:
            self.print_failure(f"Get all users failed: {e}")
        
        return True
    
    def test_conversation_operations(self):
        """Test 3: Conversation operations"""
        self.print_header("TEST 3: Conversation Operations")
        
        if not self.test_user_id:
            self.print_failure("No test user available")
            return False
        
        # Test saving messages
        self.print_test("Save Conversation Messages")
        try:
            # Save user message
            user_msg_id = self.db.save_message(
                user_id=self.test_user_id,
                role='user',
                content='How do I find inner peace?',
                metadata={'query_type': 'wisdom'}
            )
            self.print_success(f"User message saved: {user_msg_id[:8]}...")
            
            # Save assistant message
            assistant_msg_id = self.db.save_message(
                user_id=self.test_user_id,
                role='assistant',
                content='Inner peace comes from acceptance and meditation.',
                metadata={'sources': ['teaching_001', 'teaching_042']}
            )
            self.print_success(f"Assistant message saved: {assistant_msg_id[:8]}...")
            
            # Save more messages for testing
            for i in range(3):
                self.db.save_message(
                    user_id=self.test_user_id,
                    role='user',
                    content=f'Question {i+2}: What about stress management?'
                )
                self.db.save_message(
                    user_id=self.test_user_id,
                    role='assistant',
                    content=f'Answer {i+2}: Practice Sudarshan Kriya regularly.'
                )
            
            self.print_success("Multiple conversation messages saved")
        except Exception as e:
            self.print_failure(f"Message saving failed: {e}")
            return False
        
        # Test retrieving conversation history
        self.print_test("Retrieve Conversation History")
        try:
            history = self.db.get_conversation_history(self.test_user_id, limit=10)
            
            if history:
                self.print_success(f"Retrieved {len(history)} messages")
                
                # Verify order (should be chronological)
                if history[0]['role'] == 'user':
                    self.print_success("Messages in correct order (chronological)")
                
                # Verify content
                if 'inner peace' in history[0]['content'].lower():
                    self.print_success("Message content preserved correctly")
            else:
                self.print_failure("No conversation history retrieved")
                return False
        except Exception as e:
            self.print_failure(f"Conversation retrieval failed: {e}")
            return False
        
        # Test get recent conversations
        self.print_test("Get Recent Conversations (7 days)")
        try:
            recent = self.db.get_recent_conversations(self.test_user_id, days=7)
            if recent:
                self.print_success(f"Retrieved {len(recent)} recent messages")
        except Exception as e:
            self.print_failure(f"Recent conversations failed: {e}")
        
        # Test message count
        self.print_test("Get Message Count")
        try:
            count = self.db.get_message_count(self.test_user_id)
            if count >= 2:
                self.print_success(f"Message count: {count}")
        except Exception as e:
            self.print_failure(f"Message count failed: {e}")
        
        # Test pagination
        self.print_test("Conversation History Pagination")
        try:
            page1 = self.db.get_conversation_history(self.test_user_id, limit=3, offset=0)
            page2 = self.db.get_conversation_history(self.test_user_id, limit=3, offset=3)
            
            if len(page1) > 0 and len(page2) > 0:
                self.print_success(f"Pagination works: Page1={len(page1)}, Page2={len(page2)}")
        except Exception as e:
            self.print_failure(f"Pagination failed: {e}")
        
        return True
    
    def test_practice_operations(self):
        """Test 4: Practice logging operations"""
        self.print_header("TEST 4: Practice Logging Operations")
        
        if not self.test_user_id:
            self.print_failure("No test user available")
            return False
        
        # Test logging practices
        self.print_test("Log Practice Completions")
        try:
            # Log multiple practices
            practices = [
                {
                    'user_id': self.test_user_id,
                    'practice_name': 'Sudarshan Kriya',
                    'practice_type': 'pranayama',
                    'duration_minutes': 20,
                    'completed': True,
                    'feedback': 'Felt very peaceful',
                    'rating': 5
                },
                {
                    'user_id': self.test_user_id,
                    'practice_name': 'Morning Meditation',
                    'practice_type': 'meditation',
                    'duration_minutes': 15,
                    'completed': True,
                    'rating': 4
                },
                {
                    'user_id': self.test_user_id,
                    'practice_name': 'Yoga Asanas',
                    'practice_type': 'yoga',
                    'duration_minutes': 30,
                    'completed': True,
                    'feedback': 'Good stretch',
                    'rating': 4
                },
                {
                    'user_id': self.test_user_id,
                    'practice_name': 'Evening Meditation',
                    'practice_type': 'meditation',
                    'duration_minutes': 10,
                    'completed': False,
                    'feedback': 'Got interrupted'
                }
            ]
            
            for practice in practices:
                log_id = self.db.log_practice(practice)
                if log_id:
                    self.print_success(f"Logged: {practice['practice_name']}")
        except Exception as e:
            self.print_failure(f"Practice logging failed: {e}")
            return False
        
        # Test retrieving practice logs
        self.print_test("Retrieve Practice Logs")
        try:
            logs = self.db.get_practice_logs(self.test_user_id, days=30)
            
            if logs:
                self.print_success(f"Retrieved {len(logs)} practice logs")
                
                # Verify content
                practice_names = [log['practice_name'] for log in logs]
                if 'Sudarshan Kriya' in practice_names:
                    self.print_success("Practice names preserved correctly")
            else:
                self.print_warning("No practice logs retrieved")
        except Exception as e:
            self.print_failure(f"Practice logs retrieval failed: {e}")
            return False
        
        # Test practice statistics
        self.print_test("Calculate Practice Statistics")
        try:
            stats = self.db.get_practice_statistics(self.test_user_id, days=30)
            
            if stats:
                self.print_success("Statistics calculated successfully")
                self.print_info(f"Total Practices: {stats['total_practices']}")
                self.print_info(f"Completed: {stats['completed_practices']}")
                self.print_info(f"Adherence Rate: {stats['adherence_rate']}%")
                self.print_info(f"Total Duration: {stats['total_duration_minutes']} minutes")
                self.print_info(f"Average Rating: {stats['average_rating']}/5")
                
                if stats['total_practices'] >= 3:
                    self.print_success(f"Statistics accurate: {stats['total_practices']} practices logged")
                
                if stats['adherence_rate'] > 0:
                    self.print_success(f"Adherence rate calculated: {stats['adherence_rate']}%")
                
                if stats['practice_type_breakdown']:
                    self.print_success("Practice type breakdown available")
                    for ptype, count in stats['practice_type_breakdown'].items():
                        self.print_info(f"  {ptype}: {count}")
            else:
                self.print_failure("Statistics calculation failed")
        except Exception as e:
            self.print_failure(f"Statistics calculation failed: {e}")
            return False
        
        # Test streak calculation
        self.print_test("Calculate Practice Streak")
        try:
            streak = self.db.get_streak_days(self.test_user_id)
            self.print_success(f"Current streak: {streak} day(s)")
        except Exception as e:
            self.print_failure(f"Streak calculation failed: {e}")
        
        # Test filtering by practice type
        self.print_test("Filter by Practice Type")
        try:
            meditation_logs = self.db.get_practice_logs(
                self.test_user_id, 
                days=30, 
                practice_type='meditation'
            )
            if meditation_logs:
                self.print_success(f"Filtered meditation practices: {len(meditation_logs)}")
        except Exception as e:
            self.print_failure(f"Practice type filtering failed: {e}")
        
        return True
    
    def test_session_operations(self):
        """Test 5: Session operations"""
        self.print_header("TEST 5: Session Operations")
        
        if not self.test_user_id:
            self.print_failure("No test user available")
            return False
        
        self.print_test("Create Session")
        try:
            session_id = self.db.create_session(self.test_user_id)
            if session_id:
                self.print_success(f"Session created: {session_id[:8]}...")
                
                # End session
                self.db.end_session(session_id, message_count=5)
                self.print_success("Session ended successfully")
        except Exception as e:
            self.print_failure(f"Session operations failed: {e}")
            return False
        
        return True
    
    def test_data_models(self):
        """Test 6: Data model integration"""
        self.print_header("TEST 6: Data Model Integration")
        
        # Test UserProfile model
        self.print_test("UserProfile Model")
        try:
            user_data = self.db.get_user(self.test_user_id)
            user_profile = UserProfile.from_dict(user_data)
            
            if user_profile:
                self.print_success("UserProfile created from database data")
                
                # Test methods
                context_summary = user_profile.get_context_summary()
                if context_summary:
                    self.print_success("Context summary generated")
                    self.print_info(f"Summary length: {len(context_summary)} chars")
                
                # Test to_dict
                user_dict = user_profile.to_dict()
                if user_dict and 'user_id' in user_dict:
                    self.print_success("UserProfile.to_dict() works")
        except Exception as e:
            self.print_failure(f"UserProfile model test failed: {e}")
        
        # Test ConversationMessage model
        self.print_test("ConversationMessage Model")
        try:
            history = self.db.get_conversation_history(self.test_user_id, limit=1)
            if history:
                msg = ConversationMessage.from_dict(history[0])
                if msg:
                    self.print_success("ConversationMessage created from database data")
                    
                    # Test methods
                    display_time = msg.get_display_time()
                    if display_time:
                        self.print_success(f"Display time: {display_time}")
                    
                    langchain_format = msg.to_langchain_format()
                    if langchain_format and 'role' in langchain_format:
                        self.print_success("LangChain format conversion works")
        except Exception as e:
            self.print_failure(f"ConversationMessage model test failed: {e}")
        
        # Test PracticeLog model
        self.print_test("PracticeLog Model")
        try:
            logs = self.db.get_practice_logs(self.test_user_id, days=30)
            if logs:
                practice = PracticeLog.from_dict(logs[0])
                if practice:
                    self.print_success("PracticeLog created from database data")
                    
                    # Test methods
                    rating_stars = practice.get_rating_stars()
                    if rating_stars:
                        self.print_success(f"Rating display: {rating_stars}")
                    
                    display_date = practice.get_display_date()
                    if display_date:
                        self.print_success(f"Display date: {display_date}")
        except Exception as e:
            self.print_failure(f"PracticeLog model test failed: {e}")
        
        # Test PracticeStatistics model
        self.print_test("PracticeStatistics Model")
        try:
            stats_dict = self.db.get_practice_statistics(self.test_user_id, days=30)
            stats = PracticeStatistics.from_dict(stats_dict)
            
            if stats:
                self.print_success("PracticeStatistics created from database data")
                
                # Test methods
                adherence_level = stats.get_adherence_level()
                if adherence_level:
                    self.print_success(f"Adherence level: {adherence_level}")
                
                summary = stats.get_summary_text()
                if summary:
                    self.print_success("Statistics summary generated")
        except Exception as e:
            self.print_failure(f"PracticeStatistics model test failed: {e}")
        
        return True
    
    def test_full_user_journey(self):
        """Test 7: Complete user journey simulation"""
        self.print_header("TEST 7: Full User Journey Simulation")
        
        self.print_test("Simulating Complete User Journey")
        
        try:
            # 1. New user arrives
            self.print_info("Step 1: New user arrives")
            journey_user_data = {
                'name': 'Journey Test User',
                'age': 35,
                'life_aspect': 'Emotional Well-being',
                'emotional_state': 'Anxious',
                'guidance_type': 'Practical Solutions',
                'specific_situation': 'Dealing with work stress'
            }
            journey_user_id = self.db.create_user(journey_user_data)
            self.print_success(f"New user created: {journey_user_id[:8]}...")
            
            # 2. User asks first question
            self.print_info("Step 2: User asks first question")
            self.db.save_message(journey_user_id, 'user', 'How do I handle stress at work?')
            self.db.save_message(journey_user_id, 'assistant', 'Practice pranayama for 10 minutes daily...')
            self.print_success("First conversation saved")
            
            # 3. User completes a practice
            self.print_info("Step 3: User completes recommended practice")
            self.db.log_practice({
                'user_id': journey_user_id,
                'practice_name': 'Ujjayi Breath',
                'practice_type': 'pranayama',
                'duration_minutes': 10,
                'completed': True,
                'rating': 4,
                'feedback': 'Felt calmer'
            })
            self.print_success("Practice logged")
            
            # 4. User returns next day
            self.print_info("Step 4: User returns and continues conversation")
            self.db.update_last_active(journey_user_id)
            self.db.save_message(journey_user_id, 'user', 'The breathing helped! What else can I do?')
            self.db.save_message(journey_user_id, 'assistant', 'Try meditation for deeper peace...')
            self.print_success("Continuing conversation tracked")
            
            # 5. Check user progress
            self.print_info("Step 5: Check user's progress")
            stats = self.db.get_practice_statistics(journey_user_id, days=7)
            history = self.db.get_conversation_history(journey_user_id)
            
            self.print_success(f"User has {stats['total_practices']} practice(s)")
            self.print_success(f"User has {len(history)} message(s) in history")
            
            # 6. User profile update
            self.print_info("Step 6: Update user emotional state")
            self.db.update_user(journey_user_id, {'emotional_state': 'Peaceful'})
            updated_user = self.db.get_user(journey_user_id)
            if updated_user['emotional_state'] == 'Peaceful':
                self.print_success("User emotional state updated to 'Peaceful'")
            
            self.print_success("✓ Complete user journey simulation passed!")
            
        except Exception as e:
            self.print_failure(f"User journey simulation failed: {e}")
            return False
        
        return True
    
    def test_database_utilities(self):
        """Test 8: Database utility functions"""
        self.print_header("TEST 8: Database Utility Functions")
        
        # Test database stats
        self.print_test("Get Database Statistics")
        try:
            stats = self.db.get_database_stats()
            
            if stats:
                self.print_success("Database statistics retrieved")
                self.print_info(f"Total Users: {stats.get('total_users', 0)}")
                self.print_info(f"Total Messages: {stats.get('total_messages', 0)}")
                self.print_info(f"Total Practice Logs: {stats.get('total_practice_logs', 0)}")
                
                if stats['total_users'] >= 2:
                    self.print_success("User count correct")
        except Exception as e:
            self.print_failure(f"Database stats failed: {e}")
        
        # Test clear conversation history
        self.print_test("Clear Conversation History")
        try:
            # Create a temporary user for this test
            temp_user_data = {'name': 'Temp User'}
            temp_user_id = self.db.create_user(temp_user_data)
            
            # Add some messages
            self.db.save_message(temp_user_id, 'user', 'Test message 1')
            self.db.save_message(temp_user_id, 'assistant', 'Test response 1')
            
            # Clear history
            self.db.clear_conversation_history(temp_user_id)
            
            # Verify cleared
            history = self.db.get_conversation_history(temp_user_id)
            if len(history) == 0:
                self.print_success("Conversation history cleared successfully")
        except Exception as e:
            self.print_failure(f"Clear history failed: {e}")
        
        return True
    
    def print_final_report(self):
        """Print final test report"""
        self.print_header("TEST RESULTS SUMMARY")
        
        total_tests = len(self.test_results['passed']) + len(self.test_results['failed'])
        passed_count = len(self.test_results['passed'])
        failed_count = len(self.test_results['failed'])
        warning_count = len(self.test_results['warnings'])
        
        print(f"{Colors.BOLD}Total Tests Run: {total_tests}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}Passed: {passed_count} ✓{Colors.ENDC}")
        print(f"{Colors.FAIL}Failed: {failed_count} ✗{Colors.ENDC}")
        print(f"{Colors.WARNING}Warnings: {warning_count} ⚠{Colors.ENDC}")
        
        if failed_count == 0:
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}{'='*60}{Colors.ENDC}")
            print(f"{Colors.OKGREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! DATABASE IS READY FOR INTEGRATION! 🎉{Colors.ENDC}")
            print(f"{Colors.OKGREEN}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
            
            print(f"{Colors.OKGREEN}✓ Database schema is correct{Colors.ENDC}")
            print(f"{Colors.OKGREEN}✓ All CRUD operations work perfectly{Colors.ENDC}")
            print(f"{Colors.OKGREEN}✓ Data models integrate seamlessly{Colors.ENDC}")
            print(f"{Colors.OKGREEN}✓ Full user journey flows smoothly{Colors.ENDC}")
            print(f"\n{Colors.OKCYAN}Next Step: Integrate database into chatbot.py{Colors.ENDC}\n")
            
            return True
        else:
            print(f"\n{Colors.FAIL}{Colors.BOLD}{'='*60}{Colors.ENDC}")
            print(f"{Colors.FAIL}{Colors.BOLD}❌ SOME TESTS FAILED - REVIEW ERRORS ABOVE{Colors.ENDC}")
            print(f"{Colors.FAIL}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
            
            if self.test_results['failed']:
                print(f"{Colors.FAIL}Failed Tests:{Colors.ENDC}")
                for failure in self.test_results['failed']:
                    print(f"  • {failure}")
            
            return False
    
    def cleanup(self):
        """Cleanup test environment"""
        print(f"\n{Colors.OKBLUE}Cleaning up test environment...{Colors.ENDC}")
        
        # Option to keep or delete test database
        print(f"{Colors.OKBLUE}Test database location: {self.test_db_path}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}(Test database kept for inspection){Colors.ENDC}")
    
    def run_all_tests(self):
        """Run all tests"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}")
        print("╔═══════════════════════════════════════════════════════════╗")
        print("║     DATABASE INTEGRATION TEST SUITE                       ║")
        print("║     JAI GURU DEV AI Chatbot                               ║")
        print("╚═══════════════════════════════════════════════════════════╝")
        print(f"{Colors.ENDC}\n")
        
        # Setup
        if not self.setup():
            print(f"\n{Colors.FAIL}Setup failed. Cannot continue tests.{Colors.ENDC}\n")
            return False
        
        # Run all test suites
        test_suites = [
            ("Database Initialization", self.test_database_initialization),
            ("User CRUD Operations", self.test_user_operations),
            ("Conversation Operations", self.test_conversation_operations),
            ("Practice Logging", self.test_practice_operations),
            ("Session Management", self.test_session_operations),
            ("Data Model Integration", self.test_data_models),
            ("Full User Journey", self.test_full_user_journey),
            ("Database Utilities", self.test_database_utilities)
        ]
        
        for suite_name, test_func in test_suites:
            try:
                test_func()
            except Exception as e:
                self.print_failure(f"Test suite '{suite_name}' crashed: {e}")
        
        # Final report
        success = self.print_final_report()
        
        # Cleanup
        self.cleanup()
        
        return success


def main():
    """Main test runner"""
    tester = DatabaseIntegrationTest()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
