"""
JAI GURU DEV AI Chatbot - Fully Integrated Version with Database Support
=========================================================================

Features:
✅ User profile management (create/select users)
✅ Persistent conversations (survive app restart)
✅ Practice tracking UI
✅ Progress dashboard
✅ All existing RAG functionality preserved

This is the database-integrated version that adds persistent storage
while maintaining all the spiritual guidance capabilities.
"""

import streamlit as st
import os
from dotenv import load_dotenv
import yaml
from rag_system import RAGSystem, UserContext
from typing import Dict, Any, List, Optional
import time
from datetime import datetime, timedelta

# Database imports
from utils.database import Database
from models.user import UserProfile
from models.conversation import ConversationMessage, ConversationHistory
from models.practice import PracticeLog, PracticeStatistics

# Load environment variables
load_dotenv()

# Page configuration with saffron theme
st.set_page_config(
    page_title="🙏 JAI GURU DEV AI Chatbot",
    page_icon="🙏",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "JAI GURU DEV AI - Wisdom from Sri Sri Ravi Shankar's Teachings"
    }
)

# Custom CSS for saffron theme with improved dropdown visibility
st.markdown("""
<style>
    .main {
        background-color: #FFF8DC;
    }
    
    .stApp {
        background: linear-gradient(135deg, #FFF8DC 0%, #FFEFD5 100%);
    }
    
    .css-1d391kg {
        background-color: #FF8C00;
    }
    
    h1, h2, h3 {
        color: #8B4513 !important;
        font-family: 'serif';
    }
    
    .stSelectbox label, .stTextInput label, .stTextArea label {
        color: #8B4513 !important;
        font-weight: bold;
        font-size: 16px;
    }
    
    /* Improved dropdown visibility */
    .stSelectbox > div > div {
        background-color: white !important;
        border: 2px solid #FF8C00 !important;
        border-radius: 8px !important;
        color: #333333 !important;
    }
    
    .stSelectbox > div > div > div {
        color: #333333 !important;
        font-weight: 500 !important;
    }
    
    /* Dropdown options styling */
    .stSelectbox [role="listbox"] {
        background-color: white !important;
        border: 2px solid #FF8C00 !important;
        border-radius: 8px !important;
    }
    
    .stSelectbox [role="option"] {
        background-color: white !important;
        color: #333333 !important;
        font-weight: 500 !important;
        padding: 8px 12px !important;
    }
    
    .stSelectbox [role="option"]:hover {
        background-color: #FFE4B5 !important;
        color: #8B4513 !important;
    }
    
    .stSelectbox [aria-selected="true"] {
        background-color: #FF8C00 !important;
        color: white !important;
    }
    
    /* Text area and input styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: white !important;
        border: 2px solid #FF8C00 !important;
        border-radius: 8px !important;
        color: #333333 !important;
    }
    
    .user-message {
        background-color: #FFE4B5;
        padding: 10px;
        border-radius: 10px;
        border-left: 4px solid #FF8C00;
        margin: 10px 0;
    }
    
    .bot-message {
        background-color: #FFF8DC;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #DAA520;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .context-card {
        background-color: #FFFACD;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #DDD;
        margin: 10px 0;
    }
    
    .source-card {
        background-color: #F5F5DC;
        padding: 10px;
        border-radius: 5px;
        border-left: 3px solid #CD853F;
        margin: 5px 0;
        font-size: 0.9em;
    }
    
    .welcome-header {
        text-align: center;
        background: linear-gradient(45deg, #FF8C00, #DAA520);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin-bottom: 20px;
    }
    
    .context-header {
        text-align: center;
        background: linear-gradient(45deg, #FF8C00, #DAA520);
        padding: 15px;
        border-radius: 12px;
        color: white;
        margin-bottom: 15px;
    }
    
    .stats-card {
        background-color: #FFFAF0;
        padding: 15px;
        border-radius: 10px;
        border: 2px solid #FF8C00;
        margin: 10px 0;
    }
    
    .practice-card {
        background-color: #FFF8DC;
        padding: 12px;
        border-radius: 8px;
        border-left: 4px solid #DAA520;
        margin: 8px 0;
    }
    
    .stButton button {
        background-color: #FF8C00;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    
    .stButton button:hover {
        background-color: #DAA520;
        color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .sidebar .stSelectbox {
        background-color: #FFF8DC;
    }
    
    /* Form button styling */
    .stFormSubmitButton button {
        background-color: #FF8C00 !important;
        color: white !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        font-size: 16px !important;
        font-weight: bold !important;
    }
    
    .stFormSubmitButton button:hover {
        background-color: #DAA520 !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }
    
    .metric-container {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        border: 2px solid #FF8C00;
        text-align: center;
        margin: 5px;
    }
    
    .metric-value {
        font-size: 2em;
        font-weight: bold;
        color: #FF8C00;
    }
    
    .metric-label {
        font-size: 0.9em;
        color: #8B4513;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)


class ChatbotUI:
    def __init__(self):
        self.config_path = "config.yaml"
        self.knowledge_base_path = "Knowledge_Base"
        self.db_path = "database/guruji_bot.db"
        
        # Initialize database
        if 'db' not in st.session_state:
            st.session_state.db = Database(self.db_path)
        
        # Initialize session state
        if 'rag_system' not in st.session_state:
            st.session_state.rag_system = None
        if 'system_initialized' not in st.session_state:
            st.session_state.system_initialized = False
        
        # User management
        if 'current_user_id' not in st.session_state:
            st.session_state.current_user_id = None
        if 'user_profile' not in st.session_state:
            st.session_state.user_profile = None
        if 'user_selected' not in st.session_state:
            st.session_state.user_selected = False
        
        # UI state
        if 'context_gathered' not in st.session_state:
            st.session_state.context_gathered = False
        if 'show_practice_tracker' not in st.session_state:
            st.session_state.show_practice_tracker = False
        if 'show_dashboard' not in st.session_state:
            st.session_state.show_dashboard = False
        
        # Chat state - now loaded from database
        if 'chat_history_loaded' not in st.session_state:
            st.session_state.chat_history_loaded = False
    
    def initialize_system(self):
        """Initialize the RAG system"""
        try:
            with st.spinner("🙏 Initializing JAI GURU DEV AI... Please wait while I connect to the divine wisdom..."):
                st.session_state.rag_system = RAGSystem(
                    config_path=self.config_path,
                    knowledge_base_path=self.knowledge_base_path
                )
                st.session_state.system_initialized = True
                st.success("✅ System initialized! Ready to share wisdom from Gurudev's teachings.")
        except Exception as e:
            st.error(f"❌ Error initializing system: {str(e)}")
            st.error("Please check your API keys and configuration.")
            return False
        return True
    
    def load_conversation_history(self):
        """Load conversation history from database"""
        if st.session_state.current_user_id and not st.session_state.chat_history_loaded:
            history = st.session_state.db.get_conversation_history(
                st.session_state.current_user_id,
                limit=100
            )
            
            # Convert to the format expected by the UI
            st.session_state.chat_history = []
            
            # Group messages into pairs (user question + assistant response)
            i = 0
            while i < len(history):
                if history[i]['role'] == 'user':
                    user_msg = history[i]['content']
                    assistant_msg = ""
                    sources = []
                    
                    # Get the corresponding assistant message
                    if i + 1 < len(history) and history[i + 1]['role'] == 'assistant':
                        assistant_msg = history[i + 1]['content']
                        # Extract sources from metadata if available
                        if history[i + 1].get('metadata') and 'sources' in history[i + 1]['metadata']:
                            sources = history[i + 1]['metadata']['sources']
                        i += 2
                    else:
                        i += 1
                    
                    st.session_state.chat_history.append((user_msg, assistant_msg, sources))
                else:
                    i += 1
            
            st.session_state.chat_history_loaded = True
    
    def render_user_selection(self):
        """Render user selection/creation interface"""
        st.markdown("""
        <div class="welcome-header">
            <h1>🙏 JAI GURU DEV AI</h1>
            <p>Divine Wisdom from Sri Sri Ravi Shankar's Teachings</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 👤 Welcome! Please select or create your profile")
        
        # Get all users
        all_users = st.session_state.db.get_all_users()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔄 Returning User")
            if all_users:
                user_options = {f"{u['name']} (ID: {u['user_id'][:8]}...)": u['user_id'] 
                               for u in all_users}
                user_options["Create New Profile"] = "new"
                
                selected = st.selectbox(
                    "Select your profile:",
                    options=list(user_options.keys()),
                    key="user_selection"
                )
                
                if st.button("Continue with Selected Profile", use_container_width=True):
                    if user_options[selected] != "new":
                        st.session_state.current_user_id = user_options[selected]
                        user_data = st.session_state.db.get_user(st.session_state.current_user_id)
                        st.session_state.user_profile = UserProfile.from_dict(user_data)
                        st.session_state.user_selected = True
                        st.session_state.context_gathered = True
                        
                        # Update last active
                        st.session_state.db.update_last_active(st.session_state.current_user_id)
                        
                        # Load conversation history
                        self.load_conversation_history()
                        
                        st.rerun()
            else:
                st.info("No existing profiles found. Please create a new profile.")
        
        with col2:
            st.markdown("#### ✨ New User")
            with st.form("new_user_form"):
                name = st.text_input("Your Name *", placeholder="Enter your name")
                age = st.number_input("Age (optional)", min_value=10, max_value=120, value=30)
                
                life_aspect = st.selectbox(
                    "Life Aspect *",
                    options=["", "Relationships", "Spiritual Practice", "Career & Work", 
                            "Emotional Well-being", "Health & Healing", "Family Issues", 
                            "Personal Growth", "Life Purpose", "Other"]
                )
                
                emotional_state = st.selectbox(
                    "Current Emotional State *",
                    options=["", "Peaceful", "Confused", "Anxious", "Sad", "Angry", 
                            "Joyful", "Stressed", "Lonely", "Grateful", "Seeking", "Other"]
                )
                
                guidance_type = st.selectbox(
                    "Type of Guidance *",
                    options=["", "General Wisdom", "Specific Situation Help", 
                            "Daily Practice Guidance", "Philosophical Understanding", 
                            "Practical Solutions"]
                )
                
                specific_situation = st.text_area(
                    "Describe Your Situation (optional)",
                    placeholder="Share any specific details...",
                    height=100
                )
                
                experience_level = st.selectbox(
                    "Experience Level",
                    options=["beginner", "intermediate", "advanced"]
                )
                
                submitted = st.form_submit_button("Create Profile & Begin", use_container_width=True)
                
                if submitted:
                    if name and life_aspect and emotional_state and guidance_type:
                        # Create new user
                        user_data = {
                            'name': name,
                            'age': age,
                            'life_aspect': life_aspect,
                            'emotional_state': emotional_state,
                            'guidance_type': guidance_type,
                            'specific_situation': specific_situation,
                            'experience_level': experience_level
                        }
                        
                        st.session_state.current_user_id = st.session_state.db.create_user(user_data)
                        user_data['user_id'] = st.session_state.current_user_id
                        st.session_state.user_profile = UserProfile.from_dict(user_data)
                        st.session_state.user_selected = True
                        st.session_state.context_gathered = True
                        st.session_state.chat_history = []
                        
                        st.success(f"✅ Welcome, {name}! Your profile has been created.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Please fill in all required fields marked with *")
    
    def render_sidebar(self):
        """Render sidebar with configuration and stats"""
        with st.sidebar:
            # User info at top
            if st.session_state.user_profile:
                st.markdown("### 👤 Current User")
                st.markdown(f"**{st.session_state.user_profile.name}**")
                st.markdown(f"Level: {st.session_state.user_profile.experience_level}")
                
                if st.button("🔄 Switch User", use_container_width=True):
                    # Reset user session
                    st.session_state.current_user_id = None
                    st.session_state.user_profile = None
                    st.session_state.user_selected = False
                    st.session_state.context_gathered = False
                    st.session_state.chat_history_loaded = False
                    st.rerun()
                
                st.markdown("---")
            
            # Navigation
            st.markdown("## 📱 Navigation")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💬 Chat", use_container_width=True):
                    st.session_state.show_practice_tracker = False
                    st.session_state.show_dashboard = False
                    st.rerun()
            
            with col2:
                if st.button("📊 Dashboard", use_container_width=True):
                    st.session_state.show_dashboard = True
                    st.session_state.show_practice_tracker = False
                    st.rerun()
            
            if st.button("🧘 Practice Tracker", use_container_width=True):
                st.session_state.show_practice_tracker = True
                st.session_state.show_dashboard = False
                st.rerun()
            
            st.markdown("---")
            st.markdown("## ⚙️ Configuration")
            
            # Model provider selection
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            current_provider = config['model_provider']['default']
            provider = st.selectbox(
                "🤖 AI Model Provider:",
                options=["openai", "groq"],
                index=0 if current_provider == "openai" else 1,
                help="Choose between OpenAI GPT models or Groq Llama models"
            )
            
            # Update config if changed
            if provider != current_provider:
                config['model_provider']['default'] = provider
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(config, f)
                st.session_state.system_initialized = False
                st.rerun()
            
            st.markdown("---")
            st.markdown("## 📚 Knowledge Base")
            if st.session_state.rag_system:
                num_teachings = len(st.session_state.rag_system.teachings)
                st.metric("Total Teachings", num_teachings)
            
            # Quick stats
            if st.session_state.current_user_id:
                st.markdown("---")
                st.markdown("## 📈 Quick Stats")
                
                msg_count = st.session_state.db.get_message_count(st.session_state.current_user_id)
                st.metric("Messages", msg_count)
                
                stats = st.session_state.db.get_practice_statistics(
                    st.session_state.current_user_id, days=7
                )
                st.metric("7-Day Practices", stats['total_practices'])
                
                streak = st.session_state.db.get_streak_days(st.session_state.current_user_id)
                st.metric("Current Streak", f"{streak} days")
            
            st.markdown("---")
            st.markdown("## 🙏 About")
            st.markdown("""
            **JAI GURU DEV AI** brings you wisdom from Sri Sri Ravi Shankar's teachings
            with personalized tracking and progress insights.
            """)

            # Database Management Section
            st.markdown("---")
            st.markdown("## 🗄️ Database Management")

            # Clear current user's chat history
            if st.session_state.current_user_id:
                if st.button("🔄 Clear My Chat History", use_container_width=True):
                    st.session_state.db.clear_conversation_history(st.session_state.current_user_id)
                    st.session_state.chat_history = []
                    st.session_state.chat_history_loaded = False
                    st.success("Chat history cleared!")
                    st.rerun()

                # Delete current user
                if st.button("🗑️ Delete My Account", use_container_width=True, type="secondary"):
                    # Confirmation dialog
                    if 'confirm_delete_user' not in st.session_state:
                        st.session_state.confirm_delete_user = False

                    if not st.session_state.confirm_delete_user:
                        st.session_state.confirm_delete_user = True
                        st.warning("⚠️ Click again to confirm deletion of your account and all data!")
                    else:
                        try:
                            user_id = st.session_state.current_user_id
                            st.session_state.db.delete_user(user_id)

                            # Reset session
                            st.session_state.current_user_id = None
                            st.session_state.user_profile = None
                            st.session_state.user_selected = False
                            st.session_state.context_gathered = False
                            st.session_state.chat_history_loaded = False
                            st.session_state.chat_history = []
                            st.session_state.confirm_delete_user = False

                            st.success("✅ Account deleted successfully!")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting account: {e}")
                            st.session_state.confirm_delete_user = False

            # Clear entire database (admin function)
            st.markdown("---")
            st.markdown("### ⚠️ DANGER ZONE")

            if st.button("🗑️ Clear Entire Database", use_container_width=True, type="primary"):
                # Confirmation dialog
                if 'confirm_clear_db' not in st.session_state:
                    st.session_state.confirm_clear_db = False

                if not st.session_state.confirm_clear_db:
                    st.session_state.confirm_clear_db = True
                    st.error("⚠️⚠️⚠️ WARNING: This will DELETE ALL USERS and ALL DATA! Click again to confirm!")
                else:
                    try:
                        st.session_state.db.clear_all_data()

                        # Reset all session state
                        st.session_state.current_user_id = None
                        st.session_state.user_profile = None
                        st.session_state.user_selected = False
                        st.session_state.context_gathered = False
                        st.session_state.chat_history_loaded = False
                        st.session_state.chat_history = []
                        st.session_state.confirm_clear_db = False

                        st.success("✅ Database cleared successfully!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error clearing database: {e}")
                        st.session_state.confirm_clear_db = False
    
    def display_user_context(self):
        """Display user context card"""
        if not st.session_state.user_profile:
            return
        
        context_summary = st.session_state.user_profile.get_context_summary()
        
        if context_summary:
            st.markdown(f"""
            <div class="context-card">
                <h4>🎯 Your Context</h4>
                {context_summary}
            </div>
            """, unsafe_allow_html=True)
    
    def display_chat_history(self):
        """Display chat history from database"""
        if not hasattr(st.session_state, 'chat_history') or not st.session_state.chat_history:
            return
        
        for i, (question, response, sources) in enumerate(st.session_state.chat_history):
            # User message
            st.markdown(f"""
            <div class="user-message">
                <strong>🙋 You:</strong> {question}
            </div>
            """, unsafe_allow_html=True)
            
            # Bot response
            st.markdown(f"""
            <div class="bot-message">
                <strong>🙏 Gurudev's Wisdom:</strong><br>
                {response}
            </div>
            """, unsafe_allow_html=True)
            
            # Sources
            if sources:
                with st.expander(f"📚 Source Teachings ({len(sources)} referenced)"):
                    for source in sources:
                        teaching_num = source.get('teaching_number', 'N/A')
                        title = source.get('title', 'Untitled')
                        date = source.get('date', 'Unknown date')
                        topics = source.get('topics', 'N/A')
                        
                        st.markdown(f"""
                        <div class="source-card">
                            <strong>Teaching #{teaching_num}: {title}</strong><br>
                            <em>Date: {date} | Topics: {topics}</em>
                        </div>
                        """, unsafe_allow_html=True)
    
    def handle_user_query(self):
        """Handle user query and save to database"""
        user_query = st.text_input(
            "💬 Ask your question:",
            placeholder="How can I find peace in difficult times?",
            key="user_input"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🙏 Ask Gurudev", use_container_width=True):
                if user_query:
                    self.process_query(user_query)
                else:
                    st.warning("Please enter your question first.")
        
        with col2:
            if st.button("🎲 Get Random Wisdom", use_container_width=True):
                random_queries = [
                    "What is the essence of happiness?",
                    "How do I find inner peace?",
                    "What is the purpose of life?",
                    "How do I deal with stress?",
                    "What is true love?",
                    "How do I overcome fear?",
                    "What is the secret to success?",
                    "How do I find my life purpose?"
                ]
                import random
                random_query = random.choice(random_queries)
                self.process_query(random_query)
    
    def process_query(self, query: str):
        """Process query and save to database"""
        if not st.session_state.rag_system:
            st.error("System not initialized.")
            return
        
        with st.spinner("🙏 Consulting Gurudev's teachings..."):
            try:
                # Get user context from profile
                user_context = UserContext(
                    life_aspect=st.session_state.user_profile.life_aspect,
                    emotional_state=st.session_state.user_profile.emotional_state,
                    guidance_type=st.session_state.user_profile.guidance_type,
                    specific_situation=st.session_state.user_profile.specific_situation
                )
                
                response_data = st.session_state.rag_system.get_response(query, user_context)
                
                if response_data['success']:
                    # Save user message to database
                    st.session_state.db.save_message(
                        user_id=st.session_state.current_user_id,
                        role='user',
                        content=query
                    )
                    
                    # Save assistant message to database
                    st.session_state.db.save_message(
                        user_id=st.session_state.current_user_id,
                        role='assistant',
                        content=response_data['answer'],
                        metadata={'sources': response_data['sources']}
                    )
                    
                    # Add to session chat history
                    if not hasattr(st.session_state, 'chat_history'):
                        st.session_state.chat_history = []
                    
                    st.session_state.chat_history.append((
                        query,
                        response_data['answer'],
                        response_data['sources']
                    ))
                    
                    # Update last active
                    st.session_state.db.update_last_active(st.session_state.current_user_id)
                    
                    st.rerun()
                else:
                    st.error(f"Error: {response_data.get('error', 'Unknown error')}")
            
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    def render_practice_tracker(self):
        """Render practice tracking interface"""
        st.markdown("""
        <div class="welcome-header">
            <h2>🧘 Practice Tracker</h2>
            <p>Log and track your spiritual practices</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Practice logging form
        st.markdown("### ✍️ Log a Practice")
        with st.form("practice_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                practice_name = st.text_input("Practice Name *", 
                                            placeholder="e.g., Sudarshan Kriya, Meditation")
                practice_type = st.selectbox(
                    "Practice Type *",
                    options=["pranayama", "meditation", "yoga", "seva", "satsang", "other"]
                )
                duration = st.number_input("Duration (minutes)", min_value=1, value=20)
            
            with col2:
                completed = st.checkbox("Completed", value=True)
                rating = st.slider("How was it? (1-5)", 1, 5, 4)
                feedback = st.text_area("Notes/Feedback", 
                                      placeholder="How did you feel? Any insights?",
                                      height=100)
            
            submitted = st.form_submit_button("Log Practice", use_container_width=True)
            
            if submitted and practice_name:
                practice_data = {
                    'user_id': st.session_state.current_user_id,
                    'practice_name': practice_name,
                    'practice_type': practice_type,
                    'duration_minutes': duration,
                    'completed': completed,
                    'rating': rating,
                    'feedback': feedback
                }
                
                try:
                    log_id = st.session_state.db.log_practice(practice_data)
                    st.success(f"✅ Practice logged: {practice_name}")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error logging practice: {e}")
        
        st.markdown("---")
        
        # Recent practices
        st.markdown("### 📋 Recent Practices (Last 30 days)")
        
        logs = st.session_state.db.get_practice_logs(
            st.session_state.current_user_id,
            days=30
        )
        
        if logs:
            for log in logs[:10]:  # Show last 10
                practice = PracticeLog.from_dict(log)
                
                status_icon = "✅" if practice.completed else "⏸️"
                rating_stars = practice.get_rating_stars()
                display_date = practice.get_display_date()
                
                st.markdown(f"""
                <div class="practice-card">
                    <strong>{status_icon} {practice.practice_name}</strong> 
                    ({practice.practice_type})
                    <br>
                    <small>
                        🕐 {practice.duration_minutes} min | 
                        ⭐ {rating_stars} | 
                        📅 {display_date}
                    </small>
                    {f'<br><em>"{practice.feedback}"</em>' if practice.feedback else ''}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No practices logged yet. Start by logging your first practice above!")
    
    def render_dashboard(self):
        """Render progress dashboard"""
        st.markdown("""
        <div class="welcome-header">
            <h2>📊 Your Progress Dashboard</h2>
            <p>Track your spiritual journey</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Time period selector
        period = st.selectbox(
            "📅 Time Period",
            options=[7, 14, 30, 90],
            format_func=lambda x: f"Last {x} days",
            index=2
        )
        
        # Get statistics
        stats = st.session_state.db.get_practice_statistics(
            st.session_state.current_user_id,
            days=period
        )
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{stats['total_practices']}</div>
                <div class="metric-label">Total Practices</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{stats['adherence_rate']}%</div>
                <div class="metric-label">Adherence Rate</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            hours = stats['total_duration_minutes'] // 60
            minutes = stats['total_duration_minutes'] % 60
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{hours}h {minutes}m</div>
                <div class="metric-label">Total Time</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            streak = st.session_state.db.get_streak_days(st.session_state.current_user_id)
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{streak} 🔥</div>
                <div class="metric-label">Current Streak</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Practice breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Practice Type Breakdown")
            if stats['practice_type_breakdown']:
                for practice_type, count in stats['practice_type_breakdown'].items():
                    st.markdown(f"""
                    <div class="stats-card">
                        <strong>{practice_type.title()}</strong>: {count} sessions
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No practice data for this period")
        
        with col2:
            st.markdown("### ⭐ Average Rating")
            st.markdown(f"""
            <div class="stats-card">
                <div style="font-size: 2em; text-align: center; color: #FF8C00;">
                    {"⭐" * int(stats['average_rating'])} {stats['average_rating']:.1f}/5
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Conversation stats
        st.markdown("### 💬 Conversation Statistics")
        msg_count = st.session_state.db.get_message_count(st.session_state.current_user_id)
        recent_msgs = st.session_state.db.get_recent_conversations(
            st.session_state.current_user_id,
            days=period
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Messages", msg_count)
        with col2:
            st.metric(f"Messages (Last {period} days)", len(recent_msgs))
    
    def render_chat_interface(self):
        """Render main chat interface"""
        st.markdown("""
        <div class="welcome-header">
            <h1>🙏 JAI GURU DEV AI</h1>
            <p>Divine Wisdom from Sri Sri Ravi Shankar's Teachings</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display user context
        self.display_user_context()
        
        # Display chat history
        if hasattr(st.session_state, 'chat_history') and st.session_state.chat_history:
            st.markdown("## 💬 Our Conversation")
            self.display_chat_history()
        
        # Query input
        st.markdown("---")
        st.markdown("## 🙏 Ask for Guidance")
        self.handle_user_query()
        
        # Footer
        st.markdown("""
        ---
        <div style="text-align: center; color: #8B4513; font-style: italic;">
            🙏 "In the depth of silence is the source of love" - Sri Sri Ravi Shankar 🙏
        </div>
        """, unsafe_allow_html=True)
    
    def run(self):
        """Main application runner"""
        # Check if user is selected
        if not st.session_state.user_selected:
            self.render_user_selection()
            return
        
        # Initialize system if needed
        if not st.session_state.system_initialized:
            if not self.initialize_system():
                return
        
        # Load conversation history if not loaded
        if not st.session_state.chat_history_loaded:
            self.load_conversation_history()
        
        # Render sidebar
        self.render_sidebar()
        
        # Render appropriate view
        if st.session_state.show_dashboard:
            self.render_dashboard()
        elif st.session_state.show_practice_tracker:
            self.render_practice_tracker()
        else:
            self.render_chat_interface()


def main():
    """Main function"""
    chatbot = ChatbotUI()
    chatbot.run()


if __name__ == "__main__":
    main()
