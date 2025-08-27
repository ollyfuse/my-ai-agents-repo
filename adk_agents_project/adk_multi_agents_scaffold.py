"""
ADK multi-agent scaffold generator (single-file).

Run this script to create a small ADK project with two free agents:
 - learning_coach_agent
 - content_creator_agent

It writes the folder structure, agent files, a tiny shared SQLite storage helper, a .env sample, and requirements.txt.

USAGE:
1. put this file in an empty folder
2. create and activate a venv (optional but recommended)
   python -m venv .venv
   source .venv/bin/activate
3. install requirements:
   pip install -r requirements.txt
4. run this script:
   python adk_multi_agents_scaffold.py
5. copy .env.sample into each agent folder and set your API key
   cp .env.sample learning_coach_agent/.env
   cp .env.sample content_creator_agent/.env
   # then edit the .env files and paste your API key

6. run ADK dev UI:
   adk web
   # open http://127.0.0.1:8000 and pick the agent from the dropdown

NOTES:
- This scaffold is intended for *free/API-key* mode (AI Studio / Express Mode). Do not enable ADC or Vertex billing.
- The scaffold uses a local SQLite DB (agents_data.db) for journaling and simple storage; keeps data local and free.

"""

from pathlib import Path
import os
import textwrap

ROOT = Path.cwd()

FILES = {
    "requirements.txt": textwrap.dedent("""
        google-adk>=0.5.0
        google-genai>=0.2.0
    """),

    ".env.sample": textwrap.dedent("""
        # Use API key mode (no gcloud ADC, no billing required)
        GOOGLE_GENAI_USE_VERTEXAI=FALSE
        # Paste your API key from Google AI Studio or Express Mode below
        GOOGLE_API_KEY=

        # Optional: default model override (change if you want)
        #MODEL_NAME=gemini-1.5-flash
    """),

    "shared/db.py": textwrap.dedent("""
        \"\"\"Tiny local storage helper using SQLite for agents.
        Keeps journals and content lists within a local file `agents_data.db`.
        \"\"\"
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
    """),

    "learning_coach_agent/__init__.py": "from . import agent\n",

    "learning_coach_agent/agent.py": textwrap.dedent("""
        # Learning Coach agent for step-by-step lessons + journaling
        from google.adk.agents import Agent
        from shared.db import save_journal, list_journals

        def create_lesson(topic: str, level: str = "beginner", steps: int = 3) -> dict:
            \"\"\"Return a short lesson broken into steps.
            This is a toy tool - in production you'd chunk and retrieve materials.
            \"\"\"
            steps = max(1, min(10, int(steps)))
            lesson_lines = [f"Step {i+1}: A short actionable explanation for {topic} (level={level})" for i in range(steps)]
            return {"status": "success", "lesson": "\\n".join(lesson_lines)}

        def generate_quiz(topic: str, num_questions: int = 3) -> dict:
            num_questions = max(1, min(10, int(num_questions)))
            questions = [f"Q{i+1}. Brief question about {topic} (short answer)" for i in range(num_questions)]
            return {"status": "success", "quiz": questions}

        def journal(entry: str, tags: str = None) -> dict:
            save_journal("learning_coach", entry, tags and tags.split(","))
            return {"status": "saved", "entry": entry}

        # ADK expects a `root_agent` object
        root_agent = Agent(
            name="learning_coach_agent",
            model="gemini-1.5-flash",
            description="A tutor that creates short lessons, quizzes, and records reflection journals.",
            instruction=(
                "You are a focused coding coach. When asked to teach, produce concise step-by-step lessons. "
                "When asked to make quizzes, produce short questions. If asked to journal, call the `journal` tool."
            ),
            tools=[create_lesson, generate_quiz, journal],
        )
    """),

    "content_creator_agent/__init__.py": "from . import agent\n",

    "content_creator_agent/agent.py": textwrap.dedent("""
        # Content Creator agent: captions, playlists, short scripts
        from google.adk.agents import Agent
        from shared.db import save_playlist, list_playlists

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
                "Hook: 1-2 lines to catch attention",
                "Body: 3 quick points with examples",
                "Call to action: 1 line"
            ]
            return {"status": "success", "outline": bullets}

        root_agent = Agent(
            name="content_creator_agent",
            model="gemini-1.5-flash",
            description="Helps generate captions, playlists, and short script outlines.",
            instruction=(
                "You are a concise content assistant: for captions be punchy, for playlists return a list, "
                "and for script outlines return 3-5 bullet points. Prefer short sentences."
            ),
            tools=[generate_caption, make_playlist, script_outline],
        )
    """),

    "run_instructions.txt": textwrap.dedent("""
        AFTER SCAFFOLDING
        -----------------
        1) Copy the sample .env into each agent folder and paste your API key:
           cp .env.sample learning_coach_agent/.env
           cp .env.sample content_creator_agent/.env
           # Then open each .env and paste the API key value after GOOGLE_API_KEY=

        2) Create virtualenv and install requirements (if you haven't):
           python -m venv .venv
           source .venv/bin/activate
           pip install -r requirements.txt

        3) Run ADK dev UI:
           adk web
           # Open http://127.0.0.1:8000 and choose the agent.

        4) Example prompts to try in Dev UI:
           - (learning_coach_agent) "Teach me how Django migrations work in 4 steps"
           - (learning_coach_agent) "Make a 5-question quiz on Python lists"
           - (learning_coach_agent) "Journal: Today I learned about class-based views"

           - (content_creator_agent) "Write a caption for a 30-second TikTok about debugging"
           - (content_creator_agent) "Make a 12-song playlist for Afrobeat, Old School R&B"

        5) Data will be stored locally in `agents_data.db`.
    """),
}


def write_files():
    for relpath, content in FILES.items():
        path = ROOT / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        # skip overwriting if exists
        if path.exists():
            print(f"Skipping existing: {path}")
            continue
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Wrote: {path}")


if __name__ == "__main__":
    write_files()
    print("\nScaffold complete. See run_instructions.txt for next steps.")
