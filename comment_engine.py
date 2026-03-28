"""
Comment engine for social media platforms
"""
import time
import random
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import undetected_chromedriver as uc
from fake_useragent import UserAgent
from utils import logger, TextSpinner, DelayManager, RateLimiter, log_activity

class CommentEngine:
    """Handle commenting on different platforms"""
    
    def __init__(self, config: Dict, proxy_manager):
        self.config = config
        self.proxy_manager = proxy_manager
        self.drivers = {}
        self.delay_manager = DelayManager(
            config.get('MIN_DELAY', 10),
            config.get('MAX_DELAY', 60)
        )
        self.rate_limiter = RateLimiter()
        self.comment_templates = config.get('comment_templates', [])
        self.emojis = config.get('emojis', [])
    
    def create_driver(self, account_id: int, proxy: str = None) -> webdriver.Chrome:
        """Create undetected Chrome driver"""
        try:
            options = uc.ChromeOptions()
            
            # Add random user agent
            ua = UserAgent()
            options.add_argument(f'user-agent={ua.random}')
            
            # Add proxy if provided
            if proxy:
                options.add_argument(f'--proxy-server={proxy}')
            
            # Anti-detection settings
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Headless mode (optional)
            if self.config.get('HEADLESS', False):
                options.add_argument('--headless')
            
            driver = uc.Chrome(options=options)
            
            # Execute stealth script
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return driver
            
        except Exception as e:
            logger.error(f"Error creating driver for account {account_id}: {e}")
            return None
    
    def comment_on_facebook(self, account_id: int, post_url: str, comment_text: str) -> bool:
        """Comment on Facebook post"""
        try:
            driver = self.drivers.get(account_id)
            if not driver:
                proxy = self.proxy_manager.get_proxy(account_id)
                driver = self.create_driver(account_id, proxy)
                if not driver:
                    return False
                self.drivers[account_id] = driver
            
            # Navigate to post
            driver.get(post_url)
            time.sleep(random.uniform(3, 5))
            
            # Find comment box
            comment_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[aria-label="Viết bình luận"]'))
            )
            comment_box.click()
            time.sleep(random.uniform(1, 2))
            
            # Type comment with delay
            for char in comment_text:
                comment_box.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            # Post comment
            post_button = driver.find_element(By.CSS_SELECTOR, 'div[aria-label="Bình luận"]')
            post_button.click()
            
            time.sleep(random.uniform(2, 3))
            
            logger.info(f"Commented on Facebook: {comment_text[:50]}...")
            log_activity(f"Account_{account_id}", "comment", "success", comment_text[:50])
            
            return True
            
        except Exception as e:
            logger.error(f"Error commenting on Facebook: {e}")
            log_activity(f"Account_{account_id}", "comment", "failed", str(e))
            return False
    
    def comment_on_tiktok(self, account_id: int, video_url: str, comment_text: str) -> bool:
        """Comment on TikTok video"""
        try:
            driver = self.drivers.get(account_id)
            if not driver:
                proxy = self.proxy_manager.get_proxy(account_id)
                driver = self.create_driver(account_id, proxy)
                if not driver:
                    return False
                self.drivers[account_id] = driver
            
            # Navigate to video
            driver.get(video_url)
            time.sleep(random.uniform(5, 8))
            
            # Scroll to comment section
            driver.execute_script("window.scrollBy(0, 500)")
            time.sleep(random.uniform(2, 3))
            
            # Find comment input
            comment_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-e2e="comment-input"]'))
            )
            comment_input.click()
            time.sleep(random.uniform(1, 2))
            
            # Type comment
            for char in comment_text:
                comment_input.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            # Post comment
            post_button = driver.find_element(By.CSS_SELECTOR, 'button[data-e2e="comment-post"]')
            post_button.click()
            
            time.sleep(random.uniform(2, 3))
            
            logger.info(f"Commented on TikTok: {comment_text[:50]}...")
            log_activity(f"Account_{account_id}", "comment", "success", comment_text[:50])
            
            return True
            
        except Exception as e:
            logger.error(f"Error commenting on TikTok: {e}")
            log_activity(f"Account_{account_id}", "comment", "failed", str(e))
            return False
    
    def comment_on_instagram(self, account_id: int, post_url: str, comment_text: str) -> bool:
        """Comment on Instagram post"""
        try:
            driver = self.drivers.get(account_id)
            if not driver:
                proxy = self.proxy_manager.get_proxy(account_id)
                driver = self.create_driver(account_id, proxy)
                if not driver:
                    return False
                self.drivers[account_id] = driver
            
            # Navigate to post
            driver.get(post_url)
            time.sleep(random.uniform(4, 6))
            
            # Find comment box
            comment_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea[aria-label="Add a comment..."]'))
            )
            comment_box.click()
            time.sleep(random.uniform(1, 2))
            
            # Type comment
            for char in comment_text:
                comment_box.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            # Post comment
            post_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            post_button.click()
            
            time.sleep(random.uniform(2, 3))
            
            logger.info(f"Commented on Instagram: {comment_text[:50]}...")
            log_activity(f"Account_{account_id}", "comment", "success", comment_text[:50])
            
            return True
            
        except Exception as e:
            logger.error(f"Error commenting on Instagram: {e}")
            log_activity(f"Account_{account_id}", "comment", "failed", str(e))
            return False
    
    def execute_comment_task(self, account_id: int, platform: str, 
                            post_url: str, comment_text: str = None) -> bool:
        """Execute comment task"""
        # Rate limiting check
        if not self.rate_limiter.can_proceed():
            logger.warning("Rate limit reached, waiting...")
            time.sleep(60)
            return False
        
        # Generate comment if not provided
        if not comment_text:
            comment_text = TextSpinner.generate_comment(
                self.comment_templates, 
                self.emojis
            )
        
        # Platform-specific commenting
        if platform == 'facebook':
            success = self.comment_on_facebook(account_id, post_url, comment_text)
        elif platform == 'tiktok':
            success = self.comment_on_tiktok(account_id, post_url, comment_text)
        elif platform == 'instagram':
            success = self.comment_on_instagram(account_id, post_url, comment_text)
        else:
            logger.error(f"Unsupported platform: {platform}")
            return False
        
        # Report to proxy manager
        if success:
            self.proxy_manager.report_success(account_id)
        else:
            self.proxy_manager.report_failure(account_id)
        
        # Random delay between comments
        if success:
            self.delay_manager.random_delay()
        
        return success
    
    def close_driver(self, account_id: int):
        """Close driver for account"""
        if account_id in self.drivers:
            try:
                self.drivers[account_id].quit()
            except:
                pass
            del self.drivers[account_id]
    
    def close_all_drivers(self):
        """Close all drivers"""
        for account_id in list(self.drivers.keys()):
            self.close_driver(account_id)
