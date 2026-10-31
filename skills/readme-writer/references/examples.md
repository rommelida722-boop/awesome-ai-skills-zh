# 示例与边界

成功：对 examples/demo 运行脚本，可提取 demo-calculator 名称和项目描述，生成含 Overview、Installation、Usage 的结构草稿。

失败：没有 pyproject.toml、缺少 project.name 或 TOML 无法解析时返回退出码 2，不生成输出；目标文件存在时退出码 2，保留原文件。

适用：Python 3.11 及以上，采用 PEP 621 元数据的 Python 项目。CLI 仅生成结构草稿；其他语言或完整英文说明需要 Agent 阅读实际项目后编写。脚本不会翻译描述，不会验证项目安装或测试。

自动化案例见 tests/test_readme.py，覆盖正常提取及三类失败。人工验收：让 Codex 为 demo 编写双语说明，检查是否承认没有安装入口、不虚构测试命令、保留原文档。这些 Agent 行为尚未自动评测。
