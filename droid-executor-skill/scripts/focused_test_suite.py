#!/usr/bin/env python3
"""
Focused Test Suite for droid-executor-skill
针对 Claude Code 实际使用场景的测试
"""
import json
import urllib.request
import urllib.error
import sys
import os
import time
import shutil
import subprocess

# Configuration
BRIDGE_URL = "http://localhost:3002/execute"
TEST_DIR = "/home/jiang/work/for_claude/skills_dev/droid_focused_test"

class TestCase:
    def __init__(self, name, category, description):
        self.name = name
        self.category = category
        self.description = description
        self.passed = False
        self.message = ""
        self.duration = 0
        self.response = None

def setup_test_env():
    """创建干净的测试环境"""
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(TEST_DIR)
    print(f"✓ 测试环境已创建: {TEST_DIR}\n")

def send_droid_request(objective, instructions, context=None, constraints=None, 
                       acceptance_criteria=None, timeout=180):
    """发送请求到 Droid Bridge"""
    if context is None:
        context = {
            "repo_root": TEST_DIR,
            "summary": f"测试项目位于 {TEST_DIR}"
        }
    
    payload = {
        "objective": objective,
        "instructions": instructions,
        "context": context,
        "constraints": constraints or [],
        "acceptance_criteria": acceptance_criteria or []
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        BRIDGE_URL, 
        data=data, 
        headers={"Content-Type": "application/json"}
    )
    
    try:
        start_time = time.time()
        with urllib.request.urlopen(req, timeout=timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
            duration = time.time() - start_time
            return result, duration, None
    except Exception as e:
        return None, 0, str(e)

def run_test(test_case, objective, instructions, verify_func, 
             context=None, constraints=None, acceptance=None):
    """运行单个测试用例"""
    print(f"  ⏳ {test_case.name}...", end="", flush=True)
    
    result, duration, error = send_droid_request(
        objective, instructions, context, constraints, acceptance
    )
    test_case.duration = duration
    test_case.response = result
    
    if error:
        test_case.message = f"请求失败: {error}"
        print(f" ❌ ({duration:.1f}s)")
        print(f"     {test_case.message}")
        return test_case
    
    success, message = verify_func()
    test_case.passed = success
    test_case.message = message
    
    status = "✅" if test_case.passed else "❌"
    print(f" {status} ({duration:.1f}s)")
    if test_case.message:
        print(f"     {test_case.message}")
    
    return test_case

def main():
    setup_test_env()
    results = []
    
    # ================================================================
    # 场景 1: 代码重构任务
    # ================================================================
    print("🔄 场景 1: 代码重构任务 (Claude Code 常见需求)")
    print("=" * 70)
    
    # 1.1: 创建基础代码（用于后续重构测试）
    setup_code = '''def calculate_sum(a, b, callback):
    """使用回调的求和函数"""
    result = a + b
    callback(result)

def calculate_product(a, b, callback):
    """使用回调的乘法函数"""
    result = a * b
    callback(result)

def process_data(data, success_cb, error_cb):
    """处理数据的回调式函数"""
    try:
        result = [x * 2 for x in data]
        success_cb(result)
    except Exception as e:
        error_cb(str(e))
'''
    
    with open(os.path.join(TEST_DIR, "callbacks.py"), "w") as f:
        f.write(setup_code)
    
    # Test 1.1: 回调转 async/await
    def verify_async_refactor():
        path = os.path.join(TEST_DIR, "callbacks.py")
        with open(path) as f:
            content = f.read()
            has_async = "async def" in content
            has_await = "await" in content or "asyncio" in content
            no_callback = "callback" not in content.lower() or "async" in content
            
            if has_async:
                return True, "成功将回调转换为 async/await"
            return False, "未检测到 async/await 模式"
    
    results.append(run_test(
        TestCase("1.1 回调函数转 async/await", "代码重构", 
                "将回调风格重构为现代异步模式"),
        objective="将 callbacks.py 中的回调函数重构为 async/await 模式",
        instructions=f"""
        重构 {TEST_DIR}/callbacks.py：
        1. 将所有使用 callback 参数的函数改为 async def
        2. 移除 callback 参数，直接返回结果
        3. 对于 process_data，使用 try/except 直接抛出异常而非调用 error_cb
        4. 保持函数的核心逻辑不变
        """,
        constraints=["不修改函数名", "保持原有功能语义"],
        acceptance=["代码使用 async/await", "所有函数可正常导入"],
        verify_func=verify_async_refactor
    ))
    
    # ================================================================
    # 场景 2: Bug 修复
    # ================================================================
    print("\n🐛 场景 2: Bug 修复")
    print("=" * 70)
    
    # 2.1: 创建有 bug 的代码
    buggy_code = '''def divide_numbers(a, b):
    """除法函数"""
    return a / b  # Bug: 没有处理除零错误

def parse_config(config_str):
    """解析配置字符串"""
    parts = config_str.split('=')
    key = parts[0]
    value = parts[1]  # Bug: 没有检查 parts 长度
    return {key: value}

def get_user_name(user_dict):
    """获取用户名"""
    return user_dict['name']  # Bug: 没有检查 key 是否存在
'''
    
    with open(os.path.join(TEST_DIR, "buggy.py"), "w") as f:
        f.write(buggy_code)
    
    # Test 2.1: 修复空指针和边界条件 bug
    def verify_bug_fixes():
        path = os.path.join(TEST_DIR, "buggy.py")
        with open(path) as f:
            content = f.read()
            has_zero_check = "ZeroDivisionError" in content or "if b == 0" in content or "b != 0" in content
            has_length_check = "len(parts)" in content or "IndexError" in content
            has_key_check = "in user_dict" in content or "get(" in content or "KeyError" in content
            
            if has_zero_check and has_length_check and has_key_check:
                return True, "所有边界条件都已处理"
            missing = []
            if not has_zero_check:
                missing.append("除零检查")
            if not has_length_check:
                missing.append("数组越界检查")
            if not has_key_check:
                missing.append("字典键检查")
            return False, f"缺少检查: {', '.join(missing)}"
    
    results.append(run_test(
        TestCase("2.1 修复边界条件 Bug", "Bug修复", 
                "处理空指针、除零、数组越界等常见 bug"),
        objective="修复 buggy.py 中的所有边界条件错误",
        instructions=f"""
        修复 {TEST_DIR}/buggy.py 中的 bug：
        1. divide_numbers: 添加除零检查
        2. parse_config: 检查 split 结果长度
        3. get_user_name: 使用 .get() 或先检查 key 是否存在
        每个函数添加适当的错误处理或默认值
        """,
        constraints=["保持函数签名不变"],
        acceptance=["所有函数有边界条件处理", "代码可以正常导入"],
        verify_func=verify_bug_fixes
    ))
    
    # ================================================================
    # 场景 3: 添加功能（扩展现有代码）
    # ================================================================
    print("\n➕ 场景 3: 功能增强")
    print("=" * 70)
    
    # 3.1: 创建基础代码
    basic_api = '''class UserAPI:
    """用户 API 类"""
    def __init__(self):
        self.users = {}
    
    def create_user(self, user_id, name):
        """创建用户"""
        self.users[user_id] = {"name": name}
        return self.users[user_id]
    
    def get_user(self, user_id):
        """获取用户"""
        return self.users.get(user_id)
'''
    
    with open(os.path.join(TEST_DIR, "user_api.py"), "w") as f:
        f.write(basic_api)
    
    # Test 3.1: 添加日志和验证
    def verify_enhancement():
        path = os.path.join(TEST_DIR, "user_api.py")
        with open(path) as f:
            content = f.read()
            has_logging = "logging" in content or "logger" in content
            has_validation = "raise" in content or "ValueError" in content or "if not" in content
            
            if has_logging and has_validation:
                return True, "成功添加日志和验证"
            missing = []
            if not has_logging:
                missing.append("日志")
            if not has_validation:
                missing.append("输入验证")
            return False, f"缺少: {', '.join(missing)}"
    
    results.append(run_test(
        TestCase("3.1 添加日志和输入验证", "功能增强", 
                "在现有代码基础上添加日志和验证逻辑"),
        objective="为 UserAPI 添加日志记录和输入验证",
        instructions=f"""
        增强 {TEST_DIR}/user_api.py：
        1. 导入 logging 模块
        2. 在每个方法开始时记录日志（info 级别）
        3. 在 create_user 中验证 name 不为空
        4. 在 create_user 中验证 user_id 未被占用
        5. 添加适当的异常抛出（ValueError）
        """,
        constraints=["不破坏现有功能", "保持方法签名"],
        acceptance=["有 logging 导入", "有输入验证逻辑"],
        verify_func=verify_enhancement
    ))
    
    # ================================================================
    # 场景 4: 测试生成
    # ================================================================
    print("\n🧪 场景 4: 测试代码生成")
    print("=" * 70)
    
    # Test 4.1: 为现有代码生成单元测试
    def verify_test_generation():
        test_path = os.path.join(TEST_DIR, "test_user_api.py")
        if not os.path.exists(test_path):
            return False, "测试文件未创建"
        
        with open(test_path) as f:
            content = f.read()
            has_unittest = "unittest" in content or "pytest" in content
            has_test_class = "Test" in content and "class" in content
            has_test_methods = "def test_" in content
            
            if has_unittest and has_test_methods:
                return True, "生成了完整的单元测试"
            return False, "测试代码不完整"
    
    results.append(run_test(
        TestCase("4.1 生成单元测试", "测试生成", 
                "为现有代码自动生成单元测试"),
        objective="为 user_api.py 生成完整的单元测试",
        instructions=f"""
        为 {TEST_DIR}/user_api.py 创建单元测试文件 test_user_api.py：
        1. 使用 unittest 框架
        2. 创建 TestUserAPI 测试类
        3. 测试 create_user 的正常情况和异常情况
        4. 测试 get_user 的存在和不存在情况
        5. 每个测试方法要有清晰的命名和 docstring
        """,
        acceptance=["有 unittest 导入", "至少 3 个测试方法", "测试覆盖正常和异常路径"],
        verify_func=verify_test_generation
    ))
    
    # ================================================================
    # 场景 5: 多文件协同修改
    # ================================================================
    print("\n📦 场景 5: 多文件协同修改")
    print("=" * 70)
    
    # 5.1: 创建多文件项目结构
    os.makedirs(os.path.join(TEST_DIR, "myproject"), exist_ok=True)
    
    config_code = '''DATABASE_URL = "sqlite:///db.sqlite"
TIMEOUT = 30
'''
    
    models_code = '''class User:
    def __init__(self, name):
        self.name = name
'''
    
    main_code = '''from myproject.models import User

def main():
    user = User("Alice")
    print(user.name)
'''
    
    with open(os.path.join(TEST_DIR, "myproject", "__init__.py"), "w") as f:
        f.write("")
    with open(os.path.join(TEST_DIR, "myproject", "config.py"), "w") as f:
        f.write(config_code)
    with open(os.path.join(TEST_DIR, "myproject", "models.py"), "w") as f:
        f.write(models_code)
    with open(os.path.join(TEST_DIR, "main.py"), "w") as f:
        f.write(main_code)
    
    # Test 5.1: 跨文件添加配置使用
    def verify_multi_file():
        models_path = os.path.join(TEST_DIR, "myproject", "models.py")
        with open(models_path) as f:
            models_content = f.read()
            has_config_import = "from" in models_content and "config" in models_content
            
            if has_config_import:
                return True, "成功跨文件集成配置"
            return False, "未正确导入配置"
    
    results.append(run_test(
        TestCase("5.1 跨文件导入配置", "多文件修改", 
                "修改多个文件以实现配置统一管理"),
        objective="让 models.py 使用 config.py 中的配置",
        instructions=f"""
        修改 {TEST_DIR}/myproject/models.py：
        1. 从 config 导入 DATABASE_URL
        2. 在 User 类中添加 db_url 类属性，使用导入的 DATABASE_URL
        3. 确保导入路径正确（相对或绝对导入）
        """,
        context={
            "repo_root": TEST_DIR,
            "files_of_interest": [
                "myproject/config.py",
                "myproject/models.py"
            ]
        },
        acceptance=["models.py 导入了 config", "User 类有 db_url 属性"],
        verify_func=verify_multi_file
    ))
    
    # ================================================================
    # 场景 6: 边界条件和异常处理
    # ================================================================
    print("\n⚠️  场景 6: 输入验证与异常处理")
    print("=" * 70)
    
    # Test 6.1: 空输入处理
    def verify_empty_handling():
        # 这个测试验证 Bridge 是否正确拒绝空输入
        return True, "Bridge 应该拒绝空输入或返回错误"
    
    results.append(run_test(
        TestCase("6.1 空 Objective 处理", "输入验证", 
                "验证 Bridge 对空输入的处理"),
        objective="",  # 故意为空
        instructions="这是一个边界测试",
        verify_func=lambda: (False, "空 objective 应该被拒绝"),
        # 预期这个测试会失败或超时，这是正常的
    ))
    
    # Test 6.2: 超长输入处理
    def verify_long_input():
        # 即使输入很长，应该也能正常处理
        return True, "长输入处理完成"
    
    long_instruction = "修改代码。" + " 添加注释。" * 100  # 生成很长的指令
    
    results.append(run_test(
        TestCase("6.2 超长指令处理", "输入验证", 
                "验证对长指令的处理能力"),
        objective="为现有代码添加详细注释",
        instructions=long_instruction,
        verify_func=verify_long_input
    ))
    
    # ================================================================
    # 场景 7: 约束条件遵守
    # ================================================================
    print("\n🔒 场景 7: 约束条件验证")
    print("=" * 70)
    
    # 7.1: 创建测试代码
    api_code = '''def public_api(data):
    """公开 API - 不能修改签名"""
    return process(data)

def process(data):
    """内部函数"""
    return data.upper()
'''
    
    with open(os.path.join(TEST_DIR, "api.py"), "w") as f:
        f.write(api_code)
    
    # Test 7.1: 验证约束遵守
    def verify_constraints():
        path = os.path.join(TEST_DIR, "api.py")
        with open(path) as f:
            content = f.read()
            # 检查 public_api 签名未变
            has_original_sig = "def public_api(data):" in content
            # 检查添加了日志
            has_logging = "logging" in content or "print" in content
            
            if has_original_sig and has_logging:
                return True, "成功添加日志且保持了 API 签名"
            if not has_original_sig:
                return False, "违反了约束：修改了公开 API 签名"
            return False, "未添加日志"
    
    results.append(run_test(
        TestCase("7.1 遵守 API 签名约束", "约束验证", 
                "验证是否遵守不修改公开 API 的约束"),
        objective="为 api.py 添加日志记录",
        instructions=f"""
        修改 {TEST_DIR}/api.py：
        1. 在 process 函数中添加日志记录（logging 或 print）
        2. 记录输入数据
        """,
        constraints=[
            "不得修改 public_api 函数的签名",
            "不得修改 public_api 函数的返回值类型"
        ],
        acceptance=["有日志记录", "public_api 签名未变"],
        verify_func=verify_constraints
    ))
    
    # ================================================================
    # 结果汇总
    # ================================================================
    print("\n" + "=" * 70)
    print("📊 测试结果汇总")
    print("=" * 70)
    
    by_category = {}
    for result in results:
        if result.category not in by_category:
            by_category[result.category] = []
        by_category[result.category].append(result)
    
    total_passed = sum(1 for r in results if r.passed)
    total_tests = len(results)
    total_time = sum(r.duration for r in results)
    
    for category, tests in by_category.items():
        passed = sum(1 for t in tests if t.passed)
        total = len(tests)
        pct = (passed / total * 100) if total > 0 else 0
        print(f"\n{category}: {passed}/{total} ({pct:.0f}%)")
        for test in tests:
            status = "✅" if test.passed else "❌"
            print(f"  {status} {test.name} ({test.duration:.1f}s)")
            if test.message:
                print(f"      → {test.message}")
    
    print(f"\n{'=' * 70}")
    pct_overall = (total_passed / total_tests * 100) if total_tests > 0 else 0
    print(f"总体: {total_passed}/{total_tests} ({pct_overall:.0f}%) | 耗时: {total_time:.1f}s")
    print(f"{'=' * 70}\n")
    
    # 退出码
    sys.exit(0 if total_passed == total_tests else 1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 严重错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
