from typing import Dict, List, Any, Optional
import collections


def aggregate_agent_modification_data(
    impact_data: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Aggregate agent modification data across all files.

    Args:
        impact_data (Dict[str, Dict[str, Any]]):
            Output from identify_agent_modified_files_and_functions().

    Returns:
        Dict[str, Any]:
            {
                'total_files_touched': int,
                'total_functions_touched': int,
                'files_by_agent': {agent_name: [file1, ...]},
                'functions_by_agent': {agent_name: [function1, ...]},
                'file_agent_counts': {file: {agent_name: count}},
                'function_agent_counts': {function: {agent_name: count}},
                'agent_commit_counts': {agent_name: int},
                'agents': [agent_name, ...],
            }
    """
    files_by_agent = collections.defaultdict(set)
    functions_by_agent = collections.defaultdict(set)
    file_agent_counts = collections.defaultdict(lambda: collections.defaultdict(int))
    function_agent_counts = collections.defaultdict(lambda: collections.defaultdict(int))
    agent_commit_counts = collections.defaultdict(int)
    agents = set()
    all_functions = set()

    for file_path, data in impact_data.items():
        # Comments
        for hit in data.get('agent_comment_hits', []):
            agent_name = hit.get('agent_name') or 'UnknownAgent'
            agents.add(agent_name)
            files_by_agent[agent_name].add(file_path)
            file_agent_counts[file_path][agent_name] += 1
            func = hit.get('function_name')
            if func:
                functions_by_agent[agent_name].add(func)
                function_agent_counts[func][agent_name] += 1
                all_functions.add(func)
        # Commits
        for commit in data.get('agent_commit_hits', []):
            author = commit.get('author') or 'UnknownAgent'
            for agent in agents:
                # If agent name is in author or message, count it
                if (agent != 'UnknownAgent' and (
                    (agent.lower() in (author or '').lower()) or
                    (agent.lower() in (commit.get('message') or '').lower())
                )):
                    agent_commit_counts[agent] += 1
            # Fallback: if no agent matched, count as UnknownAgent
            if not any(agent.lower() in (author or '').lower() for agent in agents if agent != 'UnknownAgent'):
                agent_commit_counts['UnknownAgent'] += 1

    return {
        'total_files_touched': len(impact_data),
        'total_functions_touched': len(all_functions),
        'files_by_agent': {k: sorted(v) for k, v in files_by_agent.items()},
        'functions_by_agent': {k: sorted(v) for k, v in functions_by_agent.items()},
        'file_agent_counts': {k: dict(v) for k, v in file_agent_counts.items()},
        'function_agent_counts': {k: dict(v) for k, v in function_agent_counts.items()},
        'agent_commit_counts': dict(agent_commit_counts),
        'agents': sorted(agents),
    }
