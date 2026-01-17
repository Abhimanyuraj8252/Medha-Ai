import flet as ft
import os
import json
from core.themes import theme

class ModelSelector(ft.Container):
    def __init__(self, brain, width=200):
        super().__init__()
        self.brain = brain
        
        # Calculate styles based on current theme
        current_theme = theme.get_theme()
        
        # Styling for "Premium" look
        self.width = width
        self.border_radius = 8
        self.bgcolor = ft.Colors.with_opacity(0.05, current_theme["text_primary"])
        self.border = ft.Border.all(1, ft.Colors.with_opacity(0.2, current_theme["text_primary"]))
        self.padding = ft.Padding(left=15, right=5, top=2, bottom=2)
        
        self.dropdown = self._build_dropdown()
        
        self.content = ft.Row([
            ft.Icon(ft.Icons.PSYCHOLOGY, size=16, color=current_theme["accent"]),
            ft.VerticalDivider(width=10, color=ft.Colors.TRANSPARENT),
            ft.Container(content=self.dropdown, expand=True)
        ], alignment=ft.MainAxisAlignment.START, spacing=0)

    def _build_dropdown(self):
        current_theme = theme.get_theme()
        options = []
        
        # Helper to add section header
        def add_header(text):
            return ft.dropdown.Option(
                key=f"__header_{text}__", 
                text=f"━━ {text.upper()} ━━", 
                disabled=True
            )

        # 1. Groq Models
        groq_models = [m for m in self.brain.available_models if m['provider'] == 'groq']
        if groq_models:
            options.append(add_header("Groq (Fast)"))
            for m in groq_models:
                # Remove prefix if present to be clean
                name = m['name'].replace("Groq: ", "").replace("Groq: ", "")
                options.append(ft.dropdown.Option(key=m['id'], text=name))
        
        # 2. Gemini Models
        gemini_models = [m for m in self.brain.available_models if m['provider'] == 'gemini']
        if gemini_models:
            options.append(add_header("Google Gemini"))
            for m in gemini_models:
                name = m['name'].replace("Gemini: ", "").replace("GEMINI: ", "")
                options.append(ft.dropdown.Option(key=m['id'], text=name))

        # 3. External (AI Hub)
        external = self._load_external_models()
        if external:
            options.append(add_header("AI HUB"))
            for m in external:
                options.append(ft.dropdown.Option(key=f"hub:{m}", text=m))

        dropdown = ft.Dropdown(
            value=f"hub:{self.brain.active_model_id}" if self.brain.active_provider == "aihub" else self.brain.active_model_id,
            options=options,
            text_size=13,
            height=35,
            border=ft.InputBorder.NONE,
            content_padding=5,
            filled=False,
            dense=True,
            hint_text="Select Brain",
            text_style=ft.TextStyle(color=current_theme["text_primary"]),
            hint_style=ft.TextStyle(color=current_theme["text_secondary"]),
        )
        # Set on_change after initialization to avoid keyword argument error in some Flet versions
        dropdown.on_change = self._handle_change
        return dropdown

    def refresh_options(self):
        """Rebuild dropdown options after models load."""
        new_dropdown = self._build_dropdown()
        self.dropdown.options = new_dropdown.options
        self.dropdown.value = new_dropdown.value
        self.dropdown.update()

    def _handle_change(self, e):
        selected_key = e.control.value
        # Prevent selecting headers (though they are disabled)
        if selected_key and selected_key.startswith("__header"):
            e.control.value = self.brain.active_model_id
            e.control.update()
            return

        if selected_key.startswith("hub:"):
            self.brain.set_model(selected_key.replace("hub:", ""), provider="aihub")
        else:
            self.brain.set_model(selected_key)
            
    def update_theme(self):
        """Update colors based on current theme"""
        current_theme = theme.get_theme()
        
        # Update Container styles
        self.bgcolor = ft.Colors.with_opacity(0.05, current_theme["text_primary"])
        self.border = ft.Border.all(1, ft.Colors.with_opacity(0.2, current_theme["text_primary"]))
        
        # Update Icon
        if len(self.content.controls) > 0 and isinstance(self.content.controls[0], ft.Icon):
            self.content.controls[0].color = current_theme["accent"]
            
        # Update Dropdown text styles
        self.dropdown.text_style = ft.TextStyle(color=current_theme["text_primary"])
        self.dropdown.hint_style = ft.TextStyle(color=current_theme["text_secondary"])
        
        self.update()

    def _load_external_models(self):
        config_path = os.path.join(os.getcwd(), "user_data", "providers.json")
        if not os.path.exists(config_path):
            return []
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("models", [])
        except Exception:
            return []
