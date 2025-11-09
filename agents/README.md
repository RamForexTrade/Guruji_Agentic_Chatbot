# Base Agent Architecture Documentation

## 📋 Overview

The Base Agent Architecture provides a robust foundation for building specialized agents using **LangChain's agentic framework**. This architecture enables:

- **Tool-based agent execution** using LangChain's agent framework
- **Structured reasoning** with chain-of-thought capabilities
- **Error handling and fallbacks** for graceful degradation
- **Monitoring and logging** for observability
- **Inter-agent communication** protocols

## 🏗️ Architecture Components

### 1. **BaseAgent Class** (`agents/base_agent.py`)

The abstract base class that all specialized agents inherit from.

**Key Features:**
- LangChain integration with `AgentExecutor`
- Tool-based execution framework
- Structured input/output handling
- Automatic error handling
- Callback system for monitoring
- Confidence scoring

**Core Methods:**
```python
class BaseAgent(ABC):
    def define_tools(self) -> List[Tool]:
        """Define tools available to this agent"""
        
    def get_system_prompt(self) -> str:
        """Get system prompt for the agent"""
        
    def process(self, input_text, context, chat_history) -> AgentResponse:
        """Main processing method"""
```

### 2. **Agent Types** (`agents/agent_types.py`)

Enumerations and type definitions for the agent system.

**Enums:**
- `AgentType`: Types of agents (orchestrator, wisdom, assessment, etc.)
- `IntentType`: User intent classifications
- `MessageType`: Inter-agent message types
- `EmotionalState`: Detected emotional states
- `SeverityLevel`: Severity classifications
- `PracticeType`: Types of spiritual practices
- `ExperienceLevel`: User experience levels

### 3. **Communication Utilities** (`agents/agent_utils.py`)

Helper functions for agent communication and coordination.

**Key Classes:**
- `AgentMessage`: Structured inter-agent messages
- `AgentCommunicationProtocol`: Message handling and logging

**Helper Functions:**
- `format_user_context()`: Format user context for agents
- `extract_intent_keywords()`: Extract intent from text
- `merge_agent_responses()`: Combine multiple responses
- `calculate_average_confidence()`: Average confidence scores

### 4. **Data Structures**

#### **AgentContext**
```python
@dataclass
class AgentContext:
    user_id: str
    session_id: str
    user_profile: Dict[str, Any]
    conversation_history: List[Dict]
    timestamp: datetime
    metadata: Dict[str, Any]
```

#### **AgentResponse**
```python
@dataclass
class AgentResponse:
    agent_name: str
    content: str
    confidence: float
    metadata: Dict[str, Any]
    tools_used: List[str]
    processing_time: float
    success: bool
    error_message: Optional[str]
```

## 🚀 Creating a New Agent

### Step 1: Define Your Agent Class

```python
from agents.base_agent import BaseAgent, AgentContext, AgentResponse
from agents.agent_types import AgentType
from langchain.tools import Tool
from typing import List

class MyCustomAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_type=AgentType.WISDOM,  # Choose appropriate type
            name="my_custom_agent",
            temperature=0.7,
            verbose=True
        )
```

### Step 2: Define Tools

```python
def define_tools(self) -> List[Tool]:
    """Define tools available to this agent"""
    
    def my_tool_function(input_text: str) -> str:
        """Tool function implementation"""
        # Your logic here
        return "Tool output"
    
    return [
        Tool(
            name="my_tool",
            func=my_tool_function,
            description="Clear description of what this tool does"
        )
    ]
```

### Step 3: Define System Prompt

```python
def get_system_prompt(self) -> str:
    """Get system prompt for this agent"""
    return """You are a specialized agent for the Gurudev AI Companion.
    
Your role is to:
1. [Responsibility 1]
2. [Responsibility 2]
3. [Responsibility 3]

Available tools:
- tool_name: description

Guidelines:
- Be compassionate and supportive
- Provide clear, actionable guidance
- Stay focused on your specialized role
"""
```

