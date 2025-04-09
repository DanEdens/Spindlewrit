import json
import unittest
from unittest.mock import patch, MagicMock

from project_generator.gemma_integration import GemmaProjectClient, MockGemmaProjectClient


class TestGemmaProjectClient(unittest.TestCase):
    """Test the Gemma Project Client integration."""

    def setUp(self):
        """Set up test environment."""
        self.api_key = "test-api-key"
        self.client = GemmaProjectClient(self.api_key)
        
        # Mock response for testing
        self.mock_todo_data = {
            "id": "123",
            "description": "Create a data analysis tool",
            "project": "DataScience",
            "metadata": {
                "requirements": ["pandas", "numpy", "matplotlib"]
            }
        }
        
        self.mock_gemma_response = {
            "function_call": {
                "name": "generate_project_structure",
                "arguments": json.dumps({
                    "name": "data-analysis-tool",
                    "description": "A tool for analyzing and visualizing data",
                    "project_type": "python",
                    "additional_details": {
                        "dependencies": ["pandas", "numpy", "matplotlib"]
                    }
                })
            }
        }

    @patch('project_generator.gemma_integration.requests.get')
    def test_fetch_todo(self, mock_get):
        """Test fetching a todo item."""
        # Configure mock
        mock_response = MagicMock()
        mock_response.json.return_value = self.mock_todo_data
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Call the method
        result = self.client._fetch_todo("123")
        
        # Assert the result
        self.assertEqual(result, self.mock_todo_data)
        mock_get.assert_called_once_with(f"{self.client.todo_server_url}/api/todos/123")

    @patch('project_generator.gemma_integration.requests.get')
    def test_fetch_todo_exception(self, mock_get):
        """Test fetching a todo item with an exception."""
        # Configure mock to raise an exception
        mock_get.side_effect = Exception("Failed to fetch todo")
        
        # Call the method and check exception
        with self.assertRaises(Exception) as context:
            self.client._fetch_todo("123")
        
        # Check exception message
        self.assertIn("Failed to fetch todo", str(context.exception))

    def test_create_project_prompt(self):
        """Test creating a project prompt from todo data."""
        prompt = self.client._create_project_prompt(self.mock_todo_data)
        
        # Check if the prompt contains essential elements
        self.assertIn(self.mock_todo_data["description"], prompt)
        self.assertIn(self.mock_todo_data["project"], prompt)
        self.assertIn("requirements", prompt)  # Should include metadata

    @patch('project_generator.gemma_integration.requests.post')
    def test_call_gemma_function(self, mock_post):
        """Test calling the Gemma function."""
        # Configure mock
        mock_response = MagicMock()
        mock_response.json.return_value = self.mock_gemma_response
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        # Call the method
        result = self.client._call_gemma_function("test prompt", {"name": "test_function"})
        
        # Assert the result
        self.assertEqual(result, self.mock_gemma_response)
        mock_post.assert_called_once()
        
        # Verify headers were set correctly
        call_args = mock_post.call_args[1]
        self.assertEqual(call_args["headers"]["Authorization"], f"Bearer {self.api_key}")

    @patch('project_generator.gemma_integration.requests.post')
    def test_call_gemma_function_exception(self, mock_post):
        """Test calling the Gemma function with an exception."""
        # Configure mock to raise an exception
        mock_post.side_effect = Exception("Failed to call Gemma API")
        
        # Call the method and check exception
        with self.assertRaises(Exception) as context:
            self.client._call_gemma_function("test prompt", {"name": "test_function"})
        
        # Check exception message
        self.assertIn("Failed to call Gemma API", str(context.exception))

    @patch.object(GemmaProjectClient, '_fetch_todo')
    @patch.object(GemmaProjectClient, '_call_gemma_function')
    def test_generate_from_todo(self, mock_call_gemma, mock_fetch_todo):
        """Test generating project details from a todo."""
        # Configure mocks
        mock_fetch_todo.return_value = self.mock_todo_data
        mock_call_gemma.return_value = self.mock_gemma_response
        
        # Call the method
        result = self.client.generate_from_todo("123")
        
        # Assert the result
        self.assertEqual(result["name"], "data-analysis-tool")
        self.assertEqual(result["project_type"], "python")
        self.assertIn("dependencies", result["additional_details"])
        
        # Verify mocks were called correctly
        mock_fetch_todo.assert_called_once_with("123")
        mock_call_gemma.assert_called_once()

    @patch.object(GemmaProjectClient, '_fetch_todo')
    def test_generate_from_todo_missing_todo(self, mock_fetch_todo):
        """Test generating project details with a missing todo."""
        # Configure mock to return None
        mock_fetch_todo.return_value = None
        
        # Call the method and check exception
        with self.assertRaises(Exception) as context:
            self.client.generate_from_todo("123")
        
        # Check exception message
        self.assertIn("Todo item with ID 123 not found", str(context.exception))

    @patch.object(GemmaProjectClient, '_fetch_todo')
    @patch.object(GemmaProjectClient, '_call_gemma_function')
    def test_generate_from_todo_invalid_response(self, mock_call_gemma, mock_fetch_todo):
        """Test generating project details with an invalid Gemma response."""
        # Configure mocks
        mock_fetch_todo.return_value = self.mock_todo_data
        mock_call_gemma.return_value = {"invalid": "response"}  # No function_call key
        
        # Call the method and check exception
        with self.assertRaises(Exception) as context:
            self.client.generate_from_todo("123")
        
        # Check exception message
        self.assertIn("Failed to get function call response from Gemma", str(context.exception))


