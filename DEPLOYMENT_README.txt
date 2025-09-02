# 🤖 Habit Tracker Bot - Complete Deployment Package

## 📦 DEPLOYMENT READY PACKAGE
This zip contains everything you need to deploy your habit awareness bot on your own server.

## 🌍 MULTI-LANGUAGE SUPPORT
✅ **English** - Full localization with all commands and messages
✅ **Arabic** - Complete Arabic translation with RTL support

## 📋 ESSENTIAL FILES INCLUDED:
✓ main.py (essential)
✓ bot.py (essential)
✓ models.py (essential)
✓ config.py (essential)
✓ scheduler.py (essential)
✓ cli.py (essential)
✓ language_manager.py (essential)
✓ english.json (essential)
✓ arabic.json (essential)
✓ messages.json (essential)
✓ config.ini (essential)
✓ pyproject.toml (deployment)
✓ uv.lock (deployment)
✓ .replit (deployment)
✓ replit.md (deployment)
✓ README.md (deployment)
✓ sent_messages.log (optional)
✓ telegram_bot.log (optional)

## ❌ MISSING FILES (if any):
✅ All files present!

## 🚀 QUICK DEPLOYMENT GUIDE

### 1. INSTALL DEPENDENCIES
```bash
pip install pyTelegramBotAPI==4.29.0 schedule==1.2.2 pytz==2025.2 psycopg2-binary==2.9.9 configparser==7.2.0
```

### 2. SETUP ENVIRONMENT VARIABLES
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_from_botfather"
export TELEGRAM_CHAT_ID="your_chat_id"
export DATABASE_URL="postgresql://user:password@host:port/database"
```

### 3. RUN THE BOT
```bash
python main.py
```

## 🎯 BOT COMMANDS
- `/help` - Show help message
- `/status` - Show habit statistics  
- `/language` - Switch between English/Arabic
- `/next` - Show next reminder time
- `/zip` - Download complete bot files
- Send habit messages like "I did it" or "فعلتها"

## 📊 FEATURES
✅ **Habit Tracking** - Non-judgmental awareness tracking
✅ **Daily Reminders** - Motivational messages
✅ **Multi-Language** - English & Arabic support
✅ **PostgreSQL Database** - Reliable data storage
✅ **Statistics** - Detailed progress tracking
✅ **Auto-reconnection** - Stable database connections

## 🗄️ DATABASE SETUP
The bot automatically creates these tables:
- `users` - User language preferences
- `habit_entries` - Habit tracking data

## 🔧 CONFIGURATION
Edit `config.ini` to customize:
- Schedule times
- Timezone settings
- Log levels
- Message preferences

## 📝 HABIT TRACKING
**English patterns:** "I did it", "slipped up", "had the habit", "relapsed"
**Arabic patterns:** "فعلتها", "انتكست", "مارست العادة", "رجعت"

## 📞 SUPPORT
For technical support or questions about deployment, refer to the documentation files included.

---
**Package Created:** 2025-09-02 08:41:49 UTC
**Total Files:** 18
**Bot Version:** Multi-Language Habit Tracker v2.0
