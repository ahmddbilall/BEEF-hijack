#!/usr/bin/env python3
"""
Information Gathering Attacks
Silent attacks that collect victim information
"""
from .base_attack import BaseAttack

class FingerprintAttack(BaseAttack):
    """Get browser fingerprint"""
    
    def __init__(self, beef_api):
        super().__init__(beef_api)
        self.name = "Browser Fingerprint"
        self.description = "Collect detailed browser and system information"
        self.module_id = 289
        self.category = "info_gathering"
        self.execution_time = 3
        
    def get_params(self, **kwargs):
        return {}

class GeolocationAttack(BaseAttack):
    """Get victim's geolocation"""
    
    def __init__(self, beef_api):
        super().__init__(beef_api)
        self.name = "Geolocation"
        self.description = "Get victim's physical location (requires permission)"
        self.module_id = 104
        self.category = "info_gathering"
        self.execution_time = 3
        self.requires_user_interaction = True  # May require permission
        
    def get_params(self, **kwargs):
        return {}

class GetCookiesAttack(BaseAttack):
    """Steal browser cookies"""
    
    def __init__(self, beef_api):
        super().__init__(beef_api)
        self.name = "Get Cookies"
        self.description = "Extract all browser cookies"
        self.module_id = 277
        self.category = "info_gathering"
        self.execution_time = 2
        
    def get_params(self, **kwargs):
        return {}

class GetHistoryAttack(BaseAttack):
    """Get browsing history"""
    
    def __init__(self, beef_api):
        super().__init__(beef_api)
        self.name = "Get Browsing History"
        self.description = "Extract visited domains and URLs"
        self.module_id = 288
        self.category = "info_gathering"
        self.execution_time = 4
        
    def get_params(self, **kwargs):
        return {}

class GetClipboardAttack(BaseAttack):
    """Read clipboard content"""
    
    def __init__(self, beef_api):
        super().__init__(beef_api)
        self.name = "Get Clipboard"
        self.description = "Read clipboard content"
        self.module_id = 127
        self.category = "info_gathering"
        self.execution_time = 2
        
    def get_params(self, **kwargs):
        return {}

class DetectSocialNetworksAttack(BaseAttack):
    """Detect logged-in social networks"""
    
    def __init__(self, beef_api):
        super().__init__(beef_api)
        self.name = "Detect Social Networks"
        self.description = "Detect which social networks the user is logged into"
        self.module_id = 64
        self.category = "info_gathering"
        self.execution_time = 5
        
    def get_params(self, **kwargs):
        return {}
