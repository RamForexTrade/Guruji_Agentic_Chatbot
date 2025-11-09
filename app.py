"""
JAI GURU DEV AI Companion - Complete Agentic System UI
=======================================================

This is the main Streamlit application integrating all agents:
- Orchestrator Agent (master coordinator)
- Wisdom Agent (RAG-based wisdom retrieval)
- Assessment Agent (user state analysis)
- Practice Agent (personalized recommendations)
- Progress Agent (tracking and insights)

Features:
✅ Multi-agent orchestration
✅ User profile management
✅ Conversation history
✅ Practice recommendations
✅ Progress tracking
✅ Statistics dashboard
✅ Database persistence
✅ Vector DB integration
✅ Actionable step detection from wisdom responses
✅ Google Calendar integration for practice scheduling
"""

import streamlit as st
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import uuid
from typing import Dict, Any, List, Optional

# Load environment variables
load_dotenv()

# Configuration Loader
from utils.config_loader import (
    get_default_provider,
    get_provider_for_agent,
    get_model_for_provider,
    get_temperature_for_provider
)

# Agent imports
from agents.orchestrator import OrchestratorAgent
from agents.base_agent import AgentContext
from agents.agent_types import AgentType, EmotionalState, PracticeType

# Database imports
from utils.database import Database
from models.user import UserProfile

# Integration imports - FIXED: Added missing imports
from integrations.actionable_detector import (
    ActionableStepDetector, 
    create_practice_from_actionable_step,
    format_actionable_step_for_logging
)
from integrations.google_calendar import (
    GoogleCalendarIntegration,
    initialize_calendar,
    format_practice_for_calendar
)

# Configure page
st.set_page_config(
    page_title="🙏 JAI GURU DEV AI Companion",
    page_icon="🙏",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "JAI GURU DEV AI - Your Spiritual Companion based on Gurudev Sri Sri Ravi Shankar's Teachings"
    }
)

