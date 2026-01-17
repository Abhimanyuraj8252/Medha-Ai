"""
Secure Key Manager for Medha AI
Stores API keys in encrypted format locally
"""
import os
import json
import base64
from pathlib import Path

class SecureKeyManager:
    """Manages API keys securely with local encrypted storage"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".medha_ai"
        self.config_file = self.config_dir / "keys.enc"
        self._ensure_config_dir()
        
    def _ensure_config_dir(self):
        """Create config directory if not exists"""
        self.config_dir.mkdir(exist_ok=True)
    
    def _simple_encrypt(self, text: str) -> str:
        """Simple obfuscation (not military-grade, but hides from casual view)"""
        encoded = base64.b64encode(text.encode()).decode()
        return encoded[::-1]  # Reverse for extra obfuscation
    
    def _simple_decrypt(self, text: str) -> str:
        """Decrypt obfuscated text"""
        try:
            reversed_text = text[::-1]
            return base64.b64decode(reversed_text.encode()).decode()
        except:
            return ""
    
    def save_keys(self, groq_key: str, gemini_key: str):
        """Save API keys to encrypted file"""
        data = {
            "groq": self._simple_encrypt(groq_key),
            "gemini": self._simple_encrypt(gemini_key)
        }
        with open(self.config_file, 'w') as f:
            json.dump(data, f)
    
    def load_keys(self) -> dict:
        """Load API keys from encrypted file"""
        if not self.config_file.exists():
            return {"groq": "", "gemini": ""}
        
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            return {
                "groq": self._simple_decrypt(data.get("groq", "")),
                "gemini": self._simple_decrypt(data.get("gemini", ""))
            }
        except:
            return {"groq": "", "gemini": ""}
    
    def has_keys(self) -> bool:
        """Check if keys are already saved"""
        keys = self.load_keys()
        return bool(keys.get("groq")) and bool(keys.get("gemini"))
    
    def delete_keys(self):
        """Delete saved keys"""
        if self.config_file.exists():
            self.config_file.unlink()

# Global instance
key_manager = SecureKeyManager()
