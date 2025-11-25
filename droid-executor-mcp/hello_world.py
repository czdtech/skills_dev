#!/usr/bin/env python3
"""
简单的 Hello World 函数模块

这个模块提供了一个简单的 Hello World 函数，用于演示基本功能。
"""


def hello_world(name: str = "World") -> str:
    """
    返回 Hello World 问候语。
    
    Args:
        name: 要问候的名字，默认为 "World"
    
    Returns:
        格式化的问候语字符串
    """
    return f"Hello, {name}!"


def main():
    """主函数，用于命令行执行。"""
    # 默认问候
    print(hello_world())
    
    # 问候特定名字
    print(hello_world("Claude"))
    print(hello_world("Python"))


if __name__ == "__main__":
    main()
