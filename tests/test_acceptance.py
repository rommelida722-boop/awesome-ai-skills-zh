"""以真实任务执行 CLI，检查有用的产物与可暴露的业务错误。"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def run(*args, cwd=None):
    return subprocess.run([sys.executable, *map(str, args)], cwd=cwd or ROOT,
                          capture_output=True, text=True, encoding="utf-8", errors="replace")


class AcceptanceTests(unittest.TestCase):
    def test_review_observes_shared_state(self):
        script = ROOT / "skills/python-code-reviewer/scripts/run.py"
        result = run(script, ROOT / "examples/review_bad.py")
        self.assertEqual(result.returncode, 1)
        findings = json.loads(result.stdout)
        self.assertEqual(len(findings), 3)
        # 只执行仓库自身的可信演示样本，复现实际影响。
        namespace = {}
        exec((ROOT / "examples/review_bad.py").read_text(encoding="utf-8"), namespace)
        first = namespace["collect"]("甲")
        second = namespace["collect"]("乙")
        self.assertIs(first, second)
        self.assertEqual(second, ["甲", "乙"])

    def test_boundary_contract_detects_business_mutation(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            source = ROOT / "examples/evaluation/average.py"
            (target / "average.py").write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            result = run(ROOT / "skills/pytest-generator/scripts/run.py", source,
                         ROOT / "examples/evaluation/average-cases.json", target / "test_average.py")
            self.assertEqual(result.returncode, 0, result.stderr)
            command = ("-m", "pytest", "-q", "-p", "no:cacheprovider", "--basetemp", target / "pytest-temp", target / "test_average.py")
            correct = run(*command, cwd=target)
            self.assertEqual(correct.returncode, 0, correct.stdout + correct.stderr)
            self.assertIn("6 passed", correct.stdout)
            # 将平均值改为总和，验证断言确实表达业务规则。
            mutated = source.read_text(encoding="utf-8").replace("sum(values) / len(values)", "sum(values)")
            (target / "average.py").write_text(mutated, encoding="utf-8")
            wrong = run(*command, cwd=target)
            self.assertEqual(wrong.returncode, 1, wrong.stdout + wrong.stderr)
            self.assertIn("failed", wrong.stdout)

    def test_readme_cli_produces_honest_scaffold(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "README.md"
            result = run(ROOT / "skills/readme-writer/scripts/run.py", ROOT / "examples/demo", output)
            self.assertEqual(result.returncode, 0, result.stderr)
            content = output.read_text(encoding="utf-8")
            self.assertIn("demo-calculator", content)
            self.assertIn("用于演示的加法函数", content)
            self.assertNotIn("pip install demo-calculator", content)
            self.assertNotIn("测试通过", content)

    def test_requirements_cli_preserves_constraints_and_uncertainty(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "需求.md"
            source = ROOT / "examples/requirements/tasks.json"
            result = run(ROOT / "skills/requirements-analyst/scripts/run.py", source, output)
            self.assertEqual(result.returncode, 0, result.stderr)
            content = output.read_text(encoding="utf-8")
            data = json.loads(source.read_text(encoding="utf-8"))
            for item in data["不做的功能"] + data["待确认事项"]:
                self.assertIn(item, content)
            for case in data["成功标准"]:
                self.assertIn(case["编号"] + " → " + case["功能编号"], content)
