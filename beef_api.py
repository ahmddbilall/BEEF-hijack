#!/usr/bin/env python3
"""
BeEF API Module
Handles all BeEF API interactions with proper authentication and error handling
"""
import requests
import time
import re
from rich.console import Console

console = Console()

class BeEFAPI:
    """BeEF Framework API wrapper"""
    
    def __init__(self, host="localhost", port=3000, username="beef", password="123456"):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.base_url = f"http://{host}:{port}"
        self.token = None
        self._token_attempts = 0
        
    def is_running(self):
        """Check if BeEF is running and accessible"""
        try:
            response = requests.get(
                f'{self.base_url}/api/hooks',
                timeout=2
            )
            return response.status_code in [200, 401]
        except:
            return False
    
    def get_token(self, force_refresh=False):
        """Get BeEF API authentication token with multiple fallback methods"""
        if self.token and not force_refresh:
            return self.token
        
        # Method 1: Try official login endpoint
        try:
            response = requests.post(
                f'{self.base_url}/api/admin/login',
                json={'username': self.username, 'password': self.password},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data:
                    self.token = data['token']
                    console.print(f"[dim]✓ Got token via login endpoint[/dim]")
                    return self.token
        except Exception as e:
            console.print(f"[dim]Login endpoint failed: {e}[/dim]")
        
        # Method 2: Try to extract token from UI page
        try:
            response = requests.get(f'{self.base_url}/ui/panel', timeout=3)
            if response.status_code == 200:
                content = response.text
                patterns = [
                    r'token["\s:]+([a-f0-9]{32,})',
                    r'beeftoken["\s:]+([a-f0-9]{32,})',
                    r'BEEFTOKEN["\s:=]+([a-f0-9]{32,})',
                ]
                for pattern in patterns:
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        self.token = match.group(1)
                        console.print(f"[dim]✓ Got token from UI page[/dim]")
                        return self.token
        except Exception as e:
            console.print(f"[dim]UI scraping failed: {e}[/dim]")
        
        # Method 3: Use Basic Auth as fallback
        console.print(f"[dim]Using Basic Auth fallback[/dim]")
        self.token = 'use_basic_auth'
        return self.token
    
    def _make_request(self, method, endpoint, **kwargs):
        """Make authenticated request to BeEF API with automatic retry"""
        token = self.get_token()
        
        url = f"{self.base_url}{endpoint}"
        
        # Add authentication
        if token == 'use_basic_auth':
            kwargs['auth'] = (self.username, self.password)
        else:
            if 'params' not in kwargs:
                kwargs['params'] = {}
            kwargs['params']['token'] = token
        
        # Set default timeout
        if 'timeout' not in kwargs:
            kwargs['timeout'] = 10
        
        # Set default headers
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        if 'Content-Type' not in kwargs['headers'] and method.lower() in ['post', 'put']:
            kwargs['headers']['Content-Type'] = 'application/json'
        
        try:
            response = requests.request(method, url, **kwargs)
            
            # If unauthorized, try to refresh token once
            if response.status_code == 401 and self._token_attempts < 1:
                self._token_attempts += 1
                console.print(f"[yellow]Auth failed, refreshing token...[/yellow]")
                self.token = None
                return self._make_request(method, endpoint, **kwargs)
            
            self._token_attempts = 0
            return response
            
        except requests.exceptions.Timeout:
            console.print(f"[red]Request timeout for {endpoint}[/red]")
            return None
        except Exception as e:
            console.print(f"[red]Request error: {e}[/red]")
            return None
    
    def get_hooked_browsers(self):
        """Get list of all hooked browsers"""
        response = self._make_request('GET', '/api/hooks')
        
        if not response or response.status_code != 200:
            return []
        
        try:
            data = response.json()
            hooked = data.get('hooked-browsers', {})
            online = hooked.get('online', {})
            
            if isinstance(online, dict):
                return list(online.values())
            return online if isinstance(online, list) else []
        except:
            return []
    
    def get_browser_info(self, session_id):
        """Get detailed information about a hooked browser"""
        response = self._make_request('GET', f'/api/hooks/{session_id}')
        
        if not response or response.status_code != 200:
            return None
        
        try:
            return response.json()
        except:
            return None
    
    def get_command_module_history(self, session_id):
        """Get command history from browser logs - most reliable method"""
        response = self._make_request('GET', f'/api/logs/{session_id}')
        
        if not response or response.status_code != 200:
            return None
        
        try:
            data = response.json()
            return data
        except:
            return None
    
    def execute_module(self, session_id, module_id, params=None):
        """
        Execute a BeEF module on a hooked browser
        
        Args:
            session_id: Target browser session ID
            module_id: BeEF module ID to execute
            params: Dictionary of parameters for the module
            
        Returns:
            dict: Response data or None if failed
        """
        if params is None:
            params = {}
        
        endpoint = f'/api/modules/{session_id}/{module_id}'
        
        response = self._make_request('POST', endpoint, json=params)
        
        if not response:
            return None
        
        if response.status_code == 200:
            try:
                data = response.json()
                # BeEF returns success status in different formats
                if 'success' in data or 'command_id' in data or data.get('success') != False:
                    return data
            except:
                # Some modules return 200 with empty/non-JSON response
                return {'success': True, 'status_code': 200}
        
        return None
    
    def get_command_results(self, session_id, command_id=None):
        """Get results of executed commands - tries multiple endpoints"""
        
        # BeEF has different endpoints for command results
        endpoints_to_try = [
            f'/api/logs/{session_id}/all',  # All command logs
            f'/api/logs/{session_id}',      # Session logs
            f'/api/modules/{session_id}',   # Module results
        ]
        
        if command_id:
            endpoints_to_try.insert(0, f'/api/modules/{session_id}/{command_id}')
        
        # Try each endpoint
        for endpoint in endpoints_to_try:
            response = self._make_request('GET', endpoint)
            
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    # Check if we got meaningful data
                    if data:
                        # Different endpoints return different structures
                        if isinstance(data, dict):
                            # Check for commands array
                            if 'commands' in data or 'command_results' in data or 'logs' in data:
                                return data
                            # Or if it's a single command result
                            if 'data' in data or 'result' in data:
                                return {'commands': [data]}
                        elif isinstance(data, list) and len(data) > 0:
                            # List of commands
                            return {'commands': data}
                except:
                    continue
        
        return None
    
    def wait_for_command_completion(self, session_id, command_id, timeout=30, check_interval=2):
        """
        Wait for a command to complete execution
        
        Args:
            session_id: Browser session ID
            command_id: Command ID to monitor
            timeout: Maximum time to wait in seconds
            check_interval: How often to check in seconds
            
        Returns:
            dict: Command result data or None if timeout
        """
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            result = self.get_command_results(session_id, command_id)
            
            if result:
                # Check if command has completed
                if isinstance(result, dict):
                    status = result.get('status_text', '').lower()
                    if 'complete' in status or 'success' in status:
                        return result
            
            time.sleep(check_interval)
        
        return None

    def get_all_modules(self):
        """Get list of available BeEF modules"""
        response = self._make_request('GET', '/api/modules')
        
        if not response or response.status_code != 200:
            return {}
        
        try:
            return response.json()
        except:
            return {}
