module.exports = {
  apps: [
    {
      name: "codex-bridge",
      script: "./bridges/codex_bridge.py",
      interpreter: "python3",
      env: {
        PORT: 53001,
        CODEX_CLI_CMD: "codex exec --skip-git-repo-check --sandbox read-only"
      }
    }
  ]
};
