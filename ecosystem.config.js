module.exports = {
  apps: [
    {
      name: "nijiSupport",
      script: "main.py",
      interpreter: "python3",
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: "512M",
    }
  ]
};
