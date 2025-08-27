#!/usr/bin/env python3
"""
Test script to demonstrate the memory functionality for agents.
This script shows how to save and retrieve agent responses.
"""

from shared.db import (
    init_db, 
    save_agent_response, 
    get_agent_memory, 
    get_recent_conversations,
    format_memory_for_context,
    get_memory_tool
)

def test_memory_functionality():
    """Test the memory functionality with sample data."""
    print("🧠 Testing Agent Memory Functionality")
    print("=" * 50)
    
    # Initialize the database
    init_db()
    print("✅ Database initialized")
    
    # Test data for different agents
    test_conversations = [
        {
            "agent": "content_creator_agent",
            "user_message": "Create a caption for a video about Python programming",
            "agent_response": "🐍 [CASUAL] Master Python programming with these essential tips! From variables to functions, level up your coding game today! #Python #Programming #CodeLife"
        },
        {
            "agent": "content_creator_agent", 
            "user_message": "Make a playlist for coding music",
            "agent_response": "Created a 10-song coding playlist with Lo-fi, Electronic, and Ambient tracks perfect for deep focus sessions!"
        },
        {
            "agent": "coding_agent",
            "user_message": "Help me debug this IndexError in my Python code",
            "agent_response": "IndexError usually means you're trying to access a list index that doesn't exist. Check your list bounds and use len() to verify size before accessing elements."
        },
        {
            "agent": "coding_agent",
            "user_message": "Generate a Django model for a blog post",
            "agent_response": "Created a BlogPost model with title (CharField), content (TextField), author (ForeignKey to User), and created_at (DateTimeField) fields."
        },
        {
            "agent": "learning_coach_agent",
            "user_message": "Teach me about Django migrations in 3 steps",
            "agent_response": "Step 1: Create migration files with 'python manage.py makemigrations'\nStep 2: Apply migrations with 'python manage.py migrate'\nStep 3: Check migration status with 'python manage.py showmigrations'"
        }
    ]
    
    # Save test conversations
    print("\n📝 Saving test conversations...")
    for conv in test_conversations:
        save_agent_response(
            conv["agent"], 
            conv["user_message"], 
            conv["agent_response"],
            session_id="test_session_1"
        )
        print(f"   Saved conversation for {conv['agent']}")
    
    # Test memory retrieval for each agent
    print("\n🔍 Testing memory retrieval...")
    
    agents = ["content_creator_agent", "coding_agent", "learning_coach_agent"]
    
    for agent in agents:
        print(f"\n--- Memory for {agent} ---")
        
        # Get recent conversations
        conversations = get_recent_conversations(agent, limit=3)
        print(f"Found {len(conversations)} conversations")
        
        for i, conv in enumerate(conversations, 1):
            print(f"  {i}. User: {conv['user_message'][:50]}...")
            print(f"     Agent: {conv['agent_response'][:50]}...")
        
        # Test formatted context
        context = format_memory_for_context(agent, limit=2)
        print(f"\nFormatted context preview:")
        print(context[:200] + "..." if len(context) > 200 else context)
    
    # Test the memory tool function
    print("\n🛠️  Testing memory tool function...")
    content_memory_tool = get_memory_tool("content_creator_agent")
    
    result = content_memory_tool(limit=2)
    print(f"Memory tool result: {result['status']}")
    print(f"Conversations found: {result['count']}")
    
    print("\n✅ All memory functionality tests completed!")
    print("\n💡 Usage in agents:")
    print("   - Agents now have a get_memory() tool")
    print("   - Call get_memory(limit=5) to get recent conversations")
    print("   - Memory provides context for better responses")
    print("   - Each agent maintains separate conversation history")

if __name__ == "__main__":
    test_memory_functionality()
