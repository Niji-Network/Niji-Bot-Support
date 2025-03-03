# Discord Bot

A modular Discord bot built with [discord.py](https://github.com/Rapptz/discord.py) that features welcome messages, image commands, moderation tools, detailed logging, and real-time API status monitoring.

## Features

- **Welcome Messages:** Automatically sends an embed when a member joins.
- **Image Commands:** Retrieves random images from an API using categories like _random_, _waifu_, or _husbando_.
- **Moderation Commands:** Offers hybrid commands for kicking, banning, timing out, and clearing messages.
- **Logging:** Logs events such as command usage, message edits/deletions, and member join/leave to designated channels.
- **API Stats Monitoring:** Periodically fetches API/system stats and updates a status embed in a specified channel.

## Requirements

- Python 3.8+
- [discord.py 2.0+](https://github.com/Rapptz/discord.py) (supports slash commands)
- [aiohttp](https://docs.aiohttp.org/)
- [python-dotenv](https://github.com/theskumar/python-dotenv)

## Installation

1. **Clone the repository:**

 ```bash
git clone https://github.com/Niji-Network/Niji-Bot-Support
cd Niji-Bot-SUpport
````

2. **Create and activate virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Configuration

Rename the `example.env` file to `.env`and add the required variables.

## Running the bot

To start the bot, run:
```bash
python main.py
```

For production consider using **PM2** with the provided ecosystem.config.js` for process management.

## Contributing

Contributions are welcome! Please open issues or pull requests for bug fixes, features, or improvements.