import argparse
import os
from . import impact_identifier, aggregation, report

def parse_args():
    parser = argparse.ArgumentParser(
        description="AI Agent Code Impact Tracker: Analyze Python codebases to highlight files or functions modified by AI agents."
    )
    parser.add_argument(
        "repo_path",
        type=str,
        help="Path to the root of the Python code repository to analyze."
    )
    parser.add_argument(
        "--output-file",
        dest="output_file",
        type=str,
        default=None,
        help="Path to write the summary report to (optional)."
    )
    args = parser.parse_args()
    # Validate the path
    if not os.path.isdir(args.repo_path):
        parser.error(f"Provided path '{args.repo_path}' is not a directory.")
    return args


def main():
    args = parse_args()
    impact = impact_identifier.identify_agent_modified_files_and_functions(args.repo_path)
    agg = aggregation.aggregate_agent_modification_data(impact)
    summary = report.generate_text_summary_report(agg)
    if args.output_file:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Report written to {args.output_file}")
    else:
        print(summary)


if __name__ == "__main__":
    main()
