import os
import tempfile
import shutil
import unittest
import subprocess
from unittest.mock import patch, MagicMock
from pathlib import Path

from project_generator.models import ProjectConfig, ProjectType, ProjectResponse
from project_generator.generator import ProjectGenerator


class TestSecurityAndValidation(unittest.TestCase):
    """Test security concerns and input validation in project generation."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.generator = ProjectGenerator()
    
    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.test_dir)
    
    def test_path_traversal_attempt(self):
        """Test protection against directory traversal attempts."""
        # Attempt path traversal by including '../' in the path
        traversal_path = os.path.join(self.test_dir, "..", "outside_test_dir")
        
        config = ProjectConfig(
            name="traversal-test",
            description="Project attempting path traversal",
            project_type=ProjectType.PYTHON,
            path=traversal_path
        )
        
        result = self.generator.generate_project(config)
        
        # Check if generation was successful (should be, but in a normalized path)
        self.assertTrue(result.success)
        
        # Verify project was created in a normalized path
        normalized_path = os.path.normpath(traversal_path)
        self.assertTrue(os.path.exists(os.path.join(normalized_path, "README.md")))
        
        # Clean up the directory outside of test_dir if it was created
        if os.path.exists(normalized_path) and not normalized_path.startswith(self.test_dir):
            shutil.rmtree(normalized_path)
    
    def test_injection_in_project_name(self):
        """Test protection against potential command injection in project name."""
        # Project name with characters that could be used for command injection
        # This isn't actually a security issue for the current implementation,
        # but it's good to test to ensure future changes don't introduce vulnerabilities
        injection_name = "$(touch /tmp/security_test)"
        
        config = ProjectConfig(
            name=injection_name,
            description="Project with command injection attempt in name",
            project_type=ProjectType.PYTHON,
            path=self.test_dir
        )
        
        result = self.generator.generate_project(config)
        
        # Check if generation was successful
        self.assertTrue(result.success)
        
        # Verify the name was treated as a literal string, not executed
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "src", injection_name)))
        
        # Verify no file was created in /tmp (which would indicate command execution)
        self.assertFalse(os.path.exists("/tmp/security_test"))
    
    @patch('subprocess.run')
    def test_shell_injection_in_rust_project(self, mock_run):
        """Test protection against potential shell injection in Rust project generation."""
        # Project name with shell injection attempt
        injection_name = "test; touch /tmp/cargo_injection_test"
        
        config = ProjectConfig(
            name=injection_name,
            description="Rust project with shell injection attempt",
            project_type=ProjectType.RUST,
            path=self.test_dir
        )
        
        # In a secure implementation, the mock should receive exactly the command we expect
        # with no interpretation of the shell characters
        result = self.generator.generate_project(config)
        
        # Check if generation was successful
        self.assertTrue(result.success)
        
        # Verify that subprocess.run was called with a list (not shell=True)
        # and the injection name was treated as a single argument
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertIsInstance(args[0], list, "Command should be a list to prevent shell injection")
        self.assertEqual(args[0][3], injection_name)
    
    def test_project_name_with_spaces(self):
        """Test project generation with spaces in the name."""
        config = ProjectConfig(
            name="project with spaces",
            description="Project with spaces in name",
            project_type=ProjectType.PYTHON,
            path=self.test_dir
        )
        
        result = self.generator.generate_project(config)
        
        # Check if generation was successful
        self.assertTrue(result.success)
        
        # Verify project directory was created with spaces in name
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "src", "project with spaces")))
    
    def test_absolute_vs_relative_path(self):
        """Test that both absolute and relative paths work correctly."""
        # Create a relative path
        rel_dir = "relative_project_dir"
        orig_cwd = os.getcwd()
        
        try:
            # Change to test_dir
            os.chdir(self.test_dir)
            
            # Use a relative path for the project
            config = ProjectConfig(
                name="relative-path-project",
                description="Project with relative path",
                project_type=ProjectType.PYTHON,
                path=rel_dir
            )
            
            result = self.generator.generate_project(config)
            
            # Check if generation was successful
            self.assertTrue(result.success)
            
            # Verify project was created in the relative path
            self.assertTrue(os.path.exists(os.path.join(self.test_dir, rel_dir, "README.md")))
            
        finally:
            # Restore original working directory
            os.chdir(orig_cwd)
    
    def test_project_with_invalid_characters_sanitization(self):
        """Test validation of project name with invalid characters."""
        # Current behavior likely allows invalid characters. This test documents
        # the current behavior and helps identify enhancements for proper sanitization
        config = ProjectConfig(
            name="invalid>\0<chars",  # Includes null byte and angle brackets
            description="Project with invalid characters in name",
            project_type=ProjectType.PYTHON,
            path=self.test_dir
        )
        
        # The current implementation might accept this, but ideally these characters
        # would be sanitized or rejected with a validation error
        result = self.generator.generate_project(config)
        
        # Document current behavior
        self.assertTrue(result.success)
        
        # A sanitized implementation might replace or remove problematic characters
    
    def test_project_with_non_ascii_path(self):
        """Test project generation with non-ASCII characters in path."""
        # Path with non-ASCII characters
        nonascii_path = os.path.join(self.test_dir, "路径测试")
        
        config = ProjectConfig(
            name="nonascii-path",
            description="Project with non-ASCII path",
            project_type=ProjectType.PYTHON,
            path=nonascii_path
        )
        
        result = self.generator.generate_project(config)
        
        # Check if generation was successful
        self.assertTrue(result.success)
        
        # Verify project was created in path with non-ASCII characters
        self.assertTrue(os.path.exists(os.path.join(nonascii_path, "README.md")))
    
    def test_path_with_environment_variables(self):
        """Test paths that include environment variable references."""
        # Set a test environment variable
        os.environ["SPINDLEWRIT_TEST_PATH"] = "env_var_path"
        
        # Path with environment variable
        env_var_path = os.path.join(self.test_dir, "${SPINDLEWRIT_TEST_PATH}")
        
        config = ProjectConfig(
            name="env-var-path",
            description="Project with environment variable in path",
            project_type=ProjectType.PYTHON,
            path=env_var_path
        )
        
        result = self.generator.generate_project(config)
        
        # Check if generation was successful
        self.assertTrue(result.success)
        
        # Current implementation treats this literally, not as an environment variable
        # This is actually secure behavior against environment variable injection
        self.assertTrue(os.path.exists(os.path.join(env_var_path, "README.md")))
        
        # This might be better in a more advanced version:
        # expanded_path = os.path.join(self.test_dir, "env_var_path")
        # self.assertTrue(os.path.exists(os.path.join(expanded_path, "README.md")))
    
    def test_project_write_to_system_directory(self):
        """Test attempt to write to a sensitive system directory."""
        # Path pointing to a system directory that should be protected
        system_path = "/etc/spindlewrit_test"  # UNIX system directory
        if not os.path.exists("/etc"):
            system_path = "C:\\Windows\\spindlewrit_test"  # Windows system directory
            if not os.path.exists("C:\\Windows"):
                self.skipTest("Can't find a system directory to test against")
        
        config = ProjectConfig(
            name="system-path-test",
            description="Project attempting to write to system directory",
            project_type=ProjectType.PYTHON,
            path=system_path
        )
        
        # On a system with proper permissions, this should fail unless running as root/admin
        # We don't assert on the success/failure because it depends on the user running the test
        result = self.generator.generate_project(config)
        
        # Clean up if the test actually created the directory
        if os.path.exists(system_path):
            try:
                shutil.rmtree(system_path)
            except (PermissionError, OSError):
                # If we can't clean up, it should be handled by the system admin
                pass
    
    @patch('subprocess.run')
    def test_rust_cargo_command_security(self, mock_run):
        """Test that the Rust cargo command is executed securely."""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        
        config = ProjectConfig(
            name="secure-rust",
            description="Rust project with secure cargo execution",
            project_type=ProjectType.RUST,
            path=self.test_dir
        )
        
        result = self.generator.generate_project(config)
        
        # Check if generation was successful
        self.assertTrue(result.success)
        
        # Verify cargo was called with correct parameters and securely
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        
        # Cargo should be called with a list of arguments (not a string with shell=True)
        self.assertIsInstance(args[0], list)
        
        # Verify shell=True is not used (which would be insecure)
        self.assertNotIn('shell', kwargs or {})
    
    def test_directory_permissions(self):
        """Test that created directories have appropriate permissions."""
        config = ProjectConfig(
            name="permissions-test",
            description="Project for testing directory permissions",
            project_type=ProjectType.PYTHON,
            path=self.test_dir
        )
        
        result = self.generator.generate_project(config)
        
        # Check if generation was successful
        self.assertTrue(result.success)
        
        # Check permissions on created directories
        # This is somewhat platform-specific, so we just do a basic check
        src_dir = os.path.join(self.test_dir, "src")
        self.assertTrue(os.access(src_dir, os.R_OK))  # Should be readable
        self.assertTrue(os.access(src_dir, os.W_OK))  # Should be writable
        
        # More detailed permission checks could be added for specific platforms


if __name__ == "__main__":
    unittest.main() 
