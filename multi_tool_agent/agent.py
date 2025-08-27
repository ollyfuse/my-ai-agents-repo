import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from shared.db import get_memory_tool

def get_weather(city: str) -> dict:
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": "The weather in New York is sunny with a temperature of 25°C (77°F).",
        }
    return {"status": "error", "error_message": f"No weather info for '{city}'."}

def get_current_time(city: str) -> dict:
    if city.lower() == "new york":
        tz = ZoneInfo("America/New_York")
        now = datetime.datetime.now(tz)
        return {"status": "success", "report": now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}
    return {"status": "error", "error_message": f"No timezone info for '{city}'."}

# Create memory tool for this agent
get_memory = get_memory_tool("multi_tool_agent")

# This is what ADK looks for in the Dev UI
root_agent = Agent(
    name="multi_tool_agent",
    model="gemini-2.0-flash",  # free-tier friendly model
    description="Answers time/weather questions for a city with memory of recent conversations.",
    instruction="Be concise and helpful. You can use get_memory to recall recent conversations for context.",
    tools=[get_weather, get_current_time, get_memory],
)
