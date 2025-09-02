"""
Database models for habit tracking
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, date
import logging

class HabitTracker:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.connection = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Connect to PostgreSQL database"""
        try:
            database_url = os.getenv('DATABASE_URL')
            if not database_url:
                raise ValueError("DATABASE_URL environment variable is required")
            
            self.connection = psycopg2.connect(
                database_url,
                cursor_factory=RealDictCursor
            )
            self.logger.info("Connected to database successfully")
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            raise
    
    def _ensure_connection(self):
        """Ensure database connection is alive, reconnect if needed"""
        try:
            if not self.connection or self.connection.closed:
                self.logger.info("Database connection lost, reconnecting...")
                self._connect()
            else:
                # Test the connection
                with self.connection.cursor() as cursor:
                    cursor.execute('SELECT 1')
        except Exception as e:
            self.logger.warning(f"Connection test failed, reconnecting: {e}")
            try:
                self._connect()
            except Exception as reconnect_error:
                self.logger.error(f"Failed to reconnect: {reconnect_error}")
                raise
    
    def _create_tables(self):
        """Create habit entries and users tables if they don't exist"""
        try:
            if self.connection:
                with self.connection.cursor() as cursor:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS users (
                            user_id BIGINT PRIMARY KEY,
                            language VARCHAR(10) DEFAULT 'english',
                            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                        );
                        
                        CREATE TABLE IF NOT EXISTS habit_entries (
                            id SERIAL PRIMARY KEY,
                            user_id BIGINT NOT NULL,
                            entry_date DATE NOT NULL DEFAULT CURRENT_DATE,
                            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            notes TEXT
                        );
                        
                        CREATE INDEX IF NOT EXISTS idx_habit_entries_user_date 
                        ON habit_entries(user_id, entry_date);
                        
                        CREATE INDEX IF NOT EXISTS idx_users_user_id 
                        ON users(user_id);
                    """)
                    self.connection.commit()
                    self.logger.info("Database tables created successfully")
        except Exception as e:
            self.logger.error(f"Failed to create tables: {e}")
            raise
    
    def add_entry(self, user_id, notes=None):
        """Add a new habit entry for today"""
        try:
            self._ensure_connection()
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO habit_entries (user_id, notes) 
                    VALUES (%s, %s)
                    RETURNING id, entry_date, created_at
                """, (user_id, notes))
                
                result = cursor.fetchone()
                self.connection.commit()
                
                self.logger.info(f"Added habit entry for user {user_id}")
                return result
        except Exception as e:
            self.logger.error(f"Failed to add entry: {e}")
            try:
                if self.connection and not self.connection.closed:
                    self.connection.rollback()
            except:
                pass
            raise
    
    def get_last_entry(self, user_id):
        """Get the most recent habit entry for a user"""
        try:
            self._ensure_connection()
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT entry_date, created_at, notes
                    FROM habit_entries 
                    WHERE user_id = %s 
                    ORDER BY entry_date DESC, created_at DESC 
                    LIMIT 1
                """, (user_id,))
                
                return cursor.fetchone()
        except Exception as e:
            self.logger.error(f"Failed to get last entry: {e}")
            return None
    
    def get_total_count(self, user_id):
        """Get total number of habit entries for a user"""
        try:
            self._ensure_connection()
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) as total_count
                    FROM habit_entries 
                    WHERE user_id = %s
                """, (user_id,))
                
                result = cursor.fetchone()
                return int(result['total_count']) if result else 0
        except Exception as e:
            self.logger.error(f"Failed to get total count: {e}")
            return 0
    
    def get_days_since_last(self, user_id):
        """Get number of days since last habit entry"""
        try:
            last_entry = self.get_last_entry(user_id)
            if not last_entry:
                return None
            
            last_date = last_entry['entry_date']
            today = date.today()
            
            days_diff = (today - last_date).days
            return days_diff
        except Exception as e:
            self.logger.error(f"Failed to calculate days since last: {e}")
            return None
    
    def get_user_stats(self, user_id):
        """Get comprehensive stats for a user"""
        try:
            last_entry = self.get_last_entry(user_id)
            total_count = self.get_total_count(user_id)
            days_since = self.get_days_since_last(user_id)
            
            return {
                'last_entry': last_entry,
                'total_count': total_count,
                'days_since_last': days_since
            }
        except Exception as e:
            self.logger.error(f"Failed to get user stats: {e}")
            return None
    
    def get_user_language(self, user_id):
        """Get user's language preference"""
        try:
            self._ensure_connection()
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT language FROM users WHERE user_id = %s
                """, (user_id,))
                
                result = cursor.fetchone()
                if result:
                    return result['language']
                else:
                    # Create new user with default language
                    return self.set_user_language(user_id, 'english')
        except Exception as e:
            self.logger.error(f"Failed to get user language: {e}")
            return 'english'  # Default fallback
    
    def set_user_language(self, user_id, language):
        """Set user's language preference"""
        try:
            self._ensure_connection()
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO users (user_id, language) 
                    VALUES (%s, %s)
                    ON CONFLICT (user_id) 
                    DO UPDATE SET 
                        language = EXCLUDED.language,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING language
                """, (user_id, language))
                
                result = cursor.fetchone()
                self.connection.commit()
                
                self.logger.info(f"Set language for user {user_id} to {language}")
                return result['language'] if result else language
        except Exception as e:
            self.logger.error(f"Failed to set user language: {e}")
            try:
                if self.connection and not self.connection.closed:
                    self.connection.rollback()
            except:
                pass
            return language  # Return requested language as fallback
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.logger.info("Database connection closed")