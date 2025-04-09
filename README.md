# Project Generator

A tool to generate project structures with AI-powered suggestions from Gemma function calling.

## Overview

The Project Generator is a CLI tool that can create standardized project structures for Python, Rust, and other types of projects. It integrates with the MCP Todo Server to generate projects based on TODO items, using Gemma function calling for AI-powered suggestions.

## Features

- Generate Python, Rust, and common project structures
- Create projects from scratch with a simple CLI interface
- Generate projects from Todo items with AI-powered suggestions
- Customizable project templates

## Installation

```bash
# Clone the repository
git clone <repository-url>

# Navigate to the project directory
cd project-generator

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package in development mode
pip install -e .
```

## Usage

### Create a project from scratch

```bash
# Create a Python project
project-generator create --name my-python-project --description "A sample Python project" --type python --path /path/to/output

# Create a Rust project
project-generator create --name my-rust-project --description "A sample Rust project" --type rust --path /path/to/output
```

### Create a project from a Todo item

```bash
# Set your Gemma API key
export GEMMA_API_KEY=your-api-key

# Generate a project from a Todo item
project-generator from-todo --todo-id todo123 --output-dir /path/to/output
```

## Development

### Running tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Structure

- `src/project_generator/` - Main package code
  - `cli.py` - Command-line interface
  - `generator.py` - Project generation logic
  - `gemma_integration.py` - Integration with Gemma function calling
  - `models.py` - Data models
  - `tests/` - Test files

## Integration with Swarmonomicon

This tool integrates with the Swarmonomicon project by providing a Python implementation for project generation that can be called from the Rust ProjectAgent via a foreign function interface (FFI) or by direct CLI invocation. 
