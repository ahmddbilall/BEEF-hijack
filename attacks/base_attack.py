#!/usr/bin/env python3
"""
Base Attack Class
All attack modules inherit from this class
"""
import time
from abc import ABC, abstractmethod
from rich.console import Console

console = Console()

class BaseAttack(ABC):
    """Base class for all BeEF attack modules"""
    
    def __init__(self, beef_api):
        """
        Initialize attack module
        
        Args:
            beef_api: BeEFAPI instance for making API calls
        """
        self.api = beef_api
        self.name = "Unknown Attack"
        self.description = "No description"
        self.module_id = None
        self.category = "general"
        self.requires_user_interaction = False
        self.execution_time = 2  # Default wait time in seconds
        self.silent = True  # Whether attack is visible to user
        
    @abstractmethod
    def get_params(self, **kwargs):
        """
        Get parameters for the attack module
        
        Args:
            **kwargs: Optional parameters passed from user
            
        Returns:
            dict: Parameters to send to BeEF module
        """
        pass
    
    def execute(self, session_id, **kwargs):
        """
        Execute the attack on target browser
        
        Args:
            session_id: Target browser session ID
            **kwargs: Optional parameters for the attack
            
        Returns:
            tuple: (success: bool, result_data: dict)
        """
        try:
            console.print(f"[cyan]→ Executing: {self.name}[/cyan]")
            
            # Get parameters
            params = self.get_params(**kwargs)
            
            # Execute module
            result = self.api.execute_module(session_id, self.module_id, params)
            
            if result:
                console.print(f"[green]  ✓ {self.name} - Command sent successfully[/green]")
                
                # Wait for execution
                if self.execution_time > 0:
                    console.print(f"[dim]  ⏳ Waiting {self.execution_time}s for execution...[/dim]")
                    time.sleep(self.execution_time)
                
                return True, result
            else:
                console.print(f"[red]  ✗ {self.name} - Failed to send command[/red]")
                return False, None
                
        except Exception as e:
            console.print(f"[red]  ✗ {self.name} - Error: {e}[/red]")
            return False, None
    
    def validate_session(self, session_id):
        """Check if session is valid and online"""
        browsers = self.api.get_hooked_browsers()
        for browser in browsers:
            if browser.get('session') == session_id:
                return True
        return False
    
    def get_info(self):
        """Get attack information"""
        return {
            'name': self.name,
            'description': self.description,
            'module_id': self.module_id,
            'category': self.category,
            'requires_interaction': self.requires_user_interaction,
            'execution_time': self.execution_time,
            'silent': self.silent
        }
