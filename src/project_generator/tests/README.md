# Spindlewrit Tests

This directory contains comprehensive tests for the Spindlewrit project generator tool.

## Test Structure

The tests are organized into several categories:

1. **Unit Tests** - Tests individual components in isolation
   - `test_generator.py` - Tests the `ProjectGenerator` class functionality
   - `test_gemma_integration.py` - Tests the Gemma AI function calling integration

2. **Integration Tests** - Tests how components work together
   - `test_integration.py` - Tests CLI commands and ProjectAgent integration

## Running Tests

You can run all tests with pytest:

```bash
# From the root of the Spindlewrit repository
python -m pytest

# To run tests with coverage
python -m pytest --cov=project_generator

# To run a specific test file
python -m pytest src/project_generator/tests/test_generator.py

# To run a specific test class
python -m pytest src/project_generator/tests/test_gemma_integration.py::TestGemmaProjectClient

# To run a specific test method
python -m pytest src/project_generator/tests/test_generator.py::TestProjectGenerator::test_python_project_generation
```

## Mock Implementation

For testing the Gemma function calling integration without requiring actual API access, we use a `MockGemmaProjectClient` class. This allows us to test the integration pattern without making actual API calls.

## Test Coverage

The tests aim to cover:

1. Basic project generation for Python, Rust, and common project types
2. Error handling and edge cases
3. Gemma AI integration for generating projects from todo items
4. CLI command functionality and compatibility with ProjectAgent
5. End-to-end workflow from todo items to generated projects

## Adding New Tests

When adding new features to Spindlewrit, please also add corresponding tests. Follow these guidelines:

1. Use descriptive test method names that indicate what's being tested
2. Use appropriate mocking for external dependencies
3. Test both success and failure cases
4. Verify both the functionality and the output of methods

## ProjectAgent Integration Tests

The `test_integration.py` file specifically tests the compatibility with the Swarmonomicon ProjectAgent. It ensures that:

1. The CLI commands match the format expected by ProjectAgent
2. The project generation workflow from todo items works correctly
3. The subprocess calls that ProjectAgent would make work as expected

This ensures that Spindlewrit can be seamlessly used by the ProjectAgent in the Swarmonomicon ecosystem. 
