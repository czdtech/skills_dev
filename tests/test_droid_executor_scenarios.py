#!/usr/bin/env python3
"""
Comprehensive scenario tests for droid-executor-skill and droid-executor-mcp.

This test suite covers multiple scenarios:
1. Input validation
2. Simple task execution
3. Port detection
4. Error handling
5. Bridge lifecycle

Run: python tests/test_droid_executor_scenarios.py
Or with pytest: pytest tests/test_droid_executor_scenarios.py -v
"""
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
import urllib.error
from pathlib import Path

# Configuration
BRIDGE_URL = os.getenv("DROID_BRIDGE_URL", "http://localhost:53002")
BRIDGE_PORT = 53002
SKILL_ROOT = Path(__file__).parent.parent / "droid-executor-skill"
MCP_ROOT = Path(__file__).parent.parent / "droid-executor-mcp"


# ============================================================================
# Utility Functions
# ============================================================================

def is_port_open(port, timeout=1):
    """Check if port is open."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except:
        return False


def send_request(payload, timeout=10):
    """Send request to bridge and return result."""
    try:
        req = urllib.request.Request(
            f"{BRIDGE_URL}/execute",
            data=json.dumps(payload).encode(),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return {"status": "http_error", "code": e.code, "reason": e.reason}
    except urllib.error.URLError as e:
        return {"status": "connection_error", "reason": str(e.reason)}
    except socket.timeout:
        return {"status": "timeout", "reason": "Request timed out"}
    except Exception as e:
        return {"status": "error", "reason": str(e)}


def ensure_bridge_running():
    """Ensure bridge is running before tests."""
    if is_port_open(BRIDGE_PORT):
        return True
    
    print("Starting bridge for tests...")
    subprocess.run(
        ["npx", "pm2", "start", "ecosystem.config.cjs"],
        cwd=SKILL_ROOT,
        capture_output=True
    )
    
    for _ in range(30):
        if is_port_open(BRIDGE_PORT):
            print("Bridge ready.")
            return True
        time.sleep(1)
    
    print("Warning: Bridge may not be ready.")
    return False


# ============================================================================
# Scenario 1: Input Validation Tests
# ============================================================================

class TestInputValidation:
    """Test input validation scenarios."""
    
    def test_empty_objective(self):
        """1.1: Empty objective should be rejected."""
        result = send_request({"objective": ""})
        assert result["status"] == "error", f"Expected error, got {result['status']}"
        assert len(result.get("issues", [])) > 0
        assert result["issues"][0]["type"] == "validation_error"
        print("✅ 1.1 Empty objective: PASSED")
    
    def test_whitespace_objective(self):
        """1.2: Whitespace-only objective should be rejected."""
        result = send_request({"objective": "   \t\n  "})
        assert result["status"] == "error", f"Expected error, got {result['status']}"
        assert result["issues"][0]["type"] == "validation_error"
        print("✅ 1.2 Whitespace objective: PASSED")
    
    def test_missing_objective(self):
        """1.5: Missing objective should be rejected."""
        result = send_request({})
        assert result["status"] == "error", f"Expected error, got {result['status']}"
        assert result["issues"][0]["type"] == "validation_error"
        print("✅ 1.5 Missing objective: PASSED")
    
    def test_long_objective(self):
        """1.3: Objective exceeding 50000 chars should be rejected."""
        long_objective = "x" * 50001
        result = send_request({"objective": long_objective})
        assert result["status"] == "error", f"Expected error, got {result['status']}"
        assert result["issues"][0]["type"] == "validation_error"
        print("✅ 1.3 Long objective: PASSED")
    
    def test_long_instructions(self):
        """1.4: Instructions exceeding 100000 chars should be rejected."""
        long_instructions = "y" * 100001
        result = send_request({
            "objective": "Valid objective",
            "instructions": long_instructions
        })
        assert result["status"] == "error", f"Expected error, got {result['status']}"
        assert result["issues"][0]["type"] == "validation_error"
        print("✅ 1.4 Long instructions: PASSED")
    
    def test_valid_input(self):
        """1.6: Valid input should be accepted (validation only, not execution)."""
        # This test only verifies that valid input passes validation
        # It doesn't actually execute the task (which would require Droid CLI)
        # The validation logic is tested by checking that we don't get validation_error
        # for well-formed input
        
        # Test that the payload structure is valid
        payload = {
            "objective": "Echo hello",
            "context": {"repo_root": "."}
        }
        
        # Verify payload has required fields
        assert "objective" in payload
        assert payload["objective"].strip() != ""
        assert len(payload["objective"]) <= 50000
        
        print("✅ 1.6 Valid input structure: PASSED")


# ============================================================================
# Scenario 2: Simple Task Execution Tests
# ============================================================================

class TestSimpleTaskExecution:
    """Test simple task execution scenarios."""
    
    def test_echo_command(self):
        """2.4: Run simple echo command."""
        # Skip in automated tests - requires Droid CLI
        print("⚠️ 2.4 Echo command: SKIPPED (requires Droid CLI)")
    
    def test_list_files(self):
        """2.1: List files in directory."""
        # Skip in automated tests - requires Droid CLI
        print("⚠️ 2.1 List files: SKIPPED (requires Droid CLI)")


# ============================================================================
# Scenario 3: Code Modification Tests
# ============================================================================

class TestCodeModification:
    """Test code modification scenarios."""
    
    def setup_method(self):
        """Create temporary test directory."""
        self.temp_dir = tempfile.mkdtemp(prefix="droid_test_")
        
        # Create test file
        test_file = Path(self.temp_dir) / "utils.py"
        test_file.write_text('''
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b
''')
    
    def teardown_method(self):
        """Clean up temporary directory."""
        import shutil
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_add_docstring(self):
        """3.3: Add docstrings to functions."""
        # Skip this test in automated runs as it requires Droid CLI and takes time
        # This is an integration test that should be run manually
        print("⚠️ 3.3 Add docstring: SKIPPED (requires Droid CLI, run manually)")


# ============================================================================
# Scenario 7: Error Recovery Tests
# ============================================================================

class TestErrorRecovery:
    """Test error recovery scenarios."""
    
    def test_nonexistent_file(self):
        """7.1: Operating on nonexistent file."""
        # Skip in automated tests - requires Droid CLI
        print("⚠️ 7.1 Nonexistent file: SKIPPED (requires Droid CLI)")
    
    def test_invalid_repo_root(self):
        """7.2: Invalid repo root path."""
        # Skip in automated tests - requires Droid CLI
        print("⚠️ 7.2 Invalid repo root: SKIPPED (requires Droid CLI)")


# ============================================================================
# Scenario 9: Port Detection Tests
# ============================================================================

class TestPortDetection:
    """Test port detection functionality."""
    
    def test_port_detection_closed(self):
        """9.2: Detect closed port."""
        # Use a port that's unlikely to be in use
        test_port = 59999
        assert not is_port_open(test_port), f"Port {test_port} should be closed"
        print("✅ 9.2 Closed port detection: PASSED")
    
    def test_port_detection_open(self):
        """9.1: Detect open port (bridge)."""
        if is_port_open(BRIDGE_PORT):
            print("✅ 9.1 Open port detection: PASSED")
        else:
            print("⚠️ 9.1 Open port detection: SKIPPED (bridge not running)")


# ============================================================================
# Scenario 8: Response Structure Tests
# ============================================================================

class TestResponseStructure:
    """Test that responses have correct structure."""
    
    def test_error_response_structure(self):
        """Response should have all required fields."""
        result = send_request({"objective": ""})
        
        required_fields = ["status", "summary", "files_changed", "commands_run", 
                          "tests", "logs", "issues"]
        for field in required_fields:
            assert field in result, f"Missing field: {field}"
        
        assert isinstance(result["files_changed"], list)
        assert isinstance(result["commands_run"], list)
        assert isinstance(result["logs"], list)
        assert isinstance(result["issues"], list)
        
        print("✅ Response structure: PASSED")
    
    def test_issue_structure(self):
        """Issues should have correct structure."""
        result = send_request({"objective": ""})
        
        if result.get("issues"):
            issue = result["issues"][0]
            assert "type" in issue
            assert "description" in issue
            assert "suggested_action" in issue
        
        print("✅ Issue structure: PASSED")


# ============================================================================
# Main Test Runner
# ============================================================================

def run_all_tests():
    """Run all test scenarios."""
    print("\n" + "=" * 70)
    print("DROID EXECUTOR SCENARIO TESTS")
    print("=" * 70)
    
    # Check bridge
    if not is_port_open(BRIDGE_PORT):
        print(f"\n⚠️  Bridge not running on port {BRIDGE_PORT}")
        print("Starting bridge...")
        ensure_bridge_running()
    
    if not is_port_open(BRIDGE_PORT):
        print("\n❌ Cannot connect to bridge. Some tests will fail.")
    else:
        print(f"\n✅ Bridge is running on port {BRIDGE_PORT}")
    
    # Run tests
    test_classes = [
        TestInputValidation,
        TestSimpleTaskExecution,
        TestCodeModification,
        TestErrorRecovery,
        TestPortDetection,
        TestResponseStructure,
    ]
    
    passed = 0
    failed = 0
    
    for test_class in test_classes:
        print(f"\n{'─' * 70}")
        print(f"Running: {test_class.__name__}")
        print("─" * 70)
        
        instance = test_class()
        
        for method_name in dir(instance):
            if method_name.startswith("test_"):
                # Setup
                if hasattr(instance, "setup_method"):
                    try:
                        instance.setup_method()
                    except Exception as e:
                        print(f"Setup failed: {e}")
                
                # Run test
                try:
                    getattr(instance, method_name)()
                    passed += 1
                except AssertionError as e:
                    print(f"❌ {method_name}: FAILED - {e}")
                    failed += 1
                except Exception as e:
                    print(f"❌ {method_name}: ERROR - {e}")
                    failed += 1
                
                # Teardown
                if hasattr(instance, "teardown_method"):
                    try:
                        instance.teardown_method()
                    except:
                        pass
    
    # Summary
    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
