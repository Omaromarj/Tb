# Overview

This is a Telegram Habit Awareness Bot built in Python that helps users track their progress with unwanted habits through mindful awareness rather than judgment. The bot automatically sends daily motivational messages focused on awareness and mindfulness, while tracking habit occurrences without resetting counters. It provides detailed statistics showing the last occurrence, total count, and days since the last entry. The system features full multi-language support with English and Arabic languages, uses PostgreSQL for data persistence, the Telegram Bot API for messaging, and includes comprehensive logging and error handling.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Application Structure
The application follows a modular architecture with clear separation of concerns:

- **main.py**: Entry point handling argument parsing, configuration loading, and application lifecycle
- **config.py**: Configuration management using INI files with environment variable overrides
- **bot.py**: Telegram Bot API integration using the telebot library
- **scheduler.py**: Message scheduling using the schedule library with timezone support
- **cli.py**: Command-line interface for message management and bot administration
- **language_manager.py**: Multi-language support system for Arabic and English
- **models.py**: Database models including user language preferences and habit tracking

## Multi-Language System
The bot supports full localization with Arabic and English languages:
- **english.json**: Contains all English text including commands, status messages, daily motivational messages, and UI text
- **arabic.json**: Contains all Arabic translations with proper RTL support and culturally appropriate content
- **language_manager.py**: Centralized language handling that loads language files and provides text retrieval methods
- **Database Storage**: User language preferences are stored in PostgreSQL for persistence across sessions
- **Automatic Detection**: The system recognizes habit-related phrases in both languages for accurate tracking
- **Dynamic Switching**: Users can change language preference using the /language command with inline keyboard interface

## Message Management System
Messages are stored in multiple JSON files for multi-language support:
- **messages.json**: Legacy daily messages (maintained for compatibility)
- **english.json** and **arabic.json**: Localized content including daily messages, commands, and all UI text
- Metadata including creation and modification timestamps
- Simple file-based persistence for easy portability and backup

## Scheduling Architecture
The scheduler uses a thread-based approach:
- **schedule** library for cron-like scheduling functionality
- Configurable time and timezone settings
- Retry logic with exponential backoff for failed message deliveries
- Graceful shutdown handling with signal management

## Configuration Management
Multi-layered configuration system:
- INI file-based configuration with sections for Telegram, Schedule, and Application settings
- Environment variable overrides for sensitive data (bot tokens, chat IDs)
- Default value fallbacks for all configuration options
- Automatic config file creation if missing

## Error Handling and Logging
Comprehensive logging system:
- File-based logging with rotation capabilities
- Console output for real-time monitoring
- Configurable log levels
- Structured error handling with retry mechanisms

# External Dependencies

## Telegram Bot API
- **telebot (pyTelegramBotAPI)**: Python wrapper for Telegram Bot API
- Requires bot token from @BotFather
- Handles message sending, command processing, and webhook management

## Scheduling Libraries
- **schedule**: Python job scheduling library for cron-like functionality
- **pytz**: Timezone handling and conversion utilities

## Configuration and Data
- **configparser**: Built-in Python library for INI file parsing
- **json**: Built-in library for message data persistence
- **pathlib**: Modern path handling utilities

## System Integration
- **logging**: Built-in Python logging framework
- **signal**: Unix signal handling for graceful shutdown
- **threading**: Multi-threading support for concurrent scheduler operations
- **argparse**: Command-line argument parsing

## Required Environment Setup
- Python 3.6+ runtime environment
- Telegram bot token (obtained from @BotFather)
- Target chat ID (obtained from @userinfobot or Telegram API)
- Write permissions for log files and message data storage