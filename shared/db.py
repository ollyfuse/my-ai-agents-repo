
"""Tiny local storage helper using SQLite for agents.
Keeps journals and content lists within a local file `agents_data.db`.
"""
import sqlite3
from pathlib import Path
import json

DB_PATH = Path(__file__).resolve().parent.parent / "agents_data.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS journals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent TEXT,
            entry TEXT,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            items TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS agent_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent TEXT,
            user_message TEXT,
            agent_response TEXT,
            session_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_journal(agent: str, entry: str, tags=None):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('INSERT INTO journals (agent, entry, tags) VALUES (?, ?, ?)', (agent, entry, json.dumps(tags)))
    conn.commit()
    conn.close()
    return {"status": "ok"}

def list_journals(limit=20):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT id, agent, entry, tags, created_at FROM journals ORDER BY id DESC LIMIT ?', (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_journals_by_agent(agent_name: str, limit=20):
    """Get journals for a specific agent."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT id, agent, entry, tags, created_at FROM journals WHERE agent = ? ORDER BY id DESC LIMIT ?', (agent_name, limit))
    rows = cur.fetchall()
    conn.close()
    return rows

def search_journals(search_term: str, limit=20):
    """Search journals by content or tags."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT id, agent, entry, tags, created_at FROM journals WHERE entry LIKE ? OR tags LIKE ? ORDER BY id DESC LIMIT ?',
                (f'%{search_term}%', f'%{search_term}%', limit))
    rows = cur.fetchall()
    conn.close()
    return rows

def save_playlist(name: str, items: list):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('INSERT INTO playlists (name, items) VALUES (?, ?)', (name, json.dumps(items)))
    conn.commit()
    conn.close()
    return {"status": "ok"}

def list_playlists(limit=20):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT id, name, items, created_at FROM playlists ORDER BY id DESC LIMIT ?', (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows

def save_agent_response(agent: str, user_message: str, agent_response: str, session_id=None):
    """Save an agent's response to a user message for memory purposes."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('INSERT INTO agent_responses (agent, user_message, agent_response, session_id) VALUES (?, ?, ?, ?)',
                (agent, user_message, agent_response, session_id))
    conn.commit()
    conn.close()
    return {"status": "ok"}

def get_agent_memory(agent_name: str, limit: int = 5):
    """Get the last N responses for a specific agent to provide context/memory."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''SELECT id, user_message, agent_response, session_id, created_at
                   FROM agent_responses
                   WHERE agent = ?
                   ORDER BY id DESC
                   LIMIT ?''', (agent_name, limit))
    rows = cur.fetchall()
    conn.close()

    # Return in chronological order (oldest first) for better context
    return list(reversed(rows))

def get_recent_conversations(agent_name: str, limit: int = 5):
    """Get recent conversation history formatted for agent context."""
    memory_rows = get_agent_memory(agent_name, limit)

    conversations = []
    for row in memory_rows:
        conversations.append({
            "id": row[0],
            "user_message": row[1],
            "agent_response": row[2],
            "session_id": row[3],
            "created_at": row[4]
        })

    return conversations

def format_memory_for_context(agent_name: str, limit: int = 5):
    """Format recent conversations as context string for agent instructions."""
    conversations = get_recent_conversations(agent_name, limit)

    if not conversations:
        return "No previous conversation history."

    context_parts = ["Recent conversation history:"]
    for conv in conversations:
        context_parts.append(f"User: {conv['user_message']}")
        context_parts.append(f"You: {conv['agent_response']}")
        context_parts.append("---")

    return "\n".join(context_parts)

def get_memory_tool(agent_name: str):
    """Create a memory tool function for a specific agent."""
    def get_memory(limit: int = 5) -> dict:
        """Get recent conversation history for context."""
        limit = max(1, min(10, int(limit)))  # Limit between 1-10
        conversations = get_recent_conversations(agent_name, limit)

        return {
            "status": "success",
            "conversations": conversations,
            "count": len(conversations),
            "formatted_context": format_memory_for_context(agent_name, limit)
        }

    return get_memory
