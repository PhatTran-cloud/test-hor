import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from output_paths import get_output_root, REPO_ROOT


class OutputPathTests(unittest.TestCase):
    def test_default_is_workspace_outputs_independent_of_cwd(self):
        with patch.dict(os.environ, {"CODE2VIDEO_OUTPUT_ROOT": ""}):
            self.assertEqual(get_output_root(), (REPO_ROOT.parent / "outputs").resolve())

    def test_explicit_environment_override(self):
        requested = REPO_ROOT.parent / "test-output-root"
        with patch.dict(os.environ, {"CODE2VIDEO_OUTPUT_ROOT": str(requested)}):
            self.assertEqual(get_output_root(), requested.resolve())
