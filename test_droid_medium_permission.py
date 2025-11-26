#!/usr/bin/env python3
"""
测试文件：用于验证medium权限级别的功能
创建一个简单的fibonacci函数并包含测试用例
"""

def fibonacci(n):
    """
    计算斐波那契数列的第n项
    
    Args:
        n (int): 要计算的位置，n >= 0
        
    Returns:
        int: 斐波那契数列第n项的值
    """
    if n < 0:
        raise ValueError("位置n必须为非负整数")
    elif n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        # 使用迭代方式计算，避免递归深度问题
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b


def fibonacci_sequence(length):
    """
    生成斐波那契数列的前n项
    
    Args:
        length (int): 要生成的序列长度
        
    Returns:
        list: 包含斐波那契数列的列表
    """
    if length <= 0:
        return []
    elif length == 1:
        return [0]
    elif length == 2:
        return [0, 1]
    
    sequence = [0, 1]
    for i in range(2, length):
        sequence.append(fibonacci(i))
    
    return sequence


def run_tests():
    """运行所有测试用例"""
    print("开始运行测试用例...")
    
    # 测试基本fibonacci计算
    print("\n=== 测试基本fibonacci函数 ===")
    
    test_cases = [
        (0, 0),
        (1, 1),
        (2, 1),
        (3, 2),
        (4, 3),
        (5, 5),
        (6, 8),
        (7, 13),
        (8, 21),
        (9, 34),
        (10, 55)
    ]
    
    all_passed = True
    for n, expected in test_cases:
        try:
            result = fibonacci(n)
            if result == expected:
                print(f"✓ fibonacci({n}) = {result}")
            else:
                print(f"✗ fibonacci({n}) = {result}, 期望 {expected}")
                all_passed = False
        except Exception as e:
            print(f"✗ fibonacci({n}) 出现异常: {e}")
            all_passed = False
    
    # 测试错误情况
    print("\n=== 测试错误处理 ===")
    try:
        fibonacci(-1)
        print("✗ 应该抛出ValueError")
        all_passed = False
    except ValueError as e:
        print(f"✓ 正确处理负数输入: {e}")
    except Exception as e:
        print(f"✗ 异常类型不正确: {e}")
        all_passed = False
    
    # 测试数列生成
    print("\n=== 测试斐波那契数列生成 ===")
    test_sequences = [
        (0, []),
        (1, [0]),
        (3, [0, 1, 1]),
        (5, [0, 1, 1, 2, 3]),
        (7, [0, 1, 1, 2, 3, 5, 8])
    ]
    
    for length, expected in test_sequences:
        try:
            result = fibonacci_sequence(length)
            if result == expected:
                print(f"✓ fibonacci_sequence({length}) = {result}")
            else:
                print(f"✗ fibonacci_sequence({length}) = {result}, 期望 {expected}")
                all_passed = False
        except Exception as e:
            print(f"✗ fibonacci_sequence({length}) 出现异常: {e}")
            all_passed = False
    
    # 测试性能（较大的数字）
    print("\n=== 测试性能 ===")
    large_n = 30
    try:
        result = fibonacci(large_n)
        print(f"✓ fibonacci({large_n}) = {result} (性能测试通过)")
    except Exception as e:
        print(f"✗ 性能测试失败: {e}")
        all_passed = False
    
    # 总结
    print(f"\n=== 测试结果 ===")
    if all_passed:
        print("🎉 所有测试用例通过！")
        return True
    else:
        print("❌ 部分测试用例失败！")
        return False


if __name__ == "__main__":
    """主程序入口"""
    print("Droid Medium Permission 权限测试")
    print("=" * 40)
    
    success = run_tests()
    
    print("\n" + "=" * 40)
    if success:
        print("测试成功完成！文件可以正常执行。")
    else:
        print("测试失败！请检查代码。")
    
    exit(0 if success else 1)
