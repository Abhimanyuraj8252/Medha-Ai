import sys
import os

# Fix imports - add src directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

import flet as ft
from ui.layout import MainLayout
from config import APP_NAME
import warnings

# Suppress warnings to keep the console clean for the user
warnings.filterwarnings("ignore")

from core.themes import theme

def main(page: ft.Page):
    # Hide window initially to prevent "Flet" splash
    page.window.visible = False
    
    # Window setup
    page.title = APP_NAME
    
    # Get saved theme
    saved_theme_name = theme.get_current_theme_name()
    saved_theme = theme.get_theme()
    
    # Apply saved theme mode
    page.theme_mode = ft.ThemeMode.LIGHT if saved_theme_name == "light" else ft.ThemeMode.DARK
    page.bgcolor = saved_theme["bg_primary"]
    page.padding = 0
    
    # Window settings for Flet 0.80+
    page.window.width = 1200
    page.window.height = 800
    page.window.resizable = True
    
    # Initialize page overlay
    page.overlay.clear()
    
    # Add the main responsive layout
    app_layout = MainLayout(page)
    page.add(app_layout)
    
    # Initialize history list after page is ready
    try:
        app_layout.history_view.refresh_list()
    except Exception:
        pass
    
    page.update()
    
    # Show window after content is loaded
    page.window.visible = True
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
