import os
import ast
from typing import List, Dict, Optional, Tuple
from .comment_parser import extract_agent_signatures_from_comments
from .git_parser import parse_git_log, find_agent_commits
import datetime

def identify_agent_modified_files_and_functions(
    repo_path: str,
    agent_signature_patterns: Optional[List[str]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Dict]:
    """
    Identify files and functions modified by AI agents based on code comments and git commit metadata.

    Args:
        repo_path (str): Path to the root of the repository.
        agent_signature_patterns (Optional[List[str]]): Custom regex patterns for agent signatures.
        start_date (Optional[str]): ISO format string. Only include agent commits on or after this date.
        end_date (Optional[str]): ISO format string. Only include agent commits on or before this date.

    Returns:
        Dict[str, Dict]:
            {
                'file_path': {
                    'agent_comment_hits': [ {line_number, line, signature, agent_name, function_name} ],
                    'agent_commit_hits': [ {commit_hash, author, date, message} ],
                    'functions_touched': set(function names)
                },
                ...
            }
    """
    from .scanner import scan_python_files

    python_files = scan_python_files(repo_path)
    result = {}

    # --- 1. Check code comments for agent signatures ---
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
        except Exception:
            continue
        comment_hits = extract_agent_signatures_from_comments(content)
        if not comment_hits:
            continue
        # Map line numbers to function names
        line_to_func = _map_lines_to_functions(content)
        for hit in comment_hits:
            ln = hit['line_number']
            hit['function_name'] = line_to_func.get(ln)
        result.setdefault(file_path, {
            'agent_comment_hits': [],
            'agent_commit_hits': [],
            'functions_touched': set()
        })
        result[file_path]['agent_comment_hits'].extend(comment_hits)
        for hit in comment_hits:
            if hit['function_name']:
                result[file_path]['functions_touched'].add(hit['function_name'])

    # --- 2. Check git commits for agent signatures ---
    commits = parse_git_log(repo_path)
    agent_commits = find_agent_commits(commits)
    # Date filtering
    filtered_agent_commits = []
    for c in agent_commits:
        commit_date = c.date
        # Parse ISO format
        try:
            commit_dt = datetime.datetime.fromisoformat(commit_date)
        except Exception:
            filtered_agent_commits.append(c)
            continue
        if start_date:
            try:
                start_dt = datetime.datetime.fromisoformat(start_date)
                if commit_dt < start_dt:
                    continue
            except Exception:
                pass
        if end_date:
            try:
                end_dt = datetime.datetime.fromisoformat(end_date)
                if commit_dt > end_dt:
                    continue
            except Exception:
                pass
        filtered_agent_commits.append(c)
    # We can't reliably map commits to files offline, but if a file has a comment hit,
    # and there are agent commits, we can record the commit info for context.
    if filtered_agent_commits:
        for file_path in result:
            result[file_path]['agent_commit_hits'] = [
                {
                    'commit_hash': c.commit_hash,
                    'author': c.author,
                    'date': c.date,
                    'message': c.message
                } for c in filtered_agent_commits
            ]
    else:
        for file_path in result:
            result[file_path]['agent_commit_hits'] = []

    # Convert sets to lists for serialization
    for file_path in result:
        result[file_path]['functions_touched'] = list(result[file_path]['functions_touched'])
    return result


def _map_lines_to_functions(file_content: str) -> Dict[int, Optional[str]]:
    """
    Map line numbers to function names using AST.
    Returns a dict: {line_number: function_name or None}
    """
    try:
        tree = ast.parse(file_content)
    except Exception:
        return {}
    line_to_func = {}
    func_ranges = []  # List of (start, end, name)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            start = node.lineno
            # Try to find end line
            end = _find_end_lineno(node)
            func_ranges.append((start, end, node.name))
    # Map each line in a function's range to its name
    for start, end, name in func_ranges:
        for ln in range(start, end + 1):
            line_to_func[ln] = name
    return line_to_func

def _find_end_lineno(node: ast.FunctionDef) -> int:
    """
    Find the last line number of a function definition.
    """
    max_lineno = node.lineno
    for child in ast.walk(node):
        if hasattr(child, 'lineno'):
            max_lineno = max(max_lineno, child.lineno)
    return max_lineno