class TestMockGemmaProjectClient(unittest.TestCase):
    """Test the Mock Gemma Project Client."""

    def setUp(self):
        """Set up test environment."""
        self.mock_client = MockGemmaProjectClient()

    def test_mock_initialization(self):
        """Test the initialization of the mock client."""
        self.assertEqual(self.mock_client.api_key, "mock_api_key")

    def test_mock_call_gemma_function(self):
        """Test the mock implementation of _call_gemma_function."""
        # Test with a description in the prompt
        test_prompt = "Description: Test Project\nProject: Testing"
        result = self.mock_client._call_gemma_function(test_prompt, {})
        
        # Verify the result structure
        self.assertIn("function_call", result)
        self.assertIn("arguments", result["function_call"])
        
        # Parse the arguments JSON
        arguments = json.loads(result["function_call"]["arguments"])
        
        # Verify the generated project details
        self.assertEqual(arguments["name"], "test-project")
        self.assertEqual(arguments["description"], "Test Project")
        self.assertEqual(arguments["project_type"], "python")
        self.assertIn("dependencies", arguments["additional_details"])

    def test_mock_call_gemma_function_no_description(self):
        """Test the mock implementation with no description in the prompt."""
        test_prompt = "Some text without a description"
        result = self.mock_client._call_gemma_function(test_prompt, {})
        
        # Parse the arguments JSON
        arguments = json.loads(result["function_call"]["arguments"])
        
        # Verify the generated project details
        self.assertEqual(arguments["name"], "sample-project")
        self.assertEqual(arguments["description"], "Sample Project")

    @patch.object(MockGemmaProjectClient, '_fetch_todo')
    def test_mock_generate_from_todo(self, mock_fetch_todo):
        """Test the end-to-end flow with the mock client."""
        # Configure mock
        mock_fetch_todo.return_value = {
            "id": "123",
            "description": "Build a web scraper",
            "project": "DataCollection",
            "metadata": {}
        }
        
        # Call the method
        result = self.mock_client.generate_from_todo("123")
        
        # Verify the result
        self.assertEqual(result["name"], "build-a-web-scraper")
        self.assertEqual(result["project_type"], "python")
        self.assertIn("additional_details", result)


if __name__ == '__main__':
    unittest.main() 
