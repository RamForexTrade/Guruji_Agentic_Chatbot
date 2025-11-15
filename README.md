# JAI GURU DEV AI Companion Chatbot

**An AI-powered spiritual companion providing personalized guidance, practice recommendations, and progress tracking based on Gurudev Sri Sri Ravi Shankar's wisdom and teachings.**

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Current Status](#current-status)
3. [Architecture](#architecture)
4. [Technology Stack](#technology-stack)
5. [Quick Start](#quick-start)
6. [Agent System](#agent-system)
7. [Project Structure](#project-structure)
8. [Development Timeline](#development-timeline)
9. [Next Steps](#next-steps)
10. [Configuration](#configuration)
11. [Testing](#testing)
12. [Deployment](#deployment)
13. [Technical Documentation](#technical-documentation)

---

## Project Overview

### Vision

Build an AI-powered spiritual companion that provides personalized guidance, tracks practice progress, and supports users on their wellness journey based on Gurudev's wisdom and teachings.

### Core Objectives

- **Personalized Guidance:** Context-aware wisdom and advice based on user's current state
- **Practice Recommendation:** Suggest relevant techniques (Pranayama, Meditation, etc.)
- **Progress Monitoring:** Track daily practices and user adherence
- **Proactive Engagement:** Send reminders, nudges, and check-ins
- **Continuous Companionship:** Maintain conversation context and user journey history

### Key Features

1. **Conversational Interface:** Natural chat-based interaction
2. **User Profiling:** Collect and maintain user context (age, goals, health status)
3. **Session Management:** Remember conversations and user preferences
4. **RAG-based Wisdom Retrieval:** Fetch relevant teachings from knowledge base
5. **Multi-Agent System:** Specialized agents for different aspects (wisdom, assessment, practice, monitoring)
6. **Progress Tracking:** Log practices, feedback, and improvements
7. **Journey Analytics:** Generate insights and progress reports

---

## Current Status

**Phase:** 2 of 6 - Agentic System COMPLETED
**Last Updated:** October 26, 2025

### Completed Components

| Component | Status | Notes |
|-----------|--------|-------|
| Base Architecture | ✅ Complete | Production-ready |
| Orchestrator Agent | ✅ Complete | May need routing verification |
| Wisdom Agent | ✅ Complete | Needs vector DB loaded |
| Assessment Agent | ✅ Complete | Production-ready |
| Practice Agent | ✅ Complete | Production-ready |
| Progress Agent | ✅ Complete | Needs DB integration |
| Integration Tests | ✅ Created | Ready to run |
| Database Schema | ⚠️ Pending | Need to verify/implement |
| UI Integration | ⚠️ Pending | Need to implement |

### What's Working

- ✅ Complete multi-agent architecture
- ✅ User state detection and analysis
- ✅ Personalized practice recommendations
- ✅ Comprehensive progress tracking
- ✅ Multi-agent coordination framework
- ✅ Error resilience and fallbacks
- ✅ LLM-powered customization
- ✅ Structured data flow
- ✅ Type-safe implementations

---

## Architecture

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────┐
│              USER INTERFACE (Streamlit)                  │
│  • Chat Interface                                        │
│  • User Profile Management                               │
│  • Practice Tracking Dashboard                           │
│  • Progress Visualization                                │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│           ORCHESTRATOR AGENT (Master)                    │
│  • Routes queries to appropriate agents                  │
│  • Manages conversation flow and context                 │
│  • Coordinates multi-agent responses                     │
└──────────┬──────────┬──────────┬─────────────────────────┘
           │          │          │
    ┌──────┘          │          └──────┐
    ▼                 ▼                 ▼
┌────────┐      ┌──────────┐     ┌─────────┐
│ WISDOM │      │ASSESSMENT│     │PRACTICE │
│ AGENT  │      │  AGENT   │     │ AGENT   │
│        │      │          │     │         │
│RAG     │      │Analyzes  │     │Recommends│
│Retrieval│      │User State│     │Practices│
└────────┘      └──────────┘     └─────────┘
                      │                │
                      └────────┬───────┘
                               ▼
                      ┌─────────────────┐
                      │ PROGRESS AGENT  │
                      │ • Tracks logs   │
                      │ • Calculates    │
                      │   statistics    │
                      │ • Generates     │
                      │   insights      │
                      └─────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────┐
│                    DATA LAYER                            │
│  • SQLite (User profiles, conversations, practice logs)  │
│  • ChromaDB (Vector embeddings for RAG)                  │
│  • Streamlit Session State (Active sessions)             │
└─────────────────────────────────────────────────────────┘
```

### Agent Workflow Example

**Scenario:** User expresses anxiety

```
1. User: "I'm feeling anxious about my presentation"
   ↓
2. ORCHESTRATOR classifies intent → "expressing_state"
   ↓
3. ASSESSMENT AGENT analyzes:
   - State: anxious
   - Severity: high
   - Readiness: ready
   ↓
4. PRACTICE AGENT recommends:
   - Nadi Shodhana (5 min breathing exercise)
   - Customized instructions for anxiety
   ↓
5. User completes practice and logs: "5/5 - Feeling better!"
   ↓
6. PROGRESS AGENT:
   - Logs completion
   - Updates statistics
   - Provides motivational message
```

---

## Technology Stack

### Current Implementation (Phase 1 - MVP)

**Core:**
- Python 3.11+
- Streamlit 1.30.0+ (UI + Backend)

**AI/LLM:**
- LangChain 0.1.0+ (RAG orchestration)
- Groq (primary LLM provider - fast, cost-effective)
- OpenAI (fallback, embeddings)
- Anthropic (fallback)
- text-embedding-3-large (embeddings)

**Vector Database:**
- ChromaDB 0.4.22+ (local, embedded vector store)

**Database:**
- SQLite3 (user profiles, conversations, practice logs)

**Key Dependencies:**
```
langchain>=0.1.0
langchain-openai
langchain-groq
langchain-anthropic
chromadb>=0.4.22
streamlit>=1.30.0
python-dotenv
pandas
```

### Future Production Stack (Phase 10)

- **Frontend:** Next.js + TypeScript
- **Backend:** FastAPI + LangGraph
- **Databases:** PostgreSQL, MongoDB, Redis, Pinecone/Qdrant
- **Cloud:** AWS/GCP with Docker + Kubernetes

---

## Quick Start

### Prerequisites

- Python 3.11 or higher
- OpenAI API key (for embeddings)
- Groq API key (for LLM - free tier available)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Guruji_Chatbot_Clean
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   Create a `.env` file in the root directory:
   ```env
   # LLM API Keys
   GROQ_API_KEY=your_groq_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here

   # Application Settings
   APP_NAME=JAI GURU DEV AI Companion
   DEBUG=False

   # Database
   DATABASE_PATH=database/guruji_bot.db

   # Vector Store
   VECTOR_DB_PATH=chroma_db/
   EMBEDDING_MODEL=text-embedding-3-large

   # LLM Settings
   LLM_MODEL=llama-3.3-70b-versatile
   LLM_TEMPERATURE=0.7
   MAX_TOKENS=1000
   ```

5. **Initialize the database** (if needed)
   ```bash
   python -c "from database.db_manager import Database; Database().init_database()"
   ```

6. **Run the application**
   ```bash
   streamlit run app.py
   ```

   Or use the provided batch file:
   ```bash
   START_CHATBOT.bat
   ```

---

## Agent System

### 1. Base Agent Architecture
**Files:** `agents/base_agent.py`, `agents/agent_types.py`, `agents/llm_config.py`

- Abstract base class for all agents
- Standardized AgentContext and AgentResponse protocols
- Multi-provider LLM support (Groq, OpenAI, Anthropic)
- Type-safe enums for all classifications

### 2. Orchestrator Agent
**File:** `agents/orchestrator_enhanced_routing.py`

**Responsibilities:**
- Receives user input + context
- Analyzes intent and determines which agents to call
- Coordinates multi-agent collaboration
- Synthesizes responses from multiple agents
- Maintains conversation coherence

**Supported Intents:**
- Seeking wisdom
- Expressing emotional/mental state
- Practice completion logging
- General conversation
- Practice inquiries

### 3. Wisdom Agent
**File:** `agents/wisdom_agent.py`

**Capabilities:**
- RAG-based wisdom retrieval from knowledge base
- Semantic search using vector embeddings
- Context-aware response generation
- Source attribution and citations
- Multi-document synthesis

**Knowledge Base:**
- Teaching files from 1995-2002
- Metadata-based filtering
- Topic and keyword tagging

### 4. Assessment Agent
**File:** `agents/assessment_agent_enhanced.py`

**Capabilities:**
- Comprehensive user state analysis
- Emotional/mental state detection (anxious, stressed, calm, confused, seeking, happy, sad, neutral)
- Severity classification (low/medium/high/critical)
- Physical indicator extraction
- Readiness assessment for practices
- Intervention type recommendations
- Urgency calculation (1-10 scale)
- Confidence scoring

**Analysis Methods:**
- LLM-powered state detection (structured JSON)
- Keyword-based validation
- Pattern analysis from history
- Trend detection (worsening/improving)

### 5. Practice Agent
**File:** `agents/practice_agent.py`

**Capabilities:**
- Comprehensive practice database (8+ core practices)
- Multi-criteria filtering and ranking
- LLM-powered instruction customization
- Safety considerations and contraindications

**Practice Database:**
- **Pranayama:** Nadi Shodhana, Ujjayi, Bhastrika, Three-Minute Breathing
- **Meditation:** Body Scan, Breath Awareness, Loving-Kindness
- **Contemplation:** Self-Inquiry
- **Movement:** Gentle Yoga Flow

**Ranking Algorithm:**
- State match (40%)
- Time of day fit (20%)
- Experience level match (15%)
- Previous success history (15%)
- Urgency appropriateness (10%)

### 6. Progress Agent
**File:** `agents/progress_agent.py`

**Capabilities:**
- Practice completion logging
- Comprehensive statistics tracking
- Streak calculation (current + longest)
- Pattern analysis and trend detection
- LLM-powered insight generation
- Personalized motivational messages

**Statistics Tracked:**
- Total practices and completions
- Adherence rate (%)
- Current streak (consecutive days)
- Longest streak achieved
- Practices by type
- Average rating (1-5)
- Average duration
- Total practice time
- Recent trends (improving/stable/declining)

---

## Project Structure

```
Guruji_Chatbot_Clean/
├── agents/                         # Agent implementations
│   ├── __init__.py
│   ├── agent_types.py             # Enums and type definitions
│   ├── agent_utils.py             # Shared utilities
│   ├── base_agent.py              # Abstract base class
│   ├── llm_config.py              # LLM provider configuration
│   ├── orchestrator_enhanced_routing.py  # Master coordinator ✅
│   ├── wisdom_agent.py            # Wisdom retrieval ✅
│   ├── assessment_agent_enhanced.py  # State analysis ✅
│   ├── practice_agent.py          # Practice recommendations ✅
│   └── progress_agent.py          # Progress tracking ✅
│
├── utils/                          # Utility functions
│   ├── __init__.py
│   ├── vector_store.py            # Vector DB operations
│   ├── session.py                 # Session management
│   └── helpers.py                 # Helper functions
│
├── models/                         # Data models
│   ├── __init__.py
│   ├── user.py                    # User profile model
│   └── practice.py                # Practice log model
│
├── database/                       # Database module
│   ├── __init__.py
│   └── db_manager.py              # SQLite operations
│
├── integrations/                   # External integrations
│   └── google_calendar_manager.py # Calendar integration
│
├── chroma_db/                      # Vector database
│   └── (ChromaDB files)
│
├── Knowledge_Base/                 # Source documents
│   ├── wisdom/
│   ├── practices/
│   └── guidelines/
│
├── docs/                           # Documentation
│   ├── assessment_agent_system_prompts.md
│   └── assessment_agent_workflow_documentation.md
│
├── tests/                          # Test files
│   ├── test_agent_integration.py
│   ├── test_assessment_agent.py
│   ├── test_base_agent.py
│   └── (other test files)
│
├── app.py                          # Main Streamlit application
├── chatbot_integrated.py           # Integrated chatbot logic
├── config.yaml                     # Configuration file
├── system_prompts.yaml             # System prompts
├── .env                            # Environment variables (not in git)
├── .gitignore
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── CONTRIBUTING.md                 # Contribution guidelines
└── START_CHATBOT.bat              # Windows launcher
```

---

## Development Timeline

### ✅ Phase 1: Foundation & Base Architecture (COMPLETED)

**Task 1: Base Agent Architecture** ✅
- Abstract base class for all agents
- Multi-provider LLM support (Groq, OpenAI, Anthropic)
- Type-safe enums for all classifications
- Error handling and logging infrastructure

**Task 2: Orchestrator Agent** ✅
- Master coordinator agent
- Intent classification system
- Multi-agent routing logic
- Response synthesis

**Task 3: Wisdom Agent** ✅
- RAG-based wisdom retrieval
- Vector database integration (ChromaDB)
- Semantic search implementation
- Source attribution

### ✅ Phase 2: Specialized Agents (COMPLETED)

**Task 4: Assessment Agent** ✅
- Comprehensive user state analysis
- Emotional/mental state detection
- Severity and readiness classification
- Pattern analysis from conversation history

**Task 5: Practice Agent** ✅
- Practice recommendation system
- Multi-criteria filtering and ranking
- LLM-powered instruction customization
- Safety considerations

**Task 6: Progress Agent** ✅
- Practice completion logging
- Statistics tracking and streak calculation
- Trend detection and insight generation
- Motivational messaging

### ⏳ Phase 3: Integration & Testing (IN PROGRESS)

**Immediate Next Steps:**
1. Run integration tests
2. Database integration (SQLite)
3. Vector database setup (ChromaDB with knowledge base)
4. Streamlit UI integration
5. End-to-end testing

### Future Phases

- **Phase 4:** Enhanced Knowledge Base
- **Phase 5:** Testing & Refinement
- **Phase 6:** Deployment to Streamlit Cloud
- **Phase 7:** Proactive Features (nudges, reminders)
- **Phase 8:** Personalization Agent
- **Phase 9:** Analytics & Insights
- **Phase 10:** Production Migration (FastAPI + Next.js)

---

## Next Steps

### IMMEDIATE PRIORITIES

#### 1. Run Integration Tests
```bash
cd tests
python test_agent_integration.py
```

**What This Tests:**
- Each agent individually
- Assessment → Practice flow
- Practice → Progress flow
- Complete end-to-end user journey
- Error handling

#### 2. Database Integration

**Action Items:**
- [ ] Implement SQLite operations in `database/db_manager.py`
- [ ] Create database schema (users, conversations, practice_logs tables)
- [ ] Connect Progress Agent to practice_logs table
- [ ] Test data persistence across sessions
- [ ] Add database migration scripts

**Database Schema:**
```sql
-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER,
    goal TEXT,
    health_context TEXT,
    experience_level TEXT DEFAULT 'beginner',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
    message_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Practice logs table
CREATE TABLE IF NOT EXISTS practice_logs (
    log_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    practice_name TEXT NOT NULL,
    practice_type TEXT,
    duration_minutes INTEGER,
    completed BOOLEAN DEFAULT TRUE,
    feedback TEXT,
    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

#### 3. Vector Database Setup

**Action Items:**
- [ ] Load knowledge base documents into ChromaDB
- [ ] Set up embeddings (OpenAI text-embedding-3-large)
- [ ] Test semantic search retrieval
- [ ] Verify source attribution
- [ ] Optimize chunking strategy

#### 4. Streamlit UI Integration

**Action Items:**
- [ ] Review `app.py` main application file
- [ ] Integrate Orchestrator with Streamlit UI
- [ ] Create practice recommendation display
- [ ] Create progress tracking dashboard
- [ ] Add practice logging interface
- [ ] Create statistics visualization
- [ ] Test complete user flows in UI

---

## Configuration

### LLM Provider Configuration

The system supports multiple LLM providers with automatic fallback:

**Primary:** Groq (llama-3.3-70b-versatile)
- Fast response times
- Cost-effective
- Good performance

**Fallback 1:** OpenAI (gpt-4o)
**Fallback 2:** Anthropic (claude-3-5-sonnet-20241022)

### Switching LLM Providers

Edit `config.yaml`:
```yaml
llm:
  provider: "groq"  # Options: groq, openai, anthropic
  model: "llama-3.3-70b-versatile"
  temperature: 0.7
  max_tokens: 1000
```

Or set environment variables in `.env`:
```env
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
```

---

## Testing

### Unit Tests

Run individual agent tests:
```bash
cd tests
python test_assessment_agent.py
python test_wisdom_agent.py
python test_orchestrator.py
```

### Integration Tests

Run complete integration test suite:
```bash
cd tests
python test_agent_integration.py
```

### Test Coverage

- Agent functionality
- Database operations
- Vector store retrieval
- Prompt generation
- Data model validation
- Error handling
- Fallback mechanisms

---

## Deployment

### Local Deployment

```bash
streamlit run app.py
```

Or use the batch file:
```bash
START_CHATBOT.bat
```

### Streamlit Cloud (Future Target)

**Steps:**
1. Create Streamlit Cloud account
2. Connect GitHub repository
3. Configure deployment settings
4. Set environment variables (API keys)
5. Deploy application
6. Monitor for errors

---

## Technical Documentation

For detailed technical information, see:

- **[Assessment Agent System Prompts](docs/assessment_agent_system_prompts.md)** - Complete prompt templates and modification guidelines
- **[Assessment Agent Workflow](docs/assessment_agent_workflow_documentation.md)** - Detailed workflow and technical specifications

---

## Success Metrics

### Technical Metrics
- Response time < 3 seconds
- Retrieval relevance > 80%
- Zero critical bugs
- 99% uptime

### User Experience
- User satisfaction > 4/5
- Conversation coherence score > 80%
- Practice recommendation acceptance > 70%

### Engagement
- Practice completion rate > 50%
- Return user rate > 60%
- Average session duration > 5 minutes

---

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Acknowledgments

**Knowledge Base:** Sri Sri Ravi Shankar's Teachings (1995-2002)
**Project Type:** Agentic RAG Chatbot - AI Spiritual Companion
**Development Approach:** Phased MVP with Streamlit → Production Migration

---

## Support

**Questions or Issues?**
1. Check this README for architecture and setup details
2. Review technical documentation in `docs/` folder
3. Run integration tests to verify functionality
4. Check individual agent files for comprehensive docstrings

---

**Last Updated:** November 8, 2025
**Status:** ✅ Core agents complete, ready for integration testing and UI implementation

JAI GURU DEV 🙏
