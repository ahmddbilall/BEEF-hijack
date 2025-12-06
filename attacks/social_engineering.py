#!/usr/bin/env python3
"""
Social Engineering Attacks
Phishing and credential theft attacks
"""
from .base_attack import BaseAttack

class GooglePhishingAttack(BaseAttack):
    """Google login phishing page"""
    
    def __init__(self, beef_api):
        super().__init__(beef_api)
        self.name = "Google Phishing"
        self.description = "Display fake Google login page to steal credentials"
        self.module_id = 11
        self.category = "social_engineering"
        self.execution_time = 5
        self.requires_user_interaction = True
        self.silent = False
        
    def get_params(self, **kwargs):
        return {}

class PrettyTheftAttack(BaseAttack):
    """Pretty Theft - Facebook/LinkedIn style phishing"""
    
    def __init__(self, beef_api):
        super().__init__(beef_api)
        self.name = "Pretty Theft (Facebook Login)"
        self.description = "Display fake Facebook login dialog"
        self.module_id = 8
        self.category = "social_engineering"
        self.execution_time = 5
        self.requires_user_interaction = True
        self.silent = False
        
    def get_params(self, **kwargs):
        return {}

class FakeNotificationAttack(BaseAttack):
    """Fake browser notification bar"""
    
    def __init__(self, beef_api):
        super().__init__(beef_api)
        self.name = "Fake Notification (Chrome)"
        self.description = "Display fake Chrome notification bar"
        self.module_id = 17
        self.category = "social_engineering"
        self.execution_time = 3
        self.silent = False
        
    def get_params(self, **kwargs):
        return {}

class FakeNotification2Attack(BaseAttack):
    """Alternative fake notification"""
    
    def __init__(self, beef_api):
        super().__init__(beef_api)
        self.name = "Fake Notification Alt"
        self.description = "Display alternative fake notification"
        self.module_id = 18
        self.category = "social_engineering"
        self.execution_time = 3
        self.silent = False
        
    def get_params(self, **kwargs):
        return {}
