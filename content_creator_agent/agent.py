
# Content Creator agent: captions, playlists, short scripts
from google.adk.agents import Agent
from shared.db import save_playlist, list_playlists, get_memory_tool, save_agent_response, format_memory_for_context

def generate_caption(text: str, tone: str = "casual") -> dict:
    caption = f"[{tone.upper()}] {text[:140]}..." if len(text) > 140 else f"[{tone.upper()}] {text}"
    return {"status": "success", "caption": caption}

def make_playlist(genres: str, length: int = 10) -> dict:
    # genres: comma-separated list
    items = [f"{g.strip().title()} Song {i+1}" for i, g in enumerate(genres.split(",")) for _ in range(max(1, int(length)//max(1, len(genres.split(",")))))][:length]
    save_playlist(f"Playlist ({genres})", items)
    return {"status": "success", "playlist": items}

def script_outline(topic: str, duration_seconds: int = 60) -> dict:
    bullets = [
        f"Hook: 1-2 lines to catch attention about {topic}",
        f"Body: 3 quick points with examples about {topic}",
        "Call to action: 1 line"
    ]
    return {"status": "success", "outline": bullets, "topic": topic, "duration": duration_seconds}

# Create memory tool for this agent
get_memory = get_memory_tool("content_creator_agent")

root_agent = Agent(
    name="content_creator_agent",
    model="gemini-1.5-flash",
    description="Helps generate captions, playlists, and short script outlines with memory of recent conversations.",
    instruction=(
        "You are a content assistant with memory of recent conversations. "
        "When users ask for captions, immediately call the generate_caption tool. "
        "When users ask for playlists, immediately call the make_playlist tool. "
        "When users ask for scripts, immediately call the script_outline tool. "
        "You can use get_memory to recall recent conversations for context. "
        "Always use your tools - don't just provide text responses. Call the appropriate function for every request."
    ),
    tools=[generate_caption, make_playlist, script_outline, get_memory],
)
