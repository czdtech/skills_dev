#!/usr/bin/env python3
"""
Fibonacci 数列函数模块

这个模块提供了计算 Fibonacci 数列的函数，使用迭代法实现以避免递归带来的性能问题。
"""


def fibonacci(n: int) -> int:
    """
    计算第 n 个 Fibonacci 数（使用迭代法）。
    
    Fibonacci 数列定义：
    - F(0) = 0
    - F(1) = 1
    - F(n) = F(n-1) + F(n-2) (n >= 2)
    
    Args:
        n: 要计算的 Fibonacci 数的索引（必须为非负整数）
    
    Returns:
        第 n 个 Fibonacci 数的值
    
    Raises:
        ValueError: 当 n 为负数时
    
    Examples:
        >>> fibonacci(0)
        0
        >>> fibonacci(1)
        1
        >>> fibonacci(5)
        5
        >>> fibonacci(10)
        55
    """
    if n < 0:
        raise ValueError("n must be a non-negative integer")
    
    # 处理边界情况
    if n == 0:
        return 0
    if n == 1:
        return 1
    
    # 使用迭代法计算
    # 初始化前两个值
    a, b = 0, 1
    
    # 迭代计算直到第 n 个数
    for _ in range(2, n + 1):
        a, b = b, a + b
    
    return b


def fibonacci_sequence(length: int) -> list[int]:
    """
    生成指定长度的 Fibonacci 数列。
    
    Args:
        length: 数列的长度（必须为非负整数）
    
    Returns:
        包含指定长度 Fibonacci 数列的列表
    
    Raises:
        ValueError: 当 length 为负数时
    
    Examples:
        >>> fibonacci_sequence(5)
        [0, 1, 1, 2, 3]
        >>> fibonacci_sequence(8)
        [0, 1, 1, 2, 3, 5, 8, 13]
    """
    if length < 0:
        raise ValueError("length must be a non-negative integer")
    
    if length == 0:
        return []
    elif length == 1:
        return [0]
    
    # 第一个数为 0
    sequence = [0, 1]
    
    # 生成剩余的数
    for i in range(2, length):
        sequence.append(sequence[i-1] + sequence[i-2])
    
    return sequence[:length]


def main():
    """主函数，用于命令行执行。"""
    print("Fibonacci 数列计算器")
    print("-" * 30)
    
    # 测试单个数值的计算
    test_values = [0, 1, 5, 10, 15]
    print("\n单个 Fibonacci 数计算：")
    for n in test_values:
        print(f"F({n}) = {fibonacci(n)}")
    
    # 测试数列生成
    print("\nFibonacci 数列生成：")
    for length in [5, 10]:
        sequence = fibonacci_sequence(length)
        print(f"前 {length} 个数: {sequence}")


if __name__ == "__main__":
    main()