### Step 4: (Optional) Override Methods

```python
def enrich_input(self, input_text: str, context: AgentContext) -> str:
    """Customize input enrichment"""
    enriched = super().enrich_input(input_text, context)
    # Add agent-specific context
    enriched += f"\nAdditional Context: {context.metadata.get('key')}"
    return enriched

def calculate_confidence(self, result: Dict[str, Any]) -> float:
    """Implement custom confidence calculation"""
    # Your confidence logic
    return 0.85

def get_fallback_response(self, context: AgentContext) -> str:
    """Provide agent-specific fallback"""
    return "Custom fallback message for this agent"
```

### Step 5: Use Your Agent

```python
# Initialize agent
agent = MyCustomAgent()

# Create context
context = AgentContext(
    user_id="user123",
    session_id="session456",
    user_profile={'name': 'Alice', 'age': 28}
)

# Process input
response = agent.process(
    input_text="User's question",
    context=context
)

# Access results
print(f"Response: {response.content}")
print(f"Confidence: {response.confidence}")
print(f"Tools Used: {response.tools_used}")
```

## 🧪 Testing

### Run All Tests

```bash
# Windows
TEST_BASE_AGENT.bat

# Or directly
python test_base_agent.py
```

### Test Coverage

The test suite includes:
1. ✅ Agent initialization
2. ✅ Tool definition
3. ✅ Agent executor setup
4. ✅ Context creation
5. ✅ Agent processing (requires API key)
6. ✅ Error handling

### Expected Output

```
========================================
🧪 BASE AGENT ARCHITECTURE TESTS
========================================

TEST 1: Agent Initialization
✅ Agent created: TestAgent(name='test_agent', type=AgentType.WISDOM)

TEST 2: Tool Definition
✅ Tools defined: 2 tools
   - greet_user: Greet the user by name
   - get_wisdom_quote: Get a wisdom quote

[... more tests ...]

📊 TEST SUMMARY
✅ Agent Initialization
✅ Tool Definition
✅ Agent Executor
✅ Context Creation
⚠️  Agent Processing (skipped)
✅ Error Handling

Total: 6 | Passed: 5 | Failed: 0 | Skipped: 1

🎉 All tests passed!
```

## 🔧 Configuration

### Environment Variables

Required in `.env`:
```env
OPENAI_API_KEY=your_api_key_here
```

### LLM Configuration

Default settings:
```python
model_name="gpt-4-turbo-preview"
temperature=0.7
max_iterations=3
```

Customize in agent initialization:
```python
agent = MyAgent(
    model_name="gpt-4",
    temperature=0.5
)
```

## 📊 Monitoring & Logging

### Built-in Logging

The base agent includes automatic logging:
- Agent initialization
- Tool execution
- Processing times
- Errors and warnings

### Custom Callback Handler

```python
class AgentCallbackHandler(BaseCallbackHandler):
    def on_tool_start(self, serialized, input_str, **kwargs):
        """Called when a tool starts"""
        
    def on_tool_end(self, output, **kwargs):
        """Called when a tool completes"""
        
    def on_tool_error(self, error, **kwargs):
        """Called on tool errors"""
```

### Accessing Metrics

```python
response = agent.process(input_text, context)

print(f"Processing time: {response.processing_time}s")
print(f"Tools used: {response.tools_used}")
print(f"Success: {response.success}")
print(f"Confidence: {response.confidence}")
```

## 🔄 Agent Communication

### Sending Messages Between Agents

```python
from agents.agent_utils import AgentCommunicationProtocol, AgentMessage
from agents.agent_types import MessageType

# Initialize protocol
protocol = AgentCommunicationProtocol()

# Send message
message = protocol.send_message(
    from_agent="orchestrator",
    to_agent="wisdom_agent",
    message_type=MessageType.QUERY,
    payload={'query': 'User question', 'context': {...}}
)

# Get message history
history = protocol.get_message_history(agent_name="wisdom_agent")
```

