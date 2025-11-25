module.exports = {
  apps: [
    {
      name: "codex-bridge",
      script: "./bridges/codex_bridge.py",
      interpreter: "python3",
      env: {
        PORT: 53001,
        // 使用当前 shell 中的 codex 安装路径，确保版本最新且与终端一致
        CODEX_CLI_CMD: "/home/jiang/.nvm/versions/node/v22.12.0/bin/codex exec --skip-git-repo-check --sandbox read-only",
        // 避免 PM2 继承的代理影响 Codex 直连
        HTTPS_PROXY: "",
        https_proxy: "",
        HTTP_PROXY: "",
        http_proxy: ""
      }
    },
    {
      name: "droid-bridge",
      script: "./bridges/droid_bridge.py",
      interpreter: "python3",
      env: {
        PORT: 53002,
        // 默认开启低风险写入能力，且使用 JSON 输出，便于在仓库内真实改动代码
        DROID_CLI_CMD: "droid exec --auto low -o json"
      }
    }
  ]
};
