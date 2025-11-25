#!/usr/bin/env python3
"""
MCP 服务器功能单元测试

测试 mcp_server.py 模块中的功能，包括：
- execute_droid_task 函数的参数验证
- 网络请求处理
- 异常情况处理
- 返回值格式验证
"""

import unittest
import asyncio
import sys
import os
from unittest.mock import patch, AsyncMock, MagicMock

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server import execute_droid_task


class TestExecuteDroidTask(unittest.TestCase):
    """测试 execute_droid_task 函数"""

    def setUp(self):
        """测试前的设置"""
        self.valid_payload = {
            "objective": "测试任务目标",
            "instructions": "详细的执行指令",
            "context": {
                "files_of_interest": ["src/main.py"],
                "repo_root": "/path/to/project"
            },
            "constraints": ["保持向后兼容"],
            "acceptance_criteria": ["所有测试通过"]
        }

    def test_execute_droid_task_valid_params(self):
        """测试有效参数的基本验证"""
        # 验证参数类型检查（至少验证必需的参数存在）
        async def test_required_params():
            # 测试缺少必需的 objective 参数应该引发错误
            with self.assertRaises(TypeError):
                await execute_droid_task()
        
        # 这需要实际调用来测试，但我们先测试结构

    @patch('mcp_server.httpx.AsyncClient.post')
    async def test_execute_droid_task_success_response(self, mock_post):
        """测试成功响应的处理"""
        # 模拟成功的响应
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "status": "success",
            "summary": "任务执行成功",
            "files_changed": [{"path": "src/test.py", "change_type": "created", "highlights": ["添加了新功能"]}],
            "commands_run": [{"command": "pytest", "exit_code": 0, "stdout_excerpt": "所有测试通过"}],
            "tests": {"passed": True, "details": "5 passed"},
            "logs": ["执行开始", "任务完成"],
            "issues": []
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # 调用函数
        result = await execute_droid_task(**self.valid_payload)

        # 验证返回结果
        self.assertEqual(result["status"], "success")
        self.assertIn("summary", result)
        self.assertIn("files_changed", result)
        self.assertIn("commands_run", result)
        self.assertIn("tests", result)
        self.assertIn("logs", result)
        self.assertIn("issues", result)

    @patch('mcp_server.httpx.AsyncClient.post')
    async def test_execute_droid_task_timeout_response(self, mock_post):
        """测试超时响应的处理"""
        # 模拟超时异常
        import httpx
        mock_post.side_effect = httpx.TimeoutException("Request timeout")

        # 调用函数
        result = await execute_droid_task(**self.valid_payload)

        # 验证超时响应
        self.assertEqual(result["status"], "timeout")
        self.assertIn("Droid 执行超时", result["summary"])
        self.assertEqual(result["files_changed"], [])
        self.assertEqual(result["commands_run"], [])
        self.assertEqual(result["tests"], {})
        self.assertEqual(result["logs"], [])
        self.assertEqual(len(result["issues"]), 1)
        self.assertEqual(result["issues"][0]["type"], "timeout")

    @patch('mcp_server.httpx.AsyncClient.post')
    async def test_execute_droid_task_http_error_response(self, mock_post):
        """测试 HTTP 错误响应的处理"""
        # 模拟 HTTP 状态错误
        import httpx
        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.side_effect = httpx.HTTPStatusError("500 Server Error", request=None, response=mock_response)

        # 调用函数
        result = await execute_droid_task(**self.valid_payload)

        # 验证错误响应
        self.assertEqual(result["status"], "error")
        self.assertIn("Droid Bridge 返回错误: 500", result["summary"])
        self.assertEqual(result["files_changed"], [])
        self.assertEqual(result["commands_run"], [])
        self.assertEqual(result["tests"], {})
        self.assertEqual(len(result["logs"]), 1)
        self.assertEqual(result["logs"][0], "Internal Server Error")
        self.assertEqual(len(result["issues"]), 1)
        self.assertEqual(result["issues"][0]["type"], "bridge_error")

    @patch('mcp_server.httpx.AsyncClient.post')
    async def test_execute_droid_task_connection_error_response(self, mock_post):
        """测试连接错误响应的处理"""
        # 模拟连接异常
        import httpx
        mock_post.side_effect = httpx.ConnectError("Connection failed")

        # 调用函数
        result = await execute_droid_task(**self.valid_payload)

        # 验证连接错误响应
        self.assertEqual(result["status"], "error")
        self.assertIn("无法连接到 Droid Bridge", result["summary"])
        self.assertEqual(result["files_changed"], [])
        self.assertEqual(result["commands_run"], [])
        self.assertEqual(result["tests"], {})
        self.assertEqual(result["logs"], [])
        self.assertEqual(len(result["issues"]), 1)
        self.assertEqual(result["issues"][0]["type"], "connection_error")

    @patch('mcp_server.httpx.AsyncClient.post')
    async def test_execute_droid_task_minimal_params(self, mock_post):
        """测试最小参数（只有必需参数）"""
        # 模拟成功响应
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "status": "success",
            "summary": "任务完成",
            "files_changed": [],
            "commands_run": [],
            "tests": {},
            "logs": [],
            "issues": []
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # 最小参数调用
        result = await execute_droid_task("简单的目标")

        # 验证结果
        self.assertEqual(result["status"], "success")
        # 验证默认值被正确使用
        self.assertEqual(result["files_changed"], [])
        self.assertEqual(result["commands_run"], [])

    @patch('mcp_server.httpx.AsyncClient.post')
    async def test_execute_droid_task_different_statuses(self, mock_post):
        """测试不同的执行状态"""
        statuses = ["success", "failed", "error", "timeout"]
        
        for status in statuses:
            # 模拟该状态的响应
            mock_response = AsyncMock()
            mock_response.json.return_value = {
                "status": status,
                "summary": f"任务状态: {status}",
                "files_changed": [],
                "commands_run": [],
                "tests": {},
                "logs": [],
                "issues": []
            }
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            # 调用函数
            result = await execute_droid_task(**self.valid_payload)

            # 验证状态被正确传递
            self.assertEqual(result["status"], status)

    def test_execute_droid_task_param_types(self):
        """测试参数类型验证"""
        # 测试有效的参数类型
        valid_params = {
            "objective": "测试目标",
            "instructions": "测试指令",
            "context": {"key": "value"},
            "constraints": ["约束1", "约束2"],
            "acceptance_criteria": ["标准1", "标准2"]
        }
        
        # 参数应该能够被创建（不引发类型错误）
        # 实际的网络调用会被其他测试覆盖


