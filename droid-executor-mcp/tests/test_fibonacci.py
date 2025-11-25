#!/usr/bin/env python3
"""
斐波那契数列功能单元测试

测试 fibonacci.py 模块中的所有函数，包括：
- fibonacci(n) - 计算第 n 个斐波那契数
- fibonacci_sequence(length) - 生成指定长度的斐波那契数列
"""

import unittest
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fibonacci import fibonacci, fibonacci_sequence


class TestFibonacci(unittest.TestCase):
    """测试斐波那契数计算功能"""

    def test_fibonacci_basic_cases(self):
        """测试基本的斐波那契数计算"""
        # 测试前几个已知的斐波那契数
        self.assertEqual(fibonacci(0), 0)
        self.assertEqual(fibonacci(1), 1)
        self.assertEqual(fibonacci(2), 1)
        self.assertEqual(fibonacci(3), 2)
        self.assertEqual(fibonacci(4), 3)
        self.assertEqual(fibonacci(5), 5)
        self.assertEqual(fibonacci(6), 8)
        self.assertEqual(fibonacci(7), 13)
        self.assertEqual(fibonacci(8), 21)
        self.assertEqual(fibonacci(9), 34)
        self.assertEqual(fibonacci(10), 55)

    def test_fibonacci_larger_values(self):
        """测试更大的斐波那契数"""
        # 测试一些更大的值
        self.assertEqual(fibonacci(15), 610)
        self.assertEqual(fibonacci(20), 6765)
        self.assertEqual(fibonacci(30), 832040)

    def test_fibonacci_negative_input(self):
        """测试负数输入应抛出异常"""
        with self.assertRaises(ValueError) as context:
            fibonacci(-1)
        self.assertIn("non-negative integer", str(context.exception))

        with self.assertRaises(ValueError) as context:
            fibonacci(-10)
        self.assertIn("non-negative integer", str(context.exception))

    def test_fibonacci_sequence_basic_cases(self):
        """测试基本的斐波那契数列生成"""
        # 测试空数列
        self.assertEqual(fibonacci_sequence(0), [])
        
        # 测试长度为 1 的数列
        self.assertEqual(fibonacci_sequence(1), [0])
        
        # 测试长度为 2 的数列
        self.assertEqual(fibonacci_sequence(2), [0, 1])
        
        # 测试长度为 5 的数列
        self.assertEqual(fibonacci_sequence(5), [0, 1, 1, 2, 3])
        
        # 测试长度为 8 的数列
        self.assertEqual(fibonacci_sequence(8), [0, 1, 1, 2, 3, 5, 8, 13])

    def test_fibonacci_sequence_larger_values(self):
        """测试生成较长的斐波那契数列"""
        sequence_10 = fibonacci_sequence(10)
        expected_10 = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
        self.assertEqual(sequence_10, expected_10)
        
        # 验证最后一个数与对应的 fibonacci 函数结果一致
        self.assertEqual(sequence_10[-1], fibonacci(9))

    def test_fibonacci_sequence_negative_input(self):
        """测试负数长度应抛出异常"""
        with self.assertRaises(ValueError) as context:
            fibonacci_sequence(-1)
        self.assertIn("non-negative integer", str(context.exception))

        with self.assertRaises(ValueError) as context:
            fibonacci_sequence(-5)
        self.assertIn("non-negative integer", str(context.exception))

    def test_fibonacci_sequence_consistency(self):
        """测试数列生成与单个数计算的一致性"""
        # 生成包含前 10 个数的数列
        sequence = fibonacci_sequence(10)
        
        # 验证数列中的每个数与对应的 fibonacci 函数结果一致
        for i, value in enumerate(sequence):
            self.assertEqual(value, fibonacci(i), 
                           f"fibonacci_sequence({i}) 的第 {i} 个元素应该等于 fibonacci({i})")

    def test_fibonacci_type_annotations(self):
        """测试函数类型注解"""
        # 测试返回类型（虽然 Python 不会强制检查，但可以验证函数的健壮性）
        result = fibonacci(5)
        self.assertIsInstance(result, int)
        
        sequence = fibonacci_sequence(5)
        self.assertIsInstance(sequence, list)
        for item in sequence:
            self.assertIsInstance(item, int)


class TestFibonacciEdgeCases(unittest.TestCase):
    """测试斐波那契函数的边界情况"""

    def test_fibonacci_very_large_number(self):
        """测试非常大的数的计算（但不要太大以免运行时间过长）"""
        # 测试一个较大的数，确保算法不会溢出或出错
        result = fibonacci(50)
        # 这个值是正确的（来自已知的斐波那契数列）
        expected = 12586269025
        self.assertEqual(result, expected)

    def test_fibonacci_sequence_length_very_large(self):
        """测试生成长度较大的数列"""
        # 生成一个包含 100 个数的数列
        sequence = fibonacci_sequence(100)
        self.assertEqual(len(sequence), 100)
        
        # 验证最后几个数是正确的
        # F(95), F(96), F(97), F(98), F(99)
        expected_last_few = [31940434634990099905, 51680708854858323072, 83621143489848422977]
        self.assertEqual(sequence[-3:], expected_last_few)


if __name__ == '__main__':
    unittest.main()
