# ZeroTrace - ZeroRAT

![ZeroRAT](https://img.shields.io/badge/version-1.0-blue.svg) ![License](https://img.shields.io/badge/license-MIT-green.svg)

ZeroRAT is a powerful remote administration tool (RAT) designed for Windows systems. It allows remote control via a Telegram bot, offering functionalities such as system monitoring, file manipulation, process control, and persistence mechanisms.

## Features

- **System Information Retrieval**: Fetch CPU, RAM, OS version, and network details.
- **Remote Desktop & Webcam Capture**: Take screenshots and capture webcam images.
- **Clipboard Control**: Retrieve clipboard contents.
- **Audio Control**: Adjust volume, mute/unmute system sound.
- **File Management**: Open URLs, execute commands, and manipulate files.
- **Persistence Mechanisms**: Add to startup, registry, and task scheduler.
- **Shutdown & Restart**: Remotely power off or restart the target system.
- **TTS & Audio Playback**: Use text-to-speech and play received audio files.
- **Telegram Bot Integration**: Command the RAT using a Telegram bot.

## Installation

### Prerequisites

- Python 3.8+
- Required Libraries (install with `pip install -r requirements.txt`)
- Telegram Bot Token (create via [BotFather](https://t.me/botfather))

### Setup

1. Clone the repository:
   ```sh
   git clone https://github.com/jfrzz/ZeroTrace.git
   cd ZeroTrace
   ```

2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Set up your Telegram bot token in `ZeroRAT.py`:
   ```python
   BOT_TOKEN = "your_telegram_bot_token"
   ```

4. Run the bot:
   ```sh
   python ZeroRAT.py
   ```

## Usage

After starting the bot, use the following commands in your Telegram chat:

### Basic Commands
- `/start` - Display client info.
- `/help` - Show available commands.
- `/systeminfo` - Retrieve system specifications.

### Remote Control
- `/screenshot` - Capture the screen.
- `/webcam` - Take a picture using the webcam.
- `/clipboard` - Get clipboard content.
- `/shell [command]` - Execute shell commands.

### System Management
- `/shutdown` - Shutdown the system.
- `/restart` - Restart the system.
- `/maxvolume` - Set volume to maximum.
- `/mutevolume` - Mute the system sound.

### Persistence
- `/persistentkit` - Enable persistence.
- `/removepersistence` - Remove persistence.

## Security & Ethical Usage

**ZeroRAT is intended for ethical security research and authorized remote administration.** Unauthorized use of this tool on any system without explicit consent is illegal. The author is not responsible for any misuse of this software.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to open an issue or submit a pull request.

## Disclaimer

By using this software, you agree to use it only for ethical and legal purposes. Misuse of this tool may result in legal consequences.

---
Developed by **JfrzXCode** | GitHub: [@jfrzz](https://github.com/jfrzz)

