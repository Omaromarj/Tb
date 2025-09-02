"""
Telegram Bot implementation using telebot
"""

import os
import logging
import telebot
from datetime import datetime, date
import json
import re
import zipfile
import tempfile
from models import HabitTracker
from language_manager import LanguageManager

class TelegramBot:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize bot with token
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN', config.bot_token)
        if not bot_token:
            raise ValueError("Telegram bot token is required")
        
        self.bot = telebot.TeleBot(bot_token)
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID', config.chat_id)
        
        if not self.chat_id:
            raise ValueError("Telegram chat ID is required")
        
        # Initialize habit tracker
        try:
            self.habit_tracker = HabitTracker()
        except Exception as e:
            self.logger.error(f"Failed to initialize habit tracker: {e}")
            self.habit_tracker = None
        
        # Initialize language manager
        try:
            self.language_manager = LanguageManager()
        except Exception as e:
            self.logger.error(f"Failed to initialize language manager: {e}")
            self.language_manager = None
            
        # Setup bot handlers
        self._setup_handlers()
    
    def _get_user_language(self, user_id):
        """Get user's language preference"""
        if not self.habit_tracker:
            return 'english'
        try:
            return self.habit_tracker.get_user_language(user_id)
        except Exception as e:
            self.logger.error(f"Failed to get user language: {e}")
            return 'english'
    
    def _get_text(self, user_id, category, key, **kwargs):
        """Get localized text for user"""
        if not self.language_manager:
            return "Language system not available"
        
        language = self._get_user_language(user_id)
        return self.language_manager.get_text(language, category, key, **kwargs)
    
    def _setup_handlers(self):
        """Setup bot command handlers"""
        
        @self.bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            user_id = message.from_user.id
            help_text = self._get_text(user_id, 'commands', 'welcome')
            self.bot.reply_to(message, help_text)
        
        @self.bot.message_handler(commands=['status', 'stats'])
        def send_status(message):
            try:
                user_id = message.from_user.id
                
                if not self.habit_tracker:
                    error_text = self._get_text(user_id, 'status', 'tracking_unavailable')
                    self.bot.reply_to(message, error_text)
                    return
                
                stats = self.habit_tracker.get_user_stats(user_id)
                
                if not stats:
                    error_text = self._get_text(user_id, 'status', 'error_getting_stats')
                    self.bot.reply_to(message, error_text)
                    return
                
                status_text = self._get_text(user_id, 'status', 'title')
                
                if stats['last_entry']:
                    last_date = stats['last_entry']['entry_date']
                    status_text += self._get_text(user_id, 'status', 'last_entry', date=last_date)
                    
                    if stats['days_since_last'] is not None:
                        days = stats['days_since_last']
                        if days == 0:
                            status_text += self._get_text(user_id, 'status', 'today')
                        elif days == 1:
                            status_text += self._get_text(user_id, 'status', 'yesterday')
                        else:
                            status_text += self._get_text(user_id, 'status', 'days_ago', days=days)
                else:
                    status_text += self._get_text(user_id, 'status', 'no_entries')
                
                status_text += self._get_text(user_id, 'status', 'total_entries', count=stats['total_count'])
                status_text += self._get_text(user_id, 'status', 'next_reminder', 
                                            time=self.config.schedule_time, 
                                            timezone=self.config.timezone)
                
                self.bot.reply_to(message, status_text)
                
            except Exception as e:
                self.logger.error(f"Error getting status: {e}")
                error_text = self._get_text(message.from_user.id, 'status', 'error_getting_stats')
                self.bot.reply_to(message, error_text)
        
        @self.bot.message_handler(commands=['language'])
        def change_language(message):
            user_id = message.from_user.id
            language_text = self._get_text(user_id, 'language', 'select')
            
            # Create inline keyboard for language selection
            markup = telebot.types.InlineKeyboardMarkup()
            english_btn = telebot.types.InlineKeyboardButton("🇺🇸 English", callback_data="lang_english")
            arabic_btn = telebot.types.InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_arabic")
            markup.row(english_btn, arabic_btn)
            
            self.bot.reply_to(message, language_text, reply_markup=markup)
        
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
        def handle_language_callback(call):
            user_id = call.from_user.id
            
            try:
                if not self.habit_tracker:
                    response = "❌ Language system not available"
                elif call.data == 'lang_english':
                    self.habit_tracker.set_user_language(user_id, 'english')
                    response = self._get_text(user_id, 'language', 'changed_to_english')
                elif call.data == 'lang_arabic':
                    self.habit_tracker.set_user_language(user_id, 'arabic')
                    response = self._get_text(user_id, 'language', 'changed_to_arabic')
                else:
                    response = self._get_text(user_id, 'language', 'invalid_choice')
                
                # Delete the original message with buttons
                try:
                    self.bot.delete_message(call.message.chat.id, call.message.message_id)
                except:
                    pass  # If delete fails, just continue
                
                # Send confirmation message
                self.bot.send_message(call.message.chat.id, response)
                self.bot.answer_callback_query(call.id)
                
            except Exception as e:
                self.logger.error(f"Error handling language callback: {e}")
                try:
                    self.bot.answer_callback_query(call.id, "❌ Error changing language")
                except:
                    pass
        
        @self.bot.message_handler(commands=['test'])
        def send_test(message):
            user_id = message.from_user.id
            test_message = self._get_text(user_id, 'general', 'test_message')
            try:
                self.send_message(test_message)
                success_text = self._get_text(user_id, 'general', 'test_sent')
                self.bot.reply_to(message, success_text)
            except Exception as e:
                self.logger.error(f"Error sending test message: {e}")
                error_text = self._get_text(user_id, 'general', 'test_failed')
                self.bot.reply_to(message, error_text)
        
        @self.bot.message_handler(commands=['next'])
        def show_next_message(message):
            try:
                user_id = message.from_user.id
                from scheduler import MessageScheduler
                next_run = MessageScheduler.get_next_run_time(self.config.schedule_time)
                response = self._get_text(user_id, 'general', 'next_reminder', time=next_run)
                self.bot.reply_to(message, response)
            except Exception as e:
                self.logger.error(f"Error getting next run time: {e}")
                user_id = message.from_user.id
                error_text = self._get_text(user_id, 'general', 'error_next_time')
                self.bot.reply_to(message, error_text)
        
        @self.bot.message_handler(commands=['zip'])
        def send_zip(message):
            try:
                user_id = message.from_user.id
                creating_text = self._get_text(user_id, 'general', 'creating_zip')
                self.bot.reply_to(message, creating_text)
                
                # Create zip file with all relevant files
                zip_path = self._create_program_zip()
                
                if zip_path and os.path.exists(zip_path):
                    with open(zip_path, 'rb') as zip_file:
                        self.bot.send_document(message.chat.id, zip_file, caption="🤖 Your complete habit tracker bot files")
                    
                    # Clean up temporary file
                    os.remove(zip_path)
                    self.logger.info(f"Sent program zip to user {user_id}")
                else:
                    error_text = self._get_text(user_id, 'general', 'zip_failed')
                    self.bot.reply_to(message, error_text)
                    
            except Exception as e:
                self.logger.error(f"Error sending zip: {e}")
                user_id = message.from_user.id
                error_text = self._get_text(user_id, 'general', 'zip_error')
                self.bot.reply_to(message, error_text)
        
        # Handler for habit tracking messages
        @self.bot.message_handler(func=lambda message: self._is_habit_message(message.text, message.from_user.id))
        def track_habit(message):
            try:
                user_id = message.from_user.id
                
                if not self.habit_tracker:
                    error_text = self._get_text(user_id, 'tracking', 'failed_to_record')
                    self.bot.reply_to(message, error_text)
                    return
                
                # Add the entry
                entry = self.habit_tracker.add_entry(user_id, message.text)
                
                if not entry:
                    error_text = self._get_text(user_id, 'tracking', 'failed_to_record')
                    self.bot.reply_to(message, error_text)
                    return
                
                # Get updated stats
                stats = self.habit_tracker.get_user_stats(user_id)
                
                response = self._get_text(user_id, 'tracking', 'entry_recorded')
                
                if stats and stats['last_entry']:
                    last_date = stats['last_entry']['entry_date']
                    response += self._get_text(user_id, 'tracking', 'last_time', date=last_date)
                    
                    if stats['days_since_last'] is not None:
                        days = stats['days_since_last']
                        if days == 0:
                            response += self._get_text(user_id, 'tracking', 'was_today')
                        elif days == 1:
                            response += self._get_text(user_id, 'tracking', 'was_yesterday')
                        else:
                            response += self._get_text(user_id, 'tracking', 'was_days_ago', days=days)
                
                response += self._get_text(user_id, 'tracking', 'total_times', count=stats['total_count'] if stats else 0)
                response += self._get_text(user_id, 'tracking', 'awareness_message')
                
                self.bot.reply_to(message, response)
                
            except Exception as e:
                self.logger.error(f"Error tracking habit: {e}")
                user_id = message.from_user.id
                error_text = self._get_text(user_id, 'tracking', 'error_recording')
                self.bot.reply_to(message, error_text)
    
    def _is_habit_message(self, text, user_id):
        """Check if a message indicates habit occurrence"""
        if not text or not self.language_manager:
            return False
        
        user_language = self._get_user_language(user_id)
        return self.language_manager.is_habit_message(text, user_language)
    
    def test_connection(self):
        """Test bot connection to Telegram"""
        try:
            me = self.bot.get_me()
            self.logger.info(f"Bot connected: @{me.username}")
            return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def send_message(self, message, parse_mode=None):
        """Send message to configured chat"""
        try:
            sent_message = self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode
            )
            self.logger.info(f"Message sent successfully to chat {self.chat_id}")
            
            # Log sent message
            self._log_sent_message(message)
            
            return sent_message
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            raise
    
    def send_daily_message(self):
        """Send scheduled daily message"""
        try:
            # Get user language (use chat_id as user_id for daily messages)
            user_id = int(self.chat_id)
            user_language = self._get_user_language(user_id)
            
            # Get daily message in user's language
            if self.language_manager:
                message = self.language_manager.get_daily_message(user_language)
            else:
                # Fallback to old method
                with open('messages.json', 'r') as f:
                    data = json.load(f)
                daily_messages = data.get('daily_messages', [])
                if daily_messages:
                    today = datetime.now()
                    message_index = today.timetuple().tm_yday % len(daily_messages)
                    message = daily_messages[message_index]
                else:
                    message = "Stay mindful today!"
            
            # Add date and personalized awareness info
            if self.config.include_date:
                formatted_date = datetime.now().strftime("%B %d, %Y")
                
                # Get user stats for personalized message
                user_stats = None
                if self.habit_tracker:
                    try:
                        user_stats = self.habit_tracker.get_user_stats(user_id)
                    except:
                        pass
                
                awareness_text = ""
                if user_stats and user_stats['days_since_last'] is not None:
                    days = user_stats['days_since_last']
                    if self.language_manager:
                        if days == 0:
                            awareness_text = self.language_manager.get_text(user_language, 'awareness_progress', 'new_opportunity')
                        elif days == 1:
                            awareness_text = self.language_manager.get_text(user_language, 'awareness_progress', 'one_day')
                        elif days < 7:
                            awareness_text = self.language_manager.get_text(user_language, 'awareness_progress', 'few_days', days=days)
                        else:
                            awareness_text = self.language_manager.get_text(user_language, 'awareness_progress', 'many_days', days=days)
                    else:
                        # Fallback English awareness text
                        if days == 0:
                            awareness_text = "\n🔄 Remember, today is a new opportunity for awareness."
                        elif days == 1:
                            awareness_text = "\n💚 One day of awareness complete."
                        elif days < 7:
                            awareness_text = f"\n💚 {days} days of awareness. Stay mindful."
                        else:
                            awareness_text = f"\n🌟 {days} days of awareness. You're building strong patterns!"
                
                message = f"📅 {formatted_date}\n\n{message}{awareness_text}"
            
            self.send_message(message)
            
        except Exception as e:
            self.logger.error(f"Failed to send daily message: {e}")
            # Send error notification
            error_msg = f"❌ Failed to send scheduled message: {str(e)}"
            try:
                self.send_message(error_msg)
            except:
                pass
    
    def _log_sent_message(self, message):
        """Log sent message to file"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'message': message[:100] + "..." if len(message) > 100 else message,
                'chat_id': self.chat_id
            }
            
            # Append to log file
            try:
                with open('sent_messages.log', 'r') as f:
                    logs = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                logs = []
            
            logs.append(log_entry)
            
            # Keep only last 100 entries
            logs = logs[-100:]
            
            with open('sent_messages.log', 'w') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to log sent message: {e}")
    
    def _create_program_zip(self):
        """Create a zip file containing all bot files"""
        try:
            # Essential files for deployment
            essential_files = [
                'main.py',           # Main entry point
                'bot.py',            # Telegram bot implementation  
                'models.py',         # Database models
                'config.py',         # Configuration management
                'scheduler.py',      # Message scheduling
                'cli.py',            # Command line interface
                'language_manager.py', # Multi-language support
                'english.json',      # English language file
                'arabic.json',       # Arabic language file
                'messages.json',     # Legacy messages (fallback)
                'config.ini'         # Configuration file
            ]
            
            # Deployment support files
            deployment_files = [
                'pyproject.toml',    # Python project config
                'uv.lock',           # Package lock file
                '.replit',           # Replit configuration
                'replit.md',         # Project documentation
                'README.md'          # General documentation
            ]
            
            # Optional log files
            optional_files = [
                'sent_messages.log',
                'telegram_bot.log'
            ]
            
            # Combine all files to check
            all_files_to_check = essential_files + deployment_files + optional_files
            
            # Create temporary zip file
            temp_dir = tempfile.gettempdir()
            zip_filename = f"habit_tracker_bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            zip_path = os.path.join(temp_dir, zip_filename)
            
            files_added = []
            files_missing = []
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add essential files (these are critical for deployment)
                for filename in essential_files:
                    if os.path.exists(filename):
                        zipf.write(filename, filename)
                        files_added.append(f"✓ {filename} (essential)")
                        self.logger.info(f"Added essential file {filename} to zip")
                    else:
                        files_missing.append(f"✗ {filename} (essential - MISSING!)")
                        self.logger.error(f"Essential file {filename} not found!")
                
                # Add deployment support files
                for filename in deployment_files:
                    if os.path.exists(filename):
                        zipf.write(filename, filename)
                        files_added.append(f"✓ {filename} (deployment)")
                        self.logger.info(f"Added deployment file {filename} to zip")
                    else:
                        files_missing.append(f"✗ {filename} (deployment)")
                        self.logger.warning(f"Deployment file {filename} not found")
                
                # Add optional files if they exist
                for filename in optional_files:
                    if os.path.exists(filename):
                        zipf.write(filename, filename)
                        files_added.append(f"✓ {filename} (optional)")
                        self.logger.info(f"Added optional file {filename} to zip")
                
                # Create comprehensive deployment README
                deployment_readme = f"""# 🤖 Habit Tracker Bot - Complete Deployment Package

