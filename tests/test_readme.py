"""验证 README 元数据处理与失败行为。"""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("writer", ROOT / "skills/readme-writer/scripts/run.py")
writer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(writer)


class ReadmeTests(unittest.TestCase):
    def test_valid_project(self):
        with tempfile.TemporaryDirectory() as folder:
            Path(folder, "pyproject.toml").write_text('[project]\nname="demo"\ndescription="计算工具"', encoding="utf-8")
            result = writer.generate(folder)
            self.assertIn("计算工具", result)
            self.assertIn("Overview", result)

    def test_missing_metadata(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                writer.generate(folder)

    def test_missing_name(self):
        with tempfile.TemporaryDirectory() as folder:
            Path(folder, "pyproject.toml").write_text("[project]", encoding="utf-8")
            with self.assertRaises(ValueError):
                writer.generate(folder)

    def test_invalid_toml(self):
        with tempfile.TemporaryDirectory() as folder:
            Path(folder, "pyproject.toml").write_text("[", encoding="utf-8")
            with self.assertRaises(ValueError):
                writer.generate(folder)


class ReadmeCliTests(unittest.TestCase):
    def test_existing_output_preserved(self):
        import subprocess
        import sys
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder, "README.md")
            output.write_text("保留内容", encoding="utf-8")
            result = subprocess.run([sys.executable, str(ROOT / "skills/readme-writer/scripts/run.py"), str(ROOT / "examples/demo"), str(output)], capture_output=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(output.read_text(encoding="utf-8"), "保留内容")