class TestExecuteDroidTaskEdgeCases(unittest.TestCase):
    """测试 execute_droid_task 边界情况"""

    @patch('mcp_server.httpx.AsyncClient.post')
    async def test_execute_droid_task_very_long_objective(self, mock_post):
        """测试很长的目标描述"""
        mock_response = AsyncMock()
        mock_response.json.return_value = {"status": "success", "summary": "完成", "files_changed": [], "commands_run": [], "tests": {}, "logs": [], "issues": []}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # 测试很长的目标
        long_objective = "A" * 10000  # 10000 字符的目标
        result = await execute_droid_task(long_objective)

        self.assertEqual(result["status"], "success")

    @patch('mcp_server.httpx.AsyncClient.post')
    async def test_execute_droid_task_complex_context(self, mock_post):
        """测试复杂的上下文对象"""
        mock_response = AsyncMock()
        mock_response.json.return_value = {"status": "success", "summary": "完成", "files_changed": [], "commands_run": [], "tests": {}, "logs": [], "issues": []}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # 测试复杂的上下文
        complex_context = {
            "files_of_interest": ["file1.py", "file2.py", "file3.py"],
            "repo_root": "/complex/path/to/repo",
            "summary": "这是一个复杂的项目，包含多个模块",
            "additional_info": {
                "version": "1.0.0",
                "dependencies": ["requests", "flask"],
                "config": {"debug": True, "port": 8080}
            }
        }
        
        result = await execute_droid_task(
            objective="测试复杂上下文",
            context=complex_context
        )
        
        self.assertEqual(result["status"], "success")

    def test_function_signature(self):
        """测试函数签名正确性"""
        import inspect
        
        # 获取函数签名
        sig = inspect.signature(execute_droid_task)
        
        # 验证必需参数
        self.assertIn("objective", sig.parameters)
        
        # 验证可选参数有默认值
        self.assertTrue(sig.parameters["instructions"].default == "")
        self.assertTrue(sig.parameters["context"].default is None)
        self.assertTrue(sig.parameters["constraints"].default is None)
        self.assertTrue(sig.parameters["acceptance_criteria"].default is None)


def run_async_test(test_method):
    """运行异步测试的辅助函数"""
    def wrapper(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test_method(self))
        finally:
            loop.close()
    return wrapper

# 为每个异步测试方法应用包装器
TestExecuteDroidTask.test_execute_droid_task_success_response = run_async_test(TestExecuteDroidTask.test_execute_droid_task_success_response)
TestExecuteDroidTask.test_execute_droid_task_timeout_response = run_async_test(TestExecuteDroidTask.test_execute_droid_task_timeout_response)
TestExecuteDroidTask.test_execute_droid_task_http_error_response = run_async_test(TestExecuteDroidTask.test_execute_droid_task_http_error_response)
TestExecuteDroidTask.test_execute_droid_task_connection_error_response = run_async_test(TestExecuteDroidTask.test_execute_droid_task_connection_error_response)
TestExecuteDroidTask.test_execute_droid_task_minimal_params = run_async_test(TestExecuteDroidTask.test_execute_droid_task_minimal_params)
TestExecuteDroidTask.test_execute_droid_task_different_statuses = run_async_test(TestExecuteDroidTask.test_execute_droid_task_different_statuses)
TestExecuteDroidTask.test_execute_droid_task_very_long_objective = run_async_test(TestExecuteDroidTask.test_execute_droid_task_very_long_objective)
TestExecuteDroidTask.test_execute_droid_task_complex_context = run_async_test(TestExecuteDroidTask.test_execute_droid_task_complex_context)


if __name__ == '__main__':
    unittest.main()
