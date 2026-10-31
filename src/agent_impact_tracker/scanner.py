import os
from typing import List

def scan_python_files(repo_path: str) -> List[str]:
    """
    Recursively scan the given repository path for Python (.py) files.

    Args:
        repo_path (str): Path to the root of the repository.

    Returns:
        List[str]: List of absolute paths to Python files found.
    """
    python_files = []
    for root, dirs, files in os.walk(repo_path):
        # Skip hidden directories (like .git, .venv, etc.)
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if file.endswith('.py') and not file.startswith('.'):
                python_files.append(os.path.join(root, file))
    return python_files
