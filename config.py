"""
Configuration management for Telegram Daily Message Bot
"""

import configparser
import os
import logging
from pathlib import Path

class Config:
    def __init__(self, config_file='config.ini'):
        self.config_file = config_file
        self.logger = logging.getLogger(__name__)
        
        # Default values
        self.bot_token = ""
        self.chat_id = ""
        self.schedule_time = "09:00"
        self.timezone = "UTC"
        self.log_level = "INFO"
        self.include_date = True
        self.retry_attempts = 3
        self.retry_delay = 60
        
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        config_path = Path(self.config_file)
        
        if not config_path.exists():
            self.logger.info(f"Config file {self.config_file} not found, creating default")
            self._create_default_config()
            return
        
        try:
            config = configparser.ConfigParser()
            config.read(self.config_file)
            
            # Telegram settings
            telegram_section = config['TELEGRAM']
            self.bot_token = telegram_section.get('bot_token', self.bot_token)
            self.chat_id = telegram_section.get('chat_id', self.chat_id)
            
            # Schedule settings
            schedule_section = config['SCHEDULE']
            self.schedule_time = schedule_section.get('time', self.schedule_time)
            self.timezone = schedule_section.get('timezone', self.timezone)
            
            # Application settings
            app_section = config['APPLICATION']
            self.log_level = app_section.get('log_level', self.log_level)
            self.include_date = app_section.getboolean('include_date', self.include_date)
            self.retry_attempts = app_section.getint('retry_attempts', self.retry_attempts)
            self.retry_delay = app_section.getint('retry_delay', self.retry_delay)
            
            self.logger.info("Configuration loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            raise
    
    def _create_default_config(self):
        """Create default configuration file"""
        config = configparser.ConfigParser()
        
        config['TELEGRAM'] = {
            'bot_token': '# Get from @BotFather on Telegram',
            'chat_id': '# Your Telegram chat ID'
        }
        
        config['SCHEDULE'] = {
            'time': '09:00',
            'timezone': 'UTC'
        }
        
        config['APPLICATION'] = {
            'log_level': 'INFO',
            'include_date': 'true',
            'retry_attempts': '3',
            'retry_delay': '60'
        }
        
        try:
            with open(self.config_file, 'w') as f:
                config.write(f)
            self.logger.info(f"Default configuration created at {self.config_file}")
        except Exception as e:
            self.logger.error(f"Failed to create default configuration: {e}")
            raise
    
    def save(self):
        """Save current configuration to file"""
        config = configparser.ConfigParser()
        
        config['TELEGRAM'] = {
            'bot_token': self.bot_token,
            'chat_id': self.chat_id
        }
        
        config['SCHEDULE'] = {
            'time': self.schedule_time,
            'timezone': self.timezone
        }
        
        config['APPLICATION'] = {
            'log_level': self.log_level,
            'include_date': str(self.include_date).lower(),
            'retry_attempts': str(self.retry_attempts),
            'retry_delay': str(self.retry_delay)
        }
        
        try:
            with open(self.config_file, 'w') as f:
                config.write(f)
            self.logger.info("Configuration saved successfully")
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            raise
    
    def validate(self):
        """Validate configuration values"""
        errors = []
        
        # Check required fields
        if not self.bot_token or self.bot_token.startswith('#'):
            errors.append("Bot token is required")
        
        if not self.chat_id or self.chat_id.startswith('#'):
            errors.append("Chat ID is required")
        
        # Validate schedule time format
        try:
            time_parts = self.schedule_time.split(':')
            if len(time_parts) != 2:
                raise ValueError
            hour, minute = int(time_parts[0]), int(time_parts[1])
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError
        except ValueError:
            errors.append("Schedule time must be in HH:MM format (24-hour)")
        
        # Validate numeric values
        if self.retry_attempts < 1:
            errors.append("Retry attempts must be at least 1")
        
        if self.retry_delay < 0:
            errors.append("Retry delay must be non-negative")
        
        if errors:
            raise ValueError("Configuration validation failed: " + "; ".join(errors))
        
        return True
