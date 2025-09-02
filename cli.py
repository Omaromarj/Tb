"""
Command Line Interface for managing the Telegram bot
"""

import json
import sys
import logging
from datetime import datetime
from pathlib import Path

class CLI:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.messages_file = 'messages.json'
        
        # Ensure messages file exists
        self._ensure_messages_file()
    
    def _ensure_messages_file(self):
        """Ensure messages.json file exists with default structure"""
        messages_path = Path(self.messages_file)
        
        if not messages_path.exists():
            default_data = {
                "daily_messages": [
                    "🌅 Good morning! Have a wonderful day ahead!",
                    "💪 Stay strong and keep pushing forward!",
                    "🌟 You're doing great! Keep up the good work!",
                    "🎯 Focus on your goals and make today count!",
                    "✨ Every day is a new opportunity to shine!"
                ],
                "created_at": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat()
            }
            
            try:
                with open(self.messages_file, 'w') as f:
                    json.dump(default_data, f, indent=2)
                print(f"Created default messages file: {self.messages_file}")
            except Exception as e:
                print(f"Error creating messages file: {e}")
                sys.exit(1)
    
    def run(self):
        """Run the CLI interface"""
        print("=" * 50)
        print("  Telegram Daily Message Bot - CLI Interface")
        print("=" * 50)
        
        while True:
            self._show_menu()
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == '1':
                self._list_messages()
            elif choice == '2':
                self._add_message()
            elif choice == '3':
                self._edit_message()
            elif choice == '4':
                self._delete_message()
            elif choice == '5':
                self._show_config()
            elif choice == '6':
                self._edit_config()
            elif choice == '7':
                self._test_bot()
            elif choice == '8':
                print("Goodbye! 👋")
                break
            else:
                print("❌ Invalid choice. Please try again.")
            
            input("\nPress Enter to continue...")
    
    def _show_menu(self):
        """Display the main menu"""
        print("\n" + "=" * 50)
        print("📋 MAIN MENU")
        print("=" * 50)
        print("1. 📝 List daily messages")
        print("2. ➕ Add new message")
        print("3. ✏️  Edit message")
        print("4. 🗑️  Delete message")
        print("5. ⚙️  Show configuration")
        print("6. 🔧 Edit configuration")
        print("7. 🧪 Test bot connection")
        print("8. 🚪 Exit")
    
    def _list_messages(self):
        """List all daily messages"""
        try:
            with open(self.messages_file, 'r') as f:
                data = json.load(f)
            
            messages = data.get('daily_messages', [])
            
            print("\n📝 DAILY MESSAGES")
            print("-" * 30)
            
            if not messages:
                print("No messages configured.")
                return
            
            for i, message in enumerate(messages, 1):
                print(f"{i}. {message}")
            
            print(f"\nTotal messages: {len(messages)}")
            
        except Exception as e:
            print(f"❌ Error reading messages: {e}")
    
    def _add_message(self):
        """Add a new daily message"""
        print("\n➕ ADD NEW MESSAGE")
        print("-" * 20)
        
        message = input("Enter new message: ").strip()
        
        if not message:
            print("❌ Message cannot be empty.")
            return
        
        try:
            with open(self.messages_file, 'r') as f:
                data = json.load(f)
            
            data['daily_messages'].append(message)
            data['last_modified'] = datetime.now().isoformat()
            
            with open(self.messages_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print("✅ Message added successfully!")
            
        except Exception as e:
            print(f"❌ Error adding message: {e}")
    
    def _edit_message(self):
        """Edit an existing message"""
        self._list_messages()
        
        try:
            with open(self.messages_file, 'r') as f:
                data = json.load(f)
            
            messages = data.get('daily_messages', [])
            
            if not messages:
                print("No messages to edit.")
                return
            
            print("\n✏️ EDIT MESSAGE")
            print("-" * 15)
            
            choice = input("Enter message number to edit: ").strip()
            
            try:
                index = int(choice) - 1
                if not (0 <= index < len(messages)):
                    print("❌ Invalid message number.")
                    return
            except ValueError:
                print("❌ Please enter a valid number.")
                return
            
            current_message = messages[index]
            print(f"\nCurrent message: {current_message}")
            
            new_message = input("Enter new message (or press Enter to keep current): ").strip()
            
            if new_message:
                messages[index] = new_message
                data['last_modified'] = datetime.now().isoformat()
                
                with open(self.messages_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                print("✅ Message updated successfully!")
            else:
                print("Message unchanged.")
                
        except Exception as e:
            print(f"❌ Error editing message: {e}")
    
    def _delete_message(self):
        """Delete a message"""
        self._list_messages()
        
        try:
            with open(self.messages_file, 'r') as f:
                data = json.load(f)
            
            messages = data.get('daily_messages', [])
            
            if not messages:
                print("No messages to delete.")
                return
            
            print("\n🗑️ DELETE MESSAGE")
            print("-" * 16)
            
            choice = input("Enter message number to delete: ").strip()
            
            try:
                index = int(choice) - 1
                if not (0 <= index < len(messages)):
                    print("❌ Invalid message number.")
                    return
            except ValueError:
                print("❌ Please enter a valid number.")
                return
            
            message_to_delete = messages[index]
            print(f"\nMessage to delete: {message_to_delete}")
            
            confirm = input("Are you sure? (y/N): ").strip().lower()
            
            if confirm in ['y', 'yes']:
                messages.pop(index)
                data['last_modified'] = datetime.now().isoformat()
                
                with open(self.messages_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                print("✅ Message deleted successfully!")
            else:
                print("Delete cancelled.")
                
        except Exception as e:
            print(f"❌ Error deleting message: {e}")
    
    def _show_config(self):
        """Show current configuration"""
        print("\n⚙️ CURRENT CONFIGURATION")
        print("-" * 25)
        print(f"Bot Token: {'*' * 20}...{self.config.bot_token[-4:] if len(self.config.bot_token) > 4 else '(not set)'}")
        print(f"Chat ID: {self.config.chat_id}")
        print(f"Schedule Time: {self.config.schedule_time}")
        print(f"Timezone: {self.config.timezone}")
        print(f"Log Level: {self.config.log_level}")
        print(f"Include Date: {self.config.include_date}")
        print(f"Retry Attempts: {self.config.retry_attempts}")
        print(f"Retry Delay: {self.config.retry_delay}s")
    
    def _edit_config(self):
        """Edit configuration"""
        print("\n🔧 EDIT CONFIGURATION")
        print("-" * 20)
        print("Leave blank to keep current value")
        print()
        
        # Schedule time
        current_time = self.config.schedule_time
        new_time = input(f"Schedule time ({current_time}): ").strip()
        if new_time:
            try:
                # Validate time format
                time_parts = new_time.split(':')
                if len(time_parts) != 2:
                    raise ValueError
                hour, minute = int(time_parts[0]), int(time_parts[1])
                if not (0 <= hour <= 23 and 0 <= minute <= 59):
                    raise ValueError
                self.config.schedule_time = new_time
            except ValueError:
                print("❌ Invalid time format. Keeping current value.")
        
        # Chat ID
        current_chat = self.config.chat_id
        new_chat = input(f"Chat ID ({current_chat}): ").strip()
        if new_chat:
            self.config.chat_id = new_chat
        
        # Include date
        current_date = str(self.config.include_date)
        new_date = input(f"Include date in messages ({current_date}) [true/false]: ").strip().lower()
        if new_date in ['true', 'false']:
            self.config.include_date = new_date == 'true'
        
        try:
            self.config.save()
            print("✅ Configuration saved successfully!")
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")
    
    def _test_bot(self):
        """Test bot connection"""
        print("\n🧪 TESTING BOT CONNECTION")
        print("-" * 25)
        
        try:
            from bot import TelegramBot
            bot = TelegramBot(self.config)
            
            if bot.test_connection():
                print("✅ Bot connection successful!")
                
                # Send test message
                send_test = input("Send test message? (y/N): ").strip().lower()
                if send_test in ['y', 'yes']:
                    test_msg = "🧪 This is a test message from CLI interface!"
                    bot.send_message(test_msg)
                    print("✅ Test message sent!")
            else:
                print("❌ Bot connection failed!")
                
        except Exception as e:
            print(f"❌ Error testing bot: {e}")
