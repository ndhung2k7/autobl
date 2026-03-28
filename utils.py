"""
Utility functions for auto comment tool
"""
import random
import time
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
from fake_useragent import UserAgent
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_comment.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TextSpinner:
    """Handle text spinning for unique comments"""
    
    @staticmethod
    def spin_text(text: str) -> str:
        """Randomly spin text with {option1|option2} syntax"""
        import re
        
        def replace_option(match):
            options = match.group(1).split('|')
            return random.choice(options)
        
        pattern = r'\{([^{}]+)\}'
        spun_text = re.sub(pattern, replace_option, text)
        return spun_text
    
    @staticmethod
    def generate_comment(templates: List[str], emojis: List[str]) -> str:
        """Generate random comment from templates"""
        template = random.choice(templates)
        comment = TextSpinner.spin_text(template)
        
        # Add emoji if placeholder exists
        if '{emoji}' in comment:
            emoji = random.choice(emojis)
            comment = comment.replace('{emoji}', emoji)
        
        return comment

class DelayManager:
    """Manage delays between actions"""
    
    def __init__(self, min_delay: int = 10, max_delay: int = 60):
        self.min_delay = min_delay
        self.max_delay = max_delay
    
    def random_delay(self) -> None:
        """Sleep for random duration"""
        delay = random.uniform(self.min_delay, self.max_delay)
        logger.debug(f"Waiting for {delay:.2f} seconds")
        time.sleep(delay)
    
    def human_like_delay(self) -> None:
        """More human-like delay with typing simulation"""
        # Simulate reading time
        time.sleep(random.uniform(1, 3))
        # Simulate typing
        time.sleep(random.uniform(0.5, 2))

class RateLimiter:
    """Rate limiting mechanism"""
    
    def __init__(self, max_requests: int = 60, time_window: int = 3600):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def can_proceed(self) -> bool:
        """Check if request can proceed"""
        current_time = time.time()
        # Clean old requests
        self.requests = [t for t in self.requests 
                        if current_time - t < self.time_window]
        
        if len(self.requests) >= self.max_requests:
            wait_time = self.requests[0] + self.time_window - current_time
            logger.warning(f"Rate limit reached. Wait {wait_time:.2f} seconds")
            return False
        
        self.requests.append(current_time)
        return True

class ProxyTester:
    """Test proxy connectivity"""
    
    @staticmethod
    def test_proxy(proxy: str, test_url: str = 'http://httpbin.org/ip') -> bool:
        """Test if proxy is working"""
        try:
            proxies = {
                'http': proxy,
                'https': proxy
            }
            response = requests.get(test_url, proxies=proxies, timeout=10)
            if response.status_code == 200:
                logger.info(f"Proxy {proxy} is working")
                return True
        except Exception as e:
            logger.error(f"Proxy {proxy} test failed: {e}")
        return False

class DataValidator:
    """Validate input data"""
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return bool(url_pattern.match(url))
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate username format"""
        return bool(username and len(username) >= 3)

def log_activity(account: str, action: str, status: str, details: str = ''):
    """Log user activity"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'account': account,
        'action': action,
        'status': status,
        'details': details
    }
    logger.info(f"Activity: {json.dumps(log_entry)}")
    return log_entry
