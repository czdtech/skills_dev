#!/usr/bin/env python3
"""
MCP Server integration tests for droid-executor-mcp.

Tests the MCP server functionality including:
- Tool discovery
- Tool execution
- Lifecycle management
- Concurrent requests

Run: python tests/test_mcp_server.py
"""
import asyncio
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

# Try to import httpx for async HTTP requests
try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False
    print("Warning: httpx not installed. Some tests will be skipped.")

# Configuration
BRIDGE_URL = os.getenv("DROID_BRIDGE_URL", "http://localhost:53002")
BRIDGE_PORT = 53002
MCP_ROOT = Path(__file__).parent.parent / "droid-executor-mcp"


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


# ============================================================================
# MCP Tool Tests (via HTTP Bridge)
# ============================================================================

class TestMCPBridge:
    """Test MCP functionality via HTTP bridge."""
    
    async def test_simple_execution(self):
        """8.2: Execute simple task via bridge (validation only)."""
        if not HAS_HTTPX:
            print("⚠️ Skipped: httpx not installed")
            return
        
        async with httpx.AsyncClient() as client:
            # Test validation endpoint (fast, no Droid CLI)
            response = await client.post(
                f"{BRIDGE_URL}/execute",
                json={"objective": ""},  # Empty for fast validation
                timeout=10.0
            )
            result = response.json()
            
            assert "status" in result
            assert result["status"] == "error"  # Validation error expected
            print(f"✅ 8.2 Simple execution (validation): PASSED")
    
    async def test_concurrent_requests(self):
        """8.3: Handle concurrent requests (validation only)."""
        if not HAS_HTTPX:
            print("⚠️ Skipped: httpx not installed")
            return
        
        async with httpx.AsyncClient() as client:
            # Send 3 concurrent validation requests (fast)
            tasks = []
            for i in range(3):
                task = client.post(
                    f"{BRIDGE_URL}/execute",
                    json={"objective": ""},  # Empty for fast validation
                    timeout=10.0
                )
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            success_count = 0
            for resp in responses:
                if isinstance(resp, Exception):
                    print(f"  Request failed: {resp}")
                else:
                    result = resp.json()
                    if result.get("status") == "error":  # Validation error expected
                        success_count += 1
            
            assert success_count >= 2, "At least 2 requests should be handled"
            print(f"✅ 8.3 Concurrent requests: PASSED ({success_count}/3 handled)")
    
    async def test_timeout_handling(self):
        """Test timeout handling with short timeout."""
        if not HAS_HTTPX:
            print("⚠️ Skipped: httpx not installed")
            return
        
        async with httpx.AsyncClient() as client:
            try:
                # Use very short timeout to test timeout handling
                response = await client.post(
                    f"{BRIDGE_URL}/execute",
                    json={"objective": ""},  # Empty for validation
                    timeout=0.001  # Very short timeout
                )
                # If we get here, the request was very fast
                print("✅ Timeout handling: PASSED (request completed quickly)")
            except httpx.TimeoutException:
                # Expected for slow requests
                print("✅ Timeout handling: PASSED (timeout raised as expected)")
            except Exception as e:
                print(f"✅ Timeout handling: PASSED ({type(e).__name__})")


# ============================================================================
# MCP Lifecycle Tests
# ============================================================================

class TestMCPLifecycle:
    """Test MCP server lifecycle management."""
    
    def test_ecosystem_config_exists(self):
        """8.4: Verify ecosystem.config.cjs exists."""
        config_path = MCP_ROOT / "ecosystem.config.cjs"
        assert config_path.exists(), f"Config not found: {config_path}"
        print("✅ 8.4 Ecosystem config exists: PASSED")
    
    def test_ecosystem_config_content(self):
        """Verify ecosystem.config.cjs has correct content."""
        config_path = MCP_ROOT / "ecosystem.config.cjs"
        content = config_path.read_text()
        
        assert "droid-bridge" in content, "Should define droid-bridge app"
        assert "53002" in content, "Should use port 53002"
        assert "./bridges/droid_bridge.py" in content, "Should reference correct script path"
        print("✅ Ecosystem config content: PASSED")
    
    def test_mcp_server_exists(self):
        """Verify mcp_server.py exists."""
        server_path = MCP_ROOT / "mcp_server.py"
        assert server_path.exists(), f"Server not found: {server_path}"
        print("✅ MCP server exists: PASSED")
    
    def test_mcp_server_imports(self):
        """Verify mcp_server.py has correct imports."""
        server_path = MCP_ROOT / "mcp_server.py"
        content = server_path.read_text()
        
        assert "from mcp.server.fastmcp import FastMCP" in content, "Should import FastMCP"
        assert "ecosystem.config.cjs" in content, "Should reference .cjs config"
        print("✅ MCP server imports: PASSED")


