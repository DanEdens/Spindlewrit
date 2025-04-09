import os
import tempfile
import shutil
import unittest
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

from project_generator.models import ProjectConfig, ProjectType, ProjectResponse
from project_generator.generator import ProjectGenerator


class TestProjectGenerator(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.generator = ProjectGenerator()
    
    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_python_project_generation(self):
        """Test Python project generation."""
        config = ProjectConfig(
            name="test-project",
            description="A test Python project",
            project_type=ProjectType.PYTHON,
            path=self.test_dir
        )
        
        result = self.generator.generate_project(config)
        
        # Check if the generation was successful
        self.assertTrue(result.success)
        self.assertTrue(os.path.exists(self.test_dir))
        
        # Check if essential files were created
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "README.md")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "requirements.txt")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "setup.py")))
        
        # Check if source directories were created
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "src")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "src", "test-project")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "src", "tests")))
        
        # Check if __init__.py files were created
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "src", "test-project", "__init__.py")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "src", "tests", "__init__.py")))
        
        # Check if version file was created
        version_file = os.path.join(self.test_dir, "src", "test-project", "__version__.py")
        self.assertTrue(os.path.exists(version_file))
        
        # Verify file contents
        with open(os.path.join(self.test_dir, "setup.py"), 'r') as f:
            setup_content = f.read()
            self.assertIn(f'name="{config.name}"', setup_content)
            self.assertIn('version="0.1.0"', setup_content)
            
        with open(os.path.join(self.test_dir, "README.md"), 'r') as f:
            readme_content = f.read()
            self.assertIn(config.name, readme_content)
            self.assertIn(config.description, readme_content)
            self.assertIn("python", readme_content.lower())
            
        # Verify test file was created
        test_file = os.path.join(self.test_dir, "src", "tests", f"test_{config.name}.py")
        self.assertTrue(os.path.exists(test_file))
        
        # Check test file content
        with open(test_file, 'r') as f:
            test_content = f.read()
            self.assertIn("import unittest", test_content)
            self.assertIn(f"from {config.name} import __version__", test_content)
            self.assertIn(f"class Test{config.name.capitalize()}", test_content)

    def test_python_project_with_additional_details(self):
        """Test Python project generation with additional details."""
        config = ProjectConfig(
            name="advanced-project",
            description="An advanced Python project with custom details",
            project_type=ProjectType.PYTHON,
            path=self.test_dir,
            additional_details={
                "dependencies": ["requests", "pydantic", "click"]
            }
        )
        
        result = self.generator.generate_project(config)
        
        # Check if the generation was successful
        self.assertTrue(result.success)
        
        # Additional verification should go here if the generator uses additional_details
        # This is a placeholder as we may enhance the generator to use additional_details in the future
    
    @patch('subprocess.run')
    def test_rust_project_generation(self, mock_run):
        """Test Rust project generation."""
        # Mock the subprocess.run call to avoid actual cargo command execution
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        
        config = ProjectConfig(
            name="test-rust",
            description="A test Rust project",
            project_type=ProjectType.RUST,
            path=self.test_dir
        )
        
        result = self.generator.generate_project(config)
        
        # Check if the generation was successful
        self.assertTrue(result.success)
        
        # Verify cargo was called with correct parameters
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(kwargs['cwd'], Path(self.test_dir))
        self.assertEqual(args[0][0], "cargo")
        self.assertEqual(args[0][1], "init")
        self.assertEqual(args[0][3], config.name)
        
        # Check if README.md was created
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "README.md")))
        
        # Verify README content
        with open(os.path.join(self.test_dir, "README.md"), 'r') as f:
            readme_content = f.read()
            self.assertIn(config.name, readme_content)
            self.assertIn(config.description, readme_content)
            self.assertIn("rust", readme_content.lower())
    
    def test_rust_project_with_subprocess_error(self):
        """Test Rust project generation when subprocess fails."""
        with patch('subprocess.run') as mock_run:
            # Configure the mock to raise a CalledProcessError
            error = subprocess.CalledProcessError(1, 'cargo init')
            error.stderr = b"Command failed: cargo init"
            mock_run.side_effect = error
            
            config = ProjectConfig(
                name="test-rust-error",
                description="A test Rust project that will fail",
                project_type=ProjectType.RUST,
                path=self.test_dir
            )
            
            result = self.generator.generate_project(config)
            
            # Check if the generation failed
            self.assertFalse(result.success)
            self.assertIn("Failed to initialize Rust project", result.message)
    
    def test_common_project_generation(self):
        """Test common project generation."""
        config = ProjectConfig(
            name="test-common",
            description="A test common project",
            project_type=ProjectType.COMMON,
            path=self.test_dir
        )
        
        result = self.generator.generate_project(config)
        
        # Check if the generation was successful
        self.assertTrue(result.success)
        
        # Check if essential directories were created
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "src")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "docs")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "examples")))
        
        # Check if README.md was created
        readme_path = os.path.join(self.test_dir, "README.md")
        self.assertTrue(os.path.exists(readme_path))
        
        # Verify README content
        with open(readme_path, 'r') as f:
            readme_content = f.read()
            self.assertIn(config.name, readme_content)
            self.assertIn(config.description, readme_content)
            self.assertIn("common", readme_content.lower())
    
    def test_project_with_invalid_path(self):
        """Test project generation with an invalid path."""
        # Create a path that should not be writable
        invalid_path = "/nonexistent/directory"  # This assumes the test is not running as root
        
        config = ProjectConfig(
            name="invalid-path-project",
            description="A project with an invalid path",
            project_type=ProjectType.PYTHON,
            path=invalid_path
        )
        
        # Patch os.makedirs to simulate failure
        with patch('os.makedirs') as mock_makedirs:
            mock_makedirs.side_effect = PermissionError("Permission denied")
            
            result = self.generator.generate_project(config)
            
            # Check if the generation failed
            self.assertFalse(result.success)
            self.assertTrue("Permission denied" in result.message or "Failed to create project" in result.message)
    
    def test_project_with_special_characters(self):
        """Test project generation with special characters in name/description."""
        config = ProjectConfig(
            name="special-chars-!@#",  # This should be normalized in a robust implementation
            description="Project with special chars: !@#$%^&*()",
            project_type=ProjectType.PYTHON,
            path=self.test_dir
        )
        
        result = self.generator.generate_project(config)
        
        # Check if the generation was successful (this tests how well the generator handles unusual inputs)
        self.assertTrue(result.success)
        
        # Basic structure tests
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "README.md")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "requirements.txt")))


if __name__ == "__main__":
    unittest.main() 
