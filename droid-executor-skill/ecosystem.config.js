module.exports = {
  apps: [
    {
      name: "droid-bridge",
      script: "./bridges/droid_bridge.py",
      interpreter: "python3",
      env: {
        PORT: 53002,
        DROID_CLI_CMD: "droid exec --output-format json --auto high"
      }
    }
  ]
};
