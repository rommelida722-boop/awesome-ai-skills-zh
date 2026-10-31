"""将人工定义的 JSON 契约转为 pytest 参数化测试，不执行被测代码。"""
import argparse
import ast
import json
import keyword
import math
from pathlib import Path

ALLOWED_ERRORS = {"ValueError", "TypeError", "ZeroDivisionError", "IndexError", "KeyError"}


def identifier(value):
    """限制导入名称，防止契约被拼接成任意 Python 语句。"""
    return isinstance(value, str) and value.isidentifier() and not keyword.iskeyword(value)


def generate(source, contract):
    if not isinstance(contract, dict):
        raise ValueError("契约必须是 JSON 对象")

    def check_json(value):
        """递归拒绝不可移植的数值，避免生成含未定义 inf 或 nan 的测试。"""
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("不支持非有限数值")
        if isinstance(value, list):
            for item in value:
                check_json(item)
        elif isinstance(value, dict):
            for item in value.values():
                check_json(item)

    check_json(contract)
    tree = ast.parse(source)
    module = contract.get("module")
    function = contract.get("function")
    if not isinstance(module, str) or not all(identifier(x) for x in module.split(".")):
        raise ValueError("module 必须是有效模块路径")
    if not identifier(function):
        raise ValueError("function 必须是有效函数名")
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == function]
    if not functions:
        raise ValueError("仅支持模块顶层同步函数")
    cases = contract.get("cases")
    if not isinstance(cases, list) or len(cases) < 3:
        raise ValueError("至少提供三个契约案例，包括边界值")
    rows = []
    errors = []
    for case in cases:
        if not isinstance(case, dict) or not isinstance(case.get("args"), list):
            raise ValueError("每个案例必须有 args 数组")
        if ("expected" in case) == ("raises" in case):
            raise ValueError("expected 与 raises 必须且只能提供一个")
        # repr 只序列化 JSON 数据，不把输入当表达式执行。
        if "raises" in case:
            if not isinstance(case["raises"], str) or case["raises"] not in ALLOWED_ERRORS:
                raise ValueError("不支持的异常类型")
            errors.append((case["args"], case["raises"]))
        else:
            rows.append((case["args"], case["expected"]))
    lines = ["# 根据人工契约生成；请确认案例覆盖业务边界。", "import pytest",
             f"from {module} import {function} as target", ""]
    if rows:
        lines += [f"@pytest.mark.parametrize('args, expected', {rows!r})",
                  "def test_contract(args, expected):", "    assert target(*args) == expected", ""]
    for index, (args, error) in enumerate(errors):
        lines += [f"def test_exception_{index}():", f"    with pytest.raises({error}):",
                  f"        target(*{args!r})", ""]
    result = "\n".join(lines)
    ast.parse(result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("contract")
    parser.add_argument("output")
    args = parser.parse_args()
    try:
        source = Path(args.source)
        contract_path = Path(args.contract)
        if source.is_symlink() or contract_path.is_symlink():
            raise ValueError("不读取符号链接")
        contract = json.loads(contract_path.read_text(encoding="utf-8"),
                              parse_constant=lambda value: (_ for _ in ()).throw(ValueError("不支持非有限数值")))
        if not isinstance(contract, dict):
            raise ValueError("契约必须是 JSON 对象")
        content = generate(source.read_text(encoding="utf-8-sig"), contract)
        with Path(args.output).open("x", encoding="utf-8") as stream:
            stream.write(content)
    except (OSError, ValueError, SyntaxError) as exc:
        parser.exit(2, f"生成失败：{exc}\n")


if __name__ == "__main__":
    main()
