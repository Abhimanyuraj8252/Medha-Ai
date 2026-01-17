"""
Medha AI - Mobile Entry Point
This file is the main entry for the Flet mobile app (Android/iOS)
"""

import flet as ft
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ui.layout_mobile import MainLayout
from src.config import APP_NAME
import warnings

warnings.filterwarnings("ignore")

def main(page: ft.Page):
    """Main app entry point - Mobile optimized"""
    
    # Detect mobile platform
    is_mobile = page.platform in [
        ft.PagePlatform.ANDROID, 
        ft.PagePlatform.IOS,
        "android",  # Fallback string check
        "ios"
    ]
    
    # Force mobile mode if platform detection fails but we're in APK
    if not is_mobile and hasattr(sys, 'getandroidapilevel'):
        is_mobile = True
    
    page.title = APP_NAME
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.spacing = 0
    
    # Dark theme colors
    page.bgcolor = "#0a0a0f"
    
    # Mobile-specific optimizations
    if is_mobile:
        # Full screen mobile experience
        page.window.full_screen = False
        page.window.always_on_top = False
        
        # Optimize scrolling
        page.scroll = ft.ScrollMode.AUTO
        page.auto_scroll = True
        
        # Prevent unwanted gestures
        page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
        page.vertical_alignment = ft.MainAxisAlignment.START
        
        # Optimize fonts for mobile
        page.fonts = {
            "Roboto": "https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap"
        }
        
        # Increase touch target sizes
        page.theme = ft.Theme(
            color_scheme_seed=ft.Colors.CYAN,
            use_material3=True
        )
    else:
        # Desktop fallback
        page.window.width = 400
        page.window.height = 800
        page.window.resizable = True
        page.window.min_width = 360
        page.window.min_height = 640
    
    # Clear overlay
    page.overlay.clear()
    
    try:
        # Initialize app with mobile support
        app_layout = MainLayout(page, is_mobile=is_mobile)
        page.add(app_layout)
        
        # Load initial history
        app_layout.history_view.refresh_list()
        
        # Show welcome message
        welcome_msg = "👋 Namaste! I'm Medha, your AI assistant. Ask me anything in Hindi or English!"
        app_layout.add_chat_bubble(welcome_msg, is_user=False)
        
        page.update()
        
    except Exception as e:
        # Error handling for mobile
        error_text = ft.Text(
            f"❌ Error loading app: {str(e)}",
            color=ft.Colors.RED_400,
            size=16
        )
        page.add(
            ft.Container(
                content=error_text,
                padding=20,
                alignment=ft.Alignment(0, 0)
            )
        )
        page.update()
        print(f"App Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Launch app
    # For APK: this will be called by Flet's Android wrapper
    # For desktop: can run directly for testing
    try:
        ft.app(
            target=main,
            view=ft.AppView.FLET_APP,  # Native mobile app
            port=8550,
            assets_dir="assets"
        )
    except Exception as e:
        print(f"Failed to start app: {e}")
        import traceback
        traceback.print_exc()
