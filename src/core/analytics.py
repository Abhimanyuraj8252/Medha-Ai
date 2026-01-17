"""
Usage Analytics for Medha AI
Tracks API usage and session statistics
"""
import json
import time
from datetime import datetime
from pathlib import Path

class UsageAnalytics:
    """Tracks app usage statistics"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".medha_ai"
        self.stats_file = self.config_dir / "usage_stats.json"
        self.session_start = time.time()
        self.current_session_calls = {"groq": 0, "gemini": 0, "aihub": 0}
        self.current_session_tokens = 0
        self._ensure_config_dir()
        self._load_stats()
    
    def _ensure_config_dir(self):
        """Create config directory"""
        self.config_dir.mkdir(exist_ok=True)
    
    def _load_stats(self):
        """Load existing stats"""
        try:
            if self.stats_file.exists():
                with open(self.stats_file, 'r') as f:
                    self.all_time_stats = json.load(f)
            else:
                self.all_time_stats = self._default_stats()
        except:
            self.all_time_stats = self._default_stats()
    
    def _default_stats(self) -> dict:
        """Default stats structure"""
        return {
            "total_api_calls": {"groq": 0, "gemini": 0, "aihub": 0},
            "total_tokens": 0,
            "total_sessions": 0,
            "total_session_time_minutes": 0,
            "first_use": datetime.now().isoformat(),
            "last_use": datetime.now().isoformat(),
            "messages_sent": 0,
            "voice_inputs": 0,
            "files_processed": 0
        }
    
    def _save_stats(self):
        """Save stats to file"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.all_time_stats, f, indent=2)
        except:
            pass
    
    def track_api_call(self, provider: str, tokens: int = 0):
        """Track an API call"""
        provider = provider.lower()
        if provider in self.current_session_calls:
            self.current_session_calls[provider] += 1
            self.all_time_stats["total_api_calls"][provider] += 1
        
        self.current_session_tokens += tokens
        self.all_time_stats["total_tokens"] += tokens
        self.all_time_stats["last_use"] = datetime.now().isoformat()
        self._save_stats()
    
    def track_message(self):
        """Track a message sent"""
        self.all_time_stats["messages_sent"] += 1
        self._save_stats()
    
    def track_voice_input(self):
        """Track voice input usage"""
        self.all_time_stats["voice_inputs"] += 1
        self._save_stats()
    
    def track_file_processed(self):
        """Track file processing"""
        self.all_time_stats["files_processed"] += 1
        self._save_stats()
    
    def get_session_duration(self) -> str:
        """Get current session duration"""
        duration = time.time() - self.session_start
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        return f"{minutes}m {seconds}s"
    
    def get_session_stats(self) -> dict:
        """Get current session stats"""
        return {
            "duration": self.get_session_duration(),
            "api_calls": self.current_session_calls.copy(),
            "tokens": self.current_session_tokens
        }
    
    def get_all_time_stats(self) -> dict:
        """Get all-time stats"""
        return self.all_time_stats.copy()
    
    def end_session(self):
        """End current session and save stats"""
        duration = (time.time() - self.session_start) / 60
        self.all_time_stats["total_sessions"] += 1
        self.all_time_stats["total_session_time_minutes"] += duration
        self._save_stats()
    
    def get_formatted_stats(self) -> str:
        """Get formatted stats string for display"""
        stats = self.all_time_stats
        total_calls = sum(stats["total_api_calls"].values())
        
        return f"""📊 Usage Statistics

🔹 Current Session:
   • Duration: {self.get_session_duration()}
   • API Calls: {sum(self.current_session_calls.values())}
   • Tokens Used: {self.current_session_tokens:,}

🔹 All Time:
   • Total Sessions: {stats['total_sessions']}
   • Total API Calls: {total_calls:,}
   • Total Tokens: {stats['total_tokens']:,}
   • Messages Sent: {stats['messages_sent']:,}
   • Voice Inputs: {stats['voice_inputs']}
   • Files Processed: {stats['files_processed']}
   • First Use: {stats['first_use'][:10]}
"""

# Global instance
analytics = UsageAnalytics()
