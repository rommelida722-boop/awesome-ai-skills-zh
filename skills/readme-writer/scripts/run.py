"""从项目元数据生成双语 README 草稿；不执行项目代码。"""
import argparse
import json
from pathlib import Path
import tomllib


def generate(root):
    """只读取明确的元数据，避免扫描密钥文件及猜测项目能力。"""
    root = Path(root)
    if not root.is_dir():
        raise ValueError("项目目录不存在")
    meta = root / "pyproject.toml"
    if not meta.is_file() or meta.is_symlink():
        raise ValueError("需要普通文件 pyproject.toml")
    project = tomllib.loads(meta.read_text(encoding="utf-8")).get("project", {})
    name = project.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("缺少 project.name")
    # JSON 转义避免元数据中的换行或反引号破坏 Markdown 结构。
    name = json.dumps(name, ensure_ascii=False)
    description = json.dumps(project.get("description", "未提供描述"), ensure_ascii=False)
    return (f"# {name}\n\n## 项目说明 / Overview\n\n{description}\n\n"
            "## 安装 / Installation\n\n请根据项目依赖和构建配置确认安装步骤。\n\n"
            "## 使用 / Usage\n\n请补充经过验证的使用示例。\n\n"
            "## 测试 / Tests\n\n请确认测试框架与执行命令。\n\n"
            "## 许可证 / License\n\n请查看项目许可证文件。\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project")
    parser.add_argument("output")
    args = parser.parse_args()
    try:
        content = generate(args.project)
        # 独占创建，防止覆盖用户已有的 README。
        with Path(args.output).open("x", encoding="utf-8") as stream:
            stream.write(content)
    except (ValueError, OSError) as exc:
        parser.exit(2, f"生成失败：{exc}\n")


if __name__ == "__main__":
    main()
