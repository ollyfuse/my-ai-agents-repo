#!/usr/bin/env python3
"""
Demonstration of how the memory feature works in practice.
This simulates a conversation with an agent that remembers previous interactions.
"""

from shared.db import save_agent_response, get_memory_tool

def simulate_agent_conversation():
    """Simulate a conversation with the content creator agent using memory."""
    
    print("🎬 Content Creator Agent Memory Demo")
    print("=" * 50)
    
    # Get the memory tool for content creator agent
    get_memory = get_memory_tool("content_creator_agent")
    
    # Simulate a conversation sequence
    conversations = [
        {
            "user": "Create a caption for a video about learning Python",
            "agent": "🐍 [CASUAL] Ready to master Python? Start your coding journey today with these beginner-friendly tips! #Python #LearnToCode #Programming"
        },
        {
            "user": "Make it more professional",
            "agent": "🐍 [PROFESSIONAL] Advance your career with Python programming fundamentals. Essential skills for modern software development. #Python #ProfessionalDevelopment #TechSkills"
        },
        {
            "user": "Now create a playlist for coding sessions",
            "agent": "🎵 Created 'Focus Flow' playlist: 10 tracks of Lo-fi Hip Hop, Ambient Electronic, and Instrumental music perfect for deep coding sessions!"
        }
    ]
    
    # Simulate the conversation
    for i, conv in enumerate(conversations, 1):
        print(f"\n--- Conversation {i} ---")
        print(f"👤 User: {conv['user']}")
        
        # Agent checks memory before responding
        if i > 1:  # After first message, agent has memory
            print("🧠 Agent checking memory...")
            memory_result = get_memory(limit=3)
            print(f"   Found {memory_result['count']} previous conversations")
            
            # Show what the agent remembers
            if memory_result['conversations']:
                last_conv = memory_result['conversations'][-1]
                print(f"   Last interaction: '{last_conv['user_message'][:40]}...'")
        
        print(f"🤖 Agent: {conv['agent']}")
        
        # Save this conversation to memory
        save_agent_response(
            agent="content_creator_agent",
            user_message=conv['user'],
            agent_response=conv['agent'],
            session_id="demo_session"
        )
        print("   💾 Conversation saved to memory")
    
    # Show final memory state
    print(f"\n--- Final Memory State ---")
    final_memory = get_memory(limit=5)
    print(f"Total conversations in memory: {final_memory['count']}")
    
    print("\n📋 Complete conversation history:")
    for i, conv in enumerate(final_memory['conversations'], 1):
        print(f"  {i}. User: {conv['user_message']}")
        print(f"     Agent: {conv['agent_response'][:60]}...")
    
    print(f"\n🎯 Benefits demonstrated:")
    print("  ✅ Agent remembers previous caption style preferences")
    print("  ✅ Agent can reference past requests for context")
    print("  ✅ Conversation flows naturally with memory")
    print("  ✅ Each agent maintains separate memory")

def show_memory_across_agents():
    """Show how different agents maintain separate memories."""
    
    print(f"\n🔄 Cross-Agent Memory Demo")
    print("=" * 30)
    
    agents = ["content_creator_agent", "coding_agent", "learning_coach_agent"]
    
    for agent in agents:
        memory_tool = get_memory_tool(agent)
        memory = memory_tool(limit=5)
        
        print(f"\n{agent}:")
        print(f"  Conversations: {memory['count']}")
        
        if memory['conversations']:
            latest = memory['conversations'][-1]
            print(f"  Latest: '{latest['user_message'][:40]}...'")
        else:
            print("  No conversations yet")

if __name__ == "__main__":
    simulate_agent_conversation()
    show_memory_across_agents()
    
    print(f"\n🚀 Ready to use!")
    print("  Run 'adk web' to start the development UI")
    print("  Each agent now has memory of recent conversations")
    print("  Try asking follow-up questions to see memory in action")
