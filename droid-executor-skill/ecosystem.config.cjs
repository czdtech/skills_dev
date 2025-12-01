module.exports = {
  apps: [
    {
      name: "droid-bridge-skill",
      script: "./scripts/bridge/droid_bridge.py",
      interpreter: "python3",
      // 默认静音日志，按需通过 LOG_LEVEL 打开
      out_file: "/dev/null",
      error_file: "/dev/null",
      log_date_format: "",
      env: {
        PORT: 53002,
        DROID_CLI_CMD: "droid exec --output-format json --auto high",
        // 超时设置：10 分钟
        DROID_TIMEOUT: "600"
      }
    }
  ]
};
