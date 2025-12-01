#!/usr/bin/env python3
"""
Property-based tests for socket port detection.

**Feature: droid-executor-optimization, Property 1: Socket Port Detection Accuracy**
**Validates: Requirements 4.1**
"""
import socket
import sys
from pathlib import Path

# Add parent directory to path to import wrapper_droid
sys.path.insert(0, str(Path(__file__).parent.parent))

from hypothesis import given, settings, assume
from hypothesis import strategies as st

from wrapper_droid import is_port_open


def find_open_port():
    """Find a port that is currently open by binding to it temporarily."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 0))
    port = sock.getsockname()[1]
    return sock, port


def is_port_likely_free(port):
    """Check if a port is likely free (not in use by system services)."""
    # Avoid well-known ports and common service ports
    if port < 1024:
        return False
    # Avoid common development ports
    common_ports = {3000, 3001, 3002, 5000, 8000, 8080, 8888, 53001, 53002}
    if port in common_ports:
        return False
    return True


# **Feature: droid-executor-optimization, Property 1: Socket Port Detection Accuracy**
# **Validates: Requirements 4.1**
def test_closed_port_detection():
    """
    Property: For any port that is not listening, is_port_open should return False.
    
    We bind to a port, get its number, then close it to guarantee it's closed.
    This avoids race conditions with other processes.
    """
    # Bind to get a random available port, then close it immediately
    # This gives us a port that we know was just available
    temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    temp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    temp_sock.bind(('localhost', 0))
    port = temp_sock.getsockname()[1]
    temp_sock.close()
    
    # The port should now be closed (we just closed it)
    # The is_port_open function should correctly detect it as closed
    assert is_port_open(port, timeout=0.5) == False


# **Feature: droid-executor-optimization, Property 1: Socket Port Detection Accuracy**
# **Validates: Requirements 4.1**
def test_open_port_detection():
    """
    Property: For any port that is listening, is_port_open should return True.
    
    We create a listening socket and verify is_port_open detects it.
    """
    # Create a listening socket on a random available port
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(('localhost', 0))
    server_sock.listen(1)
    
    try:
        port = server_sock.getsockname()[1]
        # The is_port_open function should correctly detect it as open
        assert is_port_open(port, timeout=1) == True
    finally:
        server_sock.close()


# **Feature: droid-executor-optimization, Property 1: Socket Port Detection Accuracy**
# **Validates: Requirements 4.1**
def test_port_detection_consistency():
    """
    Property: For a controlled port, calling is_port_open twice should return the same result.
    
    This tests the consistency/determinism of the function by using a port we control.
    We avoid random ports because external processes may change port state between checks.
    """
    # Test consistency on a port we control (open)
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(('localhost', 0))
    server_sock.listen(1)
    
    try:
        port = server_sock.getsockname()[1]
        result1 = is_port_open(port, timeout=0.5)
        result2 = is_port_open(port, timeout=0.5)
        assert result1 == result2 == True, f"Inconsistent results for open port {port}"
    finally:
        server_sock.close()
    
    # Test consistency on a port we control (closed)
    # After closing, the port should consistently report as closed
    import time
    time.sleep(0.1)  # Small delay to ensure port is released
    result3 = is_port_open(port, timeout=0.5)
    result4 = is_port_open(port, timeout=0.5)
    assert result3 == result4 == False, f"Inconsistent results for closed port {port}"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
