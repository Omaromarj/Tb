#!/usr/bin/env python3
"""
Main entry point for the Telegram Daily Message Bot
"""

import sys
import argparse
import logging
import signal
import time
from config import Config
from bot import TelegramBot
from scheduler import MessageScheduler
from cli import CLI

def setup_logging(config):
    """Setup logging configuration"""
    # Set up file logging (detailed)
    file_handler = logging.FileHandler('telegram_bot.log')
    file_handler.setLevel(logging.INFO)
    
    # Set up console logging (errors only to reduce spam)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.ERROR)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler]
    )

def signal_handler(signum, frame):
    """Handle graceful shutdown"""
    logging.info("Received shutdown signal. Stopping bot...")
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description='Telegram Daily Message Bot')
    parser.add_argument('--config', default='config.ini', help='Configuration file path')
    parser.add_argument('--cli', action='store_true', help='Run in CLI mode')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    
    args = parser.parse_args()
    
    # Load configuration
    try:
        config = Config(args.config)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)
    
    # Setup logging
    setup_logging(config)
    logger = logging.getLogger(__name__)
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if args.cli:
        # Run CLI interface
        cli = CLI(config)
        cli.run()
    else:
        # Run bot daemon
        logger.info("Starting Telegram Daily Message Bot")
        
        try:
            # Initialize bot
            bot = TelegramBot(config)
            scheduler = MessageScheduler(bot, config)
            
            # Test bot connection
            if not bot.test_connection():
                logger.error("Failed to connect to Telegram. Check your bot token.")
                sys.exit(1)
            
            logger.info("Bot connected successfully")
            
            # Start scheduler
            scheduler.start()
            
            # Start bot polling to listen for commands
            logger.info("Starting bot polling for incoming messages...")
            bot.start_polling()
                
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