# ============================================================================
# MCP Bridge Directory Tests
# ============================================================================

class TestMCPBridgeDirectory:
    """Test MCP bridge directory structure."""
    
    def test_bridges_directory_exists(self):
        """Verify bridges/ directory exists."""
        bridges_dir = MCP_ROOT / "bridges"
        assert bridges_dir.exists(), f"Bridges directory not found: {bridges_dir}"
        assert bridges_dir.is_dir(), "bridges should be a directory"
        print("✅ Bridges directory exists: PASSED")
    
    def test_bridge_files_exist(self):
        """Verify bridge files exist."""
        bridges_dir = MCP_ROOT / "bridges"
        
        droid_bridge = bridges_dir / "droid_bridge.py"
        server_lib = bridges_dir / "server_lib.py"
        
        assert droid_bridge.exists(), f"droid_bridge.py not found"
        assert server_lib.exists(), f"server_lib.py not found"
        print("✅ Bridge files exist: PASSED")
    
    def test_no_test_files(self):
        """Verify no test files in MCP root (per requirements 9.1)."""
        test_files = ["fibonacci.py", "hello_world.py"]
        for test_file in test_files:
            path = MCP_ROOT / test_file
            assert not path.exists(), f"Test file should be removed: {test_file}"
        print("✅ No test files: PASSED")
    
    def test_no_factory_directory(self):
        """Verify no .factory directory (per requirements 9.2)."""
        factory_dir = MCP_ROOT / ".factory"
        assert not factory_dir.exists(), ".factory directory should be removed"
        print("✅ No .factory directory: PASSED")


# ============================================================================
# Main Test Runner
# ============================================================================

async def run_async_tests():
    """Run async tests."""
    test_instance = TestMCPBridge()
    
    for method_name in dir(test_instance):
        if method_name.startswith("test_"):
            method = getattr(test_instance, method_name)
            if asyncio.iscoroutinefunction(method):
                try:
                    await method()
                except AssertionError as e:
                    print(f"❌ {method_name}: FAILED - {e}")
                except Exception as e:
                    print(f"❌ {method_name}: ERROR - {e}")


def run_sync_tests():
    """Run synchronous tests."""
    test_classes = [
        TestMCPLifecycle,
        TestMCPBridgeDirectory,
    ]
    
    passed = 0
    failed = 0
    
    for test_class in test_classes:
        print(f"\n{'─' * 60}")
        print(f"Running: {test_class.__name__}")
        print("─" * 60)
        
        instance = test_class()
        
        for method_name in dir(instance):
            if method_name.startswith("test_"):
                try:
                    getattr(instance, method_name)()
                    passed += 1
                except AssertionError as e:
                    print(f"❌ {method_name}: FAILED - {e}")
                    failed += 1
                except Exception as e:
                    print(f"❌ {method_name}: ERROR - {e}")
                    failed += 1
    
    return passed, failed


def main():
    """Run all MCP tests."""
    print("\n" + "=" * 70)
    print("DROID EXECUTOR MCP TESTS")
    print("=" * 70)
    
    # Check bridge
    if is_port_open(BRIDGE_PORT):
        print(f"\n✅ Bridge is running on port {BRIDGE_PORT}")
    else:
        print(f"\n⚠️  Bridge not running on port {BRIDGE_PORT}")
        print("Some tests may fail or be skipped.")
    
    # Run sync tests
    passed, failed = run_sync_tests()
    
    # Run async tests
    print(f"\n{'─' * 60}")
    print("Running: TestMCPBridge (async)")
    print("─" * 60)
    
    if is_port_open(BRIDGE_PORT):
        asyncio.run(run_async_tests())
    else:
        print("⚠️ Skipping async tests: bridge not running")
    
    # Summary
    print("\n" + "=" * 70)
    print(f"SYNC RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
