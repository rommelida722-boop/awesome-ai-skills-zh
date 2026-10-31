"""验证需求契约、可追踪关系与输出保护，不代替 Agent 语义评测。"""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/requirements-analyst/scripts/run.py"
spec = importlib.util.spec_from_file_location("requirements", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class RequirementsTests(unittest.TestCase):
    def setUp(self):
        self.input = ROOT / "examples/requirements/tasks.json"
        self.data = json.loads(self.input.read_text(encoding="utf-8"))

    def test_valid_traceability(self):
        result = module.render(self.data)
        self.assertIn("A-002 → F-001", result)
        self.assertIn(self.data["核心功能"][0]["来源"], result)
        self.assertIn(self.data["待确认事项"][0], result)
        self.assertIn("草稿", result)

    def test_missing_user(self):
        del self.data["目标用户"]
        with self.assertRaises(module.ContractError):
            module.render(self.data)

    def test_whitespace_rule(self):
        self.data["核心功能"][0]["规则"] = "  "
        with self.assertRaises(module.ContractError):
            module.render(self.data)

    def test_duplicate_id(self):
        self.data["核心功能"].append(copy.deepcopy(self.data["核心功能"][0]))
        with self.assertRaises(module.ContractError):
            module.render(self.data)

    def test_dangling_reference(self):
        self.data["成功标准"][0]["功能编号"] = "F-999"
        with self.assertRaises(module.ContractError):
            module.render(self.data)

    def test_uncovered_feature(self):
        self.data["成功标准"] = self.data["成功标准"][:2]
        with self.assertRaises(module.ContractError):
            module.render(self.data)

    def test_wrong_list_type(self):
        self.data["技术约束"] = "本地"
        with self.assertRaises(module.ContractError):
            module.render(self.data)

    def test_cli_success_and_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "需求.md"
            command = [sys.executable, str(SCRIPT), str(self.input), str(output)]
            first = subprocess.run(command, capture_output=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            original = output.read_bytes()
            second = subprocess.run(command, capture_output=True)
            self.assertEqual(second.returncode, 2)
            self.assertEqual(output.read_bytes(), original)

    def test_malformed_input_writes_nothing(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "bad.json"
            output = Path(folder) / "需求.md"
            source.write_text("{", encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPT), str(source), str(output)], capture_output=True)
            self.assertEqual(result.returncode, 2)
            self.assertFalse(output.exists())
