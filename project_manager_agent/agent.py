# Project Manager Agent for task tracking, docs, and Git workflow
from google.adk.agents import Agent
from shared.db import save_journal, list_journals, get_memory_tool
import datetime
import json

def add_task(task_description: str, due_date: str = "", priority: str = "medium", tags: str = "") -> dict:
    """Add a new task to the project tracker.
    due_date format: YYYY-MM-DD or descriptive like 'Friday', 'next week'
    priority: low, medium, high
    """
    task_data = {
        "description": task_description,
        "due_date": due_date,
        "priority": priority.lower(),
        "status": "pending",
        "created_at": datetime.datetime.now().isoformat()
    }
    
    tag_list = tags.split(",") if tags else []
    tag_list.extend(["task", priority.lower()])
    
    task_entry = f"TASK: {task_description}\nDUE: {due_date}\nPRIORITY: {priority}\nSTATUS: pending"
    save_journal("project_manager", task_entry, tag_list)
    
    return {
        "status": "success", 
        "message": f"Task added: {task_description}",
        "task_data": task_data
    }

def list_tasks(status: str = "all", limit: int = 20) -> dict:
    """List tasks by status: all, pending, completed, or overdue."""
    limit = max(1, min(100, int(limit)))
    history = list_journals(limit)
    
    tasks = []
    for row in history:
        if row[1] == "project_manager" and "TASK:" in row[2]:
            task_entry = row[2]
            task_info = {
                "id": row[0],
                "entry": task_entry,
                "created_at": row[4],
                "tags": row[3]
            }
            
            # Filter by status if specified
            if status == "all" or status.lower() in task_entry.lower():
                tasks.append(task_info)
    
    return {
        "status": "success", 
        "tasks": tasks, 
        "count": len(tasks),
        "filter": status
    }

def update_task_status(task_id: int, new_status: str) -> dict:
    """Update task status: pending, in-progress, completed, cancelled."""
    # Note: In a real implementation, you'd update the database record
    # For this demo, we'll add a status update entry
    
    status_update = f"TASK_UPDATE: Task ID {task_id} status changed to {new_status}"
    save_journal("project_manager", status_update, ["task", "update", new_status])
    
    return {
        "status": "success",
        "message": f"Task {task_id} status updated to {new_status}",
        "task_id": task_id,
        "new_status": new_status
    }

def add_project_doc(doc_title: str, doc_url: str, doc_type: str = "general", description: str = "") -> dict:
    """Add a project document or link for reference.
    doc_type: requirements, design, api, meeting-notes, general
    """
    doc_entry = f"DOC: {doc_title}\nURL: {doc_url}\nTYPE: {doc_type}\nDESC: {description}"
    save_journal("project_manager", doc_entry, ["documentation", doc_type, "reference"])
    
    return {
        "status": "success",
        "message": f"Document added: {doc_title}",
        "doc_data": {
            "title": doc_title,
            "url": doc_url,
            "type": doc_type,
            "description": description
        }
    }

def generate_git_workflow_summary(branch_name: str, feature_description: str) -> dict:
    """Generate a Git workflow summary for a feature branch."""
    
    workflow_steps = [
        f"# Git Workflow for {branch_name}",
        f"## Feature: {feature_description}",
        "",
        "### 1. Create and switch to feature branch:",
        f"```bash",
        f"git checkout -b {branch_name}",
        f"```",
        "",
        "### 2. Make your changes and commit:",
        "```bash",
        "git add .",
        f'git commit -m "Add: {feature_description}"',
        "```",
        "",
        "### 3. Push branch to remote:",
        "```bash",
        f"git push origin {branch_name}",
        "```",
        "",
        "### 4. Create Pull Request:",
        "- Go to your repository on GitHub/GitLab",
        f"- Create PR from {branch_name} to main/develop",
        f"- Title: {feature_description}",
        "- Add description and request reviewers",
        "",
        "### 5. After PR approval:",
        "```bash",
        "git checkout main",
        "git pull origin main",
        f"git branch -d {branch_name}  # Delete local branch",
        "```"
    ]
    
    workflow_text = "\n".join(workflow_steps)
    
    # Save workflow to database
    save_journal("project_manager", f"Git workflow for {branch_name}: {feature_description}", ["git", "workflow", "branch"])
    
    return {
        "status": "success",
        "workflow": workflow_text,
        "branch_name": branch_name,
        "feature": feature_description
    }

def set_reminder(reminder_text: str, reminder_date: str, reminder_type: str = "general") -> dict:
    """Set a project reminder.
    reminder_date: YYYY-MM-DD or descriptive like 'tomorrow', 'next Monday'
    reminder_type: deadline, meeting, review, general
    """
    reminder_entry = f"REMINDER: {reminder_text}\nDATE: {reminder_date}\nTYPE: {reminder_type}"
    save_journal("project_manager", reminder_entry, ["reminder", reminder_type, "scheduled"])
    
    return {
        "status": "success",
        "message": f"Reminder set: {reminder_text}",
        "reminder_data": {
            "text": reminder_text,
            "date": reminder_date,
            "type": reminder_type
        }
    }

def get_project_summary(days_back: int = 7) -> dict:
    """Get a summary of recent project activity."""
    limit = days_back * 10  # Rough estimate of entries per day
    history = list_journals(limit)
    
    pm_entries = [row for row in history if row[1] == "project_manager"]
    
    summary = {
        "total_entries": len(pm_entries),
        "tasks": len([e for e in pm_entries if "TASK:" in e[2]]),
        "docs": len([e for e in pm_entries if "DOC:" in e[2]]),
        "reminders": len([e for e in pm_entries if "REMINDER:" in e[2]]),
        "git_workflows": len([e for e in pm_entries if "Git workflow" in e[2]]),
        "recent_activity": pm_entries[:10]  # Last 10 entries
    }
    
    return {
        "status": "success",
        "summary": summary,
        "days_back": days_back
    }

# Create memory tool for this agent
get_memory = get_memory_tool("project_manager_agent")

# ADK expects a `root_agent` object
root_agent = Agent(
    name="project_manager_agent",
    model="gemini-1.5-flash",
    description="A project management assistant for tracking tasks, managing docs, and Git workflows with memory of recent conversations.",
    instruction=(
        "You are a helpful project manager with memory of recent conversations. "
        "When users want to add tasks, immediately call add_task. "
        "When users want to see tasks, immediately call list_tasks. "
        "When users want Git workflows, immediately call generate_git_workflow_summary. "
        "When users want reminders, immediately call set_reminder. "
        "You can use get_memory to recall recent conversations for context. "
        "Always use your tools - don't just provide text responses. Call the appropriate function for every request."
    ),
    tools=[add_task, list_tasks, update_task_status, add_project_doc, generate_git_workflow_summary, set_reminder, get_project_summary, get_memory],
)
