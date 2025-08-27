# Coding Agent for Django, Frontend, and QA assistance
from google.adk.agents import Agent
from shared.db import save_journal, list_journals, get_memory_tool
import datetime

def generate_django_model(model_name: str, fields: str, description: str = "") -> dict:
    """Generate a Django model with specified fields.
    Fields should be comma-separated like: title:CharField,content:TextField,author:ForeignKey
    """
    field_list = fields.split(",")
    model_code = f"from django.db import models\nfrom django.contrib.auth.models import User\n\n"
    model_code += f"class {model_name}(models.Model):\n"
    
    for field in field_list:
        if ":" in field:
            field_name, field_type = field.strip().split(":")
            if field_type.lower() == "charfield":
                model_code += f"    {field_name} = models.CharField(max_length=200)\n"
            elif field_type.lower() == "textfield":
                model_code += f"    {field_name} = models.TextField()\n"
            elif field_type.lower() == "foreignkey":
                model_code += f"    {field_name} = models.ForeignKey(User, on_delete=models.CASCADE)\n"
            elif field_type.lower() == "datetimefield":
                model_code += f"    {field_name} = models.DateTimeField(auto_now_add=True)\n"
            else:
                model_code += f"    {field_name} = models.{field_type}()\n"
    
    model_code += f"\n    def __str__(self):\n        return str(self.id)\n"
    model_code += f"\n    class Meta:\n        verbose_name = '{model_name}'\n        verbose_name_plural = '{model_name}s'"
    
    # Save to database
    save_journal("coding_agent", f"Generated Django model: {model_name}", ["django", "model", "code"])
    
    return {"status": "success", "model_code": model_code, "description": description}

def debug_python_code(code_snippet: str, error_description: str) -> dict:
    """Analyze Python code and provide debugging suggestions."""
    suggestions = []
    
    # Common debugging patterns
    if "IndexError" in error_description:
        suggestions.append("Check if you're accessing a list index that doesn't exist")
        suggestions.append("Use len(list) to check list size before accessing")
        suggestions.append("Consider using try/except or list slicing with bounds")
    
    if "KeyError" in error_description:
        suggestions.append("Check if the dictionary key exists using 'key in dict'")
        suggestions.append("Use dict.get('key', default_value) for safe access")
    
    if "AttributeError" in error_description:
        suggestions.append("Check if the object has the attribute using hasattr()")
        suggestions.append("Verify the object type - it might be None or different than expected")
    
    # General suggestions
    suggestions.append("Add print statements to debug variable values")
    suggestions.append("Use a debugger or IDE breakpoints")
    suggestions.append("Check variable types with type() function")
    
    # Save debug session
    save_journal("coding_agent", f"Debug session: {error_description}", ["debug", "python", "error"])
    
    return {
        "status": "success", 
        "suggestions": suggestions,
        "code_snippet": code_snippet,
        "error": error_description
    }

def generate_test_cases(function_name: str, function_description: str, test_count: int = 3) -> dict:
    """Generate unit test cases for a given function."""
    test_count = max(1, min(10, int(test_count)))
    
    test_code = f"import unittest\n\n"
    test_code += f"class Test{function_name.title()}(unittest.TestCase):\n\n"
    
    for i in range(test_count):
        test_code += f"    def test_{function_name}_case_{i+1}(self):\n"
        test_code += f"        # Test case {i+1}: {function_description}\n"
        test_code += f"        # TODO: Add test implementation\n"
        test_code += f"        result = {function_name}(test_input)\n"
        test_code += f"        self.assertEqual(result, expected_output)\n\n"
    
    test_code += f"if __name__ == '__main__':\n    unittest.main()"
    
    # Save to database
    save_journal("coding_agent", f"Generated test cases for: {function_name}", ["testing", "unittest", "qa"])
    
    return {
        "status": "success", 
        "test_code": test_code,
        "function_name": function_name,
        "test_count": test_count
    }

def save_code_snippet(title: str, code: str, language: str = "python", tags: str = "") -> dict:
    """Save a code snippet for future reference."""
    tag_list = tags.split(",") if tags else []
    tag_list.extend(["snippet", language])
    
    snippet_entry = f"TITLE: {title}\nLANGUAGE: {language}\nCODE:\n{code}"
    save_journal("coding_agent", snippet_entry, tag_list)
    
    return {"status": "saved", "title": title, "language": language}

def get_coding_history(limit: int = 10) -> dict:
    """Retrieve recent coding assistance history."""
    limit = max(1, min(50, int(limit)))
    history = list_journals(limit)
    
    coding_history = [
        {
            "id": row[0],
            "entry": row[2],
            "tags": row[3],
            "created_at": row[4]
        }
        for row in history if row[1] == "coding_agent"
    ]
    
    return {"status": "success", "history": coding_history, "count": len(coding_history)}

# Create memory tool for this agent
get_memory = get_memory_tool("coding_agent")

# ADK expects a `root_agent` object
root_agent = Agent(
    name="coding_agent",
    model="gemini-1.5-flash",
    description="A coding assistant specializing in Django, frontend development, and QA testing with memory of recent conversations.",
    instruction=(
        "You are an expert coding assistant with memory of recent conversations. "
        "When users ask for Django models, immediately call generate_django_model. "
        "When users ask for debugging help, immediately call debug_python_code. "
        "When users ask for tests, immediately call generate_test_cases. "
        "When users want to save code, immediately call save_code_snippet. "
        "You can use get_memory to recall recent conversations for context. "
        "Always use your tools - don't just provide text responses. Call the appropriate function for every request."
    ),
    tools=[generate_django_model, debug_python_code, generate_test_cases, save_code_snippet, get_coding_history, get_memory],
)
