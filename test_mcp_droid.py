#!/usr/bin/env python3
"""
Droid Executor计算器测试文件
用于验证Droid Executor的代码生成和测试能力

该文件包含：
1. Calculator类：实现基本的数学运算
2. CalculatorTest类：使用unittest验证计算器功能
"""

import unittest


class Calculator:
    """简单的计算器类，支持基本的数学运算"""
    
    def __init__(self):
        """初始化计算器"""
        self.history = []
    
    def add(self, a, b):
        """加法运算
        
        Args:
            a (float): 第一个数字
            b (float): 第二个数字
            
        Returns:
            float: 两个数字的和
        """
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def subtract(self, a, b):
        """减法运算
        
        Args:
            a (float): 被减数
            b (float): 减数
            
        Returns:
            float: 两个数字的差
        """
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result
    
    def multiply(self, a, b):
        """乘法运算
        
        Args:
            a (float): 第一个数字
            b (float): 第二个数字
            
        Returns:
            float: 两个数字的乘积
        """
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result
    
    def divide(self, a, b):
        """除法运算
        
        Args:
            a (float): 被除数
            b (float): 除数
            
        Returns:
            float: 两个数字的商
            
        Raises:
            ValueError: 当除数为0时抛出异常
        """
        if b == 0:
            raise ValueError("除数不能为零")
        result = a / b
        self.history.append(f"{a} / {b} = {result}")
        return result
    
    def get_history(self):
        """获取计算历史记录
        
        Returns:
            list: 历史计算记录列表
        """
        return self.history
    
    def clear_history(self):
        """清除计算历史记录"""
        self.history.clear()


class CalculatorTest(unittest.TestCase):
    """计算器测试类，验证所有计算器功能"""
    
    def setUp(self):
        """每个测试方法执行前的准备工作"""
        self.calc = Calculator()
    
    def test_add_basic(self):
        """测试基本加法功能"""
        result = self.calc.add(2, 3)
        self.assertEqual(result, 5, "2 + 3 应该等于 5")
        
        result = self.calc.add(-1, 1)
        self.assertEqual(result, 0, "-1 + 1 应该等于 0")
        
        result = self.calc.add(0, 0)
        self.assertEqual(result, 0, "0 + 0 应该等于 0")
    
    def test_subtract_basic(self):
        """测试基本减法功能"""
        result = self.calc.subtract(5, 3)
        self.assertEqual(result, 2, "5 - 3 应该等于 2")
        
        result = self.calc.subtract(0, 5)
        self.assertEqual(result, -5, "0 - 5 应该等于 -5")
    
    def test_multiply_basic(self):
        """测试基本乘法功能"""
        result = self.calc.multiply(4, 3)
        self.assertEqual(result, 12, "4 * 3 应该等于 12")
        
        result = self.calc.multiply(-2, 3)
        self.assertEqual(result, -6, "-2 * 3 应该等于 -6")
        
        result = self.calc.multiply(5, 0)
        self.assertEqual(result, 0, "5 * 0 应该等于 0")
    
    def test_divide_basic(self):
        """测试基本除法功能"""
        result = self.calc.divide(6, 2)
        self.assertEqual(result, 3, "6 / 2 应该等于 3")
        
        result = self.calc.divide(7, 2)
        self.assertEqual(result, 3.5, "7 / 2 应该等于 3.5")
        
        result = self.calc.divide(-10, 2)
        self.assertEqual(result, -5, "-10 / 2 应该等于 -5")
    
    def test_divide_by_zero(self):
        """测试除零异常处理"""
        with self.assertRaises(ValueError):
            self.calc.divide(5, 0)
    
    def test_history_tracking(self):
        """测试计算历史记录功能"""
        self.calc.add(2, 3)
        self.calc.multiply(4, 5)
        
        history = self.calc.get_history()
        self.assertEqual(len(history), 2, "应该记录两次计算")
        self.assertIn("2 + 3 = 5", history)
        self.assertIn("4 * 5 = 20", history)
    
    def test_history_clear(self):
        """测试清除历史记录功能"""
        self.calc.add(1, 1)
        self.calc.clear_history()
        
        history = self.calc.get_history()
        self.assertEqual(len(history), 0, "历史记录应该被清除")
    
    def test_complex_operations(self):
        """测试复合运算"""
        # 计算 (2 + 3) * 4 - 6 / 2
        step1 = self.calc.add(2, 3)  # 5
        step2 = self.calc.multiply(step1, 4)  # 20
        step3 = self.calc.divide(6, 2)  # 3
        result = self.calc.subtract(step2, step3)  # 17
        
        self.assertEqual(result, 17, "(2 + 3) * 4 - 6 / 2 应该等于 17")


def main():
    """主函数：运行所有测试"""
    print("=" * 50)
    print("Droid Executor计算器测试")
    print("=" * 50)
    print()
    
    # 创建测试套件
    test_suite = unittest.TestLoader().loadTestsFromTestCase(CalculatorTest)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print()
    print("=" * 50)
    print("测试结果汇总:")
    print(f"运行测试: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("✅ 所有测试通过！Droid Executor功能正常。")
    else:
        print("❌ 存在测试失败或错误。")
    
    print("=" * 50)
    
    # 演示计算器使用
    print("\n计算器演示:")
    print("-" * 30)
    demo_calc = Calculator()
    
    demos = [
        ("演示加法", lambda: demo_calc.add(15, 27)),
        ("演示减法", lambda: demo_calc.subtract(100, 38)),
        ("演示乘法", lambda: demo_calc.multiply(7, 8)),
        ("演示除法", lambda: demo_calc.divide(144, 12)),
    ]
    
    for desc, operation in demos:
        try:
            result = operation()
            print(f"{desc}: {result}")
        except Exception as e:
            print(f"{desc}: 错误 - {e}")
    
    print(f"\n计算历史记录 ({len(demo_calc.get_history())} 条):")
    for record in demo_calc.get_history():
        print(f"  • {record}")


if __name__ == "__main__":
    main()
