#!/bin/bash

# Define the virtual environment base directory
VENV_CFG_PATH="/home/e/pos/pyvenv.cfg"
VENV_DIR=$(dirname "$VENV_CFG_PATH")

# Check if the virtual environment exists
if [ ! -f "$VENV_CFG_PATH" ]; then
    echo "Error: Virtual environment configuration not found at $VENV_CFG_PATH"
    exit 1
fi

# Activate the virtual environment
if [ -f "$VENV_DIR/bin/activate" ]; then
    # Source the activate script to configure the environment
    source "$VENV_DIR/bin/activate"
    
    echo "Virtual environment activated from $VENV_DIR"
    echo "Python version: $(python3 --version)"
    echo "Python path: $(which python3)"

    python3 ./office-printer/telegram_printer_bot.py

    # Deactivate the virtual environment when done
    deactivate
else
    echo "Error: Virtual environment activation script not found at $VENV_DIR/bin/activate"
    exit 1
fi