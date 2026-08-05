"""Regression tests for the packaged command-line interface."""

from __future__ import annotations

import sys
import tempfile
import tomllib
import types
import unittest
from contextlib import redirect_stderr, redirect_stdout
from importlib import import_module
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from aggrequant.cli import main


class CliTests(unittest.TestCase):
    def test_packaged_entry_point_resolves_to_main(self):
        pyproject = Path(__file__).parents[2] / "pyproject.toml"
        project = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]
        module_name, attribute_name = project["scripts"]["aggrequant"].split(":", 1)

        entry_point = getattr(import_module(module_name), attribute_name)

        self.assertIs(entry_point, main)

    def test_missing_config_returns_error_without_importing_pipeline(self):
        missing = Path(tempfile.gettempdir()) / "aggrequant-missing-config.yaml"
        stderr = StringIO()

        with patch.dict(sys.modules, {"aggrequant.pipeline": None}), redirect_stderr(stderr):
            status = main([str(missing)])

        self.assertEqual(status, 1)
        self.assertIn("Config file not found", stderr.getvalue())

    def test_cli_delegates_all_options_to_pipeline(self):
        calls: dict[str, object] = {}

        class FakePipeline:
            def __init__(self, config_path, verbose=False):
                calls["init"] = (config_path, verbose)

            def run(self, max_fields=None, segmentation_only=False):
                calls["run"] = (max_fields, segmentation_only)

        fake_module = types.ModuleType("aggrequant.pipeline")
        fake_module.SegmentationPipeline = FakePipeline

        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "config.yaml"
            config.write_text("plate_name: test\n", encoding="utf-8")

            with patch.dict(sys.modules, {"aggrequant.pipeline": fake_module}):
                with redirect_stdout(StringIO()):
                    status = main(
                        [str(config), "--verbose", "--max-fields", "5", "--segmentation-only"]
                    )

        self.assertEqual(status, 0)
        self.assertEqual(calls["init"], (config, True))
        self.assertEqual(calls["run"], (5, True))


if __name__ == "__main__":
    unittest.main()
