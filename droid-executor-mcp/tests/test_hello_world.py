#!/usr/bin/env python3
"""
Hello World 功能单元测试

测试 hello_world.py 模块中的函数
"""

import unittest
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hello_world import hello_world


class TestHelloWorld(unittest.TestCase):
    """测试 Hello World 功能"""

    def test_hello_world_default(self):
        """测试默认参数的 Hello World 功能"""
        result = hello_world()
        expected = "Hello, World!"
        self.assertEqual(result, expected)

    def test_hello_world_custom_name(self):
        """测试自定义名字的问候"""
        # 测试单个名字
        result = hello_world("Alice")
        expected = "Hello, Alice!"
        self.assertEqual(result, expected)

        # 测试不同的名字
        names = ["Bob", "Charlie", "Diana", "Eve"]
        for name in names:
            result = hello_world(name)
            expected = f"Hello, {name}!"
            self.assertEqual(result, expected)

    def test_hello_world_empty_string(self):
        """测试空字符串作为名字"""
        result = hello_world("")
        expected = "Hello, !"
        self.assertEqual(result, expected)

    def test_hello_world_special_characters(self):
        """测试包含特殊字符的名字"""
        # 测试包含空格的名字
        result = hello_world("John Doe")
        expected = "Hello, John Doe!"
        self.assertEqual(result, expected)

        # 测试包含数字的名字
        result = hello_world("User123")
        expected = "Hello, User123!"
        self.assertEqual(result, expected)

        # 测试包含特殊符号的名字
        result = hello_world("John-Doe_2024")
        expected = "Hello, John-Doe_2024!"
        self.assertEqual(result, expected)

    def test_hello_world_unicode(self):
        """测试 Unicode 字符"""
        # 测试中文字符
        result = hello_world("张三")
        expected = "Hello, 张三!"
        self.assertEqual(result, expected)

        # 测试 emoji
        result = hello_world("😊")
        expected = "Hello, 😊!"
        self.assertEqual(result, expected)

    def test_hello_world_return_type(self):
        """测试返回值的类型"""
        result = hello_world()
        self.assertIsInstance(result, str)

    def test_hello_world_format(self):
        """测试返回值的格式"""
        result = hello_world("Test")
        
        # 验证返回值以 "Hello, " 开头
        self.assertTrue(result.startswith("Hello, "))
        
        # 验证返回值以 "!" 结尾
        self.assertTrue(result.endswith("!"))
        
        # 验证返回值包含给定的名字
        self.assertIn("Test", result)

    def test_hello_world_consistency(self):
        """测试函数的一致性"""
        name = "ConsistencyTest"
        result1 = hello_world(name)
        result2 = hello_world(name)
        
        # 多次调用应该返回相同结果
        self.assertEqual(result1, result2)


class TestHelloWorldEdgeCases(unittest.TestCase):
    """测试 Hello World 边界情况"""

    def test_hello_world_very_long_name(self):
        """测试非常长的名字"""
        long_name = "A" * 1000
        result = hello_world(long_name)
        expected = f"Hello, {long_name}!"
        self.assertEqual(result, expected)

    def test_hello_world_none_input(self):
        """测试 None 输入（应该引发异常）"""
        with self.assertRaises(TypeError):
            hello_world(None)

    def test_hello_world_numeric_input(self):
        """测试数字输入（应该被转换为字符串）"""
        result = hello_world(123)
        expected = "Hello, 123!"
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
