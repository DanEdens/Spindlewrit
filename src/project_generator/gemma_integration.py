import os
import json
from typing import Dict, Any, Optional
import requests


class GemmaProjectClient:
    """Client for Gemma function calling integration for project generation."""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """
        Initialize the Gemma client.
        
        Args:
            api_key: Gemma API key
            base_url: Optional custom API URL
        """
        self.api_key = api_key
        self.base_url = base_url or "https://api.gemma.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Todo Server URL for fetching todo items
        self.todo_server_url = os.environ.get("TODO_SERVER_URL", "http://localhost:8000")
    
    def generate_from_todo(self, todo_id: str) -> Dict[str, Any]:
        """
        Generate project details from a todo item using Gemma function calling.
        
        Args:
            todo_id: ID of the todo item to use
            
        Returns:
            Dictionary with project details
        """
        # 1. Fetch the todo item from the Todo Server
        todo_data = self._fetch_todo(todo_id)
        if not todo_data:
            raise Exception(f"Todo item with ID {todo_id} not found")
            
        # 2. Define the function schema for Gemma
        function_schema = {
            "name": "generate_project_structure",
            "description": "Generate a new project structure based on a todo description",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Project name (in kebab-case format)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Short description of the project"
                    },
                    "project_type": {
                        "type": "string",
                        "enum": ["python", "rust", "common"],
                        "description": "Type of project to create"
                    },
                    "additional_details": {
                        "type": "object",
                        "description": "Additional project details specific to the project type"
                    }
                },
                "required": ["name", "description", "project_type"]
            }
        }
        
        # 3. Create the prompt for Gemma
        prompt = self._create_project_prompt(todo_data)
        
        # 4. Call Gemma's function calling API
        response = self._call_gemma_function(prompt, function_schema)
        
        # 5. Parse and return the result
        try:
            function_call = response.get("function_call", {})
            if not function_call or "arguments" not in function_call:
                raise Exception("Failed to get function call response from Gemma")
                
            # Parse the arguments JSON
            arguments = json.loads(function_call["arguments"])
            return arguments
            
        except json.JSONDecodeError:
            raise Exception("Invalid JSON response from Gemma function call")
    
    def _fetch_todo(self, todo_id: str) -> Dict[str, Any]:
        """Fetch a todo item from the Todo Server."""
        try:
            response = requests.get(f"{self.todo_server_url}/api/todos/{todo_id}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch todo: {str(e)}")
    
    def _create_project_prompt(self, todo_data: Dict[str, Any]) -> str:
        """Create a prompt for Gemma based on the todo data."""
        description = todo_data.get("description", "")
        project = todo_data.get("project", "")
        metadata = todo_data.get("metadata", {})
        
        prompt = f"""
        Generate a project structure based on the following TODO item:
        
        Description: {description}
        Project: {project}
        
        Additional context:
        {json.dumps(metadata, indent=2) if metadata else "No additional context provided."}
        
        Your task is to determine:
        1. An appropriate project name (in kebab-case format)
        2. A concise project description
        3. The most suitable project type (python, rust, or common)
        4. Any additional details needed for the project setup
        
        Please use the function calling to provide structured output.
        """
        
        return prompt
    
    def _call_gemma_function(self, prompt: str, function_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Call Gemma's function calling API."""
        payload = {
            "model": "gemma-7b-it",  # Use appropriate model
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "tools": [{"type": "function", "function": function_schema}],
            "tool_choice": {"type": "function", "function": {"name": function_schema["name"]}}
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to call Gemma API: {str(e)}")


# Mock implementation for testing without actual Gemma API
class MockGemmaProjectClient(GemmaProjectClient):
    """Mock implementation of the Gemma client for testing."""
    
    def __init__(self):
        super().__init__("mock_api_key")
    
    def _fetch_todo(self, todo_id: str) -> Dict[str, Any]:
        """Mock todo fetch - returns a realistic todo item."""
        return {
            "id": todo_id,
            "description": f"Create a comprehensive test automation framework for todo-{todo_id}",
            "project": "test-framework",
            "status": "pending",
            "metadata": {
                "priority": "high",
                "tags": ["testing", "automation", "framework"]
            }
        }
    
    def _call_gemma_function(self, prompt: str, function_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Mock Gemma API response with more intelligent parsing."""
        # Extract meaningful info from the prompt
        import re
        description_match = re.search(r"Description: (.*?)(?:\n|$)", prompt)
        project_match = re.search(r"Project: (.*?)(?:\n|$)", prompt)
        
        description = description_match.group(1) if description_match else "AI-Generated Test Project"
        project = project_match.group(1) if project_match else "test-project"
        
        # Create a more realistic project name from the description
        name = description.lower()
        name = re.sub(r'[^a-z0-9\s-]', '', name)  # Remove special chars
        name = re.sub(r'\s+', '-', name)  # Replace spaces with hyphens
        name = name[:30]  # Limit length
        if not name:
            name = f"generated-project-{hash(description) % 1000}"

        # Determine project type based on keywords
        project_type = "python"
        if any(word in description.lower() for word in ["rust", "cargo", "rustc"]):
            project_type = "rust"
        elif any(word in description.lower() for word in ["web", "html", "css", "js"]):
            project_type = "common"
        
        return {
            "function_call": {
                "name": "generate_project_structure",
                "arguments": json.dumps({
                    "name": name,
                    "description": description,
                    "project_type": project_type,
                    "additional_details": {
                        "dependencies": ["pytest", "requests"] if project_type == "python" else [],
                        "testing_framework": "pytest" if project_type == "python" else "cargo test",
                        "generated_by": "spindlewrit_mock_client"
                    }
                })
            }
        } 
