"""
Main entry point for Auto Comment Tool
"""
import os
import sys
import json
import threading
from dotenv import load_dotenv
from account_manager import AccountManager
from proxy_manager import ProxyManager
from comment_engine import CommentEngine
from scheduler import CommentScheduler
from web_dashboard import WebDashboard
from utils import logger

# Load environment variables
load_dotenv()

class AutoCommentTool:
    """Main application class"""
    
    def __init__(self):
        self.config = self.load_config()
        self.account_manager = AccountManager()
        self.proxy_manager = ProxyManager(self.config)
        self.comment_engine = CommentEngine(self.config, self.proxy_manager)
        self.scheduler = CommentScheduler(self.config)
        self.dashboard = WebDashboard(
            self.account_manager,
            self.proxy_manager,
            self.comment_engine,
            self.scheduler,
            self.config
        )
    
    def load_config(self):
        """Load configuration from file"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Override with environment variables
            config['PROXY_TEST_URL'] = os.getenv('PROXY_TEST_URL', config.get('PROXY_TEST_URL'))
            config['MIN_DELAY'] = int(os.getenv('MIN_DELAY', config.get('MIN_DELAY', 10)))
            config['MAX_DELAY'] = int(os.getenv('MAX_DELAY', config.get('MAX_DELAY', 60)))
            
            return config
            
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def start(self):
        """Start the application"""
        logger.info("Starting Auto Comment Tool...")
        
        # Start web dashboard in a separate thread
        dashboard_thread = threading.Thread(
            target=self.dashboard.run,
            kwargs={'host': '0.0.0.0', 'port': 5000, 'debug': False},
            daemon=True
        )
        dashboard_thread.start()
        
        logger.info("Web dashboard started at http://localhost:5000")
        logger.info("Press Ctrl+C to stop")
        
        try:
            # Keep main thread alive
            while True:
                import time
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self.scheduler.stop()
            self.comment_engine.close_all_drivers()
            logger.info("Shutdown complete")

def main():
    """Main function"""
    tool = AutoCommentTool()
    tool.start()

if __name__ == '__main__':
    main()
