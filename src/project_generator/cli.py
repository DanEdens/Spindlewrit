import os
import sys
import click
from pathlib import Path

from .models import ProjectConfig, ProjectType
from .generator import ProjectGenerator
from .gemma_integration import GemmaProjectClient, MockGemmaProjectClient


@click.group()
def cli():
    """Project Generator CLI tool."""
    pass


@cli.command()
@click.option('--name', required=True, help='Name of the project')
@click.option('--description', required=True, help='Short description of the project')
@click.option(
    '--type', 'project_type',
    type=click.Choice(['python', 'rust', 'common']),
    default='python',
    help='Type of project to create'
)
@click.option(
    '--path',
    type=click.Path(),
    default=os.getcwd(),
    help='Path where to create the project (defaults to current directory)'
)
def create(name, description, project_type, path):
    """Create a new project with the specified configuration."""
    config = ProjectConfig(
        name=name,
        description=description,
        project_type=ProjectType(project_type),
        path=path
    )
    
    generator = ProjectGenerator()
    result = generator.generate_project(config)
    
    if result.success:
        click.echo(click.style(result.message, fg='green'))
        click.echo(f"Project created at: {result.project_path}")
    else:
        click.echo(click.style(result.message, fg='red'))
        if result.errors:
            for error in result.errors:
                click.echo(f"- {error}")
        sys.exit(1)


@cli.command()
@click.option('--todo-id', required=True, help='ID of the TODO item to use for project generation')
@click.option(
    '--output-dir',
    type=click.Path(),
    default=os.getcwd(),
    help='Directory where to create the project (defaults to current directory)'
)
@click.option('--api-key', help='Gemma API key (defaults to GEMMA_API_KEY env variable)')
@click.option('--mock', is_flag=True, help='Use mock Gemma client for testing (no API key required)')
def from_todo(todo_id, output_dir, api_key, mock):
    """Create a project from a TODO item using Gemma-powered AI suggestions."""
    if mock:
        client = MockGemmaProjectClient()
        click.echo(click.style("Using mock Gemma client for testing", fg='yellow'))
    else:
        api_key = api_key or os.environ.get('GEMMA_API_KEY')
        if not api_key:
            click.echo(click.style(
                "Error: Gemma API key not provided. Use --api-key or set GEMMA_API_KEY environment variable.",
                fg='red'
            ))
            sys.exit(1)
        client = GemmaProjectClient(api_key)
    
    try:
        project_details = client.generate_from_todo(todo_id)
        
        if not project_details:
            click.echo(click.style("Failed to generate project details from TODO", fg='red'))
            sys.exit(1)
        
        config = ProjectConfig(
            name=project_details['name'],
            description=project_details['description'],
            project_type=ProjectType(project_details['project_type']),
            path=Path(output_dir) / project_details['name'],
            additional_details=project_details.get('additional_details')
        )
        
        generator = ProjectGenerator()
        result = generator.generate_project(config)
        
        if result.success:
            click.echo(click.style(result.message, fg='green'))
            click.echo(f"Project created at: {result.project_path}")
        else:
            click.echo(click.style(result.message, fg='red'))
            if result.errors:
                for error in result.errors:
                    click.echo(f"- {error}")
            sys.exit(1)
    
    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg='red'))
        sys.exit(1)


def main():
    """Entry point for the CLI."""
    cli() 
