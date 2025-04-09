import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

from .models import ProjectConfig, ProjectResponse, ProjectType


class ProjectGenerator:
    def __init__(self):
        pass

    def generate_project(self, config: ProjectConfig) -> ProjectResponse:
        """
        Generate a new project based on the provided configuration.
        
        Args:
            config: ProjectConfig object with project details
            
        Returns:
            ProjectResponse with status and details
        """
        try:
            project_path = Path(config.path)
            
            # Create the project directory if it doesn't exist
            os.makedirs(project_path, exist_ok=True)
            
            # Generate project based on type
            if config.project_type == ProjectType.PYTHON:
                self._generate_python_project(config, project_path)
            elif config.project_type == ProjectType.RUST:
                self._generate_rust_project(config, project_path)
            else:
                self._generate_common_project(config, project_path)
                
            return ProjectResponse(
                success=True,
                message=f"Successfully created {config.project_type} project: {config.name}",
                project_path=str(project_path)
            )
        
        except Exception as e:
            return ProjectResponse(
                success=False,
                message=f"Failed to create project: {str(e)}",
                errors=[str(e)]
            )
    
    def _generate_python_project(self, config: ProjectConfig, path: Path) -> None:
        """Generate a Python project structure."""
        # Create project structure
        src_dir = path / "src"
        os.makedirs(src_dir, exist_ok=True)
        os.makedirs(src_dir / config.name, exist_ok=True)
        os.makedirs(src_dir / "tests", exist_ok=True)

        # Create __init__.py files
        self._write_file(src_dir / config.name / "__init__.py", "")
        self._write_file(src_dir / "tests" / "__init__.py", "")

        # Create requirements.txt
        self._write_file(path / "requirements.txt", "# Core dependencies\n")

        # Create setup.py
        setup_content = f"""from setuptools import setup, find_packages

setup(
    name="{config.name}",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={{"": "src"}},
    install_requires=[],
    python_requires=">=3.8",
)"""
        self._write_file(path / "setup.py", setup_content)

        # Create README.md
        self._create_readme(config, path, "python")
        
        # Create a simple test file
        test_content = f"""import unittest
from {config.name} import __version__

class Test{config.name.capitalize()}(unittest.TestCase):
    def test_version(self):
        self.assertTrue(__version__)

if __name__ == '__main__':
    unittest.main()
"""
        self._write_file(src_dir / "tests" / f"test_{config.name}.py", test_content)
        
        # Create version file
        self._write_file(src_dir / config.name / "__version__.py", '__version__ = "0.1.0"')

    def _generate_rust_project(self, config: ProjectConfig, path: Path) -> None:
        """Generate a Rust project structure."""
        try:
            # Use cargo to initialize the project
            subprocess.run(
                ["cargo", "init", "--name", config.name],
                cwd=path,
                check=True,
                capture_output=True
            )
            
            # Create README.md
            self._create_readme(config, path, "rust")
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to initialize Rust project: {e.stderr.decode()}")

    def _generate_common_project(self, config: ProjectConfig, path: Path) -> None:
        """Generate a common project structure."""
        os.makedirs(path / "src", exist_ok=True)
        os.makedirs(path / "docs", exist_ok=True)
        os.makedirs(path / "examples", exist_ok=True)

        # Create README.md
        self._create_readme(config, path, "common")

    def _create_readme(self, config: ProjectConfig, path: Path, project_type: str) -> None:
        """Create a README.md file for the project."""
        content = f"""# {config.name}

{config.description}

## Overview

This is a {project_type} project created with the Project Generator tool.

## Setup

"""
        if project_type == "python":
            content += """
1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
"""
        elif project_type == "rust":
            content += """
1. Build the project:
   ```bash
   cargo build
   ```
2. Run tests:
   ```bash
   cargo test
   ```
"""

        self._write_file(path / "README.md", content)
    
    def _write_file(self, path: Path, content: str) -> None:
        """Write content to a file, creating parent directories if needed."""
        os.makedirs(path.parent, exist_ok=True)
        with open(path, 'w') as f:
            f.write(content) 
