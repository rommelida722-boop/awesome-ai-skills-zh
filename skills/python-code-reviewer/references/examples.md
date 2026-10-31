# 示例与边界

成功：examples/demo/calculator.py 返回空数组和退出码 0。
发现问题：examples/review_bad.py 报告可变默认参数、裸 except 和吞掉异常，附行号，退出码 1。
失败：语法损坏、文件不存在或非 .py 输入返回退出码 2。

测试见 tests/test_tools.py。当前规则不覆盖可变构造器调用、类型推断、跨模块数据流、资源泄漏和全部 PEP 8。人工项目审查仍须读取上下文，不将提示当成确定漏洞。
