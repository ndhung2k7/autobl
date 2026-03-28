"""
Scheduler for auto comment tasks
"""
import time
import threading
import schedule
from typing import List, Dict, Callable
from datetime import datetime, timedelta
from utils import logger, DelayManager

class CommentScheduler:
    """Manage scheduling of comment tasks"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.delay_manager = DelayManager(
            config.get('account_delay', {}).get('min', 30),
            config.get('account_delay', {}).get('max', 120)
        )
        self.tasks = []
        self.running = False
        self.thread = None
        self.account_delays = {}  # Track last comment time per account
    
    def add_task(self, account_id: int, platform: str, 
                 post_url: str, comment_text: str = None,
                 interval: int = None) -> Dict:
        """Add comment task"""
        task = {
            'id': len(self.tasks) + 1,
            'account_id': account_id,
            'platform': platform,
            'post_url': post_url,
            'comment_text': comment_text,
            'interval': interval or 300,  # Default 5 minutes
            'last_run': None,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        self.tasks.append(task)
        logger.info(f"Task added: {task}")
        return task
    
    def remove_task(self, task_id: int) -> bool:
        """Remove task"""
        for task in self.tasks:
            if task['id'] == task_id:
                self.tasks.remove(task)
                logger.info(f"Task {task_id} removed")
                return True
        return False
    
    def get_tasks(self) -> List[Dict]:
        """Get all tasks"""
        return self.tasks
    
    def execute_task(self, task: Dict, comment_engine) -> bool:
        """Execute single task"""
        try:
            # Check account delay
            account_id = task['account_id']
            if account_id in self.account_delays:
                last_comment = self.account_delays[account_id]
                min_delay = self.config.get('account_delay', {}).get('min', 30)
                if (datetime.now() - last_comment).total_seconds() < min_delay:
                    logger.info(f"Account {account_id} still in delay period")
                    return False
            
            # Execute comment
            success = comment_engine.execute_comment_task(
                account_id,
                task['platform'],
                task['post_url'],
                task.get('comment_text')
            )
            
            # Update last run time
            if success:
                task['last_run'] = datetime.now()
                self.account_delays[account_id] = datetime.now()
                task['status'] = 'success'
            else:
                task['status'] = 'failed'
            
            return success
            
        except Exception as e:
            logger.error(f"Error executing task {task['id']}: {e}")
            task['status'] = 'error'
            return False
    
    def run_continuous(self, comment_engine, callback: Callable = None):
        """Run tasks continuously"""
        self.running = True
        self.thread = threading.Thread(target=self._continuous_loop, 
                                      args=(comment_engine, callback))
        self.thread.daemon = True
        self.thread.start()
        logger.info("Scheduler started in continuous mode")
    
    def run_scheduled(self, comment_engine, callback: Callable = None):
        """Run tasks on schedule"""
        self.running = True
        self.thread = threading.Thread(target=self._scheduled_loop, 
                                      args=(comment_engine, callback))
        self.thread.daemon = True
        self.thread.start()
        logger.info("Scheduler started in scheduled mode")
    
    def _continuous_loop(self, comment_engine, callback):
        """Continuous execution loop"""
        while self.running:
            for task in self.tasks:
                if task['status'] == 'pending' or task['status'] == 'failed':
                    self.execute_task(task, comment_engine)
                    
                    # Random delay between tasks
                    delay = self.delay_manager.random_delay()
                    time.sleep(delay)
                    
                    if callback:
                        callback(task)
            
            # Wait before next round
            time.sleep(60)
    
    def _scheduled_loop(self, comment_engine, callback):
        """Scheduled execution loop"""
        # Schedule tasks
        for task in self.tasks:
            interval = task['interval']
            schedule.every(interval).seconds.do(self.execute_task, task, comment_engine)
        
        while self.running:
            schedule.run_pending()
            time.sleep(1)
            
            if callback:
                # Trigger callback with latest tasks
                callback(self.tasks)
    
    def stop(self):
        """Stop scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Scheduler stopped")
    
    def update_task_interval(self, task_id: int, interval: int) -> bool:
        """Update task interval"""
        for task in self.tasks:
            if task['id'] == task_id:
                task['interval'] = interval
                logger.info(f"Task {task_id} interval updated to {interval}s")
                return True
        return False
