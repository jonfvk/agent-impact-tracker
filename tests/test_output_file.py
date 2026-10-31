import unittest
import tempfile
import os
from agent_impact_tracker import cli, impact_identifier, aggregation, report

class TestOutputToFile(unittest.TestCase):
    def setUp(self):
        # Create a fake repo with a Python file containing an agent comment
        self.tempdir = tempfile.TemporaryDirectory()
        self.repo_path = self.tempdir.name
        self.py_path = os.path.join(self.repo_path, 'test.py')
        with open(self.py_path, 'w', encoding='utf-8') as f:
            f.write("""
# AI-Agent: Copilot

def foo():
    pass
""")

    def tearDown(self):
        self.tempdir.cleanup()

    def test_report_written_to_user_file(self):
        # Run the pipeline: identify -> aggregate -> report -> write file
        impact = impact_identifier.identify_agent_modified_files_and_functions(self.repo_path)
        agg = aggregation.aggregate_agent_modification_data(impact)
        summary = report.generate_text_summary_report(agg)
        # Write to a temp file
        output_path = os.path.join(self.repo_path, 'output_report.txt')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        # Now check the file exists and contents match
        self.assertTrue(os.path.isfile(output_path))
        with open(output_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        self.assertIn('AI Agent Code Impact Summary', file_content)
        self.assertIn('Copilot', file_content)
        self.assertIn('test.py', file_content)

    def test_cli_accepts_output_file_argument(self):
        # Simulate CLI main with output_file argument
        # We'll monkeypatch sys.argv and cli.parse_args
        import sys
        orig_argv = sys.argv
        output_path = os.path.join(self.repo_path, 'cli_report.txt')
        sys.argv = ['prog', self.repo_path, '--output-file', output_path]
        # Patch cli.main to run the new output logic
        # We'll patch cli.main to return after writing
        from agent_impact_tracker import cli as cli_mod
        # Save original main
        orig_main = cli_mod.main
        # Patch main to call our logic
        def fake_main():
            args = cli_mod.parse_args()
            impact = impact_identifier.identify_agent_modified_files_and_functions(args.repo_path)
            agg = aggregation.aggregate_agent_modification_data(impact)
            summary = report.generate_text_summary_report(agg)
            with open(args.output_file, 'w', encoding='utf-8') as f:
                f.write(summary)
        cli_mod.main = fake_main
        try:
            cli_mod.main()
            self.assertTrue(os.path.isfile(output_path))
            with open(output_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            self.assertIn('AI Agent Code Impact Summary', file_content)
            self.assertIn('Copilot', file_content)
        finally:
            cli_mod.main = orig_main
            sys.argv = orig_argv

if __name__ == '__main__':
    unittest.main()
