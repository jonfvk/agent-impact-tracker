import unittest
from agent_impact_tracker import report

class TestReportHighFrequencyHighlight(unittest.TestCase):
    def setUp(self):
        # Simulate aggregation output with file_agent_counts
        self.aggregation = {
            'total_files_touched': 3,
            'total_functions_touched': 4,
            'agents': ['Copilot', 'UnknownAgent'],
            'files_by_agent': {
                'Copilot': ['a.py', 'b.py'],
                'UnknownAgent': ['b.py', 'c.py']
            },
            'functions_by_agent': {
                'Copilot': ['foo', 'bar'],
                'UnknownAgent': ['baz', 'qux']
            },
            'agent_commit_counts': {
                'Copilot': 2,
                'UnknownAgent': 1
            },
            'file_agent_counts': {
                'a.py': {'Copilot': 3},
                'b.py': {'Copilot': 2, 'UnknownAgent': 5},
                'c.py': {'UnknownAgent': 4}
            },
            'function_agent_counts': {
                'foo': {'Copilot': 2},
                'bar': {'Copilot': 1},
                'baz': {'UnknownAgent': 3},
                'qux': {'UnknownAgent': 2}
            }
        }

    def test_high_frequency_files_section_present(self):
        summary = report.generate_text_summary_report(self.aggregation)
        self.assertIn("Top files by agent modification frequency:", summary)

    def test_high_frequency_files_sorted(self):
        summary = report.generate_text_summary_report(self.aggregation)
        # b.py has 7 touches, c.py has 4, a.py has 3
        # Find the line numbers for each file in the summary
        lines = summary.splitlines()
        file_lines = [line for line in lines if any(f in line for f in ("a.py", "b.py", "c.py"))]
        # Build a mapping from file to its index in the file_lines list
        file_to_idx = {}
        for idx, line in enumerate(file_lines):
            if 'b.py' in line:
                file_to_idx['b.py'] = idx
            if 'c.py' in line:
                file_to_idx['c.py'] = idx
            if 'a.py' in line:
                file_to_idx['a.py'] = idx
        idx_b = file_to_idx.get('b.py', -1)
        idx_c = file_to_idx.get('c.py', -1)
        idx_a = file_to_idx.get('a.py', -1)
        self.assertTrue(idx_b < idx_c < idx_a)

    def test_high_frequency_files_counts(self):
        summary = report.generate_text_summary_report(self.aggregation)
        self.assertIn('b.py (7 touches): Copilot: 2, UnknownAgent: 5', summary)
        self.assertIn('c.py (4 touches): UnknownAgent: 4', summary)
        self.assertIn('a.py (3 touches): Copilot: 3', summary)

    def test_handles_empty_file_agent_counts(self):
        agg = dict(self.aggregation)
        agg['file_agent_counts'] = {}
        summary = report.generate_text_summary_report(agg)
        self.assertNotIn('Top files by agent modification frequency:', summary)

if __name__ == '__main__':
    unittest.main()
