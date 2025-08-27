# Agent Memory Feature 🧠

This document describes the memory functionality added to the multi-agent system, allowing agents to remember and reference previous conversations.

## Overview

The memory feature enables agents to:
- Store conversation history in SQLite database
- Retrieve last 3-5 responses per agent for context
- Provide better, contextually-aware responses
- Maintain separate memory for each agent

## Database Schema

### New Table: `agent_responses`
```sql
CREATE TABLE agent_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent TEXT,                    -- Agent name (e.g., "content_creator_agent")
    user_message TEXT,             -- User's input message
    agent_response TEXT,           -- Agent's response
    session_id TEXT,               -- Optional session identifier
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## New Functions in `shared/db.py`

### Core Memory Functions

1. **`save_agent_response(agent, user_message, agent_response, session_id=None)`**
   - Saves a conversation exchange to the database
   - Used to build conversation history

2. **`get_agent_memory(agent_name, limit=5)`**
   - Retrieves last N responses for a specific agent
   - Returns raw database rows in chronological order

3. **`get_recent_conversations(agent_name, limit=5)`**
   - Returns formatted conversation history as dictionaries
   - Easier to work with than raw database rows

4. **`format_memory_for_context(agent_name, limit=5)`**
   - Formats conversations as a context string
   - Ready to use in agent instructions or prompts

5. **`get_memory_tool(agent_name)`**
   - Creates a memory tool function for a specific agent
   - Returns a callable tool that agents can use

## Agent Integration

### Memory Tool Added to All Agents

Each agent now has a `get_memory()` tool that can be called to retrieve recent conversations:

```python
# Example usage in agent
get_memory = get_memory_tool("content_creator_agent")

# Agent can call this tool
result = get_memory(limit=3)
# Returns: {
#   "status": "success",
#   "conversations": [...],
#   "count": 3,
#   "formatted_context": "Recent conversation history:\nUser: ...\nYou: ...\n---"
# }
```

### Updated Agents

All agents have been updated with memory functionality:

1. **Content Creator Agent** (`content_creator_agent`)
   - Remembers previous caption styles, playlist preferences
   - Can reference past creative requests

2. **Coding Agent** (`coding_agent`)
   - Remembers debugging sessions, code patterns
   - Can reference previous solutions and approaches

3. **Learning Coach Agent** (`learning_coach_agent`)
   - Remembers learning progress, topics covered
   - Can build on previous lessons

4. **Project Manager Agent** (`project_manager_agent`)
   - Remembers project context, task history
   - Can reference previous planning decisions

5. **Multi-Tool Agent** (`multi_tool_agent`)
   - Remembers weather/time queries
   - Can provide contextual responses

## Usage Examples

### For Agent Developers

```python
from shared.db import get_memory_tool, save_agent_response

# Create memory tool for your agent
get_memory = get_memory_tool("my_agent")

# In your agent's tool list
tools = [my_tool1, my_tool2, get_memory]

# Save responses (typically done by the framework)
save_agent_response(
    agent="my_agent",
    user_message="User's question",
    agent_response="Agent's response",
    session_id="optional_session_id"
)
```

### For Users

Agents can now reference previous conversations:

```
User: "Create a caption for a Python tutorial"
Agent: [Creates caption]

User: "Make it more technical"
Agent: [Can reference the previous caption and adjust the tone]
```

## Testing

Run the test script to verify memory functionality:

```bash
python test_memory.py
```

This will:
- Initialize the database with the new table
- Save sample conversations for different agents
- Retrieve and display memory for each agent
- Test the memory tool function

## Benefits

1. **Contextual Responses**: Agents can reference previous conversations
2. **Better User Experience**: No need to repeat context
3. **Learning Capability**: Agents can build on previous interactions
4. **Session Continuity**: Maintain context across multiple exchanges
5. **Agent Specialization**: Each agent maintains its own memory

## Configuration

### Memory Limits
- Default: 5 recent conversations per agent
- Configurable: 1-10 conversations (adjustable in tool calls)
- Storage: Unlimited (SQLite database grows as needed)

### Performance
- Indexed by agent name for fast retrieval
- Chronological ordering for context relevance
- Minimal overhead on agent response time

## Future Enhancements

Potential improvements:
- Semantic search within memory
- Memory summarization for long histories
- Cross-agent memory sharing
- Memory expiration/cleanup policies
- Advanced session management
