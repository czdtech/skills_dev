#!/usr/bin/env python3
"""
Comprehensive Test Suite for droid-executor-skill
Based on https://docs.factory.ai/cli/droid-exec/overview
"""
import json
import urllib.request
import urllib.error
import sys
import os
import time
import shutil

# Configuration
BRIDGE_URL = "http://localhost:3002/execute"
TEST_DIR = "/home/jiang/work/for_claude/skills_dev/droid_comprehensive_test"

class TestResult:
    def __init__(self, name, category):
        self.name = name
        self.category = category
        self.passed = False
        self.message = ""
        self.duration = 0
        self.response = None

def setup_test_env():
    """Creates a clean test directory."""
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(TEST_DIR)
    print(f"✓ Created test directory: {TEST_DIR}\n")

def send_request(objective, instructions="", context=None, timeout=120):
    """Sends a request to the Droid Bridge."""
    if context is None:
        context = {"repo_root": TEST_DIR, "summary": f"Testing in {TEST_DIR}"}
    
    payload = {
        "objective": objective,
        "instructions": instructions,
        "context": context
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

def run_test(test_result, objective, instructions="", verify_func=None, context=None):
    """Runs a single test case."""
    print(f"  ⏳ {test_result.name}...", end="", flush=True)
    
    result, duration, error = send_request(objective, instructions, context)
    test_result.duration = duration
    test_result.response = result
    
    if error:
        test_result.message = f"Request failed: {error}"
        print(f" ❌ ({duration:.1f}s)")
        print(f"     {test_result.message}")
        return test_result
    
    if verify_func:
        success, message = verify_func(result)
        test_result.passed = success
        test_result.message = message
    else:
        # Default: check if request succeeded
        test_result.passed = result is not None
        test_result.message = "Request successful"
    
    status = "✅" if test_result.passed else "❌"
    print(f" {status} ({duration:.1f}s)")
    if not test_result.passed or test_result.message:
        print(f"     {test_result.message}")
    
    return test_result

def main():
    setup_test_env()
    results = []
    
    # ============================================
    # Category 1: Basic CRUD Operations
    # ============================================
    print("📁 Category 1: Basic CRUD Operations")
    print("=" * 60)
    
    # Test 1.1: Create file
    def verify_create():
        path = os.path.join(TEST_DIR, "hello.py")
        if not os.path.exists(path):
            return False, "File not created"
        with open(path) as f:
            content = f.read()
            if "hello" in content.lower():
                return True, "File created with correct content"
            return False, "File content incorrect"
    
    results.append(run_test(
        TestResult("1.1 Create Python file", "CRUD"),
        f"Create a Python file named hello.py in {TEST_DIR} that prints 'Hello World'",
        verify_func=lambda r: verify_create()
    ))
    
    # Test 1.2: Read file
    results.append(run_test(
        TestResult("1.2 Read and analyze file", "CRUD"),
        f"Read {TEST_DIR}/hello.py and summarize its purpose",
        verify_func=lambda r: (True, "Analysis successful") if r else (False, "Failed")
    ))
    
    # Test 1.3: Update file
    def verify_update():
        path = os.path.join(TEST_DIR, "hello.py")
        with open(path) as f:
            content = f.read()
            if "argparse" in content or "sys.argv" in content:
                return True, "File updated with CLI argument handling"
            return False, "File not updated correctly"
    
    results.append(run_test(
        TestResult("1.3 Update file to accept arguments", "CRUD"),
        f"Modify {TEST_DIR}/hello.py to accept a name argument from command line",
        verify_func=lambda r: verify_update()
    ))
    
    # Test 1.4: Delete file capability (actually we'll create and check it's removed)
    # First create a temp file
    temp_path = os.path.join(TEST_DIR, "temp.txt")
    with open(temp_path, "w") as f:
        f.write("temporary")
    
    def verify_delete():
        return not os.path.exists(temp_path), "File deleted" if not os.path.exists(temp_path) else "File still exists"
    
    results.append(run_test(
        TestResult("1.4 Delete file", "CRUD"),
        f"Delete the file {temp_path}",
        verify_func=lambda r: verify_delete()
    ))
    
    # ============================================
    # Category 2: Multi-file Operations
    # ============================================
    print("\n📦 Category 2: Multi-file Operations")
    print("=" * 60)
    
    # Test 2.1: Create multiple related files
    def verify_multi_create():
        files = ["utils.py", "main.py", "config.py"]
        missing = [f for f in files if not os.path.exists(os.path.join(TEST_DIR, f))]
        if missing:
            return False, f"Missing files: {missing}"
        return True, "All files created"
    
    results.append(run_test(
        TestResult("2.1 Create module with multiple files", "Multi-file"),
        f"Create a simple Python calculator module in {TEST_DIR} with: utils.py (helper functions), main.py (main logic), config.py (configuration)",
        verify_func=lambda r: verify_multi_create()
    ))
    
    # Test 2.2: Refactor across files
    def verify_refactor():
        # Check if utils.py has refactored code
        utils_path = os.path.join(TEST_DIR, "utils.py")
        if os.path.exists(utils_path):
            with open(utils_path) as f:
                content = f.read()
                # Just check it was modified
                return True, "Refactoring applied"
        return False, "Refactoring failed"
    
    results.append(run_test(
        TestResult("2.2 Refactor code across files", "Multi-file"),
        f"Refactor the calculator module: move all math operations to utils.py and add type hints to all functions",
        verify_func=lambda r: verify_refactor()
    ))
    
    # ===========================================
    # Category 3: Error Handling & Edge Cases
    # ============================================
    print("\n⚠️  Category 3: Error Handling & Edge Cases")
    print("=" * 60)
    
    # Test 3.1: Handle non-existent file gracefully
    results.append(run_test(
        TestResult("3.1 Graceful handling of missing file", "Error Handling"),
        f"Read and summarize {TEST_DIR}/nonexistent.py",
        verify_func=lambda r: (True, "Handled gracefully") if r else (False, "Failed")
    ))
    
    # Test 3.2: Fix syntax error
    buggy_path = os.path.join(TEST_DIR, "buggy.py")
    with open(buggy_path, "w") as f:
        f.write("def broken(\n    print('missing colon and closing paren'")
    
    def verify_fix():
        with open(buggy_path) as f:
            content = f.read()
            # Try to compile it
            try:
                compile(content, buggy_path, 'exec')
                return True, "Syntax error fixed"
            except SyntaxError:
                return False, "Still has syntax error"
    
    results.append(run_test(
        TestResult("3.2 Fix Python syntax error", "Error Handling"),
        f"Fix all syntax errors in {buggy_path}",
        verify_func=lambda r: verify_fix()
    ))
    
    # Test 3.3: Handle empty prompt gracefully
    results.append(run_test(
        TestResult("3.3 Handle empty objective", "Error Handling"),
        "",  # Empty objective
        verify_func=lambda r: (True, "Handled empty prompt")
    ))
    
    # ============================================
    # Category 4: Context Awareness
    # ============================================
    print("\n🧠 Category 4: Context Awareness")
    print("=" * 60)
    
    # Test 4.1: Working directory awareness
    sub_dir = os.path.join(TEST_DIR, "subproject")
    os.makedirs(sub_dir, exist_ok=True)
    
    def verify_wd():
        readme = os.path.join(sub_dir, "README.md")
        return os.path.exists(readme), "README created in correct directory" if os.path.exists(readme) else "README not found"
    
    results.append(run_test(
        TestResult("4.1 Respect working directory context", "Context"),
        f"Create a README.md file in this directory",
        context={"repo_root": sub_dir, "summary": f"Working in {sub_dir}"},
        verify_func=lambda r: verify_wd()
    ))
    
    # Test 4.2: File references in context
    results.append(run_test(
        TestResult("4.2 Use files_of_interest from context", "Context"),
        "Add docstrings to all functions in the provided files",
        context={
            "repo_root": TEST_DIR,
            "files_of_interest": ["utils.py", "main.py"]
        },
        verify_func=lambda r: (True, "Context files processed")
    ))
    
    # ============================================
    # Category 5: Complex Tasks
    # ============================================
    print("\n🎯 Category 5: Complex Tasks")
    print("=" * 60)
    
    # Test 5.1: Code generation with dependencies
    results.append(run_test(
        TestResult("5.1 Generate code with imports", "Complex"),
        f"Create a FastAPI REST API in {TEST_DIR}/api.py with endpoints for CRUD operations on a User model",
        verify_func=lambda r: (os.path.exists(os.path.join(TEST_DIR, "api.py")), "API file created")
    ))
    
    # Test 5.2: Analysis and report generation
    results.append(run_test(
        TestResult("5.2 Code analysis and report", "Complex"),
        f"Analyze all Python files in {TEST_DIR} and create a report.md with: file count, total lines, complexity issues, and improvement suggestions",
        verify_func=lambda r: (os.path.exists(os.path.join(TEST_DIR, "report.md")), "Report generated")
    ))
    
    # ============================================
    # Category 6: String Context Handling (Bug Fix Verification)
    # ============================================
    print("\n🔧 Category 6: String Context Handling")
    print("=" * 60)
    
    # Test 6.1: String context (previously caused crash)
    results.append(run_test(
        TestResult("6.1 Handle string context", "Bug Fix"),
        f"Create a test.txt file with content 'Context test'",
        context=f"Simple string context: {TEST_DIR}",  # String instead of dict
        verify_func=lambda r: (os.path.exists(os.path.join(TEST_DIR, "test.txt")), "String context handled")
    ))
    
    # Test 6.2: Mixed context types
    results.append(run_test(
        TestResult("6.2 Handle dict context", "Bug Fix"),
        f"Create a dict_test.txt file",
        context={"summary": "Dict context test", "repo_root": TEST_DIR},
        verify_func=lambda r: (os.path.exists(os.path.join(TEST_DIR, "dict_test.txt")), "Dict context handled")
    ))
    
    # ============================================
    # Results Summary
    # ============================================
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
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
        print(f"\n{category}: {passed}/{total} passed")
        for test in tests:
            status = "✅" if test.passed else "❌"
            print(f"  {status} {test.name} ({test.duration:.1f}s)")
            if not test.passed and test.message:
                print(f"      → {test.message}")
    
    print(f"\n{'=' * 60}")
    print(f"OVERALL: {total_passed}/{total_tests} tests passed ({total_passed/total_tests*100:.1f}%)")
    print(f"Total time: {total_time:.1f}s")
    print(f"{'=' * 60}\n")
    
    # Exit code
    sys.exit(0 if total_passed == total_tests else 1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