# Custom CSS
st.markdown("""
<style>
    /* Main theme - Saffron */
    .main {
        background-color: #FFF8DC;
    }
    
    .stApp {
        background: linear-gradient(135deg, #FFF8DC 0%, #FFEFD5 100%);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #8B4513 !important;
        font-family: 'serif';
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: white !important;
        border-left: 4px solid #FF8C00 !important;
        border-radius: 8px !important;
        padding: 15px !important;
        margin: 10px 0 !important;
    }
    
    /* User message */
    [data-testid="stChatMessageContent"][data-message-author="user"] {
        background-color: #FFE4B5 !important;
        border-left-color: #FF8C00 !important;
    }
    
    /* Assistant message */
    [data-testid="stChatMessageContent"][data-message-author="assistant"] {
        background-color: #FFF8E7 !important;
        border-left-color: #DAA520 !important;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #FF8C00 !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        border: none !important;
    }
    
    .stButton > button:hover {
        background-color: #FF7000 !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFEFD5 !important;
    }
    
    /* Metrics */
    [data-testid="stMetric"] {
        background-color: white !important;
        padding: 15px !important;
        border-radius: 8px !important;
        border: 2px solid #FF8C00 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #FFE4B5 !important;
        color: #8B4513 !important;
        font-weight: bold !important;
    }
    
    /* Success/Info boxes */
    .stSuccess {
        background-color: #90EE90 !important;
        border-left: 4px solid #228B22 !important;
    }
    
    .stInfo {
        background-color: #ADD8E6 !important;
        border-left: 4px solid #4169E1 !important;
    }
    
    .stWarning {
        background-color: #FFE4B5 !important;
        border-left: 4px solid #FF8C00 !important;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# Initialize Components
# ============================================================================

@st.cache_resource
def initialize_agents():
    """Initialize all agents (cached to persist across reruns)"""
    try:
        print("🚀 Initializing agent system...")
        default_provider = get_default_provider()
        print(f"📡 LLM Provider: {default_provider.upper()}")

        # Get provider configuration
        orchestrator_provider = get_provider_for_agent("orchestrator")
        assessment_provider = get_provider_for_agent("assessment")
        practice_provider = get_provider_for_agent("practice")
        progress_provider = get_provider_for_agent("progress")

        # Initialize orchestrator
        orchestrator = OrchestratorAgent(
            llm_provider=orchestrator_provider,
            model_name=get_model_for_provider(orchestrator_provider),
            temperature=get_temperature_for_provider(orchestrator_provider),
            verbose=False
        )
        print(f"✅ Orchestrator initialized ({orchestrator_provider})")

        # Initialize specialized agents
        from agents.wisdom_agent import WisdomAgent
        from agents.assessment_agent_enhanced_v2 import EnhancedAssessmentAgentV2
        from agents.practice_agent import PracticeAgent
        from agents.progress_agent import ProgressAgent

        print("🔧 Initializing Wisdom Agent...")
        wisdom_agent = WisdomAgent(
            config_path="config.yaml",
            knowledge_base_path="Knowledge_Base",
            verbose=False
        )
        print("✅ Wisdom Agent initialized")

        print(f"🔧 Initializing Enhanced Assessment Agent V2 - Deeply Empathetic ({assessment_provider})...")
        assessment_agent = EnhancedAssessmentAgentV2(
            llm_provider=assessment_provider,
            model_name=get_model_for_provider(assessment_provider),
            temperature=0.8,  # Higher for more empathetic, natural responses
            verbose=False
        )
        print(f"✅ Enhanced Assessment Agent initialized ({assessment_provider})")

        print(f"🔧 Initializing Practice Agent ({practice_provider})...")
        practice_agent = PracticeAgent(
            llm_provider=practice_provider,
            model_name=get_model_for_provider(practice_provider),
            temperature=get_temperature_for_provider(practice_provider),
            verbose=False
        )
        print(f"✅ Practice Agent initialized ({practice_provider})")

        print(f"🔧 Initializing Progress Agent ({progress_provider})...")
        progress_agent = ProgressAgent(
            llm_provider=progress_provider,
            model_name=get_model_for_provider(progress_provider),
            temperature=get_temperature_for_provider(progress_provider),
            verbose=False
        )
        print(f"✅ Progress Agent initialized ({progress_provider})")
        
        # Register specialized agents with orchestrator
        print("🔧 Registering agents with orchestrator...")
        orchestrator.set_specialized_agents(
            wisdom_agent=wisdom_agent,
            assessment_agent=assessment_agent,
            practice_agent=practice_agent,
            progress_agent=progress_agent
        )
        print("✅ All agents registered")
        
        return {
            'orchestrator': orchestrator,
            'wisdom_agent': wisdom_agent,
            'assessment_agent': assessment_agent,
            'practice_agent': practice_agent,
            'progress_agent': progress_agent,
            'initialized': True
        }
        
    except Exception as e:
        print(f"❌ Error initializing agents: {e}")
        import traceback
        traceback.print_exc()
        st.error(f"Error initializing agents: {e}")
        return {'orchestrator': None, 'initialized': False}


@st.cache_resource
def initialize_database():
    """Initialize database (cached)"""
    try:
        db = Database()
        return db
    except Exception as e:
        st.error(f"Error initializing database: {e}")
        return None


# ============================================================================
# Session State Initialization
# ============================================================================

def init_session_state():
    """Initialize all session state variables"""
    
    # User session
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = None
    
    # Conversation
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    # Agent context
    if 'agent_context' not in st.session_state:
        st.session_state.agent_context = None
    
    # Assessment results
    if 'current_assessment' not in st.session_state:
        st.session_state.current_assessment = None
    
    # Practice recommendation
    if 'current_recommendation' not in st.session_state:
        st.session_state.current_recommendation = None
    
    # Practice history
    if 'practice_history' not in st.session_state:
        st.session_state.practice_history = []
    
    # UI state
    if 'show_practice_log' not in st.session_state:
        st.session_state.show_practice_log = False
    
    if 'show_progress' not in st.session_state:
        st.session_state.show_progress = False
    
    # FIXED: Added calendar integration state
    if 'calendar_integration' not in st.session_state:
        st.session_state.calendar_integration = None
    
    if 'calendar_authenticated' not in st.session_state:
        st.session_state.calendar_authenticated = False
    
    if 'show_calendar_setup' not in st.session_state:
        st.session_state.show_calendar_setup = False
    
    # Calendar authorization flow state
    if 'calendar_auth_in_progress' not in st.session_state:
        st.session_state.calendar_auth_in_progress = False
    
    if 'calendar_auth_url' not in st.session_state:
        st.session_state.calendar_auth_url = None


# ============================================================================
# User Management Functions
# ============================================================================

def render_user_selection(db):
    """Render user selection/creation in sidebar"""
    st.sidebar.markdown("### 👤 User Profile")
    
    # Get all users
    users = db.get_all_users()
    
    if users:
        # User selection
        user_options = ["Create New User"] + [f"{u['name']} (ID: {u['user_id'][:8]}...)" for u in users]
        selected = st.sidebar.selectbox(
            "Select User",
            options=user_options,
            key="user_selector"
        )
        
        if selected != "Create New User" and selected != st.session_state.get('last_selected_user'):
            # Extract user_id from selection
            user_id = selected.split("ID: ")[1].split("...")[0]
            
            # Find full user_id
            for user in users:
                if user['user_id'].startswith(user_id):
                    load_user(user, db)
                    st.session_state.last_selected_user = selected
                    st.rerun()
                    break
        
        if selected == "Create New User":
            render_user_creation(db)
    else:
        # No users yet, show creation form
        render_user_creation(db)


def render_user_creation(db):
    """Render user creation form"""
    st.sidebar.markdown("#### Create Your Profile")
    
    with st.sidebar.form("user_creation_form"):
        name = st.text_input("Name *", placeholder="Enter your name")
        age = st.number_input("Age", min_value=1, max_value=120, value=30)
        
        experience_level = st.selectbox(
            "Spiritual Practice Experience",
            ["beginner", "intermediate", "advanced"]
        )
        
        life_aspect = st.text_area(
            "What brings you here?",
            placeholder="e.g., seeking peace, dealing with stress, spiritual growth..."
        )
        
        submitted = st.form_submit_button("Create Profile 🙏")
        
        if submitted:
            if not name:
                st.sidebar.error("Please enter your name")
            else:
                # Create user profile
                user_id = str(uuid.uuid4())
                
                user_data = {
                    'user_id': user_id,
                    'name': name,
                    'age': age,
                    'experience_level': experience_level,
                    'life_aspect': life_aspect,
                    'emotional_state': 'neutral',
                    'created_at': datetime.now()
                }
                
                try:
                    # Create user and get user_id
                    created_user_id = db.create_user(user_data)
                    
                    # Verify user was created successfully
                    if not created_user_id:
                        st.sidebar.error("Failed to create user. Please try again.")
                        return
                    
                    # Load the new user
                    user = db.get_user(created_user_id)
                    
                    # Verify user was retrieved successfully
                    if not user:
                        st.sidebar.error("User created but could not be loaded. Please refresh and select your profile.")
                        return
                    
                    load_user(user, db)
                    
                    st.sidebar.success(f"Welcome, {name}! 🙏")
                    st.rerun()
                    
                except Exception as e:
                    st.sidebar.error(f"Error creating user: {str(e)}")
                    import traceback
                    st.sidebar.error(f"Details: {traceback.format_exc()}")


def load_user(user: Dict[str, Any], db):
    """Load user and their data"""
    # Safety check
    if not user:
        st.error("Invalid user data. Cannot load user.")
        return
    
    st.session_state.user_id = user['user_id']
    st.session_state.user_profile = user
    
    # Load conversation history
    history = db.get_conversation_history(user['user_id'])
    st.session_state.conversation_history = history
    
    # Load practice history
    practices = db.get_practice_logs(user['user_id'], days=90)
    st.session_state.practice_history = practices
    
    # Create agent context
    st.session_state.agent_context = AgentContext(
        user_id=user['user_id'],
        session_id=str(uuid.uuid4()),
        user_profile={
            'name': user['name'],
            'age': user.get('age'),
            'experience_level': user.get('experience_level', 'beginner'),
            'life_aspect': user.get('life_aspect', ''),
            'emotional_state': user.get('emotional_state', 'neutral')
        },
        conversation_history=history,
        metadata={
            'practice_history': practices
        }
    )
    
    # Convert history to chat format
    messages = []
    for msg in history[-10:]:  # Last 10 messages
        messages.append({
            'role': msg['role'],
            'content': msg['content']
        })
    st.session_state.messages = messages
    
    # FIXED: Initialize calendar integration for user
    try:
        calendar = initialize_calendar(user['user_id'])
        st.session_state.calendar_integration = calendar
        st.session_state.calendar_authenticated = calendar.is_authenticated()
    except Exception as e:
        print(f"Calendar initialization error: {e}")
        st.session_state.calendar_integration = None
        st.session_state.calendar_authenticated = False


# ============================================================================
# Chat Interface
# ============================================================================

def render_chat_interface(agents, db):
    """Render main chat interface"""
    
    if not st.session_state.user_profile:
        st.info("👈 Please select or create a user profile in the sidebar to begin")
        return
    
    # Welcome message
    st.markdown(f"### 🙏 Namaste, {st.session_state.user_profile['name']}!")
    st.markdown("*Ask me anything about spiritual wisdom, practices, or your journey...*")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get orchestrator
        orchestrator = agents['orchestrator']
        
        # Process with orchestrator
        with st.chat_message("assistant"):
            with st.spinner("🧘 Thinking..."):
                try:
                    # Update context with latest info
                    context = st.session_state.agent_context
                    context.conversation_history = st.session_state.conversation_history
                    context.metadata['practice_history'] = st.session_state.practice_history
                    
                    # Process through orchestrator
                    response = orchestrator.process(
                        input_text=prompt,
                        context=context,
                        chat_history=None
                    )
                    
                    # Display response
                    st.markdown(response.content)
                    
                    # Extract assessment and recommendation from nested agent responses
                    agent_responses = response.metadata.get('agent_responses', [])
                    
                    # Save assessment if present
                    if 'assessment' in response.metadata:
                        st.session_state.current_assessment = response.metadata['assessment']
                    else:
                        # Check in nested agent responses
                        for agent_resp in agent_responses:
                            if agent_resp.get('agent_name') == 'assessment':
                                if 'assessment' in agent_resp.get('metadata', {}):
                                    st.session_state.current_assessment = agent_resp['metadata']['assessment']
                                    break
                    
                    # Save recommendation if present
                    if 'recommendation' in response.metadata:
                        st.session_state.current_recommendation = response.metadata['recommendation']
                        st.session_state.show_practice_log = True
                    else:
                        # Check in nested agent responses
                        for agent_resp in agent_responses:
                            if agent_resp.get('agent_name') == 'practice':
                                if 'recommendation' in agent_resp.get('metadata', {}):
                                    st.session_state.current_recommendation = agent_resp['metadata']['recommendation']
                                    st.session_state.show_practice_log = True
                                    break
                    
                    # FIXED: Detect actionable steps from wisdom responses
                    wisdom_response_text = None
                    for agent_resp in agent_responses:
                        if agent_resp.get('agent_name') == 'wisdom':
                            wisdom_response_text = agent_resp.get('content', '')
                            break
                    
                    # If no explicit practice recommendation but wisdom response exists, check for actionable steps
                    if not st.session_state.current_recommendation and wisdom_response_text:
                        detector = ActionableStepDetector()
                        actionable_practice = detector.detect_actionable_step(wisdom_response_text)
                        
                        if actionable_practice:
                            # Format as recommendation
                            formatted_recommendation = format_actionable_step_for_logging(actionable_practice)
                            st.session_state.current_recommendation = formatted_recommendation
                            st.session_state.show_practice_log = True
                            
                            # Show notification
                            st.info("💡 I've detected an actionable practice in this guidance! Check the sidebar to log it.")
                    
                    # Add to messages
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response.content
                    })
                    
                    # Save to database
                    db.save_message(
                        user_id=st.session_state.user_id,
                        role="user",
                        content=prompt
                    )
                    db.save_message(
                        user_id=st.session_state.user_id,
                        role="assistant",
                        content=response.content
                    )
                    
                    # Update conversation history
                    st.session_state.conversation_history.append({
                        'role': 'user',
                        'content': prompt
                    })
                    st.session_state.conversation_history.append({
                        'role': 'assistant',
                        'content': response.content
                    })
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error processing message: {e}")
                    st.error("Please try again or check the logs for details.")


# ============================================================================
# Calendar Integration Functions - FIXED: Added calendar features
# ============================================================================

def render_calendar_setup():
    """Render Google Calendar setup UI - FIXED: Persistent authorization flow"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📅 Google Calendar")
    
    if not st.session_state.calendar_integration:
        st.sidebar.warning("Calendar integration not available")
        return
    
    calendar = st.session_state.calendar_integration
    
    if not st.session_state.calendar_authenticated:
        # Check if we're in the authorization flow
        if not st.session_state.calendar_auth_in_progress:
            # Initial state - show connect button
            st.sidebar.info("Connect your Google Calendar to schedule practices")
            
            if st.sidebar.button("🔗 Connect Calendar", use_container_width=True):
                try:
                    auth_url = calendar.get_auth_url(st.session_state.user_id)
                    if auth_url:
                        st.session_state.calendar_auth_in_progress = True
                        st.session_state.calendar_auth_url = auth_url
                        st.rerun()
                    else:
                        st.sidebar.error("Calendar setup not configured. Please add client_secrets.json")
                except Exception as e:
                    st.sidebar.error(f"Error: {e}")
        else:
            # Authorization in progress - show persistent form
            st.sidebar.success("✅ Step 1: Authorization link generated")
            
            # Show authorization link
            if st.session_state.calendar_auth_url:
                st.sidebar.markdown(f"[📋 Click here to authorize Google Calendar]({st.session_state.calendar_auth_url})")
            
            st.sidebar.info("👆 After authorizing, paste the full callback URL below")
            
            # Persistent callback URL input
            callback_url = st.sidebar.text_input(
                "Callback URL",
                key="calendar_callback_url",
                placeholder="http://localhost:8501/?code=..."
            )
            
            col1, col2 = st.sidebar.columns(2)
            
            with col1:
                if st.button("✅ Complete Setup", use_container_width=True):
                    if callback_url:
                        try:
                            with st.spinner("Connecting to Google Calendar..."):
                                success = calendar.handle_oauth_callback(callback_url, st.session_state.user_id)
                                
                            if success:
                                st.session_state.calendar_authenticated = True
                                st.session_state.calendar_auth_in_progress = False
                                st.session_state.calendar_auth_url = None
                                st.sidebar.success("Calendar connected! 🎉")
                                st.rerun()
                            else:
                                st.sidebar.error("Failed to connect. Check the terminal/console for detailed error logs.")
                                with st.sidebar.expander("🔍 Troubleshooting Tips"):
                                    st.markdown("""
                                    **Common Issues:**
                                    1. Make sure you copied the **entire** URL (including `http://localhost:8501/?...`)
                                    2. The URL should contain `code=` and `state=` parameters
                                    3. Check that `client_secrets.json` is correctly configured
                                    4. See terminal/console for detailed error messages
                                    """)
                        except Exception as e:
                            st.sidebar.error(f"Error: {type(e).__name__}: {str(e)}")
                            st.sidebar.info("Check terminal/console for full error details")
                    else:
                        st.sidebar.warning("Please paste the callback URL")
            
            with col2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.calendar_auth_in_progress = False
                    st.session_state.calendar_auth_url = None
                    st.rerun()
    else:
        st.sidebar.success("✅ Calendar Connected")
        
        # Show upcoming practices
        if st.sidebar.button("📋 View Scheduled Practices", use_container_width=True):
            try:
                upcoming = calendar.get_upcoming_practices(days_ahead=7)
                if upcoming:
                    st.sidebar.markdown("**Upcoming Practices:**")
                    for practice in upcoming[:5]:
                        st.sidebar.markdown(f"• {practice['name']} - {practice['start_time']}")
                else:
                    st.sidebar.info("No scheduled practices")
            except Exception as e:
                st.sidebar.error(f"Error fetching practices: {e}")
        
        # Disconnect option
        if st.sidebar.button("🔌 Disconnect Calendar", use_container_width=True):
            st.session_state.calendar_authenticated = False
            st.session_state.calendar_auth_in_progress = False
            st.session_state.calendar_auth_url = None
            st.sidebar.info("Calendar disconnected")
            st.rerun()


