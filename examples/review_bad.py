"""故意保留缺陷，作为审查失败示例。"""
def collect(value, items=[]):
    """此处默认列表会跨调用共享。"""
    try:
        items.append(value)
    except:
        pass
    return items
