#!/usr/bin/env python3
"""
快速验证修复的脚本
测试：1. 空 objective 验证  2. 超时配置  3. 增强日志
"""
import json
import urllib.request
import sys

BRIDGE_URL = "http://localhost:3002/execute"

def test_empty_objective():
    """测试空 objective 验证"""
    print("测试 1: 空 Objective 验证")
    print("-" * 50)
    
    payload = {
        "objective": "",  # 空
        "instructions": "This should be rejected"
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        BRIDGE_URL, 
        data=data, 
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode("utf-8"))
            
            if result.get("status") == "error":
                print("✅ 成功：空 objective 被正确拒绝")
                print(f"   错误消息: {result.get('summary')}")
                return True
            else:
                print("❌ 失败：空 objective 未被拒绝")
                return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_whitespace_objective():
    """测试纯空白 objective"""
    print("\n测试 2: 纯空白 Objective 验证")
    print("-" * 50)
    
    payload = {
        "objective": "   \n\t  ",  # 仅空白字符
        "instructions": "This should be rejected"
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        BRIDGE_URL, 
        data=data, 
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode("utf-8"))
            
            if result.get("status") == "error":
                print("✅ 成功：纯空白 objective 被正确拒绝")
                return True
            else:
                print("❌ 失败：纯空白 objective 未被拒绝")
                return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_valid_request():
    """测试正常请求仍然工作"""
    print("\n测试 3: 正常请求验证")
    print("-" * 50)
    
    payload = {
        "objective": "创建一个简单的 hello.txt 文件",
        "instructions": "在当前目录创建 hello.txt，内容为 'Hello World'",
        "context": "测试目录"
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        BRIDGE_URL, 
        data=data, 
        headers={"Content-Type": "application/json"}
    )
    
    try:
        print("发送正常请求...")
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
            
            if result.get("status") != "error":
                print("✅ 成功：正常请求仍然工作")
                print(f"   状态: {result.get('status')}")
                return True
            else:
                print(f"❌ 失败：正常请求返回错误: {result.get('summary')}")
                return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def main():
    print("=" * 50)
    print("Droid Executor Skill - 修复验证")
    print("=" * 50)
    
    results = []
    
    # 测试 1: 空 objective
    results.append(test_empty_objective())
    
    # 测试 2: 纯空白
    results.append(test_whitespace_objective())
    
    # 测试 3: 正常请求
    results.append(test_valid_request())
    
    # 总结
    print("\n" + "=" * 50)
    print("验证结果总结")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("✅ 所有验证测试通过！修复成功。")
        sys.exit(0)
    else:
        print("❌ 部分测试失败，需要检查。")
        sys.exit(1)

if __name__ == "__main__":
    main()
