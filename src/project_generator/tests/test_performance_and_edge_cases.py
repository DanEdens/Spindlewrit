import os
import tempfile
import shutil
import unittest
import time
import random
import string
from unittest.mock import patch, MagicMock
from pathlib import Path

from project_generator.models import ProjectConfig, ProjectType, ProjectResponse
from project_generator.generator import ProjectGenerator


class TestPerformanceAndEdgeCases(unittest.TestCase):
    """Test performance and edge cases for project generation."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.generator = ProjectGenerator()
    
    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.test_dir)
    
    def test_large_project_name(self):
        """Test generation with an unusually large project name."""
        # Create a long name (100 characters)
        long_name = "a" * 100
        
        config = ProjectConfig(
            name=long_name,
            description="Project with an extremely long name",
            project_type=ProjectType.PYTHON,
            path=self.test_dir
        )
        
        result = self.generator.generate_project(config)
        
        # Check if generation was successful
        self.assertTrue(result.success)
        
        # Verify project was created with long name
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "src", long_name)))
    
    def test_long_description(self):
        """Test generation with an unusually long description."""
        # Create a long description (1000 characters)
        long_desc = "This is a very long description. " * 50
        
        config = ProjectConfig(
            name="long-desc-project",
            description=long_desc,
            project_type=ProjectType.PYTHON,
            path=self.test_dir
        )
        
        result = self.generator.generate_project(config)
        
        # Check if generation was successful
        self.assertTrue(result.success)
        
        # Verify README contains the long description
        with open(os.path.join(self.test_dir, "README.md"), 'r') as f:
            content = f.read()
            self.assertIn(long_desc, content)
    
    def test_deep_nested_directory_structure(self):
        """Test generation in a deeply nested directory structure."""
        # Create a deeply nested path (more than 10 levels)
        nested_parts = ["level" + str(i) for i in range(15)]
        nested_path = os.path.join(self.test_dir, *nested_parts)
        
        config = ProjectConfig(
            name="deep-nested",
            description="Project in a deeply nested directory",
            project_type=ProjectType.PYTHON,
            path=nested_path
        )
        
        result = self.generator.generate_project(config)
        
        # Check if generation was successful
        self.assertTrue(result.success)
        
        # Verify project was created in deeply nested path
        self.assertTrue(os.path.exists(os.path.join(nested_path, "README.md")))
    
    def test_special_characters_in_path(self):
        """Test generation with special characters in the path."""
        # Path with spaces and special characters
        special_path = os.path.join(self.test_dir, "Special Path (with) [chars]!")
        
        config = ProjectConfig(
            name="special-path",
            description="Project with special characters in path",
            project_type=ProjectType.PYTHON,
            path=special_path
        )
        
        result = self.generator.generate_project(config)
        
        # Check if generation was successful
        self.assertTrue(result.success)
        
        # Verify project was created in path with special characters
        self.assertTrue(os.path.exists(os.path.join(special_path, "README.md")))
    
    def test_performance_basic(self):
        """Basic performance test for project generation."""
        start_time = time.time()
        
        config = ProjectConfig(
            name="perf-test",
            description="Project for performance testing",
            project_type=ProjectType.PYTHON,
            path=self.test_dir
        )
        
        result = self.generator.generate_project(config)
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        # Record the performance metric
        print(f"\nBasic Python project generation time: {generation_time:.4f} seconds")
        
        # Check if generation was successful
        self.assertTrue(result.success)
        
        # Assert generation happens within a reasonable time (adjust as needed)
        # This threshold should be far larger than expected to avoid flaky tests
        self.assertLess(generation_time, 5.0, "Generation took too long")
    
    @patch('subprocess.run')
    def test_performance_rust(self, mock_run):
        """Performance test for Rust project generation."""
        # Mock subprocess.run to avoid actual cargo execution
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        
        start_time = time.time()
        
        config = ProjectConfig(
            name="rust-perf-test",
            description="Rust project for performance testing",
            project_type=ProjectType.RUST,
            path=self.test_dir
        )
        
        result = self.generator.generate_project(config)
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        # Record the performance metric
        print(f"\nRust project generation time: {generation_time:.4f} seconds")
        
        # Check if generation was successful
        self.assertTrue(result.success)
        
        # Assert generation happens within a reasonable time (adjust as needed)
        self.assertLess(generation_time, 5.0, "Generation took too long")
    
    def test_sequential_project_generation(self):
        """Test generating multiple projects sequentially for performance."""
        num_projects = 5
        total_time = 0
        
        for i in range(num_projects):
            project_dir = os.path.join(self.test_dir, f"project{i}")
            
            start_time = time.time()
            
            config = ProjectConfig(
                name=f"seq-project-{i}",
                description=f"Sequential project {i}",
                project_type=ProjectType.PYTHON,
                path=project_dir
            )
            
            result = self.generator.generate_project(config)
            
            end_time = time.time()
            project_time = end_time - start_time
            total_time += project_time
            
            # Check if generation was successful
            self.assertTrue(result.success)
            self.assertTrue(os.path.exists(os.path.join(project_dir, "README.md")))
        
        # Record the performance metric
        print(f"\nAverage time for sequential project generation: {total_time/num_projects:.4f} seconds")
    
    def test_random_project_names(self):
        """Test with randomly generated project names to detect edge cases."""
        for i in range(5):
            # Generate random project name with mixed characters
            random_name = ''.join(random.choices(
                string.ascii_letters + string.digits + "-_", k=random.randint(5, 30)))
            
            config = ProjectConfig(
                name=random_name,
                description=f"Randomly named project {i}",
                project_type=ProjectType.PYTHON,
                path=os.path.join(self.test_dir, random_name)
            )
            
            result = self.generator.generate_project(config)
            
            # Check if generation was successful
            self.assertTrue(result.success, f"Failed with random name: {random_name}")
            
            # Verify project was created
            self.assertTrue(os.path.exists(os.path.join(self.test_dir, random_name, "README.md")))
    
    def test_project_with_very_short_name(self):
        """Test project generation with a very short name."""
        config = ProjectConfig(
            name="a",  # Single character
            description="Project with a single character name",
            project_type=ProjectType.PYTHON,
            path=self.test_dir
        )
        
        result = self.generator.generate_project(config)
        
        # Check if generation was successful
        self.assertTrue(result.success)
        
        # Verify project was created with single character name
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "src", "a")))
    
    def test_path_with_symlinks(self):
        """Test project generation where the path contains symlinks."""
        # Create a directory and a symlink to it
        real_dir = os.path.join(self.test_dir, "real_dir")
        symlink_dir = os.path.join(self.test_dir, "symlink_dir")
        os.makedirs(real_dir)
        
        try:
            # Create symlink (might not work on all platforms)
            os.symlink(real_dir, symlink_dir)
            
            config = ProjectConfig(
                name="symlink-project",
                description="Project in directory accessed via symlink",
                project_type=ProjectType.PYTHON,
                path=symlink_dir
            )
            
            result = self.generator.generate_project(config)
            
            # Check if generation was successful
            self.assertTrue(result.success)
            
            # Verify project was created through the symlink
            self.assertTrue(os.path.exists(os.path.join(symlink_dir, "README.md")))
            # Verify it also exists in the real directory
            self.assertTrue(os.path.exists(os.path.join(real_dir, "README.md")))
            
        except OSError:
            # Skip test if symlinks cannot be created (e.g., on some Windows configurations)
            self.skipTest("Symlink creation not supported on this system")
    
    def test_project_with_reserved_characters(self):
        """Test project generation with reserved characters in name that should be sanitized."""
        config = ProjectConfig(
            name="project/with:reserved*chars?",
            description="Project with reserved characters in name",
            project_type=ProjectType.PYTHON,
            path=self.test_dir
        )
        
        result = self.generator.generate_project(config)
        
        # Currently, the generator doesn't sanitize reserved characters
        # This test documents the current behavior and highlights a potential enhancement
        # Ideally, the generator would sanitize the name to avoid file system issues
        self.assertTrue(result.success)
    
    def test_concurrent_project_creation(self):
        """
        Test simulating concurrent project creation.
        
        This test doesn't actually create threads, but it tests that the generator
        is robust when creating multiple projects accessing the same files.
        """
        # Create a shared parent directory for both projects
        shared_dir = os.path.join(self.test_dir, "shared")
        os.makedirs(shared_dir)
        
        # Create two projects in subdirectories of the shared directory
        config1 = ProjectConfig(
            name="project1",
            description="First concurrent project",
            project_type=ProjectType.PYTHON,
            path=os.path.join(shared_dir, "project1")
        )
        
        config2 = ProjectConfig(
            name="project2",
            description="Second concurrent project",
            project_type=ProjectType.PYTHON,
            path=os.path.join(shared_dir, "project2")
        )
        
        # Generate both projects
        result1 = self.generator.generate_project(config1)
        self.assertTrue(result1.success)
        
        result2 = self.generator.generate_project(config2)
        self.assertTrue(result2.success)
        
        # Verify both projects were created correctly
        self.assertTrue(os.path.exists(os.path.join(shared_dir, "project1", "README.md")))
        self.assertTrue(os.path.exists(os.path.join(shared_dir, "project2", "README.md")))
        
        # Verify they have different content
        with open(os.path.join(shared_dir, "project1", "README.md"), 'r') as f:
            content1 = f.read()
        
        with open(os.path.join(shared_dir, "project2", "README.md"), 'r') as f:
            content2 = f.read()
            
        self.assertNotEqual(content1, content2)
        self.assertIn("project1", content1)
        self.assertIn("project2", content2)


if __name__ == "__main__":
    unittest.main() 
