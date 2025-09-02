"""
Language Manager for multi-language support
"""

import json
import logging
from pathlib import Path

class LanguageManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.languages = {}
        self.load_languages()
    
    def load_languages(self):
        """Load language files"""
        try:
            # Load English
            with open('english.json', 'r', encoding='utf-8') as f:
                self.languages['english'] = json.load(f)
            
            # Load Arabic
            with open('arabic.json', 'r', encoding='utf-8') as f:
                self.languages['arabic'] = json.load(f)
            
            self.logger.info("Language files loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load language files: {e}")
            # Fallback to basic English
            self.languages['english'] = {
                "commands": {"welcome": "Welcome! Language files not found."},
                "general": {"error": "Error loading languages"}
            }
    
    def get_text(self, language, category, key, **kwargs):
        """Get text for specific language, category and key"""
        try:
            # Default to English if language not found
            if language not in self.languages:
                language = 'english'
            
            # Get the text
            text = self.languages[language].get(category, {}).get(key, "Text not found")
            
            # Format with provided arguments
            if kwargs:
                text = text.format(**kwargs)
            
            return text
        except Exception as e:
            self.logger.error(f"Failed to get text: {e}")
            return "Error loading text"
    
    def get_daily_message(self, language):
        """Get a random daily message"""
        try:
            import random
            if language not in self.languages:
                language = 'english'
            
            messages = self.languages[language].get('daily_messages', ['Stay mindful today!'])
            return random.choice(messages)
        except Exception as e:
            self.logger.error(f"Failed to get daily message: {e}")
            return "Stay mindful today!"
    
    def get_habit_patterns(self, language):
        """Get habit recognition patterns for a language"""
        try:
            if language == 'arabic':
                return self.languages['arabic'].get('habit_patterns', [])
            else:
                # English patterns (default)
                return [
                    "i did it", "did it", "slipped up", "had the habit", 
                    "relapsed", "fell back", "messed up", "gave in",
                    "happened again", "went back to it", "did the thing",
                    "broke my streak", "couldn't resist", "lost control"
                ]
        except Exception as e:
            self.logger.error(f"Failed to get habit patterns: {e}")
            return ["did it", "slipped up"]
    
    def is_habit_message(self, text, language):
        """Check if a message indicates a habit occurrence"""
        try:
            patterns = self.get_habit_patterns(language)
            text_lower = text.lower()
            return any(pattern in text_lower for pattern in patterns)
        except Exception as e:
            self.logger.error(f"Failed to check habit message: {e}")
            return False