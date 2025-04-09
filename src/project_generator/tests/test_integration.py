import os
import sys
import unittest
import tempfile
import shutil
import subprocess
from unittest.mock import patch, MagicMock
from pathlib import Path

from project_generator.models import ProjectConfig, ProjectType
from project_generator.generator import ProjectGenerator
from project_generator.gemma_integration import MockGemmaProjectClient
from project_generator.cli import create, from_todo


class TestSpindlewritIntegration(unittest.TestCase):
    """Test the integration of Spindlewrit with external systems, focusing on CLI and ProjectAgent compatibility."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.generator = ProjectGenerator()
        
        # Mock Click context
        self.mock_ctx = MagicMock()
        
        # Mock filesystem state for CLI testing
        self.cwd_patch = patch('os.getcwd')
        self.mock_cwd = self.cwd_patch.start()
        self.mock_cwd.return_value = self.test_dir
    
    def tearDown(self):
        """Clean up after tests."""
        self.cwd_patch.stop()
        shutil.rmtree(self.test_dir)
    
    @patch('project_generator.cli.click.echo')
    def test_cli_create_command(self, mock_echo):
        """Test the CLI create command."""
        # Call the CLI function
        create(
            name="test-cli-project", 
            description="A test project created via CLI", 
            project_type="python", 
            path=self.test_dir
        )
        
        # Verify directory structure was created
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "README.md")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "src")))
        
        # Verify click.echo was called with success message
        mock_echo.assert_any_call(mock_echo.call_args_list[0].args[0])
    
    @patch('project_generator.cli.click.echo')
    @patch('project_generator.cli.GemmaProjectClient')
    def test_from_todo_command(self, mock_client_class, mock_echo):
        """Test the from_todo CLI command."""
        # Mock environment
        with patch.dict(os.environ, {"GEMMA_API_KEY": "test-key"}):
            # Mock the GemmaProjectClient
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            
            # Set up mock return value for generate_from_todo
            mock_client.generate_from_todo.return_value = {
                "name": "todo-project",
                "description": "Project generated from a todo",
                "project_type": "python",
                "additional_details": {}
            }
            
            # Call the CLI function
            from_todo(todo_id="123", output_dir=self.test_dir, api_key=None)
            
            # Verify client was initialized and method was called
            mock_client_class.assert_called_once_with("test-key")
            mock_client.generate_from_todo.assert_called_once_with("123")
            
            # Verify project was created
            project_dir = os.path.join(self.test_dir, "todo-project")
            self.assertTrue(os.path.exists(project_dir))
            self.assertTrue(os.path.exists(os.path.join(project_dir, "README.md")))
    
    @patch('subprocess.run')
    def test_project_agent_subprocess_calls(self, mock_run):
        """Test the types of subprocess calls that ProjectAgent would make."""
        # Mock subprocess.run to return success
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        
        # Test generating a python project with cargo
        config = ProjectConfig(
            name="rust-proj",
            description="A Rust project via subprocess",
            project_type=ProjectType.RUST,
            path=self.test_dir
        )
        
        result = self.generator.generate_project(config)
        
        # Verify success
        self.assertTrue(result.success)
        
        # Verify subprocess was called with expected arguments
        mock_run.assert_called_with(
            ["cargo", "init", "--name", "rust-proj"],
            cwd=Path(self.test_dir),
            check=True,
            capture_output=True
        )
    
    @patch('project_generator.gemma_integration.requests.get')
    @patch('project_generator.gemma_integration.requests.post')
    def test_todo_to_project_workflow(self, mock_post, mock_get):
        """Test the workflow of converting a todo to a project."""
        # Mock todo API response
        mock_todo_response = MagicMock()
        mock_todo_response.json.return_value = {
            "id": "todo-123",
            "description": "Create a machine learning model for text classification",
            "project": "ML",
            "metadata": {
                "requirements": ["scikit-learn", "tensorflow", "pandas"]
            }
        }
        mock_todo_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_todo_response
        
        # Mock Gemma API response
        mock_gemma_response = MagicMock()
        mock_gemma_response.json.return_value = {
            "function_call": {
                "name": "generate_project_structure",
                "arguments": json.dumps({
                    "name": "text-classification-model",
                    "description": "A machine learning model for text classification",
                    "project_type": "python",
                    "additional_details": {
                        "dependencies": ["scikit-learn", "tensorflow", "pandas"]
                    }
                })
            }
        }
        mock_gemma_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_gemma_response
        
        # Create client and generate project
        client = GemmaProjectClient("test-key")
        project_details = client.generate_from_todo("todo-123")
        
        # Create the project using the generator
        config = ProjectConfig(
            name=project_details["name"],
            description=project_details["description"],
            project_type=ProjectType(project_details["project_type"]),
            path=self.test_dir,
            additional_details=project_details.get("additional_details")
        )
        
        result = self.generator.generate_project(config)
        
        # Verify
        self.assertTrue(result.success)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "README.md")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "src")))


# Import here to avoid circular import in the test
import json
from project_generator.gemma_integration import GemmaProjectClient


class TestCLICommands(unittest.TestCase):
    """Test CLI command compatibility with the ProjectAgent."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.test_dir)
    
    @patch('subprocess.run')
    def test_cli_command_format(self, mock_run):
        """Test that Spindlewrit CLI commands match the format expected by ProjectAgent."""
        # Mock subprocess.run to simulate CLI call
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        
        # Create CLI command similar to what ProjectAgent would run
        cli_cmd = [
            "spindlewrit",
            "create",
            "--name", "test-cli-integration",
            "--description", "Testing CLI integration",
            "--type", "python",
            "--path", self.test_dir
        ]
        
        # Run the command
        subprocess.run(cli_cmd)
        
        # Verify subprocess.run was called with the expected arguments
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], cli_cmd)
    
    @patch('subprocess.run')
    def test_todo_cli_command_format(self, mock_run):
        """Test that Spindlewrit from-todo CLI commands match the format expected by ProjectAgent."""
        # Mock subprocess.run to simulate CLI call
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        
        # Create CLI command similar to what ProjectAgent would run
        todo_cmd = [
            "spindlewrit",
            "from-todo",
            "--todo-id", "todo-123",
            "--output-dir", self.test_dir,
            "--api-key", "test-api-key"
        ]
        
        # Run the command
        subprocess.run(todo_cmd)
        
        # Verify subprocess.run was called with the expected arguments
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], todo_cmd)


if __name__ == '__main__':
    unittest.main() 
