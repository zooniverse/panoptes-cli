from click.testing import CliRunner
from panoptes_cli.commands.project import ls

import unittest

import warnings
import sys

class TestProject(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestProject, self).__init__(*args, **kwargs)
        self.runner = CliRunner()

    def test_ls_id_public(self):
        if sys.version_info >= (3, 0):
            # avoid client socket warnings polluting our test results
            # this can go when the underlying client issue is fixed
            # https://github.com/zooniverse/panoptes-python-client/issues/270
            warnings.filterwarnings(
                action="ignore", message="unclosed", category=ResourceWarning)

        result = self.runner.invoke(ls, ['--project-id', '1'])
        self.assertEqual(
            result.output,
            '1 zooniverse/snapshot-supernova Snapshot Supernova\n'
        )

    def test_ls_id_private_anon(self):
        result = self.runner.invoke(ls, ['--project-id', '7'])
        self.assertEqual(result.output, '')

    def test_ls_slug_public(self):
        result = self.runner.invoke(
            ls,
            ['--slug', 'zooniverse/snapshot-supernova']
        )
        self.assertEqual(
            result.output,
            '1 zooniverse/snapshot-supernova Snapshot Supernova\n'
        )

    def test_ls_slug_private_anon(self):
        result = self.runner.invoke(ls, ['--slug', 'astopy/testing'])
        self.assertEqual(result.output, '')