## 📦 DEPLOYMENT READY PACKAGE
This zip contains everything you need to deploy your habit awareness bot on your own server.

## 🌍 MULTI-LANGUAGE SUPPORT
✅ **English** - Full localization with all commands and messages
✅ **Arabic** - Complete Arabic translation with RTL support

## 📋 ESSENTIAL FILES INCLUDED:
{chr(10).join(files_added)}

## ❌ MISSING FILES (if any):
{chr(10).join(files_missing) if files_missing else "✅ All files present!"}

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
**Package Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
**Total Files:** {len(files_added)}
**Bot Version:** Multi-Language Habit Tracker v2.0
"""
                
                # Add the deployment README to the zip
                zipf.writestr('DEPLOYMENT_README.txt', deployment_readme)
                
                # Create a requirements.txt file for easy deployment
                requirements_content = """# Habit Tracker Bot Dependencies
# Install with: pip install -r requirements.txt

pyTelegramBotAPI==4.29.0
schedule==1.2.2
pytz==2025.2
psycopg2-binary==2.9.9
configparser==7.2.0
"""
                zipf.writestr('requirements.txt', requirements_content)
            
            self.logger.info(f"Created deployment zip: {zip_path}")
            self.logger.info(f"Files included: {len(files_added)}")
            if files_missing:
                self.logger.warning(f"Missing files: {len(files_missing)}")
            
            return zip_path
            
        except Exception as e:
            self.logger.error(f"Failed to create zip file: {e}")
            return None
    
    def start_polling(self):
        """Start bot polling for incoming messages"""
        try:
            self.logger.info("Starting bot polling...")
            self.bot.infinity_polling(none_stop=True, timeout=10, long_polling_timeout=5)
        except Exception as e:
            self.logger.error(f"Polling error: {e}")
