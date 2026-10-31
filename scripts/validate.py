"""校验本仓库 Skill 规范子集、引用与 Python 语法。"""
import ast
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
expected = {"readme-writer", "python-code-reviewer", "pytest-generator", "requirements-analyst"}
actual = {p.name for p in (root / "skills").iterdir() if p.is_dir()}
if actual != expected:
    raise SystemExit("Skill 清单与预期不一致")
for name in sorted(expected):
    skill = root / "skills" / name
    content = (skill / "SKILL.md").read_text(encoding="utf-8")
    parts = content.split("---", 2)
    if len(parts) != 3 or parts[0] or not re.search(rf"^name: {re.escape(name)}$", parts[1], re.M):
        raise SystemExit(f"元数据或名称错误：{name}")
    if not re.search(r"^description: \S.+$", parts[1], re.M):
        raise SystemExit(f"缺少描述：{name}")
    for target in re.findall(r"\]\(([^)]+)\)", content):
        if not target.startswith("https://") and not (skill / target).is_file():
            raise SystemExit(f"失效引用：{target}")
    if not (skill / "scripts/run.py").is_file():
        raise SystemExit(f"缺少脚本：{name}")
for path in root.rglob("*.py"):
    if "__pycache__" not in path.parts:
        ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
print("四个 Skill 的结构、引用和 Python 语法校验通过")
