import unittest
import tempfile
import os
import datetime
from agent_impact_tracker import impact_identifier
from agent_impact_tracker.git_parser import GitCommit

class TestDateRangeFilter(unittest.TestCase):
    def setUp(self):
        # Create a fake repo structure in a temp dir
        self.tempdir = tempfile.TemporaryDirectory()
        self.repo_path = self.tempdir.name
        # Create a simple Python file with an agent comment
        self.py_path = os.path.join(self.repo_path, 'test.py')
        with open(self.py_path, 'w', encoding='utf-8') as f:
            f.write("""
# AI-Agent: Copilot

def foo():
    pass
""")
        # Patch parse_git_log to return fake commits
        self.fake_commits = [
            GitCommit('abc', 'Copilot', '2023-01-01T12:00:00', 'AI-Agent: Copilot', []),
            GitCommit('def', 'Copilot', '2023-06-01T12:00:00', 'AI-Agent: Copilot', []),
            GitCommit('ghi', 'Human', '2023-07-01T12:00:00', 'Refactor', [])
        ]
        self._orig_parse_git_log = impact_identifier.parse_git_log
        impact_identifier.parse_git_log = lambda repo_path: self.fake_commits

    def tearDown(self):
        impact_identifier.parse_git_log = self._orig_parse_git_log
        self.tempdir.cleanup()

    def test_no_filter_returns_all(self):
        result = impact_identifier.identify_agent_modified_files_and_functions(
            self.repo_path
        )
        # Should include both Copilot commits
        agent_commits = result[self.py_path]['agent_commit_hits']
        self.assertEqual(len(agent_commits), 2)
        dates = sorted([c['date'] for c in agent_commits])
        self.assertEqual(dates, ['2023-01-01T12:00:00', '2023-06-01T12:00:00'])

    def test_filter_start_date(self):
        result = impact_identifier.identify_agent_modified_files_and_functions(
            self.repo_path,
            start_date='2023-05-01T00:00:00'
        )
        agent_commits = result[self.py_path]['agent_commit_hits']
        # Only the June commit should remain
        self.assertEqual(len(agent_commits), 1)
        self.assertEqual(agent_commits[0]['date'], '2023-06-01T12:00:00')

    def test_filter_end_date(self):
        result = impact_identifier.identify_agent_modified_files_and_functions(
            self.repo_path,
            end_date='2023-02-01T00:00:00'
        )
        agent_commits = result[self.py_path]['agent_commit_hits']
        # Only the January commit should remain
        self.assertEqual(len(agent_commits), 1)
        self.assertEqual(agent_commits[0]['date'], '2023-01-01T12:00:00')

    def test_filter_start_and_end_date(self):
        result = impact_identifier.identify_agent_modified_files_and_functions(
            self.repo_path,
            start_date='2023-01-15T00:00:00',
            end_date='2023-06-15T00:00:00'
        )
        agent_commits = result[self.py_path]['agent_commit_hits']
        # Only the June commit should remain
        self.assertEqual(len(agent_commits), 1)
        self.assertEqual(agent_commits[0]['date'], '2023-06-01T12:00:00')

    def test_filter_excludes_all(self):
        result = impact_identifier.identify_agent_modified_files_and_functions(
            self.repo_path,
            start_date='2024-01-01T00:00:00',
            end_date='2024-12-31T00:00:00'
        )
        agent_commits = result[self.py_path]['agent_commit_hits']
        self.assertEqual(agent_commits, [])

if __name__ == '__main__':
    unittest.main()
