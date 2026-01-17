"""
Auto-Update Checker for Medha AI
Checks GitHub for new releases
"""
import json
import urllib.request
from datetime import datetime
from pathlib import Path

# Current version of the app
CURRENT_VERSION = "2.1.0"
GITHUB_REPO = "Abhimanyuraj8252/Medha-Ai"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

class UpdateChecker:
    """Checks for app updates from GitHub"""
    
    def __init__(self):
        self.current_version = CURRENT_VERSION
        self.config_dir = Path.home() / ".medha_ai"
        self.cache_file = self.config_dir / "update_cache.json"
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Create config directory"""
        self.config_dir.mkdir(exist_ok=True)
    
    def _version_tuple(self, version: str) -> tuple:
        """Convert version string to tuple for comparison"""
        try:
            parts = version.replace("v", "").split(".")
            return tuple(int(p) for p in parts[:3])
        except:
            return (0, 0, 0)
    
    def check_for_updates(self) -> dict:
        """Check GitHub for new releases"""
        try:
            # Create request with headers
            req = urllib.request.Request(
                GITHUB_API_URL,
                headers={"User-Agent": "Medha-AI-UpdateChecker"}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            latest_version = data.get("tag_name", "").replace("v", "")
            release_name = data.get("name", "")
            release_url = data.get("html_url", "")
            release_notes = data.get("body", "")[:500]  # Limit notes length
            
            # Compare versions
            current = self._version_tuple(self.current_version)
            latest = self._version_tuple(latest_version)
            
            update_available = latest > current
            
            result = {
                "success": True,
                "update_available": update_available,
                "current_version": self.current_version,
                "latest_version": latest_version,
                "release_name": release_name,
                "release_url": release_url,
                "release_notes": release_notes,
                "checked_at": datetime.now().isoformat()
            }
            
            # Cache result
            self._cache_result(result)
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "update_available": False,
                "current_version": self.current_version
            }
    
    def _cache_result(self, result: dict):
        """Cache update check result"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(result, f)
        except:
            pass
    
    def get_cached_result(self) -> dict:
        """Get cached update check result"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"update_available": False, "current_version": self.current_version}
    
    def get_current_version(self) -> str:
        """Get current app version"""
        return self.current_version
    
    def get_download_url(self) -> str:
        """Get GitHub releases page URL"""
        return f"https://github.com/{GITHUB_REPO}/releases"

# Global instance
updater = UpdateChecker()