### Message Structure

```python
{
    'from_agent': 'orchestrator',
    'to_agent': 'wisdom_agent',
    'message_type': 'query',
    'payload': {
        'user_input': '...',
        'context': {...}
    },
    'timestamp': '2025-10-26T...',
    'message_id': 'uuid...'
}
```

## 🛡️ Error Handling

### Automatic Error Handling

All agents automatically handle errors:
1. **Validation errors**: Invalid input catches
2. **Processing errors**: Graceful fallback responses
3. **Tool errors**: Error logging and recovery
4. **LLM errors**: Retry logic and fallbacks

### Custom Error Handling

```python
def handle_error(self, error: Exception, context: AgentContext) -> AgentResponse:
    """Override for custom error handling"""
    logger.error(f"Custom error handler: {error}")
    
    # Implement custom logic
    if isinstance(error, SpecificError):
        return self.handle_specific_error(error, context)
    
    # Fallback to base class
    return super().handle_error(error, context)
```

## 📈 Best Practices

### 1. Tool Design
- **Single responsibility**: Each tool should do one thing well
- **Clear descriptions**: Help the LLM understand when to use the tool
- **Input validation**: Validate inputs in tool functions
- **Error handling**: Handle errors within tools gracefully

### 2. Prompt Engineering
- **Be specific**: Clear instructions for the agent's role
- **Provide examples**: Show expected behavior patterns
- **Set boundaries**: Define what the agent should NOT do
- **List tools**: Explicitly mention available tools

### 3. Context Management
- **Enrich carefully**: Add only relevant context
- **Validate context**: Ensure required fields are present
- **Update metadata**: Track important state changes
- **Limit history**: Don't overload with conversation history

### 4. Performance
- **Cache tools**: Reuse tool instances when possible
- **Limit iterations**: Set reasonable max_iterations
- **Monitor tokens**: Track token usage in metadata
- **Optimize prompts**: Keep prompts concise

### 5. Testing
- **Unit test tools**: Test each tool independently
- **Mock LLM calls**: Use mocks for faster testing
- **Test error paths**: Verify error handling works
- **Integration tests**: Test agent collaboration

## 🔜 Next Steps

After implementing the base architecture, proceed to:

1. **Create Orchestrator Agent** (`agents/orchestrator.py`)
   - Intent classification
   - Query routing
   - Multi-agent coordination

2. **Create Wisdom Agent** (`agents/wisdom_agent.py`)
   - Wrap existing RAG system
   - Enhanced retrieval
   - Source attribution

3. **Create Assessment Agent** (`agents/assessment_agent.py`)
   - Emotional state detection
   - Severity classification
   - Readiness assessment

4. **Create Practice Agent** (`agents/practice_agent.py`)
   - Practice recommendations
   - Instruction generation
   - Alternative suggestions

5. **Create Progress Agent** (`agents/progress_agent.py`)
   - Practice tracking
   - Progress analytics
   - Motivational messages

## 📚 Additional Resources

- [LangChain Agent Documentation](https://python.langchain.com/docs/modules/agents/)
- [LangChain Tools](https://python.langchain.com/docs/modules/agents/tools/)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [Master Plan](docs/GURUDEV_CHATBOT_MASTER_PLAN.md)

## 🤝 Contributing

When adding new agents:
1. Inherit from `BaseAgent`
2. Implement required abstract methods
3. Add comprehensive tests
4. Update this documentation
5. Follow naming conventions

## 📝 Notes

- **API Key Required**: OpenAI API key needed for agent processing
- **LangChain Version**: Tested with LangChain 0.1.0+
- **Python Version**: Requires Python 3.11+
- **Thread Safety**: Agents are not thread-safe by default

---

**Status**: ✅ Base architecture implemented and tested
**Version**: 1.0.0
**Last Updated**: October 26, 2025
