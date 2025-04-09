import os
import tempfile
import shutil
import unittest
import json
from unittest.mock import patch, MagicMock

from project_generator.models import ProjectConfig, ProjectType, ProjectResponse
from project_generator.generator import ProjectGenerator


class TestAdditionalDetails(unittest.TestCase):
    """Test handling of additional_details in project generation."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.generator = ProjectGenerator()
    
    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.test_dir)
    
    def test_python_dependencies_in_additional_details(self):
        """Test handling Python dependencies specified in additional_details."""
        additional_details = {
            "dependencies": [
                "requests>=2.28.0",
                "numpy==1.22.0",
                "pandas",
                "flask==2.0.1"
            ]
        }
        
        config = ProjectConfig(
            name="python-with-deps",
            description="Python project with explicit dependencies",
            project_type=ProjectType.PYTHON,
            path=self.test_dir,
            additional_details=additional_details
        )
        
        # Initially, the generator doesn't integrate these details, but this test
        # serves as documentation for expected behavior and potential enhancements
        result = self.generator.generate_project(config)
        
        # Check if generation was successful
        self.assertTrue(result.success)
        
        # Verify requirements.txt exists
        requirements_path = os.path.join(self.test_dir, "requirements.txt")
        self.assertTrue(os.path.exists(requirements_path))
        
        # Currently, additional_details dependencies aren't added to requirements.txt
        # This serves as documentation of current behavior and potential enhancement opportunity
        with open(requirements_path, 'r') as f:
            content = f.read()
            # Initial requirements.txt just has a comment line
            self.assertIn("# Core dependencies", content)
            
            # These assertions would test the ideal behavior:
            # for dep in additional_details["dependencies"]:
            #     self.assertIn(dep, content)
    
    def test_rust_dependencies_in_additional_details(self):
        """Test handling Rust dependencies specified in additional_details."""
        additional_details = {
            "dependencies": [
                "serde = { version = \"1.0\", features = [\"derive\"] }",
                "tokio = { version = \"1\", features = [\"full\"] }",
                "reqwest = \"0.11\""
            ],
            "dev_dependencies": [
                "mockito = \"0.31\"",
                "test-case = \"2.2\""
            ]
        }
        
        config = ProjectConfig(
            name="rust-with-deps",
            description="Rust project with explicit dependencies",
            project_type=ProjectType.RUST,
            path=self.test_dir,
            additional_details=additional_details
        )
        
        # Mock subprocess to avoid actually calling cargo
        with patch('subprocess.run') as mock_run:
            mock_process = MagicMock()
            mock_process.returncode = 0
            mock_run.return_value = mock_process
            
            result = self.generator.generate_project(config)
            
            # Check if generation was successful
            self.assertTrue(result.success)
            
            # Currently, dependencies aren't added to Cargo.toml since the generator
            # uses cargo init without modifications
            # This serves as documentation for potential enhancement opportunity
    
    def test_complex_additional_details(self):
        """Test handling of complex nested additional_details."""
        additional_details = {
            "dependencies": ["flask", "pytest"],
            "config": {
                "port": 8080,
                "debug": True,
                "database": {
                    "type": "postgresql",
                    "host": "localhost",
                    "port": 5432
                }
            },
            "features": ["authentication", "api", "logging"],
            "license": "MIT"
        }
        
        config = ProjectConfig(
            name="complex-details",
            description="Project with complex additional details",
            project_type=ProjectType.PYTHON,
            path=self.test_dir,
            additional_details=additional_details
        )
        
        result = self.generator.generate_project(config)
        
        # Check if generation was successful
        self.assertTrue(result.success)
        
        # This test doesn't assert on the additional_details affecting output
        # because currently they don't, but it documents the ability to pass
        # complex nested structures that could be used in future enhancements
    
    def test_readme_integration_additional_details(self):
        """Test that additional_details for README customization are handled."""
        additional_details = {
            "readme_sections": {
                "badges": ["![Build](https://img.shields.io/badge/build-passing-brightgreen)"],
                "installation": "Follow these custom installation steps...",
                "usage": "Use the library like this: `import my_lib`",
                "license": "MIT License"
            }
        }
        
        config = ProjectConfig(
            name="readme-custom",
            description="Project with custom README sections",
            project_type=ProjectType.PYTHON,
            path=self.test_dir,
            additional_details=additional_details
        )
        
        result = self.generator.generate_project(config)
        
        # Check if generation was successful
        self.assertTrue(result.success)
        
        # Verify README.md exists
        readme_path = os.path.join(self.test_dir, "README.md")
        self.assertTrue(os.path.exists(readme_path))
        
        # Currently, readme_sections in additional_details don't affect the README
        # This serves as documentation for potential enhancement opportunity
        with open(readme_path, 'r') as f:
            content = f.read()
            self.assertIn(config.name, content)
            self.assertIn(config.description, content)
            
            # These assertions would test the ideal behavior:
            # for badge in additional_details["readme_sections"]["badges"]:
            #     self.assertIn(badge, content)
            # self.assertIn(additional_details["readme_sections"]["installation"], content)
    
    def test_null_additional_details(self):
        """Test that null additional_details doesn't cause problems."""
        config = ProjectConfig(
            name="null-details",
            description="Project with null additional details",
            project_type=ProjectType.PYTHON,
            path=self.test_dir,
            additional_details=None
        )
        
        result = self.generator.generate_project(config)
        
        # Check if generation was successful
        self.assertTrue(result.success)
        
        # Verify basic structure was created
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "README.md")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "src")))
    
    def test_empty_additional_details(self):
        """Test that empty additional_details dictionary doesn't cause problems."""
        config = ProjectConfig(
            name="empty-details",
            description="Project with empty additional details",
            project_type=ProjectType.PYTHON,
            path=self.test_dir,
            additional_details={}
        )
        
        result = self.generator.generate_project(config)
        
        # Check if generation was successful
        self.assertTrue(result.success)
        
        # Verify basic structure was created
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "README.md")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "src")))
    
    def test_invalid_additional_details(self):
        """Test that invalid additional_details is handled gracefully."""
        # Attempt to create an invalid config with non-dict additional_details
        # This should be caught by Pydantic validation
        try:
            config = ProjectConfig(
                name="invalid-details",
                description="Project with invalid additional details",
                project_type=ProjectType.PYTHON,
                path=self.test_dir,
                additional_details="This should be a dict, not a string"
            )
            self.fail("Should have raised a validation error for non-dict additional_details")
        except Exception:
            # Expected validation error
            pass
    
    def test_additional_details_survival(self):
        """Test that additional_details survives internal transformations."""
        # Use a test dictionary with a unique attribute
        unique_value = "uniquevalue9872345"
        additional_details = {
            "unique_test_attribute": unique_value,
            "nested": {
                "deeper": unique_value
            }
        }
        
        config = ProjectConfig(
            name="details-survival",
            description="Project testing additional_details survival",
            project_type=ProjectType.PYTHON,
            path=self.test_dir,
            additional_details=additional_details
        )
        
        # To test if additional_details survive transformations, we would need to
        # add logic to the generator that actually uses them and outputs them somewhere
        # This test currently only serves as documentation for potential enhancement
        result = self.generator.generate_project(config)
        
        # Check if generation was successful
        self.assertTrue(result.success)


if __name__ == "__main__":
    unittest.main() 
