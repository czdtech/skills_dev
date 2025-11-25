module.exports = {
    apps: [
        {
            name: "droid-bridge",
            script: "./bridges/droid_bridge.py",
            interpreter: "python3",
            env: {
                PORT: 53002,
                // 默认开启低风险写入能力，且使用 JSON 输出，便于在仓库内真实改动代码
                DROID_CLI_CMD: "droid exec --auto low -o json",
                // 超时设置：10 分钟，适合执行任务
                DROID_TIMEOUT: "600"
            }
        }
    ]
};
