"""验证静态审查、契约生成及真实 pytest 行为。"""
import ast
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"skills/{name}/scripts/run.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


reviewer = load("python-code-reviewer")
generator = load("pytest-generator")


class ReviewerTests(unittest.TestCase):
    def test_clean(self):
        self.assertEqual(reviewer.review("def f(x): return x + 1"), [])

    def test_mutable_keyword_default(self):
        result = reviewer.review("def f(*, items=[]): return items")
        self.assertEqual(result[0]["规则"], "mutable-default")
        self.assertEqual(result[0]["行号"], 1)

    def test_exception(self):
        result = reviewer.review("try: x = 1\nexcept: pass")
        self.assertEqual({x["规则"] for x in result}, {"bare-except", "swallowed-exception"})

    def test_invalid_source(self):
        with self.assertRaises(SyntaxError):
            reviewer.review("def (")

    def test_cli_exit_codes(self):
        script = ROOT / "skills/python-code-reviewer/scripts/run.py"
        for source, code in [("examples/demo/calculator.py", 0), ("examples/review_bad.py", 1), ("missing.py", 2)]:
            result = subprocess.run([sys.executable, str(script), str(ROOT / source)], capture_output=True)
            self.assertEqual(result.returncode, code)


class GeneratorTests(unittest.TestCase):
    def setUp(self):
        self.source = (ROOT / "examples/demo/calculator.py").read_text(encoding="utf-8")
        self.contract = json.loads((ROOT / "examples/demo/cases.json").read_text(encoding="utf-8"))

    def test_non_finite_values_rejected(self):
        for value in (float("inf"), float("-inf"), float("nan")):
            with self.subTest(value=value):
                self.contract["cases"][0]["args"] = [{"nested": [value]}]
                with self.assertRaises(ValueError):
                    generator.generate(self.source, self.contract)

    def test_non_object_contract(self):
        with self.assertRaises(ValueError):
            generator.generate(self.source, [])

    def test_valid_ast(self):
        ast.parse(generator.generate(self.source, self.contract))

    def test_too_few_cases(self):
        self.contract["cases"] = []
        with self.assertRaises(ValueError):
            generator.generate(self.source, self.contract)

    def test_missing_function(self):
        self.contract["function"] = "missing"
        with self.assertRaises(ValueError):
            generator.generate(self.source, self.contract)

    def test_injection_rejected(self):
        self.contract["module"] = "os; print(1)"
        with self.assertRaises(ValueError):
            generator.generate(self.source, self.contract)

    def test_ambiguous_case(self):
        self.contract["cases"][0]["raises"] = "ValueError"
        with self.assertRaises(ValueError):
            generator.generate(self.source, self.contract)

    def test_real_pytest_and_wrong_implementation(self):
        # 同一契约先验证正确实现，再确认它能发现错误实现。
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            (path / "test_generated.py").write_text(generator.generate(self.source, self.contract), encoding="utf-8")
            target = path / "calculator.py"
            target.write_text(self.source, encoding="utf-8")
            command = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--basetemp", str(path / "pytest-temp"), str(path / "test_generated.py")]
            good = subprocess.run(command, cwd=path, capture_output=True, text=True)
            self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
            target.write_text("def add(a, b): return 999999\n", encoding="utf-8")
            bad = subprocess.run(command, cwd=path, capture_output=True, text=True)
            self.assertEqual(bad.returncode, 1, bad.stdout + bad.stderr)
