
# Learning Coach agent for step-by-step lessons + journaling
from google.adk.agents import Agent
from shared.db import save_journal, list_journals, get_memory_tool

def create_lesson(topic: str, level: str, steps: int) -> dict:
    """Create a step-by-step lesson on the given topic.

    Args:
        topic: The subject to teach (e.g., "Django models", "Python functions")
        level: Difficulty level ("beginner", "intermediate", "advanced")
        steps: Number of steps in the lesson (1-10)

    Returns:
        A dictionary with lesson content
    """
    # Set defaults if not provided
    if not level:
        level = "beginner"
    if not steps or steps < 1:
        steps = 3

    steps = max(1, min(10, int(steps)))
    lesson_lines = [f"Step {i+1}: A short actionable explanation for {topic} (level={level})" for i in range(steps)]
    return {"status": "success", "lesson": "\n".join(lesson_lines)}

def generate_quiz(topic: str, num_questions: int) -> dict:
    """Generate a quiz with multiple questions on the given topic.

    Args:
        topic: The subject for the quiz (e.g., "Python basics", "Django")
        num_questions: Number of questions to generate (1-10)

    Returns:
        A dictionary with quiz questions
    """
    # Set default if not provided
    if not num_questions or num_questions < 1:
        num_questions = 3

    num_questions = max(1, min(10, int(num_questions)))
    questions = [f"Q{i+1}. Brief question about {topic} (short answer)" for i in range(num_questions)]
    return {"status": "success", "quiz": questions}

def journal(entry: str, tags: str) -> dict:
    """Save a journal entry for learning reflection.

    Args:
        entry: The journal entry text
        tags: Comma-separated tags for categorization

    Returns:
        Confirmation of saved entry
    """
    # Handle empty tags
    if not tags:
        tags = ""

    tag_list = tags.split(",") if tags else None
    save_journal("learning_coach", entry, tag_list)
    return {"status": "saved", "entry": entry}

# Create memory tool for this agent
get_memory = get_memory_tool("learning_coach_agent")

# ADK expects a `root_agent` object
root_agent = Agent(
    name="learning_coach_agent",
    model="gemini-1.5-flash",
    description="A tutor that creates short lessons, quizzes, and records reflection journals with memory of recent conversations.",
    instruction=(
        "You are a focused coding coach with memory of recent conversations. "
        "When users ask you to teach something, immediately call the create_lesson tool. "
        "When users ask for quizzes, immediately call the generate_quiz tool. "
        "When users ask to journal something, immediately call the journal tool. "
        "You can use get_memory to recall recent conversations for context. "
        "Always use your tools - don't just provide text responses. Call the appropriate function for every request."
    ),
    tools=[create_lesson, generate_quiz, journal, get_memory],
)
