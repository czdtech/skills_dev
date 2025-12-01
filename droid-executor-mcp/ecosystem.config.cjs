module.exports = {
    apps: [
        {
            name: "droid-bridge",
            script: "./bridges/droid_bridge.py",
            interpreter: "python3",
            // 默认静音，避免在用户环境落盘日志
            out_file: "/dev/null",
            error_file: "/dev/null",
            log_date_format: "",
            env: {
                PORT: 53002,
                // 开启高风险自动执行能力，确保 MCP 能够修改文件
                DROID_CLI_CMD: "droid exec --auto high -o json",
                // 超时设置：10 分钟，适合执行任务
                DROID_TIMEOUT: "600"
            }
        }
    ]
};
