# Telegram Daily Message Bot 🤖

A Python application that sends controllable daily Telegram messages with scheduling features. Stay motivated with personalized daily messages delivered directly to your Telegram chat!

## Features

- 📱 **Daily Telegram Messages**: Automated daily message delivery
- ⏰ **Flexible Scheduling**: Customize time and timezone
- 💬 **Message Management**: Add, edit, and delete daily messages
- 🎛️ **CLI Interface**: Easy-to-use command-line management
- 🔄 **Retry Logic**: Automatic retry on failed deliveries
- 📊 **Status Monitoring**: Track bot status and message history
- 🛡️ **Error Handling**: Robust error handling and logging

## Quick Start

### 1. Create a Telegram Bot

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the instructions
3. Save your bot token (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Get Your Chat ID

1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. Save your chat ID (numerical ID)

### 3. Configure the Bot

Edit `config.ini` with your bot token and chat ID:

```ini
[TELEGRAM]
bot_token = YOUR_BOT_TOKEN_HERE
chat_id = YOUR_CHAT_ID_HERE

[SCHEDULE]
time = 09:00
timezone = UTC
