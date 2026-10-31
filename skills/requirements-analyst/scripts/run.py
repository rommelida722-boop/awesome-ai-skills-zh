"""校验结构化需求并导出中文 Markdown，不调用 API 或猜测需求。"""
import argparse
import json
from pathlib import Path
import re


class ContractError(ValueError):
    """表示需求契约缺失、类型错误或引用不一致。"""


def text(value, label):
    """拒绝空白内容，避免空标题被误认为完整需求。"""
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{label} 必须是非空文本")
    return value.strip()


def strings(value, label):
    if not isinstance(value, list):
        raise ContractError(f"{label} 必须是数组")
    for item in value:
        text(item, label)
    return value


def render(data):
    """先完整校验，再渲染，保证失败输入不会写出半份文档。"""
    if not isinstance(data, dict):
        raise ContractError("需求根节点必须是对象")
    for key in ("项目名称", "一句话描述", "目标用户", "要解决的问题"):
        text(data.get(key), key)
    for key in ("不做的功能", "用户流程", "技术约束", "风险", "待确认事项"):
        strings(data.get(key), key)
    if not data["用户流程"]:
        raise ContractError("至少需要一条用户流程")
    features = data.get("核心功能")
    criteria = data.get("成功标准")
    if not isinstance(features, list) or not features or not isinstance(criteria, list) or not criteria:
        raise ContractError("核心功能和成功标准必须是非空数组")
    feature_ids = set()
    for feature in features:
        if not isinstance(feature, dict):
            raise ContractError("功能必须是对象")
        fid = text(feature.get("编号"), "功能编号")
        if not re.fullmatch(r"F-\d{3}", fid) or fid in feature_ids:
            raise ContractError("功能编号应为唯一的 F-001 格式")
        feature_ids.add(fid)
        if feature.get("优先级") not in ("P0", "P1", "P2"):
            raise ContractError("优先级必须为 P0、P1 或 P2")
        for key in ("名称", "来源", "输入", "规则", "输出"):
            text(feature.get(key), key)
    covered = set()
    criterion_ids = set()
    for criterion in criteria:
        if not isinstance(criterion, dict):
            raise ContractError("验收项必须是对象")
        aid = text(criterion.get("编号"), "验收编号")
        if not re.fullmatch(r"A-\d{3}", aid) or aid in criterion_ids:
            raise ContractError("验收编号应为唯一的 A-001 格式")
        criterion_ids.add(aid)
        fid = text(criterion.get("功能编号"), "关联功能编号")
        if fid not in feature_ids:
            raise ContractError(f"验收项引用了不存在的功能：{fid}")
        covered.add(fid)
        for key in ("前置条件", "动作", "预期结果"):
            text(criterion.get(key), key)
    if covered != feature_ids:
        raise ContractError("每个功能至少需要一个验收项")

    # 保留用户文本但转义 HTML，避免被浏览器当成标签执行。
    def safe(value):
        return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    lines = [f"# {safe(data['项目名称'])}：需求分析", "", "状态：草稿，尚未代表用户确认或业务验证。", ""]
    for key in ("一句话描述", "目标用户", "要解决的问题"):
        lines += [f"## {key}", "", safe(data[key]), ""]
    lines += ["## 核心功能", ""]
    for feature in features:
        lines += [f"### {feature['编号']} {safe(feature['名称'])}（{feature['优先级']}）", ""]
        lines += [f"- {key}：{safe(feature[key])}" for key in ("来源", "输入", "规则", "输出")]
        lines += [""]
    for key in ("不做的功能", "用户流程", "技术约束"):
        lines += [f"## {key}", ""] + [f"- {safe(item)}" for item in data[key]] + [""]
    lines += ["## 成功标准", ""]
    for criterion in criteria:
        lines += [f"### {criterion['编号']} → {criterion['功能编号']}", ""]
        lines += [f"- {key}：{safe(criterion[key])}" for key in ("前置条件", "动作", "预期结果")]
        lines += [""]
    for key in ("风险", "待确认事项"):
        lines += [f"## {key}", ""] + [f"- {safe(item)}" for item in data[key]] + [""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="UTF-8 JSON 需求文件")
    parser.add_argument("output", help="新的 Markdown 文件")
    args = parser.parse_args()
    try:
        path = Path(args.input)
        if path.is_symlink():
            raise ContractError("不读取符号链接")
        content = render(json.loads(path.read_text(encoding="utf-8-sig")))
        # 独占创建，避免覆盖已确认的需求文档。
        with Path(args.output).open("x", encoding="utf-8") as stream:
            stream.write(content)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"需求导出失败：{exc}\n")


if __name__ == "__main__":
    main()
