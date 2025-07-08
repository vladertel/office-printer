#!/usr/bin/env python3
import os
import sys

# Import the necessary functions from the bot script
from telegram_printer_bot import read_config, custom_reasons, default_reasons

# Create a test config file
with open('test_config.txt', 'w') as f:
    f.write("""TELEGRAM_BOT_TOKEN=test_token
ALLOWED_USERS=testuser1,testuser2
MINISTRY_NAME=TEST MINISTRY
CITATION_TYPE=TEST CITATION
GLORY_TEXT=TEST GLORY

# Custom reasons
CUSTOM_REASON=Test custom reason 1
CUSTOM_REASON=Test custom reason 2
""")

# Redirect the config file path
os.rename('test_config.txt', 'config.txt')

try:
    # Read the config
    token = read_config()
    
    # Print the results
    print("Token:", token)
    
    print("\nCustom reasons (should be populated from config):")
    for i, reason in enumerate(custom_reasons):
        print(f"{i+1}. {reason}")
    
    print("\nDefault reasons (should remain unchanged):")
    for i, reason in enumerate(default_reasons):
        print(f"{i+1}. {reason}")
    
    # Simulate what the suggest_reasons function would do
    combined_reasons = custom_reasons + default_reasons
    
    print("\nCombined reasons (custom reasons should be at the top):")
    for i, reason in enumerate(combined_reasons):
        print(f"{i+1}. {reason}")
    
    # Verify custom reasons are loaded correctly
    if len(custom_reasons) == 2 and custom_reasons[0] == "Test custom reason 1" and custom_reasons[1] == "Test custom reason 2":
        print("\nTest PASSED: Custom reasons are loaded correctly")
    else:
        print("\nTest FAILED: Custom reasons are not loaded correctly")
        
finally:
    # Clean up
    if os.path.exists('config.txt'):
        os.remove('config.txt')
    
    print("\nTest completed and config file removed.")