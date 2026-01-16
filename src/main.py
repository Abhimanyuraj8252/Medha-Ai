import flet as ft
from ui.layout import MainLayout
from config import APP_NAME
import warnings

# Suppress warnings to keep the console clean for the user
warnings.filterwarnings("ignore")

def main(page: ft.Page):
    # Window setup
    page.title = APP_NAME
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.window_bgcolor = ft.Colors.TRANSPARENT
    page.bgcolor = ft.Colors.TRANSPARENT
    
    # Initialize page overlay
    page.overlay.clear()
    
    # Enable glassmorphism effect (blur) if supported by OS/Flet version
    # Note: Full acrylic blur might require specific window settings or native calls, 
    # but we will simulate the look with semi-transparent backgrounds.
    
    # Add the main responsive layout
    app_layout = MainLayout(page)
    page.add(app_layout)
    
    # Initialize history list after page is ready
    app_layout.history_view.refresh_list()
    
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
