#!/usr/bin/env python3

import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from escpos.printer import Serial
import textwrap
from datetime import datetime

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global configuration
printer = None
allowed_users = set()
ministry_name = "MINISTRY OF ADMISSION"  # Default value
citation_type = "CITATION - M.O.A"      # Default value
glory_text = "GLORY TO ARSTOTZKA"       # Default value

def is_ascii(text: str) -> bool:
    """Check if the text contains only ASCII characters."""
    try:
        text.encode('ascii')
        return True
    except UnicodeEncodeError:
        return False

def center_text(text: str, width: int = 32) -> str:
    """Center text within given width."""
    text = text.strip()
    padding = width - len(text)
    left_padding = padding // 2
    return " " * left_padding + text

def format_citation(username: str, message: str) -> str:
    """Format message as a citation."""
    # Get current date
    current_date = datetime.now().strftime("%Y.%m.%d")
    
    # Create the header
    header = [
        "********************************",  # 32 chars
        f"*{center_text(ministry_name, 30)}*",
        f"*{center_text(citation_type, 30)}*",
        "********************************",
        f"DATE: {current_date}",
        "--------------------------------"
    ]
    
    # Format the message content with word wrap
    content = []
    # Wrap text to 30 chars to account for margins
    wrapped_text = textwrap.wrap(message, width=30)
    for line in wrapped_text:
        content.append(line)
    
    # Add footer
    footer = [
        "--------------------------------",
        f"BY: @{username}",
        f"{center_text(glory_text, 32)}",
        "********************************"
    ]
    
    # Combine all parts
    citation = header + [""] + content + [""] + footer
    
    # Return formatted text
    return "\n".join(citation) + "\n"

def read_config():
    """Read the configuration from config file."""
    global allowed_users, ministry_name, citation_type, glory_text
    try:
        with open('config.txt', 'r') as file:
            token = None
            
            for line in file:
                line = line.strip()
                if line.startswith('#'):  # Skip comments
                    continue
                    
                if line.startswith('TELEGRAM_BOT_TOKEN='):
                    token = line.split('=')[1]
                    if not token or token == '<TELEGRAM_BOT_TOKEN>':
                        raise ValueError("Bot token not found or not set in config.txt")
                elif line.startswith('ALLOWED_USERS='):
                    users_part = line.split('=')[1]
                    if users_part:
                        allowed_users.update(
                            username.strip().lower() 
                            for username in users_part.split(',')
                            if username.strip()
                        )
                elif line.startswith('MINISTRY_NAME='):
                    ministry_name = line.split('=')[1].strip()
                elif line.startswith('CITATION_TYPE='):
                    citation_type = line.split('=')[1].strip()
                elif line.startswith('GLORY_TEXT='):
                    glory_text = line.split('=')[1].strip()
            
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
        await update.message.reply_text("ACCESS DENIED - No valid entry permit")
        logger.warning(f"Unauthorized access attempt by @{user.username}")
        return

    welcome_message = (
        "APPROVED FOR ENTRY\n\n"
        f"{ministry_name}\n"
        "Official Communications Channel\n\n"
        "Send message to generate citation.\n"
        "ASCII characters only.\n\n"
        f"{glory_text}!"
    )
    await update.message.reply_text(welcome_message)

async def print_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Print the received message on the thermal printer."""
    user = update.message.from_user
    
    # Check if user is authorized
    if not is_user_authorized(user.username):
        await update.message.reply_text("Sorry, you are not authorized to use this bot.")
        logger.warning(f"Unauthorized message attempt by @{user.username}")
        return
    
    message_text = update.message.text
    
    # Check if message contains only ASCII characters
    if not is_ascii(message_text):
        await update.message.reply_text("Error: Message contains non-ASCII characters. Please use only ASCII characters (standard English letters, numbers, and punctuation).")
        logger.warning(f"Non-ASCII message attempt from @{user.username}: {message_text}")
        return
    
    # Log the message
    logger.info(f"Received message from @{user.username}: {message_text}")
    
    try:
        # Format and print the message as a citation
        formatted_message = format_citation(user.username, message_text)
        printer.text(formatted_message)
        printer.text("\n" * 2)  # Add some spacing after the citation
        
        # Send confirmation to user
        await update.message.reply_text(f"Citation has been printed! {glory_text}! 🖨")
    except Exception as e:
        error_message = f"Failed to print citation: {str(e)}"
        logger.error(error_message)
        await update.message.reply_text("Sorry, there was an error printing your citation.")

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

        # Print welcome message on thermal printer
        printer.text("********************************\n")
        printer.text(f"*   {center_text(ministry_name, 24)}    *\n")
        printer.text("*    PRINTER ACTIVATED       *\n")
        printer.text("********************************\n")
        printer.text("\n")
        printer.text("READY TO PROCESS CITATIONS\n")
        printer.text(f"{glory_text}\n")
        printer.text("\n")
        
        # Start the Bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")
        raise

if __name__ == '__main__':
    main() 