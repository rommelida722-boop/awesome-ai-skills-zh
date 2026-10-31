# 四个 Skill 的实际试用报告

评测日期：2026-10-31。环境：Windows、Python 3.12.9、pytest 9.1.1。

## 结论

这些 Skill 对明确范围内的任务有帮助，但不能将四个辅助脚本描述为四个独立的通用 AI 工具。测试生成器与需求导出器要求人工或 Agent 先提供正确契约；README 脚本仅解决起草结构的问题。

本轮为维护者在当前 Codex 会话中的定向试用与自动测试，不是独立模型盲测，也没有安装前后的对照实验，不能据此量化 Skill 对模型的提升幅度或自动触发准确率。

| Skill | 实际任务与证据 | 判断与局限 |
| --- | --- | --- |
| readme-writer | CLI 对 demo 生成文件，核对项目名称、描述，检查未编造安装命令与测试通过记录 | 对结构起草有效；脚本没有生成完整双语正文，本轮未证明完整双语写作效果 |
| python-code-reviewer | CLI 命中 review_bad.py 的三类问题；执行可信样本的两次调用，确认默认列表跨调用污染；见 review_findings.md | 对三条规则有效，能定位实际缺陷；纯业务计算错误仍会漏报 |
| pytest-generator | 根据 average-cases.json 生成测试，正确实现的六项测试通过；将平均值改成总和后测试失败 | 能覆盖正常值、零值、负数、空列表、布尔值及字符串，能发现业务错误；正确答案仍须来自需求 |
| requirements-analyst | 按 Skill 对原始想法和冲突场景形成 requirements-analysis.md；另实际导出结构化需求并检查范围、待确认项及验收追踪保留 | 对需求整理有帮助；语义部分为维护者按流程自查，脚本本身不判断矛盾是否解决或需求是否合理 |

## 新发现并修复的缺陷

生成器原先允许极大浮点数解析成无穷大，随后生成含未定义 inf 的 Python 测试。已增加递归有限值检查，覆盖嵌套的 inf、-inf、nan。非对象契约也改为清晰拒绝。

## 自动化证据

运行 `python -m unittest discover -s tests -v`：31 项通过。其中 tests/test_acceptance.py 的四个真实 CLI 场景覆盖四个 Skill；正确实现通过、错误实现失败的变异检查实际执行，没有把预期结果写成运行结果。

运行 `python scripts/validate.py`：四个 Skill 的结构、引用和 Python 语法校验通过。

Skill Creator 的 quick_validate.py 对四个 Skill 分别校验。Windows 下通过 Python 的 UTF-8 模式读取中文文件。

## 复现与后续评测

查看 examples/evaluation 中原始输入、函数与契约；从仓库根目录运行全部测试即可复现脚本试用。review_findings.md 和 requirements-analysis.md 是本轮人工使用产物，不是自动评分结果。

后续需在新的 Codex 聊天中分别安装及不安装 Skill 重复相同任务，比较事实错误、遗漏、修改次数和任务成功率；尤其补测完整双语 README、需求模糊和冲突场景。当前不声称这些盲测已完成。

GitHub Actions 的 Python 3.11—3.13 结果以仓库实际运行记录为准；此文只证明上述本地环境结果。

## 发布后的远程验证

公开仓库已创建并推送。GitHub Actions 在 Ubuntu 上的 Python 3.11、3.12、3.13 三组全部成功：[实际运行记录](https://github.com/rommelida722-boop/awesome-ai-skills-zh/actions/runs/41190109838)。这补充了跨版本脚本与自动测试证据，不等于跨模型行为验证。
