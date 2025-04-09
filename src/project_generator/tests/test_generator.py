import os
import tempfile
import shutil
import unittest
from pathlib import Path

from project_generator.models import ProjectConfig, ProjectType
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
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "README.md")))


if __name__ == "__main__":
    unittest.main() 
