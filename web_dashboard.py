"""
Web dashboard for managing auto comment tool
"""
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import threading
import os
from utils import logger

class WebDashboard:
    """Web interface for the tool"""
    
    def __init__(self, account_manager, proxy_manager, 
                 comment_engine, scheduler, config):
        self.app = Flask(__name__)
        CORS(self.app)
        self.account_manager = account_manager
        self.proxy_manager = proxy_manager
        self.comment_engine = comment_engine
        self.scheduler = scheduler
        self.config = config
        
        self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            return send_from_directory('static', 'index.html')
        
        @self.app.route('/api/accounts', methods=['GET'])
        def get_accounts():
            accounts = self.account_manager.get_accounts()
            return jsonify(accounts)
        
        @self.app.route('/api/accounts', methods=['POST'])
        def add_account():
            data = request.json
            success = self.account_manager.add_account(
                username=data.get('username'),
                password=data.get('password'),
                cookie=data.get('cookie'),
                token=data.get('token'),
                proxy=data.get('proxy'),
                platform=data.get('platform', 'facebook')
            )
            return jsonify({'success': success})
        
        @self.app.route('/api/accounts/<int:account_id>', methods=['PUT'])
        def update_account(account_id):
            data = request.json
            success = self.account_manager.update_account(account_id, **data)
            return jsonify({'success': success})
        
        @self.app.route('/api/accounts/<int:account_id>', methods=['DELETE'])
        def delete_account(account_id):
            success = self.account_manager.delete_account(account_id)
            return jsonify({'success': success})
        
        @self.app.route('/api/proxy/test', methods=['POST'])
        def test_proxy():
            data = request.json
            proxy = data.get('proxy')
            from utils import ProxyTester
            working = ProxyTester.test_proxy(proxy)
            return jsonify({'working': working})
        
        @self.app.route('/api/proxy/stats', methods=['GET'])
        def proxy_stats():
            stats = self.proxy_manager.get_proxy_stats()
            return jsonify(stats)
        
        @self.app.route('/api/tasks', methods=['GET'])
        def get_tasks():
            tasks = self.scheduler.get_tasks()
            return jsonify(tasks)
        
        @self.app.route('/api/tasks', methods=['POST'])
        def add_task():
            data = request.json
            task = self.scheduler.add_task(
                account_id=data.get('account_id'),
                platform=data.get('platform'),
                post_url=data.get('post_url'),
                comment_text=data.get('comment_text'),
                interval=data.get('interval')
            )
            return jsonify(task)
        
        @self.app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
        def delete_task(task_id):
            success = self.scheduler.remove_task(task_id)
            return jsonify({'success': success})
        
        @self.app.route('/api/control/start', methods=['POST'])
        def start_scheduler():
            data = request.json
            mode = data.get('mode', 'continuous')
            
            if mode == 'continuous':
                self.scheduler.run_continuous(self.comment_engine)
            else:
                self.scheduler.run_scheduled(self.comment_engine)
            
            return jsonify({'success': True, 'mode': mode})
        
        @self.app.route('/api/control/stop', methods=['POST'])
        def stop_scheduler():
            self.scheduler.stop()
            return jsonify({'success': True})
        
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            status = {
                'running': self.scheduler.running,
                'total_accounts': len(self.account_manager.get_accounts()),
                'active_proxies': self.proxy_manager.get_proxy_stats()['active'],
                'total_tasks': len(self.scheduler.get_tasks())
            }
            return jsonify(status)
        
        @self.app.route('/api/config', methods=['GET'])
        def get_config():
            return jsonify(self.config)
        
        @self.app.route('/api/config', methods=['PUT'])
        def update_config():
            data = request.json
            self.config.update(data)
            # Save to file
            with open('config.json', 'w') as f:
                json.dump(self.config, f, indent=2)
            return jsonify({'success': True})
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the web server"""
        self.app.run(host=host, port=port, debug=debug)
