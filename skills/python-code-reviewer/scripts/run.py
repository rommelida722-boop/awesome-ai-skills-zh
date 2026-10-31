"""使用 AST 输出可复查的 Python 静态审查结果，不导入目标模块。"""
import argparse
import ast
import json
from pathlib import Path


def review(source, filename="输入.py"):
    """提供局部、可定位的规则；不能证明程序没有缺陷。"""
    tree = ast.parse(source, filename=filename)
    findings = []

    def report(node, rule, message):
        findings.append({"文件": filename, "行号": node.lineno,
                         "规则": rule, "说明": message})

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defaults = node.args.defaults + [x for x in node.args.kw_defaults if x is not None]
            for default in defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set, ast.ListComp, ast.DictComp, ast.SetComp)):
                    report(default, "mutable-default", "可变默认参数会在多次调用间共享；考虑使用 None 并在函数内创建。")
        if isinstance(node, ast.ExceptHandler):
            if node.type is None:
                report(node, "bare-except", "裸 except 也会捕获退出和中断；考虑指定异常类型。")
            if all(isinstance(item, ast.Pass) for item in node.body):
                report(node, "swallowed-exception", "异常被直接忽略；确认是否需要记录、恢复或重新抛出。")
    return sorted(findings, key=lambda item: (item["行号"], item["规则"]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="单个 Python 文件")
    args = parser.parse_args()
    try:
        path = Path(args.source)
        if path.is_symlink() or path.suffix != ".py":
            raise ValueError("需要普通 .py 文件")
        result = review(path.read_text(encoding="utf-8-sig"), str(path))
    except (OSError, ValueError, SyntaxError) as exc:
        parser.exit(2, f"审查失败：{exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result else 0


if __name__ == "__main__":
    raise SystemExit(main())