# ============================================================================
# Sidebar Components
# ============================================================================

def render_sidebar(db):
    """Render sidebar with user info and controls"""
    
    st.sidebar.markdown("# 🙏 JAI GURU DEV AI")
    st.sidebar.markdown("*Your Spiritual Companion*")
    st.sidebar.markdown("---")
    
    # Show notification if practice logging is available
    if st.session_state.show_practice_log and st.session_state.current_recommendation:
        st.sidebar.success("✅ New practice recommendation! Scroll down to log it.")
        st.sidebar.markdown("---")
    
    # If viewing progress, show back button prominently
    if st.session_state.show_progress:
        st.sidebar.markdown("### 📊 Progress View")
        if st.sidebar.button("← Back to Chat", use_container_width=True, key="sidebar_back_chat"):
            st.session_state.show_progress = False
            st.rerun()
        st.sidebar.markdown("---")
    
    # User selection/creation
    render_user_selection(db)
    
    if st.session_state.user_profile:
        st.sidebar.markdown("---")
        
        # Quick actions
        st.sidebar.markdown("### ⚡ Quick Actions")
        
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            if st.button("📊 Progress", use_container_width=True):
                st.session_state.show_progress = True
                st.rerun()
        
        with col2:
            if st.button("🆕 New Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        
        # Current assessment (if any)
        if st.session_state.current_assessment:
            st.sidebar.markdown("---")
            st.sidebar.markdown("### 🔍 Assessment Debug")

            assessment = st.session_state.current_assessment

            # Debug display for all assessment fields
            with st.sidebar.expander("📊 Assessment Details", expanded=True):
                # Age
                age = assessment.get('user_age')
                if age:
                    st.markdown(f"**Age:** {age} years")
                else:
                    st.markdown("**Age:** Not collected yet")

                # Emotion
                emotion = assessment.get('primary_emotion')
                if emotion:
                    # Handle both string and enum values
                    emotion_value = emotion.value if hasattr(emotion, 'value') else emotion
                    st.markdown(f"**Emotion:** {emotion_value}")
                else:
                    st.markdown("**Emotion:** Not collected yet")

                # Life Situation
                situation = assessment.get('life_situation')
                if situation:
                    # Handle both string and enum values
                    situation_value = situation.value if hasattr(situation, 'value') else situation
                    st.markdown(f"**Life Situation:** {situation_value}")
                else:
                    st.markdown("**Life Situation:** Not collected yet")

                # Location
                location = assessment.get('user_location')
                if location:
                    # Handle both string and enum values
                    location_value = location.value if hasattr(location, 'value') else location
                    st.markdown(f"**Location:** {location_value}")
                else:
                    st.markdown("**Location:** Not collected yet")

                # Time Available
                time_available = assessment.get('time_available')
                if time_available:
                    # Handle both string and enum values
                    time_value = time_available.value if hasattr(time_available, 'value') else time_available
                    st.markdown(f"**Time Available:** {time_value}")
                else:
                    st.markdown("**Time Available:** Not collected yet")

                # Meal Status
                meal_status = assessment.get('meal_status')
                if meal_status:
                    # Handle both string and enum values
                    meal_value = meal_status.value if hasattr(meal_status, 'value') else meal_status
                    st.markdown(f"**Meal Status:** {meal_value}")
                else:
                    st.markdown("**Meal Status:** Not collected yet")
        
        # FIXED: Calendar integration UI
        render_calendar_setup()
        
        # Practice logging (if recommendation exists)
        if st.session_state.show_practice_log and st.session_state.current_recommendation:
            render_practice_logging(db)


def render_practice_logging(db):
    """Render practice logging form in sidebar - FIXED: Added calendar scheduling"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ✅ Log Practice")
    
    recommendation = st.session_state.current_recommendation
    
    # Debug info (remove in production)
    if st.sidebar.checkbox("Debug: Show recommendation data", value=False):
        st.sidebar.json(recommendation)
    
    practice = recommendation.get('primary_practice', {})
    
    st.sidebar.markdown(f"**Practice:** {practice.get('name', 'N/A')}")
    
    with st.sidebar.form("practice_log_form"):
        completed = st.checkbox("I completed this practice", value=True)
        
        rating = st.select_slider(
            "How was it?",
            options=[1, 2, 3, 4, 5],
            value=4,
            format_func=lambda x: "⭐" * x
        )
        
        feedback = st.text_area(
            "Feedback (optional)",
            placeholder="How did you feel? Any insights?"
        )
        
        # FIXED: Calendar scheduling option
        schedule_to_calendar = False
        schedule_time = None
        recurrence = None
        
        if st.session_state.calendar_authenticated:
            st.markdown("---")
            schedule_to_calendar = st.checkbox("📅 Schedule to Google Calendar")
            
            if schedule_to_calendar:
                schedule_date = st.date_input(
                    "Date",
                    value=datetime.now() + timedelta(days=1)
                )
                schedule_hour = st.time_input(
                    "Time",
                    value=datetime.now().time()
                )
                
                # Combine date and time
                schedule_time = datetime.combine(schedule_date, schedule_hour)
                
                # Recurrence options
                recurrence_option = st.selectbox(
                    "Repeat",
                    ["None", "Daily", "Weekly", "Monthly"]
                )
                
                if recurrence_option == "Daily":
                    recurrence = "RRULE:FREQ=DAILY"
                elif recurrence_option == "Weekly":
                    recurrence = "RRULE:FREQ=WEEKLY"
                elif recurrence_option == "Monthly":
                    recurrence = "RRULE:FREQ=MONTHLY"
        
        submitted = st.form_submit_button("Log Practice 🙏")
        
        if submitted:
            try:
                # Create practice log
                log_data = {
                    'log_id': str(uuid.uuid4()),
                    'user_id': st.session_state.user_id,
                    'practice_id': practice.get('practice_id', 'unknown'),
                    'practice_name': practice.get('name', 'Practice'),
                    'practice_type': practice.get('practice_type', 'meditation'),
                    'duration_minutes': practice.get('duration_minutes', 15),
                    'completed': completed,
                    'rating': rating,
                    'feedback': feedback,
                    'timestamp': datetime.now()
                }
                
                # Save to database
                db.log_practice(log_data)
                
                # Update session state
                st.session_state.practice_history.append(log_data)
                
                # FIXED: Schedule to calendar if requested
                if schedule_to_calendar and schedule_time:
                    calendar = st.session_state.calendar_integration
                    if calendar and calendar.is_authenticated():
                        try:
                            event_data = format_practice_for_calendar(practice, schedule_time)
                            
                            event_id = calendar.create_practice_event(
                                practice_name=event_data['practice_name'],
                                description=event_data['description'],
                                start_time=schedule_time,
                                duration_minutes=event_data['duration_minutes'],
                                recurrence=recurrence
                            )
                            
                            if event_id:
                                st.sidebar.success(f"✅ Practice logged and scheduled to calendar!")
                            else:
                                st.sidebar.warning("Practice logged, but calendar scheduling failed")
                        except Exception as e:
                            st.sidebar.warning(f"Practice logged, but calendar error: {e}")
                    else:
                        st.sidebar.warning("Practice logged, but calendar not connected")
                else:
                    st.sidebar.success("Practice logged! 🎉")
                
                # Reset state
                st.session_state.show_practice_log = False
                st.session_state.current_recommendation = None
                
                st.rerun()
                
            except Exception as e:
                st.sidebar.error(f"Error logging practice: {e}")


# ============================================================================
# Progress Dashboard
# ============================================================================

def render_progress_dashboard(db):
    """Render progress dashboard"""
    
    # Add back button at the top
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("← Back to Chat", use_container_width=True):
            st.session_state.show_progress = False
            st.rerun()
    
    with col2:
        st.markdown("## 📊 Your Progress Journey")
    
    st.markdown("---")
    
    practices = st.session_state.practice_history
    
    if not practices:
        st.info("No practices logged yet. Complete a practice to see your progress!")
        st.markdown("---")
        
        # Show helpful message
        st.markdown("### 💡 How to Log a Practice")
        st.markdown("""
        1. Ask me for a practice recommendation (e.g., "What practice should I do?")
        2. Complete the recommended practice
        3. Use the sidebar form to log your practice
        4. Come back here to see your progress!
        
        **Note:** I can also detect actionable practices from wisdom guidance!
        """)
        
        # Another back button for easy access
        if st.button("🏠 Return to Chat", use_container_width=False, key="back_bottom_empty"):
            st.session_state.show_progress = False
            st.rerun()
        return
    
    # Calculate statistics
    total_practices = len(practices)
    completed_practices = sum(1 for p in practices if p.get('completed', True))
    adherence_rate = completed_practices / total_practices if total_practices > 0 else 0
    
    # Ratings
    ratings = [p.get('rating') for p in practices if p.get('rating')]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    
    # Total time
    total_minutes = sum(p.get('duration_minutes', 0) for p in practices)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Practices", completed_practices)
    
    with col2:
        st.metric("Adherence Rate", f"{adherence_rate:.0%}")
    
    with col3:
        st.metric("Avg Rating", f"{avg_rating:.1f} ⭐")
    
    with col4:
        st.metric("Total Time", f"{total_minutes} min")
    
    st.markdown("---")
    
    # Recent practices
    st.markdown("### 📝 Recent Practices")
    
    recent = practices[-10:]  # Last 10
    
    for practice in reversed(recent):
        with st.expander(
            f"{'✅' if practice.get('completed') else '⏸️'} {practice.get('practice_name')} - {practice.get('timestamp', 'Unknown date')}"
        ):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Type:** {practice.get('practice_type', 'N/A').title()}")
                st.markdown(f"**Duration:** {practice.get('duration_minutes', 0)} minutes")
                
                if practice.get('rating'):
                    st.markdown(f"**Rating:** {'⭐' * practice['rating']}")
                
                if practice.get('feedback'):
                    st.markdown(f"**Feedback:** {practice['feedback']}")
            
            with col2:
                st.markdown(f"**Status:** {'Completed' if practice.get('completed') else 'Incomplete'}")
    
    # Back button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🏠 Return to Chat", use_container_width=True, key="back_to_chat_bottom"):
            st.session_state.show_progress = False
            st.rerun()


# ============================================================================
# Main Application
# ============================================================================

def main():
    """Main application function"""
    
    # Initialize session state
    init_session_state()
    
    # Show initialization message
    with st.spinner("🚀 Initializing JAI GURU DEV AI System..."):
        # Initialize components
        agents = initialize_agents()
        db = initialize_database()
    
    if not agents['initialized']:
        st.error("❌ Failed to initialize agent system. Please check:")
        st.error("1. Your .env file has the required API keys")
        st.error("2. The Knowledge_Base directory exists and contains teachings")
        st.error("3. Check the terminal/console for detailed error messages")
        return
    
    if not db:
        st.error("❌ Failed to initialize database. Please check the configuration.")
        return
    
    # Render sidebar
    render_sidebar(db)
    
    # Main content
    if st.session_state.show_progress:
        render_progress_dashboard(db)
    else:
        render_chat_interface(agents, db)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #8B4513; font-style: italic;'>"
        "🙏 Based on Sri Sri Ravi Shankar's Teachings (1995-2002) | "
        "Powered by Multi-Agent AI System | "
        "✨ Now with Actionable Detection & Calendar Integration"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
