module.exports = {
  apps: [
    {
      name: "codex-bridge-skill",
      script: "./scripts/bridge/codex_bridge.py",
      interpreter: "python3",
      // 默认静音日志，按需通过 LOG_LEVEL 打开
      out_file: "/dev/null",
      error_file: "/dev/null",
      log_date_format: "",
      env: {
        PORT: 53001,
        CODEX_CLI_CMD: "/home/jiang/.nvm/versions/node/v22.12.0/bin/codex exec --skip-git-repo-check --sandbox read-only",
        // 超时设置：30 分钟
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
