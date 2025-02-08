#!/usr/bin/env python3

import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from escpos.printer import Serial

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Printer configuration
printer = None
allowed_users = set()

def read_config():
    """Read the configuration from config file."""
    global allowed_users
    try:
        with open('config.txt', 'r') as file:
            token = None
            
            for line in file:
                line = line.strip()
                if line.startswith('TELEGRAM_BOT_TOKEN='):
                    token = line.split('=')[1]
                    if not token or token == '<TELEGRAM_BOT_TOKEN>':
                        raise ValueError("Bot token not found or not set in config.txt")
                elif line.startswith('ALLOWED_USERS='):
                    # Split the line at '=' and get the users part
                    users_part = line.split('=')[1]
                    # Split by comma and add each username to the set
                    if users_part:
                        allowed_users.update(
                            username.strip().lower() 
                            for username in users_part.split(',')
                            if username.strip()
                        )
            
            if not allowed_users:
                raise ValueError("No allowed users specified in config.txt")
            
            return token
            
    except FileNotFoundError:
        raise FileNotFoundError("config.txt file not found. Please create it with your bot token and allowed users.")

def is_user_authorized(username: str) -> bool:
    """Check if a user is authorized to use the bot."""
    return username.lower() in allowed_users

def init_printer():
    """Initialize the thermal printer with the specified settings."""
    global printer
    printer = Serial(
        devfile='/dev/serial0',
        baudrate=9600,
        bytesize=8,
        parity='N',
        stopbits=1,
        timeout=1.00,
        dsrdtr=True
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user = update.message.from_user
    if not is_user_authorized(user.username):
        await update.message.reply_text("Sorry, you are not authorized to use this bot.")
        logger.warning(f"Unauthorized access attempt by @{user.username}")
        return

    welcome_message = "Welcome! I will print any message you send me on the thermal printer."
    await update.message.reply_text(welcome_message)
    
    # Print welcome message on thermal printer
    printer.text("Bot started! Ready to print messages.\n")
    printer.text(f"Authorized user @{user.username} connected\n")
    printer.text("-" * 32 + "\n")

async def print_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Print the received message on the thermal printer."""
    user = update.message.from_user
    
    # Check if user is authorized
    if not is_user_authorized(user.username):
        await update.message.reply_text("Sorry, you are not authorized to use this bot.")
        logger.warning(f"Unauthorized message attempt by @{user.username}")
        return
    
    message_text = update.message.text
    
    # Log the message
    logger.info(f"Received message from @{user.username}: {message_text}")
    
    try:
        # Format and print the message
        printer.text(message_text + "\n")
        printer.text("-" * 32 + "\n" * 4)  # Separator
        # Send confirmation to user
        await update.message.reply_text("Message has been printed! 🖨")
    except Exception as e:
        error_message = f"Failed to print message: {str(e)}"
        logger.error(error_message)
        await update.message.reply_text("Sorry, there was an error printing your message.")

def main():
    """Start the bot."""
    try:
        # Get the configuration
        token = read_config()
        
        # Initialize printer
        init_printer()
        
        # Log the authorized users
        logger.info(f"Authorized users: {', '.join(sorted(allowed_users))}")
        
        # Create the Application and pass it your bot's token
        application = Application.builder().token(token).build()

        # Add command handlers
        application.add_handler(CommandHandler("start", start))
        
        # Add message handler
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, print_message))

        # Start the Bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")
        raise

if __name__ == '__main__':
    main() 