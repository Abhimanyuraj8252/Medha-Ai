"""
Theme Customization for Medha AI
Multiple color themes for the app
"""
import json
from pathlib import Path

THEMES = {
    "dark": {
        "name": "Dark Night",
        "emoji": "🌙",
        "bg_primary": "#0a0a0f",
        "bg_secondary": "#1a1a2e",
        "bg_sidebar": "#16213e",
        "text_primary": "#ffffff",
        "text_secondary": "#a0a0a0",
        "accent": "#00d4ff",
        "accent_secondary": "#7b2cbf",
        "success": "#00ff88",
        "error": "#ff4444",
        "warning": "#ffaa00",
        "user_bubble": "#16213e",
        "ai_bubble": "#2b2b2b"
    },
    "light": {
        "name": "Light Day",
        "emoji": "☀️",
        "bg_primary": "#ffffff",
        "bg_secondary": "#f0f2f5",
        "bg_sidebar": "#e4e6eb",
        "text_primary": "#000000",
        "text_secondary": "#222222",
        "accent": "#0066cc",
        "accent_secondary": "#6b21a8",
        "success": "#00aa55",
        "error": "#cc0000",
        "warning": "#cc8800",
        "user_bubble": "#e7f3ff",
        "ai_bubble": "#ffffff"
    },
    "cyber": {
        "name": "Cyberpunk",
        "emoji": "🤖",
        "bg_primary": "#0d0d0d",
        "bg_secondary": "#1a0a2e",
        "bg_sidebar": "#2d1b4e",
        "text_primary": "#00ff00",
        "text_secondary": "#00cc00",
        "accent": "#ff00ff",
        "accent_secondary": "#00ffff",
        "success": "#00ff00",
        "error": "#ff0066",
        "warning": "#ffff00",
        "user_bubble": "#330066",
        "ai_bubble": "#1a0a2e"
    },
    "ocean": {
        "name": "Ocean Blue",
        "emoji": "🌊",
        "bg_primary": "#0a1628",
        "bg_secondary": "#0f2847",
        "bg_sidebar": "#1e3a5f",
        "text_primary": "#e0f7ff",
        "text_secondary": "#8cd3ff",
        "accent": "#00bcd4",
        "accent_secondary": "#4fc3f7",
        "success": "#26a69a",
        "error": "#ef5350",
        "warning": "#ffa726",
        "user_bubble": "#0d47a1",
        "ai_bubble": "#1565c0"
    },
    "forest": {
        "name": "Forest Green",
        "emoji": "🌲",
        "bg_primary": "#0a1a0a",
        "bg_secondary": "#1a2f1a",
        "bg_sidebar": "#2d4a2d",
        "text_primary": "#e0ffe0",
        "text_secondary": "#90ee90",
        "accent": "#4caf50",
        "accent_secondary": "#81c784",
        "success": "#66bb6a",
        "error": "#f44336",
        "warning": "#ffb74d",
        "user_bubble": "#1b5e20",
        "ai_bubble": "#2e7d32"
    },
    "sunset": {
        "name": "Sunset Orange",
        "emoji": "🌅",
        "bg_primary": "#1a0a0a",
        "bg_secondary": "#2d1a1a",
        "bg_sidebar": "#4a2d2d",
        "text_primary": "#fff0e0",
        "text_secondary": "#ffcc99",
        "accent": "#ff6b35",
        "accent_secondary": "#f7931e",
        "success": "#4caf50",
        "error": "#f44336",
        "warning": "#ffeb3b",
        "user_bubble": "#bf360c",
        "ai_bubble": "#e65100"
    }
}

class ThemeManager:
    """Manages theme preferences"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".medha_ai"
        self.config_file = self.config_dir / "theme.json"
        self.current_theme = self._load_preference()
    
    def _load_preference(self) -> str:
        """Load saved theme preference"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    return data.get("theme", "dark")
        except:
            pass
        return "dark"
    
    def save_preference(self, theme_name: str):
        """Save theme preference"""
        self.config_dir.mkdir(exist_ok=True)
        self.current_theme = theme_name
        with open(self.config_file, 'w') as f:
            json.dump({"theme": theme_name}, f)
    
    def get_theme(self) -> dict:
        """Get current theme colors"""
        return THEMES.get(self.current_theme, THEMES["dark"])
    
    def get_color(self, key: str) -> str:
        """Get specific color from current theme"""
        return self.get_theme().get(key, "#ffffff")
    
    def get_all_themes(self) -> dict:
        """Get all available themes"""
        return {k: {"name": v["name"], "emoji": v["emoji"]} for k, v in THEMES.items()}
    
    def get_current_theme_name(self) -> str:
        """Get current theme name"""
        return self.current_theme

# Global instance
theme = ThemeManager()
