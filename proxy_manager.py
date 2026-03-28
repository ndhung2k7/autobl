"""
Proxy management module
"""
import random
import time
import requests
from typing import List, Dict, Optional
from urllib.parse import urlparse
import socks
import socket
from utils import logger, ProxyTester

class ProxyManager:
    """Manage proxies for accounts"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.proxy_pool = {}
        self.failed_proxies = {}
        self.test_url = config.get('PROXY_TEST_URL', 'http://httpbin.org/ip')
        self.max_failures = 3
        self.failure_timeout = 300  # 5 minutes
    
    def add_proxy(self, account_id: int, proxy: str) -> bool:
        """Add proxy for account"""
        try:
            # Validate proxy format
            if not self._validate_proxy_format(proxy):
                logger.error(f"Invalid proxy format: {proxy}")
                return False
            
            # Test proxy
            if ProxyTester.test_proxy(proxy, self.test_url):
                self.proxy_pool[account_id] = {
                    'proxy': proxy,
                    'failures': 0,
                    'last_failure': None
                }
                logger.info(f"Proxy added for account {account_id}: {proxy}")
                return True
            else:
                logger.error(f"Proxy test failed: {proxy}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding proxy: {e}")
            return False
    
    def remove_proxy(self, account_id: int) -> bool:
        """Remove proxy for account"""
        if account_id in self.proxy_pool:
            del self.proxy_pool[account_id]
            logger.info(f"Proxy removed for account {account_id}")
            return True
        return False
    
    def get_proxy(self, account_id: int) -> Optional[str]:
        """Get proxy for account"""
        if account_id in self.proxy_pool:
            proxy_info = self.proxy_pool[account_id]
            
            # Check if proxy has too many failures
            if proxy_info['failures'] >= self.max_failures:
                last_failure = proxy_info['last_failure']
                if time.time() - last_failure < self.failure_timeout:
                    logger.warning(f"Proxy for account {account_id} is blocked temporarily")
                    return None
                else:
                    # Reset failures after timeout
                    proxy_info['failures'] = 0
                    proxy_info['last_failure'] = None
            
            return proxy_info['proxy']
        
        return None
    
    def report_failure(self, account_id: int):
        """Report proxy failure"""
        if account_id in self.proxy_pool:
            self.proxy_pool[account_id]['failures'] += 1
            self.proxy_pool[account_id]['last_failure'] = time.time()
            logger.warning(f"Proxy failure reported for account {account_id}")
    
    def report_success(self, account_id: int):
        """Report proxy success"""
        if account_id in self.proxy_pool:
            self.proxy_pool[account_id]['failures'] = 0
    
    def get_proxy_stats(self) -> Dict:
        """Get proxy statistics"""
        stats = {
            'total': len(self.proxy_pool),
            'active': 0,
            'failed': 0
        }
        
        for account_id, proxy_info in self.proxy_pool.items():
            if proxy_info['failures'] >= self.max_failures:
                stats['failed'] += 1
            else:
                stats['active'] += 1
        
        return stats
    
    def _validate_proxy_format(self, proxy: str) -> bool:
        """Validate proxy URL format"""
        try:
            # Check if proxy has authentication
            if '@' in proxy:
                # Format: user:pass@ip:port
                auth_part, host_part = proxy.split('@')
                if ':' not in auth_part:
                    return False
            else:
                host_part = proxy
            
            # Parse host:port
            if ':' not in host_part:
                return False
            
            host, port = host_part.split(':')
            if not port.isdigit():
                return False
            
            return True
            
        except Exception:
            return False
    
    def get_proxy_for_request(self, account_id: int) -> Dict:
        """Get proxy dict for requests library"""
        proxy_url = self.get_proxy(account_id)
        if proxy_url:
            return {
                'http': proxy_url,
                'https': proxy_url
            }
        return None
    
    def rotate_proxy(self, account_id: int, new_proxy: str) -> bool:
        """Rotate to new proxy"""
        self.remove_proxy(account_id)
        return self.add_proxy(account_id, new_proxy)
