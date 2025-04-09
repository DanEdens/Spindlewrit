from setuptools import setup, find_packages

setup(
    name="project_generator",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "gemma-function-calling>=0.1.0",
        "pydantic>=2.0.0",
        "click>=8.0.0",
        "pyyaml>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "project-generator=project_generator.cli:main",
        ],
    },
    python_requires=">=3.8",
) 
