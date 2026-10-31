from typing import Dict, Any, List, Optional
import datetime

def generate_text_summary_report(
    aggregation: Dict[str, Any],
    report_title: Optional[str] = None,
    include_details: bool = True,
) -> str:
    """
    Generate a human-readable text summary report of agent impact.

    Args:
        aggregation (Dict[str, Any]): Output from aggregate_agent_modification_data().
        report_title (Optional[str]): Optional title for the report.
        include_details (bool): Whether to include detailed lists of files/functions.

    Returns:
        str: The formatted report as a string.
    """
    lines = []
    now = datetime.datetime.now().isoformat(timespec='seconds')
    title = report_title or "AI Agent Code Impact Summary"
    lines.append(f"{title}")
    lines.append(f"Generated: {now}")
    lines.append("")
    lines.append(f"Total files touched by AI agents: {aggregation.get('total_files_touched', 0)}")
    lines.append(f"Total functions touched by AI agents: {aggregation.get('total_functions_touched', 0)}")
    lines.append("")
    agents = aggregation.get('agents', [])
    if agents:
        lines.append(f"Agents detected: {', '.join(sorted(agents))}")
    else:
        lines.append("Agents detected: None")
    lines.append("")
    # Per-agent summary
    lines.append("Agent modification summary:")
    for agent in sorted(agents):
        files = aggregation.get('files_by_agent', {}).get(agent, [])
        funcs = aggregation.get('functions_by_agent', {}).get(agent, [])
        commit_count = aggregation.get('agent_commit_counts', {}).get(agent, 0)
        lines.append(f"  - {agent}:")
        lines.append(f"      Files touched: {len(files)}")
        lines.append(f"      Functions touched: {len(funcs)}")
        lines.append(f"      Commits detected: {commit_count}")
    lines.append("")
    if include_details:
        # List files by agent
        lines.append("Files touched by each agent:")
        for agent in sorted(agents):
            files = aggregation.get('files_by_agent', {}).get(agent, [])
            if files:
                lines.append(f"  {agent}:")
                for f in files:
                    lines.append(f"    - {f}")
            else:
                lines.append(f"  {agent}: None")
        lines.append("")
        # List functions by agent
        lines.append("Functions touched by each agent:")
        for agent in sorted(agents):
            funcs = aggregation.get('functions_by_agent', {}).get(agent, [])
            if funcs:
                lines.append(f"  {agent}:")
                for func in funcs:
                    lines.append(f"    - {func}")
            else:
                lines.append(f"  {agent}: None")
        lines.append("")
    # Top files/functions by agent touch frequency
    file_agent_counts = aggregation.get('file_agent_counts', {})
    if file_agent_counts:
        lines.append("Top files by agent modification frequency:")
        # Sort by total agent touches per file
        file_counts = [
            (f, sum(agent_counts.values()))
            for f, agent_counts in file_agent_counts.items()
        ]
        file_counts.sort(key=lambda x: x[1], reverse=True)
        for f, count in file_counts[:10]:
            lines.append(f"  {f}: {count} agent touches")
        lines.append("")
    function_agent_counts = aggregation.get('function_agent_counts', {})
    if function_agent_counts:
        lines.append("Top functions by agent modification frequency:")
        func_counts = [
            (func, sum(agent_counts.values()))
            for func, agent_counts in function_agent_counts.items()
        ]
        func_counts.sort(key=lambda x: x[1], reverse=True)
        for func, count in func_counts[:10]:
            lines.append(f"  {func}: {count} agent touches")
        lines.append("")
    return '\n'.join(lines)
