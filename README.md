# awesome-ai-skills-zh

帮助中文开发者通过可独立安装的 AI Skills 编写需求分析与项目文档、审查 Python 代码、生成基于业务契约的 pytest 测试。

四个 Skill 均包含中文指令、可运行脚本、适用边界与测试。基础脚本离线运行，无需 API Key；它们提供范围明确的自动化辅助，不等同于通用 AI 分析。

## 30 秒快速开始

需要 Python 3.11 或以上。在仓库根目录运行：

```sh
python scripts/validate.py
python skills/python-code-reviewer/scripts/run.py examples/demo/calculator.py
```

第二条输出 `[]`，退出码 0，表示三类静态规则未发现问题。

## 可复现示例与安装

无需安装本项目即可运行脚本。执行测试需要免费的 pytest：

```sh
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python skills/readme-writer/scripts/run.py examples/demo README.generated.md
python skills/pytest-generator/scripts/run.py examples/demo/calculator.py examples/demo/cases.json examples/demo/test_generated.py
python -m pytest -q examples/demo/test_generated.py
```

README 草稿包含 demo-calculator 名称、描述和双语章节。测试生成示例包括普通加法、零值、正负抵消、非法类型四个测试项。两个生成命令拒绝覆盖已有文件：重复执行前请自行改用新输出路径。

审查的失败示例：

```sh
python skills/python-code-reviewer/scripts/run.py examples/review_bad.py
```

预期报告 `mutable-default`、`bare-except`、`swallowed-exception`，附文件与行号，退出码 **1**。这是示例成功发现问题，并非工具崩溃。输入文件缺失或格式错误返回 2。

## Skills 清单与适用场景

| Skill | Agent 使用场景 | 本地脚本边界 |
| --- | --- | --- |
| [requirements-analyst](skills/requirements-analyst/SKILL.md) | 将想法和访谈整理为需求分析与 PRD | 校验结构化需求、功能与验收引用，导出 Markdown |
| [readme-writer](skills/readme-writer/SKILL.md) | 分析项目并编写中英文 README | 读取 pyproject.toml，生成双语章节草稿，不翻译正文 |
| [python-code-reviewer](skills/python-code-reviewer/SKILL.md) | 审查项目维护性、潜在 Bug 与规范 | 单文件 AST，检查可变默认参数、裸 except 和吞掉异常 |
| [pytest-generator](skills/pytest-generator/SKILL.md) | 根据业务需求编写正常、边界与异常测试 | 根据 JSON 契约生成顶层同步函数的位置参数测试 |

## Codex 安装与使用教程

将所需 Skill 的整个目录复制到目标项目的 `.agents/skills/` 下，例如 `.agents/skills/readme-writer/SKILL.md`。保留 scripts 与 references。重新加载目标项目，在 Codex 中输入以下任一请求：

- `使用 $requirements-analyst 根据以下想法编写需求分析，区分事实和假设，给出 MVP 范围与可验证验收标准。`
- `使用 $readme-writer 分析当前项目，编写中文和英文 README，列出验证依据。`
- `使用 $python-code-reviewer 审查当前 Python 项目，按影响给出行号、触发条件及修复建议。`
- `使用 $pytest-generator 根据需求为 add 函数补充正常、边界及类型错误测试。`

脚本路径在 Skill 指令中相对于各 Skill 自身目录。Codex Agent 需要你自己的可用 Codex 环境；本项目不承诺 Agent 服务免费。不可信项目的生成测试不能直接运行，因为 Python import 会执行模块顶层代码。

## 标准目录

```text
skills/
  requirements-analyst/
  readme-writer/
  python-code-reviewer/
  pytest-generator/
    SKILL.md
    scripts/run.py
    references/examples.md
scripts/validate.py
tests/
examples/
.github/workflows/ci.yml
CONTRIBUTING.md
LICENSE
requirements-dev.txt
```

四个 Skill 采用相同结构，可单独复制，不依赖本仓库共享模块。

## 验证与 CI

最新本地结果：31 项测试通过，包含平均值函数的六个真实生成测试项，以及故意改错后测试失败的验证。详见 [实际试用报告](EVALUATION.md)。README 脚本仍仅生成结构草稿；当前不宣称完整双语写作已经通过实际评测。


自动测试覆盖元数据解析和失败保护、审查定位与退出码、契约拒绝、生成测试实际运行，并将被测加法故意改错，确认测试能失败。每个 Skill 至少三个测试，具体记录见 [验收报告](VALIDATION.md)。

GitHub Actions 在 Ubuntu 的 Python 3.11、3.12、3.13 上安装 pytest，运行结构校验和全套 unittest。本地检查通过不代表远程 CI 已通过；公开仓库首次推送后需查看 Actions 结果。Agent 指令质量仍需实际用户反馈，自动测试不证明所有模型的行为。

## 常见问题

- **为什么生成器需要预期结果？** 当前实现可能有 Bug，运行结果不能自动当正确答案。请从业务需求确认预期值。
- **为什么 README 仍需完善？** 元数据无法证明安装入口与功能，脚本只生成结构；完整双语内容由 Agent 基于实际项目补齐。
- **为什么没有发现问题？** 审查脚本只覆盖三类局部规则，不包含完整类型检查、PEP 8 或跨模块分析。
- **生成器支持异步、fixture 或浮点近似吗？** 本地脚本暂不支持，Agent 需按需求补充。不要把简单相等断言用于存在舍入误差的结果。
- **临时目录权限错误怎么办？** 把环境变量 TEMP 和 TMP 设置为可写目录后再运行测试。
- **会上传代码吗？** 本地脚本不联网。Agent 的数据处理取决于所用环境及设置。

## 贡献指南

参见 [贡献指南](CONTRIBUTING.md)。提交可复现输入、行为测试与边界说明；不要上传凭据、真实私有代码或个人数据。许可证为 [MIT](LICENSE)。

规范依据：[官方 Skills 文档](https://developers.openai.com/codex/skills/)，核对日期为 2026-10-31。SKILL.md 包含 name、description 元数据；项目校验器仅验证采用的规范子集，不冒充官方完整验证器。

## 需求分析示例

新增 Skill 依据用户提供的 course07-Prompt 课程方法重新整理，参见 [学习来源](skills/requirements-analyst/references/sources.md)。课程原文不随项目分发。

完整虚构输入见 [任务清单契约](examples/requirements/tasks.json)，实际导出结果见 [需求分析示例](examples/requirements/requirements.md)。从仓库根目录运行：

```sh
python skills/requirements-analyst/scripts/run.py examples/requirements/tasks.json requirements.generated.md
```

退出码 0 表示结构校验及导出完成。已有输出、字段缺失或验收引用失效时返回 2，不覆盖原文件。请使用新文件名重试。该脚本不自动理解一句话想法、不证明需求合理；自然语言分析使用 `$requirements-analyst`。人工行为测试案例见该 Skill 的 references/examples.md。
