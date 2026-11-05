import json
from pathlib import Path
import tempfile
import unittest

from validate_release import validate_release


class ReleaseValidationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for name in ("n8n", "agno", "agentgateway"):
            directory = self.root / "integrations" / name
            directory.mkdir(parents=True)
            if name == "n8n":
                (directory / "package.json").write_text(json.dumps({"version": "1.2.3"}))
            elif name == "agno":
                (directory / "pyproject.toml").write_text('[project]\nversion = "1.2.3"\n')

    def test_package_versions(self):
        for integration in ("n8n", "agno", "agentgateway"):
            with self.subTest(integration=integration):
                self.assertEqual(validate_release(self.root, integration, f"{integration}/v1.2.3"), "1.2.3")

    def test_version_mismatch(self):
        with self.assertRaisesRegex(ValueError, "does not match"):
            validate_release(self.root, "n8n", "n8n/v1.2.4")

    def test_wrong_integration_tag(self):
        with self.assertRaises(ValueError):
            validate_release(self.root, "agno", "n8n/v1.2.3")

    def test_invalid_or_injected_tags(self):
        for tag in ("v1.2.3", "agno/v1.2", "agno/v1.2.3; echo unsafe", "agno/v1.2.3-rc1"):
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                validate_release(self.root, "agno", tag)

    def test_original_source_tag_has_no_monorepo_path(self):
        with self.assertRaisesRegex(ValueError, "monorepo"):
            validate_release(self.root, "strands", "strands/v1.2.3")

    def test_reject_path_traversal(self):
        with self.assertRaises(ValueError):
            validate_release(self.root, "../agno", "../agno/v1.2.3")
