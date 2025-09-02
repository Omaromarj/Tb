"""
Message scheduling functionality
"""

import schedule
import time
import logging
import threading
from datetime import datetime, timedelta
import pytz

class MessageScheduler:
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.scheduler_thread = None
        
        self._setup_schedule()
    
    def _setup_schedule(self):
        """Setup the daily message schedule"""
        try:
            # Clear existing schedules
            schedule.clear()
            
            # Schedule daily message
            schedule.every().day.at(self.config.schedule_time).do(self._send_scheduled_message)
            
            self.logger.info(f"Daily message scheduled for {self.config.schedule_time} ({self.config.timezone})")
            
        except Exception as e:
            self.logger.error(f"Failed to setup schedule: {e}")
            raise
    
    def _send_scheduled_message(self):
        """Send scheduled message with retry logic"""
        attempt = 1
        max_attempts = self.config.retry_attempts
        
        while attempt <= max_attempts:
            try:
                self.logger.info(f"Sending daily message (attempt {attempt}/{max_attempts})")
                self.bot.send_daily_message()
                self.logger.info("Daily message sent successfully")
                return
                
            except Exception as e:
                self.logger.error(f"Attempt {attempt} failed: {e}")
                
                if attempt < max_attempts:
                    self.logger.info(f"Retrying in {self.config.retry_delay} seconds...")
                    time.sleep(self.config.retry_delay)
                else:
                    self.logger.error("All retry attempts failed")
                    # Send failure notification
                    try:
                        error_msg = f"❌ Failed to send daily message after {max_attempts} attempts.\nLast error: {str(e)}"
                        self.bot.send_message(error_msg)
                    except:
                        self.logger.error("Failed to send error notification")
                
                attempt += 1
    
    def start(self):
        """Start the scheduler in a separate thread"""
        if self.running:
            self.logger.warning("Scheduler is already running")
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.info("Message scheduler started")
        
        # Send startup notification
        try:
            startup_msg = f"🤖 Daily Message Bot started!\n\n📅 Next message scheduled for: {self.get_next_run_time(self.config.schedule_time)}"
            self.bot.send_message(startup_msg)
        except Exception as e:
            self.logger.error(f"Failed to send startup notification: {e}")
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        schedule.clear()
        self.logger.info("Message scheduler stopped")
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
                time.sleep(60)  # Wait longer on error
    
    @staticmethod
    def get_next_run_time(schedule_time, timezone_str='UTC'):
        """Get the next scheduled run time"""
        try:
            # Parse schedule time
            hour, minute = map(int, schedule_time.split(':'))
            
            # Get timezone
            tz = pytz.timezone(timezone_str) if timezone_str != 'UTC' else pytz.UTC
            
            # Get current time in specified timezone
            now = datetime.now(tz)
            
            # Create next scheduled time
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # If the time has already passed today, schedule for tomorrow
            if next_run <= now:
                next_run += timedelta(days=1)
            
            return next_run.strftime("%Y-%m-%d %H:%M:%S %Z")
            
        except Exception as e:
            return f"Error calculating next run time: {e}"
    
    def reschedule(self, new_time):
        """Reschedule the daily message time"""
        try:
            self.config.schedule_time = new_time
            self._setup_schedule()
            self.logger.info(f"Rescheduled daily message to {new_time}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to reschedule: {e}")
            return False
    
    def get_status(self):
        """Get scheduler status information"""
        jobs = schedule.jobs
        status = {
            'running': self.running,
            'scheduled_jobs': len(jobs),
            'next_run': self.get_next_run_time(self.config.schedule_time, self.config.timezone) if jobs else "No jobs scheduled"
        }
        return status
