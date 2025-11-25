# Multi-Agent Studio (MCP Edition)

This directory contains the **MCP Server** implementation for Multi-Agent Studio. It allows you to use the studio's capabilities (Codex, Droid) in any MCP-compatible environment (like Claude Desktop, VS Code, etc.).

## Prerequisites

1.  **Node.js & NPM**: For running the Bridge services and CLIs.
2.  **Python 3.10+**: For running the MCP Server.

## Setup

1.  Install Node.js dependencies (Bridge services):
    ```bash
    npm install
    ```

2.  Create a Python virtual environment and install dependencies:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install mcp httpx uvicorn
    ```

## Configuration

### Add to Claude Code

Use the `claude mcp add` command to register the MCP server:

```bash
claude mcp add --transport stdio multi-agent-studio -- /home/jiang/work/for_claude/skills_dev/multi-agent-mcp/.venv/bin/python /home/jiang/work/for_claude/skills_dev/multi-agent-mcp/mcp_server.py
```

### Verify Installation

List all configured MCP servers:
```bash
claude mcp list
```

```

## Usage

### Available Tools

Once connected, the MCP Server exposes the following tools to your AI assistant:

1.  **`ask_codex_advisor`**:
    *   **Description**: Consult Codex for architectural advice or technical analysis.
    *   **Arguments**: `problem` (string), `context` (string, optional), `focus_areas` (list, optional).
    *   **Example Prompt**: "Ask Codex to recommend a database schema for a user profile system."

2.  **`execute_droid_task`**:
    *   **Description**: Delegate coding tasks or command execution to Droid.
    *   **Arguments**: `objective` (string), `instructions` (string, optional).
    *   **Example Prompt**: "Use Droid to create a Python script that calculates Fibonacci numbers."

## Development Workflow

If you want to extend or modify the Multi-Agent Studio MCP Server, follow this workflow.

### Architecture

*   **Frontend (`mcp_server.py`)**: The MCP Server implementation using `FastMCP`. It defines the tools and handles the lifecycle.
*   **Backend (`bridges/`)**: A set of lightweight Python HTTP servers that wrap the official CLIs.
*   **Communication**: `mcp_server.py` -> HTTP POST -> Bridge Server -> CLI.

### Adding a New Tool

1.  **Modify `mcp_server.py`**:
    *   Define a new function decorated with `@mcp.tool()`.
    *   Implement the logic to call the appropriate Bridge endpoint (or a new one).

    ```python
    @mcp.tool()
    async def my_new_tool(arg1: str) -> str:
        """Description for the AI."""
        # ... logic ...
        return "result"
    ```

2.  **Restart the Server**:
    *   If using Claude Code, you may need to restart the session or re-add the server.
    *   If using Claude Desktop, click "Retry" in the MCP settings.

### Modifying Bridge Logic

1.  **Edit Bridge Code**:
    *   Navigate to `bridges/` and modify the relevant `.py` file (e.g., `codex_bridge.py`).
    *   These are Python scripts running as HTTP servers (using `http.server`).

2.  **Restart Bridges**:
    *   Since Bridges are managed by PM2, you need to restart them to apply changes:
    ```bash
    npx pm2 restart all
    ```

### Debugging

*   **MCP Server Logs**: Check the stderr output of the MCP server (Claude Code usually shows this if connection fails, or use `--debug`).
*   **Bridge Logs**: Use PM2 to view backend logs:
    ```bash
    npx pm2 logs
    ```

## Lifecycle

When the MCP Server starts, it will automatically attempt to start the local Bridge services using PM2. When it stops, it will attempt to stop them.
