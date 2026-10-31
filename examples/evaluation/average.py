"""可信评测样本：计算整数列表的平均值。"""
def average(values):
    """空列表报 ValueError；非整数或布尔值报 TypeError。"""
    if not values:
        raise ValueError("列表不能为空")
    if any(type(value) is not int for value in values):
        raise TypeError("只接受整数")
    return sum(values) / len(values)
