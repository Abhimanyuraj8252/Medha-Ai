"""
Error Reporter for Medha AI
Logs errors and provides user-friendly error handling
"""
import sys
import traceback
import json
from datetime import datetime
from pathlib import Path

class ErrorReporter:
    """Handles error logging and reporting"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".medha_ai"
        self.log_dir = self.config_dir / "error_logs"
        self.current_log_file = None
        self._ensure_dirs()
        self._setup_global_handler()
    
    def _ensure_dirs(self):
        """Create necessary directories"""
        self.config_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)
    
    def _setup_global_handler(self):
        """Set up global exception handler"""
        self.original_excepthook = sys.excepthook
        sys.excepthook = self._global_exception_handler
    
    def _global_exception_handler(self, exc_type, exc_value, exc_tb):
        """Global exception handler"""
        self.log_error(exc_type, exc_value, exc_tb)
        # Call original handler
        self.original_excepthook(exc_type, exc_value, exc_tb)
    
    def log_error(self, exc_type=None, exc_value=None, exc_tb=None, 
                  context: str = "", custom_message: str = ""):
        """Log an error to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"error_{timestamp}.log"
        
        # Build error info
        if exc_type and exc_value and exc_tb:
            error_type = exc_type.__name__
            error_message = str(exc_value)
            stack_trace = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        else:
            error_type = "UnknownError"
            error_message = custom_message or "Unknown error occurred"
            stack_trace = traceback.format_exc()
        
        log_content = f"""
{'='*60}
MEDHA AI ERROR REPORT
{'='*60}

Timestamp: {datetime.now().isoformat()}
Error Type: {error_type}
Error Message: {error_message}
Context: {context or "General"}

Stack Trace:
{stack_trace}

{'='*60}
System Info:
- Python: {sys.version}
- Platform: {sys.platform}
{'='*60}
"""
        
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(log_content)
            self.current_log_file = log_file
            print(f"[ErrorReporter] Error logged to: {log_file}")
        except Exception as e:
            print(f"[ErrorReporter] Failed to write log: {e}")
        
        return str(log_file)
    
    def get_friendly_message(self, error: Exception) -> str:
        """Get user-friendly error message"""
        error_type = type(error).__name__
        
        friendly_messages = {
            "ConnectionError": "🌐 Internet connection problem. Please check your connection.",
            "TimeoutError": "⏰ Request timed out. Please try again.",
            "APIError": "🤖 AI service error. The AI might be busy, try again.",
            "AuthenticationError": "🔑 API key error. Please check your API keys in settings.",
            "RateLimitError": "⏳ Too many requests. Please wait a moment and try again.",
            "FileNotFoundError": "📁 File not found. Please check the file path.",
            "PermissionError": "🔒 Permission denied. Cannot access the required resource.",
            "ValueError": "❌ Invalid input. Please check your input and try again.",
            "KeyError": "🔍 Missing data. Something went wrong internally.",
        }
        
        return friendly_messages.get(error_type, 
            f"❌ An error occurred: {str(error)[:100]}")
    
    def get_recent_logs(self, count: int = 5) -> list:
        """Get recent error log files"""
        try:
            logs = sorted(self.log_dir.glob("error_*.log"), reverse=True)
            return [str(log) for log in logs[:count]]
        except:
            return []
    
    def get_log_content(self, log_path: str) -> str:
        """Read log file content"""
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return "Could not read log file."
    
    def clear_old_logs(self, days: int = 7):
        """Clear logs older than specified days"""
        import os
        cutoff = datetime.now().timestamp() - (days * 86400)
        
        for log_file in self.log_dir.glob("error_*.log"):
            try:
                if os.path.getmtime(log_file) < cutoff:
                    log_file.unlink()
            except:
                pass
    
    def get_log_count(self) -> int:
        """Get number of error logs"""
        try:
            return len(list(self.log_dir.glob("error_*.log")))
        except:
            return 0

# Global instance
error_reporter = ErrorReporter()
