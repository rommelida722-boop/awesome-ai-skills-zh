# 契约格式与边界

完整输入见 examples/demo/cases.json；正常加法、零值、正负抵消及类型错误构成四个可运行案例。运行命令见根 README。

成功：四个契约生成四个 pytest 测试项。失败：少于三个案例、缺少目标函数、同时给 expected 与 raises、非法模块名均拒绝。异常仅支持 ValueError、TypeError、ZeroDivisionError、IndexError、KeyError。

测试见 tests/test_tools.py。源码只用于确认函数存在，不证明契约正确。参数数量错误会在 pytest 运行时暴露；需在生成前人工核对。不要运行来源不明项目的生成测试，因为 import 会执行项目代码。

有限浮点值可作为 JSON 数据；非有限值及数值溢出为无穷大时拒绝。实际平均值函数评测见 examples/evaluation/average-cases.json，包含正常、零值、负数和异常案例，并验证错误实现会失败。
