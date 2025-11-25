#!/usr/bin/env python3
"""
测试运行器

运行所有单元测试并生成测试报告
"""

import unittest
import sys
import os
from io import StringIO

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_all_tests():
    """运行所有单元测试"""
    
    # 导入所有测试模块
    from tests.test_fibonacci import TestFibonacci, TestFibonacciEdgeCases
    from tests.test_hello_world import TestHelloWorld, TestHelloWorldEdgeCases
    from tests.test_mcp_server import TestExecuteDroidTask, TestExecuteDroidTaskEdgeCases
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestFibonacci))
    suite.addTests(loader.loadTestsFromTestCase(TestFibonacciEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestHelloWorld))
    suite.addTests(loader.loadTestsFromTestCase(TestHelloWorldEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestExecuteDroidTask))
    suite.addTests(loader.loadTestsFromTestCase(TestExecuteDroidTaskEdgeCases))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出测试结果统计
    print("\n" + "="*60)
    print("测试结果统计")
    print("="*60)
    print(f"运行测试数量: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('Exception:')[-1].strip()}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
