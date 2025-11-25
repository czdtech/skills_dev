#!/usr/bin/env python3
"""
Codex Advisor Skill - Verification Script
验证修复的有效性
"""
import json
import urllib.request
import sys

BRIDGE_URL = "http://localhost:3001/analyze"

def test_empty_problem():
    """测试空 problem 验证"""
    print("测试 1: 空 Problem 验证")
    print("-" * 50)
    
    payload = {
        "problem": "",  # 空
        "context": "This should be rejected"
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
            
            if result.get("error") == "validation_error":
                print("✅ 成功：空 problem 被正确拒绝")
                print(f"   错误消息: {result.get('message')}")
                return True
            else:
                print("❌ 失败：空 problem 未被拒绝")
                return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_whitespace_problem():
    """测试纯空白 problem"""
    print("\n测试 2: 纯空白 Problem 验证")
    print("-" * 50)
    
    payload = {
        "problem": "   \n\t  ",  # 仅空白字符
        "context": "This should be rejected"
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
            
            if result.get("error") == "validation_error":
                print("✅ 成功：纯空白 problem 被正确拒绝")
                return True
            else:
                print("❌ 失败：纯空白 problem 未被拒绝")
                return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_valid_request():
    """测试正常请求仍然工作"""
    print("\n测试 3: 正常请求验证")
    print("-" * 50)
    
    payload = {
        "problem": "Should we use PostgreSQL or MongoDB for storing user session data?",
        "context": "E-commerce application with 100k daily active users. Current stack: Node.js backend, React frontend. Need to store: user preferences, shopping cart (max 100 items), last 10 visited pages.",
        "candidate_plans": [
            {
                "name": "PostgreSQL",
                "description": "Use existing PostgreSQL database with a dedicated sessions table",
                "pros": ["ACID guarantees", "Existing infrastructure", "Good query capabilities"],
                "cons": ["May have lower performance than NoSQL", "Schema changes need migrations"]
            },
            {
                "name": "MongoDB",
                "description": "Deploy MongoDB for flexible session storage",
                "pros": ["High write performance", "Flexible schema", "Easy to scale horizontally"],
                "cons": ["New infrastructure to maintain", "Less strict consistency"]
            }
        ],
        "focus_areas": ["performance", "operational_complexity", "cost"]
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        BRIDGE_URL, 
        data=data, 
        headers={"Content-Type": "application/json"}
    )
    
    try:
        print("发送正常请求...")
        print(f"问题: {payload['problem'][:80]}...")
        with urllib.request.urlopen(req, timeout=300) as response:  # 5 分钟超时
            result = json.loads(response.read().decode("utf-8"))
            
            if result.get("error"):
                print(f"❌ 失败：正常请求返回错误: {result.get('message')}")
                return False
            else:
                print("✅ 成功：正常请求工作正常")
                # 检查返回的结构
                keys = list(result.keys())
                print(f"   返回字段: {keys}")
                return True
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def main():
    print("=" * 50)
    print("Codex Advisor Skill - 修复验证")
    print("=" * 50)
    
    results = []
    
    # 测试 1: 空 problem
    results.append(test_empty_problem())
    
    # 测试 2: 纯空白
    results.append(test_whitespace_problem())
    
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
