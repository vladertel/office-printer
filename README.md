# Telegram Printer Bot

This Python script runs a Telegram bot that automatically prints received messages on a QR204 thermal printer connected to a Raspberry Pi 3B via serial interface. Only authorized users can send messages to the printer, and only ASCII characters are supported.

## Prerequisites

- Raspberry Pi 3B
- QR204 thermal printer connected via serial interface
- Python 3.x installed
- Telegram bot token (obtain from [@BotFather](https://t.me/botfather))
- Telegram usernames of authorized users

## Hardware Setup

1. Connect the QR204 thermal printer to your Raspberry Pi's serial interface (/dev/serial0)
2. Enable serial interface on your Raspberry Pi:
   ```bash
   sudo raspi-config
   # Navigate to Interface Options > Serial > Enable Serial port
   ```

## Installation

1. Clone this repository or download the files to your Raspberry Pi
2. Install the required Python packages:
   ```bash
   pip3 install -r requirements.txt
   ```
3. Configure your bot:
   - Open `config.txt`
   - Replace `<TELEGRAM_BOT_TOKEN>` with your actual bot token from @BotFather
   - On the `ALLOWED_USERS=` line, add the Telegram usernames (without @ symbol) separated by commas
   - Save the file
   - Keep this file secret and never commit it to version control

Example `config.txt`:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
ALLOWED_USERS=john_doe,jane_smith,bob_wilson

# Customizable text elements
MINISTRY_NAME=MINISTRY OF ADMISSION
CITATION_TYPE=CITATION - M.O.A
GLORY_TEXT=GLORY TO ARSTOTZKA

# Custom citation reasons (will appear at the top of the list)
# You can add multiple CUSTOM_REASON lines
CUSTOM_REASON=Unauthorized coffee break
CUSTOM_REASON=Excessive keyboard noise
```

## Running the Bot

1. Make the script executable:
   ```bash
   chmod +x telegram_printer_bot.py
   ```

2. Run the bot:
   ```bash
   ./telegram_printer_bot.py
   ```

## Usage

1. Start a chat with your bot on Telegram
2. If you're an authorized user:
   - Send the `/start` command to initialize the bot
   - Send any text message containing only ASCII characters to print it as a citation
   - Use the `/reasons` command to select from predefined citation reasons (including your custom reasons)
   - Messages with non-ASCII characters (emojis, special symbols, etc.) will be rejected
3. Unauthorized users will receive an error message and their attempts will be logged

### Message Requirements

The bot only accepts messages containing ASCII characters, which include:
- Standard English letters (A-Z, a-z)
- Numbers (0-9)
- Common punctuation marks (!@#$%^&*()_+-=[]{}|;:'",./<>?)
- Basic ASCII symbols (~`\)
- Space and newline characters

Messages containing any other characters (emojis, accented letters, special symbols, etc.) will be rejected with an error message.

## Features

- Prints incoming Telegram messages on the thermal printer
- Includes sender's username and message content
- Restricts access to authorized users only
- Validates messages for ASCII-only characters
- Adds a separator line between messages
- Logs all activity to console
- Sends confirmation messages back to users
- Securely stores bot token and user list in a separate configuration file
- Logs unauthorized access attempts and invalid message formats
- Provides a `/reasons` command to select from predefined citation reasons
- Supports custom citation reasons via configuration (displayed at the top of the list)

## Error Handling

The bot includes basic error handling for:
- Printer issues
- Missing or invalid configuration file
- Invalid bot token
- Unauthorized access attempts
- Non-ASCII character usage
- General runtime errors

The bot will log errors and notify users if there are any problems. 