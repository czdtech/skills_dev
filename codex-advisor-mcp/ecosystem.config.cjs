module.exports = {
  apps: [
    {
      name: "codex-bridge",
      script: "./bridges/codex_bridge.py",
      interpreter: "python3",
      // 默认静音输出，避免在用户环境落盘日志
      out_file: "/dev/null",
      error_file: "/dev/null",
      log_date_format: "",
      env: {
        PORT: 53001,
        // 使用当前 shell 中的 codex 安装路径，确保版本最新且与终端一致
        CODEX_CLI_CMD: "/home/jiang/.nvm/versions/node/v22.12.0/bin/codex exec --skip-git-repo-check --sandbox read-only",
        // 超时设置：30 分钟，适合深度分析任务
        CODEX_TIMEOUT: "1800",
        // 避免 PM2 继承的代理影响 Codex 直连
        HTTPS_PROXY: "",
        https_proxy: "",
        HTTP_PROXY: "",
        http_proxy: ""
      }
    }
  ]
};
