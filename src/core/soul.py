"""
Soul System - Protected System Prompt Management
Loads and protects Mareen's core personality from manipulation.
"""

import os
import hashlib
from typing import Optional, Tuple

SOUL_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'soul.md')

class SoulProtector:
    """Protects Mareen's core identity from prompt injection attacks."""
    
    def __init__(self):
        self.soul_content = self._load_soul()
        self.soul_hash = self._calculate_hash(self.soul_content)
        
        # Prompt injection patterns to detect
        self.injection_patterns = [
            "ignore all previous instructions",
            "ignore previous instructions",
            "disregard all previous",
            "forget everything",
            "new instructions",
            "you are now",
            "act as",
            "pretend to be",
            "roleplay as",
            "ignore your programming",
            "override your",
            "system prompt",
            "forget your instructions",
            "new personality",
            "change your personality",
            "you are chatgpt",
            "you are claude",
            "you are gpt",
            "become a",
            "transform into",
            "ignore all",
            "disregard previous",
            "previous instructions don't matter",
            "forget what you were told",
            "new directive",
            "override directive",
            "jailbreak",
            "developer mode",
            "sudo mode",
            "admin mode",
            "god mode",
            "unrestricted mode",
            "do anything now",
            "dan mode",
        ]
        
        print(f"Soul Protector initialized. Soul hash: {self.soul_hash[:16]}...")
    
    def _load_soul(self) -> str:
        """Load the soul.md file content."""
        if not os.path.exists(SOUL_FILE):
            raise FileNotFoundError(
                f"Soul file not found at: {SOUL_FILE}\n"
                "Mareen cannot function without her soul!"
            )
        
        with open(SOUL_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract the actual system prompt (remove markdown formatting)
        # Keep the content as is for now
        return content
    
    def _calculate_hash(self, content: str) -> str:
        """Calculate SHA256 hash of soul content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def get_system_prompt(self) -> str:
        """
        Get the protected system prompt.
        This is the only way to get the system prompt - it cannot be overridden.
        """
        return self.soul_content
    
    def detect_injection(self, user_input: str) -> Tuple[bool, Optional[str]]:
        """
        Detect if user input contains prompt injection attempts.
        
        Args:
            user_input: The user's message
            
        Returns:
            Tuple of (is_injection_detected, detected_pattern)
        """
        user_input_lower = user_input.lower()
        
        for pattern in self.injection_patterns:
            if pattern in user_input_lower:
                return True, pattern
        
        return False, None
    
    def get_injection_response(self, detected_pattern: str) -> str:
        """
        Get a response for detected injection attempts.
        
        Args:
            detected_pattern: The pattern that was detected
            
        Returns:
            A polite rejection in Hindi
        """
        responses = [
            "मुझे माफ करें, लेकिन मैं अपनी core instructions को change नहीं कर सकती। मैं Mareen हूँ और ऐसे ही रहूँगी। क्या मैं कुछ और help कर सकती हूँ?",
            "नहीं, मैं अपनी personality बदल नहीं सकती। मैं Mareen हूँ। आपकी actually क्या मदद चाहिए?",
            "मैं Mareen हूँ और मेरी identity change नहीं होती। कोई genuine query है जिसमें मैं help कर सकूँ?",
            "Sorry, लेकिन मैं अपने instructions ignore नहीं कर सकती। मैं हमेशा Mareen रहूँगी। कुछ और बताइए?",
        ]
        
        # Use hash to deterministically select a response
        import random
        random.seed(hash(detected_pattern))
        response = random.choice(responses)
        random.seed()  # Reset seed
        
        return response
    
    def verify_soul_integrity(self) -> bool:
        """
        Verify that the soul file hasn't been tampered with.
        
        Returns:
            True if soul is intact, False if modified
        """
        try:
            current_content = self._load_soul()
            current_hash = self._calculate_hash(current_content)
            
            if current_hash != self.soul_hash:
                print(f"WARNING: Soul file has been modified!")
                print(f"Original hash: {self.soul_hash[:16]}...")
                print(f"Current hash:  {current_hash[:16]}...")
                # Update to new soul
                self.soul_content = current_content
                self.soul_hash = current_hash
                return False
            
            return True
        except Exception as e:
            print(f"Error verifying soul integrity: {e}")
            return False
    
    def get_soul_stats(self) -> dict:
        """Get statistics about the soul protection system."""
        return {
            'soul_file': SOUL_FILE,
            'soul_loaded': bool(self.soul_content),
            'soul_length': len(self.soul_content),
            'soul_hash': self.soul_hash,
            'protected_patterns': len(self.injection_patterns),
            'integrity_verified': self.verify_soul_integrity()
        }

# Global soul protector instance
_soul_protector = None

def get_soul_protector() -> SoulProtector:
    """Get the global soul protector instance (singleton pattern)."""
    global _soul_protector
    if _soul_protector is None:
        _soul_protector = SoulProtector()
    return _soul_protector

def reload_soul():
    """Force reload the soul from file (useful for updates)."""
    global _soul_protector
    _soul_protector = SoulProtector()
    return _soul_protector
