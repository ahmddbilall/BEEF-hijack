"""
Attack Modules for BeEF Exploitation
Each module represents a specific attack/exploit
"""

from .base_attack import BaseAttack

# Import all attack modules
from .info_gathering import *
from .media_capture import *
from .social_engineering import *
from .basic_attacks import *
