"""
Settings View for Medha AI
Provides UI for all settings: Language, Theme, Analytics, Updates, API Keys
"""
import flet as ft
import webbrowser
from core.languages import lang, LANGUAGES
from core.themes import theme, THEMES
from core.analytics import analytics
from core.updater import updater
from core.error_reporter import error_reporter
from core.secure_keys import key_manager

class SettingsView(ft.Column):
    """Settings page with all configuration options"""
    
    def __init__(self, page: ft.Page, on_theme_change=None, on_language_change=None):
        super().__init__()
        self.app_page = page
        self.on_theme_change = on_theme_change
        self.on_language_change = on_language_change
        self.expand = True
        self.scroll = ft.ScrollMode.AUTO
        self.spacing = 20
        
        self._build_ui()
    
    def _build_ui(self):
        """Build the settings UI"""
        current_theme = theme.get_theme()
        
        self.controls = [
            # Header
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.SETTINGS, size=32, color=current_theme["accent"]),
                    ft.Text("Settings", size=28, weight=ft.FontWeight.BOLD, 
                           color=current_theme["text_primary"])
                ], spacing=15),
                padding=20
            ),
            
            # Language Section
            self._build_section(
                "🌐 Language",
                "Choose your preferred language",
                self._build_language_selector()
            ),
            
            # Theme Section
            self._build_section(
                "🎨 Theme",
                "Customize app appearance",
                self._build_theme_selector()
            ),
            
            # API Keys Section
            self._build_section(
                "🔐 API Keys",
                "Manage your AI service credentials",
                self._build_api_keys_section()
            ),
            
            # Usage Stats Section
            self._build_section(
                "📊 Usage Statistics",
                "Track your app usage",
                self._build_stats_section()
            ),
            
            # Updates Section
            self._build_section(
                "🔄 Updates",
                f"Current version: {updater.get_current_version()}",
                self._build_updates_section()
            ),
            
            # Error Logs Section
            self._build_section(
                "⚠️ Error Logs",
                f"{error_reporter.get_log_count()} error logs saved",
                self._build_error_logs_section()
            ),
            
            # Footer
            ft.Container(
                content=ft.Text(
                    "Made with ❤️ by Team Medha",
                    size=12,
                    color=ft.Colors.WHITE54,
                    text_align=ft.TextAlign.CENTER
                ),
                padding=20,
                alignment=ft.Alignment(0, 0)
            )
        ]
    
    def _build_section(self, title: str, subtitle: str, content):
        """Build a settings section card"""
        current_theme = theme.get_theme()
        
        return ft.Container(
            content=ft.Column([
                ft.Text(title, size=18, weight=ft.FontWeight.BOLD, 
                       color=current_theme["text_primary"]),
                ft.Text(subtitle, size=12, color=current_theme["text_secondary"]),
                ft.Container(height=10),
                content
            ], spacing=5),
            padding=20,
            bgcolor=current_theme["bg_secondary"],
            border_radius=15,
            margin=ft.margin.symmetric(horizontal=10)
        )
    
    def _build_language_selector(self):
        """Build language dropdown"""
        current_theme = theme.get_theme()
        
        options = [
            ft.dropdown.Option(code, name) 
            for code, name in LANGUAGES.items()
        ]
        
        dropdown = ft.Dropdown(
            label="Select Language",
            value=lang.get_current_language(),
            options=options,
            width=300,
            border_color=current_theme["accent"]
        )
        dropdown.on_change = self._on_language_change
        
        return dropdown
    
    def _build_theme_selector(self):
        """Build theme selection grid"""
        current_theme_name = theme.get_current_theme_name()
        
        theme_buttons = []
        for theme_id, info in theme.get_all_themes().items():
            is_selected = theme_id == current_theme_name
            theme_colors = THEMES[theme_id]
            
            btn = ft.Container(
                content=ft.Column([
                    ft.Text(info["emoji"], size=24),
                    ft.Text(info["name"], size=11, 
                           color=ft.Colors.WHITE if is_selected else ft.Colors.WHITE54)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                padding=15,
                bgcolor=theme_colors["bg_secondary"],
                border=ft.border.all(2, theme_colors["accent"] if is_selected else ft.Colors.TRANSPARENT),
                border_radius=10,
                on_click=lambda e, tid=theme_id: self._on_theme_change(tid),
                ink=True
            )
            theme_buttons.append(btn)
        
        return ft.Row(theme_buttons, wrap=True, spacing=10)
    
    def _build_api_keys_section(self):
        """Build API keys management section"""
        current_theme = theme.get_theme()
        keys = key_manager.load_keys()
        
        self.groq_field = ft.TextField(
            label="Groq API Key",
            value=keys.get("groq", "")[:20] + "..." if keys.get("groq") else "",
            password=True,
            can_reveal_password=True,
            width=400,
            border_color=current_theme["accent"]
        )
        
        self.gemini_field = ft.TextField(
            label="Gemini API Key",
            value=keys.get("gemini", "")[:20] + "..." if keys.get("gemini") else "",
            password=True,
            can_reveal_password=True,
            width=400,
            border_color=current_theme["accent"]
        )
        
        return ft.Column([
            self.groq_field,
            self.gemini_field,
            ft.Row([
                ft.ElevatedButton(
                    "Save Keys",
                    icon=ft.Icons.SAVE,
                    bgcolor=current_theme["accent"],
                    color=ft.Colors.WHITE,
                    on_click=self._save_api_keys
                ),
                ft.OutlinedButton(
                    "Clear Keys",
                    icon=ft.Icons.DELETE,
                    on_click=self._clear_api_keys
                )
            ], spacing=10),
            ft.Text(
                "⚠️ Keys are stored locally with encryption",
                size=11,
                color=ft.Colors.WHITE54
            )
        ], spacing=15)
    
    def _build_stats_section(self):
        """Build usage statistics display"""
        current_theme = theme.get_theme()
        stats = analytics.get_all_time_stats()
        session = analytics.get_session_stats()
        
        total_calls = sum(stats["total_api_calls"].values())
        
        return ft.Column([
            ft.Row([
                self._stat_card("Session", session["duration"], ft.Icons.TIMER),
                self._stat_card("API Calls", str(total_calls), ft.Icons.API),
                self._stat_card("Messages", str(stats["messages_sent"]), ft.Icons.CHAT),
                self._stat_card("Voice", str(stats["voice_inputs"]), ft.Icons.MIC),
            ], wrap=True, spacing=10),
            ft.Container(height=10),
            ft.Text(
                f"First use: {stats.get('first_use', 'N/A')[:10]} | Total sessions: {stats['total_sessions']}",
                size=11,
                color=ft.Colors.WHITE54
            )
        ])
    
    def _stat_card(self, label: str, value: str, icon):
        """Create a stat display card"""
        current_theme = theme.get_theme()
        
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, size=20, color=current_theme["accent"]),
                ft.Text(value, size=18, weight=ft.FontWeight.BOLD, 
                       color=current_theme["text_primary"]),
                ft.Text(label, size=10, color=current_theme["text_secondary"])
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
            padding=15,
            bgcolor=current_theme["bg_primary"],
            border_radius=10,
            width=100
        )
    
    def _build_updates_section(self):
        """Build update checker section"""
        current_theme = theme.get_theme()
        
        self.update_status = ft.Text(
            "Click to check for updates",
            size=12,
            color=current_theme["text_secondary"]
        )
        
        return ft.Column([
            ft.Row([
                ft.ElevatedButton(
                    "Check for Updates",
                    icon=ft.Icons.REFRESH,
                    bgcolor=current_theme["accent"],
                    color=ft.Colors.WHITE,
                    on_click=self._check_updates
                ),
                ft.OutlinedButton(
                    "View Releases",
                    icon=ft.Icons.OPEN_IN_NEW,
                    on_click=lambda e: webbrowser.open(updater.get_download_url())
                )
            ], spacing=10),
            self.update_status
        ], spacing=10)
    
    def _build_error_logs_section(self):
        """Build error logs section"""
        current_theme = theme.get_theme()
        
        logs = error_reporter.get_recent_logs(3)
        
        log_widgets = []
        for log in logs:
            log_name = log.split("\\")[-1].split("/")[-1]
            log_widgets.append(
                ft.Text(f"• {log_name}", size=11, color=ft.Colors.WHITE54)
            )
        
        if not log_widgets:
            log_widgets.append(
                ft.Text("No errors logged! 🎉", size=12, color=current_theme["success"])
            )
        
        return ft.Column([
            *log_widgets,
            ft.Container(height=10),
            ft.OutlinedButton(
                "Clear Old Logs",
                icon=ft.Icons.DELETE_SWEEP,
                on_click=self._clear_old_logs
            )
        ], spacing=5)
    
    # Event Handlers
    def _on_language_change(self, e):
        """Handle language change"""
        lang.save_preference(e.control.value)
        if self.on_language_change:
            self.on_language_change(e.control.value)
        self.app_page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Language changed! Restart app for full effect."),
            action="OK"
        )
        self.app_page.snack_bar.open = True
        self.app_page.update()
    
    def _on_theme_change(self, theme_id: str):
        """Handle theme change"""
        theme.save_preference(theme_id)
        if self.on_theme_change:
            self.on_theme_change(theme_id)
        
        # Rebuild UI with new theme
        self._build_ui()
        self.update()
        
        self.app_page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Theme changed to {THEMES[theme_id]['name']}!"),
            action="OK"
        )
        self.app_page.snack_bar.open = True
        self.app_page.update()
    
    def _save_api_keys(self, e):
        """Save API keys"""
        groq = self.groq_field.value if not self.groq_field.value.endswith("...") else ""
        gemini = self.gemini_field.value if not self.gemini_field.value.endswith("...") else ""
        
        if groq or gemini:
            keys = key_manager.load_keys()
            key_manager.save_keys(
                groq if groq else keys.get("groq", ""),
                gemini if gemini else keys.get("gemini", "")
            )
            
            self.app_page.snack_bar = ft.SnackBar(
                content=ft.Text("API keys saved securely! ✅"),
                action="OK"
            )
        else:
            self.app_page.snack_bar = ft.SnackBar(
                content=ft.Text("Enter new keys to save"),
                action="OK"
            )
        
        self.app_page.snack_bar.open = True
        self.app_page.update()
    
    def _clear_api_keys(self, e):
        """Clear saved API keys"""
        key_manager.delete_keys()
        self.groq_field.value = ""
        self.gemini_field.value = ""
        self.groq_field.update()
        self.gemini_field.update()
        
        self.app_page.snack_bar = ft.SnackBar(
            content=ft.Text("API keys cleared"),
            action="OK"
        )
        self.app_page.snack_bar.open = True
        self.app_page.update()
    
    def _check_updates(self, e):
        """Check for updates"""
        self.update_status.value = "Checking..."
        self.update_status.update()
        
        result = updater.check_for_updates()
        
        if result.get("success"):
            if result.get("update_available"):
                self.update_status.value = f"🎉 New version available: {result['latest_version']}"
                self.update_status.color = ft.Colors.GREEN_400
            else:
                self.update_status.value = "✅ You have the latest version!"
                self.update_status.color = ft.Colors.GREEN_400
        else:
            self.update_status.value = f"❌ Check failed: {result.get('error', 'Unknown error')}"
            self.update_status.color = ft.Colors.RED_400
        
        self.update_status.update()
    
    def _clear_old_logs(self, e):
        """Clear old error logs"""
        error_reporter.clear_old_logs(7)
        
        self.app_page.snack_bar = ft.SnackBar(
            content=ft.Text("Old logs cleared!"),
            action="OK"
        )
        self.app_page.snack_bar.open = True
        self.app_page.update()
        
        # Rebuild to update log count
        self._build_ui()
        self.update()
