import argparse
import os


def parse_args():
    parser = argparse.ArgumentParser(
        description="AI Agent Code Impact Tracker: Analyze Python codebases to highlight files or functions modified by AI agents."
    )
    parser.add_argument(
        "repo_path",
        type=str,
        help="Path to the root of the Python code repository to analyze."
    )
    args = parser.parse_args()
    # Validate the path
    if not os.path.isdir(args.repo_path):
        parser.error(f"Provided path '{args.repo_path}' is not a directory.")
    return args


def main():
    args = parse_args()
    print(f"Repository path provided: {args.repo_path}")


if __name__ == "__main__":
    main()
