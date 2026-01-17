import flet as ft
import threading
import time
from core.ai_brain import AIBrain
from ui.model_selector import ModelSelector

from features.study import StudyNotesView
from features.quiz import QuizView
from features.coder import CoderView
from features.ai_hub import AIHubView
from core.voice_handler import VoiceHandler
from core.file_handler import FileHandler
from core.session_manager import SessionManager
from ui.history_view import SessionHistoryView
from ui.settings_view import SettingsView
from core.chat_exporter import chat_exporter
from core.analytics import analytics
from core.error_reporter import error_reporter
from core.themes import theme
from core.updater import updater

class MainLayout(ft.Row):
    def __init__(self, page: ft.Page):
        super().__init__()
        self._page = page  # Store page reference
        self.expand = True
        self.spacing = 0
        
        # Initialize AI Brain and Session Manager
        self.brain = AIBrain()
        self.session_manager = SessionManager()
        self.current_session_id = self.session_manager.create_new_session_id()
        
        self.voice = VoiceHandler(page)
        self.file_handler = FileHandler()
        self.current_file_context = None
        
        # Request tracking for interruption handling
        self.current_request_id = 0
        self.processing_request = False
        
        # Init Views - Need to build these with current theme
        self.sidebar = self.build_sidebar()
        self.chat_view = self.build_chat_area()
        self.study_view = StudyNotesView(self.brain)
        self.quiz_view = QuizView(self.brain)
        self.coder_view = CoderView(self.brain)
        self.ai_hub_view = AIHubView()  # Initialize AI Hub
        self._settings_view = None  # Lazy loaded
        
        # Default View
        current_theme = theme.get_theme()
        self.content_area = ft.Container(
            content=self.chat_view,
            expand=True,
            bgcolor=current_theme["bg_primary"],
            padding=20,
        )

        # History Sidebar
        self.history_view = SessionHistoryView(
            section="chat",
            current_session_id=self.current_session_id,
            on_session_select=self.load_session,
            on_new_chat=self.start_new_chat
        )
        
        self.history_container = ft.Container(
            content=self.history_view,
            width=0, 
            opacity=0,
            animate=300,
            bgcolor=current_theme["bg_secondary"]
        )

        self.controls = [
            self.sidebar,
            self.history_container,
            self.content_area
        ]

    def build_sidebar(self):
        current_theme = theme.get_theme()
        self.sidebar_column = ft.Column(
            controls=[
                ft.Text("Medha AI", size=24, weight=ft.FontWeight.BOLD, color=current_theme["accent"]),
                ft.Divider(color=ft.Colors.with_opacity(0.1, current_theme["text_primary"])),
                self.sidebar_button("Chat", ft.Icons.CHAT_BUBBLE, lambda e: self.navigate_to(self.chat_view)),
                self.sidebar_button("Study Notes", ft.Icons.BOOK, lambda e: self.navigate_to(self.study_view)),
                self.sidebar_button("Quiz Mode", ft.Icons.QUIZ, lambda e: self.navigate_to(self.quiz_view)),
                self.sidebar_button("Coder Mode", ft.Icons.CODE, lambda e: self.navigate_to(self.coder_view)),
                self.sidebar_button("AI Hub", ft.Icons.HUB, lambda e: self.navigate_to(self.ai_hub_view)), # Added AI Hub Button
                ft.Divider(color=ft.Colors.with_opacity(0.1, current_theme["text_primary"])),
                self.sidebar_button("Settings", ft.Icons.SETTINGS, self.open_settings),
                ft.Divider(color=ft.Colors.with_opacity(0.1, current_theme["text_primary"])),
                ft.TextButton(
                    "Export Chat",
                    icon=ft.Icons.DOWNLOAD,
                    on_click=self.export_chat,
                    style=ft.ButtonStyle(color=current_theme["accent"])
                ),
                ft.TextButton(
                    "Clear Chat History",
                    icon=ft.Icons.DELETE_OUTLINE,
                    on_click=self.clear_history,
                    style=ft.ButtonStyle(color=current_theme["error"] if "error" in current_theme else ft.Colors.RED_300)
                ),
                ft.Container(expand=True),
                ft.Text(f"v{updater.get_current_version()}", size=10, color=current_theme["text_secondary"])
            ]
        )
        
        return ft.Container(
            width=250,
            bgcolor=current_theme["bg_secondary"],
            padding=10,
            content=self.sidebar_column
        )

    def navigate_to(self, view_control):
        self.content_area.content = view_control
        self.content_area.update()
    
    def get_settings_view(self):
        """Lazy-load settings view"""
        if self._settings_view is None:
            self._settings_view = SettingsView(self._page, on_theme_change=self.apply_theme)
        return self._settings_view
    
    def open_settings(self, e):
        """Open settings view with lazy initialization"""
        self.navigate_to(self.get_settings_view())
    
    def export_chat(self, e):
        """Export current chat to HTML file"""
        try:
            messages = self.brain.chat_history
            if not messages:
                self._page.snack_bar = ft.SnackBar(
                    content=ft.Text("No messages to export!"),
                    action="OK"
                )
                self._page.snack_bar.open = True
                self._page.update()
                return
            
            # Export to HTML (prettier)
            filepath = chat_exporter.export_to_html(messages, "Medha AI Chat")
            
            self._page.snack_bar = ft.SnackBar(
                content=ft.Text(f"✅ Chat exported to Documents folder!"),
                action="Open",
                on_action=lambda e: self._open_export_folder()
            )
            self._page.snack_bar.open = True
            self._page.update()
            
        except Exception as ex:
            error_reporter.log_error(context="Export Chat", custom_message=str(ex))
            self._page.snack_bar = ft.SnackBar(
                content=ft.Text(f"❌ Export failed: {str(ex)[:50]}"),
                action="OK"
            )
            self._page.snack_bar.open = True
            self._page.update()
    
    def _open_export_folder(self):
        """Open the export folder"""
        import os
        import subprocess
        folder = chat_exporter.get_export_dir()
        if os.path.exists(folder):
            subprocess.Popen(f'explorer "{folder}"')
    
    def apply_theme(self, theme_id):
        """Apply new theme to the app"""
        current_theme = theme.get_theme()
        
        # 1. Update Main Containers
        self.content_area.bgcolor = current_theme["bg_primary"]
        self.history_container.bgcolor = current_theme["bg_secondary"]
        
        # 2. Rebuild Sidebar
        # We replace the content of the existing sidebar container
        self.sidebar.bgcolor = current_theme["bg_secondary"]
        self.sidebar.content = ft.Column(
            controls=[
                ft.Text("Medha AI", size=24, weight=ft.FontWeight.BOLD, color=current_theme["accent"]),
                ft.Divider(color=ft.Colors.with_opacity(0.1, current_theme["text_primary"])),
                self.sidebar_button("Chat", ft.Icons.CHAT_BUBBLE, lambda e: self.navigate_to(self.chat_view)),
                self.sidebar_button("Study Notes", ft.Icons.BOOK, lambda e: self.navigate_to(self.study_view)),
                self.sidebar_button("Quiz Mode", ft.Icons.QUIZ, lambda e: self.navigate_to(self.quiz_view)),
                self.sidebar_button("Coder Mode", ft.Icons.CODE, lambda e: self.navigate_to(self.coder_view)),
                self.sidebar_button("AI Hub", ft.Icons.HUB, lambda e: self.navigate_to(self.ai_hub_view)), # Added AI Hub Button
                ft.Divider(color=ft.Colors.with_opacity(0.1, current_theme["text_primary"])),
                self.sidebar_button("Settings", ft.Icons.SETTINGS, self.open_settings),
                ft.Divider(color=ft.Colors.with_opacity(0.1, current_theme["text_primary"])),
                ft.TextButton(
                    "Export Chat",
                    icon=ft.Icons.DOWNLOAD,
                    on_click=self.export_chat,
                    style=ft.ButtonStyle(color=current_theme["accent"])
                ),
                ft.TextButton(
                    "Clear Chat History",
                    icon=ft.Icons.DELETE_OUTLINE,
                    on_click=self.clear_history,
                    style=ft.ButtonStyle(color=current_theme["error"] if "error" in current_theme else ft.Colors.RED_300)
                ),
                ft.Container(expand=True),
                ft.Text(f"v{updater.get_current_version()}", size=10, color=current_theme["text_secondary"])
            ]
        )
        
        # 3. Update Chat Area Components
        self.input_container.bgcolor = ft.Colors.with_opacity(0.05, current_theme["text_primary"])
        
        self.input_box.text_style.color = current_theme["text_primary"]
        self.input_box.hint_style.color = current_theme["text_secondary"]
        self.input_box.bgcolor = ft.Colors.with_opacity(0.1, current_theme["text_primary"])
        self.input_box.color = current_theme["text_primary"]
        
        self.history_btn.icon_color = current_theme["text_primary"]
        self.mic_button.icon_color = current_theme["error"] if "error" in current_theme else ft.Colors.RED_400
        
        # 4. Update Model Selector
        if hasattr(self, 'model_dropdown'):
            self.model_dropdown.update_theme()
            
        # Update Other Views
        if self.study_view: self.study_view.update_theme()
        if self.quiz_view: self.quiz_view.update_theme()
        if self.coder_view: self.coder_view.update_theme()
        if self.ai_hub_view: self.ai_hub_view.update_theme() # Update AI Hub Theme
            
        # 5. Update Chat History Bubbles
        for bubble in self.chat_history.controls:
            if isinstance(bubble, ft.Row):
                is_user = bubble.alignment == ft.MainAxisAlignment.END
                new_bubble_color = current_theme["accent"] if is_user else current_theme["bg_secondary"]
                
                # Find the container with message content
                # User: Row -> [Container]
                # AI: Row -> [Column -> [Container, Container(Icon)]]
                
                message_container = None
                icon_button = None
                
                if is_user:
                    if len(bubble.controls) > 0 and isinstance(bubble.controls[0], ft.Container):
                        message_container = bubble.controls[0]
                else:
                    if len(bubble.controls) > 0 and isinstance(bubble.controls[0], ft.Column):
                        col = bubble.controls[0]
                        if len(col.controls) > 0 and isinstance(col.controls[0], ft.Container):
                            message_container = col.controls[0]
                        # Update speak button icon color if present
                        if len(col.controls) > 1:
                            btn_container = col.controls[1]
                            if isinstance(btn_container.content, ft.IconButton):
                                icon_button = btn_container.content
                
                if message_container:
                    message_container.bgcolor = new_bubble_color
                    # Text color for user is white (on accent), for AI is text_primary
                    # We can't easily change Markdown style inside without rebuilding, 
                    # but usually Markdown inherits or we set it globally? 
                    # Actually Markdown takes explicit style. 
                    # Let's just update container bg for now, text usually adapts if not hardcoded.
                
                if icon_button:
                     # Reset to default state color (not speaking)
                     icon_button.icon_color = current_theme["accent"]

        # 6. Rebuild settings view with new theme (if open)
        self._settings_view = SettingsView(self._page, on_theme_change=self.apply_theme)
        if self.content_area.content and isinstance(self.content_area.content, SettingsView):
             self.navigate_to(self._settings_view)
        
        self.update()

    def sidebar_button(self, text, icon, on_click_handler):
        current_theme = theme.get_theme()
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=current_theme["text_secondary"]),
                ft.Text(text, color=current_theme["text_secondary"])
            ]),
            padding=10,
            border_radius=10,
            on_hover=lambda e: self.highlight_button(e.control),
            ink=True,
            on_click=on_click_handler
        )

    def highlight_button(self, container):
        # Simple hover effect could be added here
        pass

    def build_chat_area(self):
        current_theme = theme.get_theme()
        
        self.chat_history = ft.ListView(
            expand=True,
            spacing=10,
            auto_scroll=True
        )
        
        self.input_box = ft.TextField(
            hint_text="Ask Medha anything...",
            hint_style=ft.TextStyle(color=current_theme["text_secondary"]),
            text_style=ft.TextStyle(color=current_theme["text_primary"]),
            border_color=ft.Colors.TRANSPARENT,
            bgcolor=ft.Colors.with_opacity(0.1, current_theme["text_primary"]),
            border_radius=20,
            expand=True,
            on_submit=self.send_message,
            color=current_theme["text_primary"]
        )
        
        # Model Selector
        self.model_dropdown = ModelSelector(self.brain, width=220)
        
        # History Toggle
        self.history_btn = ft.IconButton(
            icon=ft.Icons.HISTORY,
            icon_color=current_theme["text_primary"],
            tooltip="Chat History",
            on_click=self.toggle_history
        )
        
        # Continuous voice mode state
        self.continuous_voice_mode = False
        
        self.mic_button = ft.IconButton(
            icon=ft.Icons.MIC,
            icon_color=current_theme["error"] if "error" in current_theme else ft.Colors.RED_400,
            tooltip="🎤 Voice Input (Hindi/English)",
            on_click=self.start_listening
        )
        
        self.continuous_voice_button = ft.IconButton(
            icon=ft.Icons.RECORD_VOICE_OVER,
            icon_color=ft.Colors.PURPLE_400,
            tooltip="🎙️ Continuous Voice Mode",
            on_click=self.toggle_continuous_voice
        )
        
        self.input_container = ft.Container(
            content=ft.Row([
                self.input_box,
                self.mic_button,
                self.continuous_voice_button,
                ft.IconButton(
                    icon=ft.Icons.SEND_ROUNDED, 
                    icon_color=current_theme["accent"],
                    tooltip="Send Message",
                    on_click=self.send_message
                )
            ]),
            padding=10,
            bgcolor=ft.Colors.with_opacity(0.05, current_theme["text_primary"]),
            border_radius=25
        )
        
        return ft.Column([
            ft.Row([
                self.history_btn, 
                ft.Container(expand=True), 
                self.model_dropdown
            ], alignment=ft.MainAxisAlignment.END), # Header
            self.chat_history,
            self.input_container
        ])

    def toggle_history(self, e):
        if self.history_container.width == 0:
            self.history_container.width = 250
            self.history_container.opacity = 1
            self.history_view.refresh_list()
        else:
            self.history_container.width = 0
            self.history_container.opacity = 0
        if self.page:
            self.update()

    def start_new_chat(self):
        # Save current if needed (handled on message send)
        self.current_session_id = self.session_manager.create_new_session_id()
        self.brain.chat_history = []
        self.chat_history.controls.clear()
        
        # Add greeting
        greeting = "Hi! I'm Medha. How can I help you today? ❤️"
        self.brain.chat_history.append({"role": "assistant", "content": greeting})
        self.add_chat_bubble(greeting, False)
        
        # Refresh history list to show new (or deselect old)
        self.history_view.current_session_id = self.current_session_id
        self.history_view.refresh_list()
        if self.page:
            self.update()

    def load_session(self, session_id):
        self.current_session_id = session_id
        session_data = self.session_manager.get_session_content("chat", session_id)
        messages = session_data.get('messages', []) if session_data else []
        
        # Update Brain History
        self.brain.chat_history = messages
        
        # Rebuild UI
        self.chat_history.controls.clear()
        for msg in messages:
            if msg['role'] != 'system':
                self.add_chat_bubble(msg['content'], msg['role'] == 'user')
        
        self.history_view.current_session_id = session_id
        self.history_view.refresh_list() # Update selection highlighting
        if self.page:
            self.update()

    def save_current_chat(self):
        # Determine title from first user message
        title = "New Chat"
        for msg in self.brain.chat_history:
            if msg['role'] == 'user':
                title = msg['content'][:30]
                break
        
        self.session_manager.save_session(
            "chat", 
            self.current_session_id, 
            title, 
            self.brain.chat_history
        )
        self.history_view.refresh_list()

    def start_listening(self, e):
        """Single voice input - listens once and sends"""
        self.input_box.hint_text = "🎤 Listening... Speak now..."
        self.input_box.disabled = True
        self._page.update()
        
        def on_speech(text):
            self.input_box.disabled = False
            self.input_box.hint_text = "Ask Medha anything..."
            
            if not text or text.strip() == "":
                self.input_box.update()
                return
                
            # Show what was heard in text box
            self.input_box.value = text
            self.input_box.update()
            
            # Auto-send the message
            self.send_message(None, use_voice=True)
            
        self.voice.listen(on_speech, language="hi-IN")  # Changed to hi-IN for better Hindi support
    
    def toggle_continuous_voice(self, e):
        """Toggle continuous voice conversation mode"""
        self.continuous_voice_mode = not self.continuous_voice_mode
        
        if self.continuous_voice_mode:
            # Enable continuous mode
            self.continuous_voice_button.icon_color = ft.Colors.GREEN_400
            self.continuous_voice_button.tooltip = "🛑 Stop Continuous Mode"
            self.add_chat_bubble("🎙️ Continuous Voice Mode ENABLED! Keep talking...", is_user=False)
            self._page.update()
            
            # Start continuous listening loop
            self._continuous_listen()
        else:
            # Disable continuous mode
            self.continuous_voice_button.icon_color = ft.Colors.PURPLE_400
            self.continuous_voice_button.tooltip = "🎙️ Continuous Voice Mode"
            self.add_chat_bubble("⏹️ Continuous Voice Mode STOPPED", is_user=False)
            self._page.update()
    
    def _continuous_listen(self):
        """Continuous listening loop for real-time conversation - Like Gemini/ChatGPT"""
        if not self.continuous_voice_mode:
            return
        
        self.input_box.hint_text = "🎙️ CONTINUOUS MODE - Always Listening..."
        self._page.update()
        
        def on_speech(text):
            # Check mode status first
            if not self.continuous_voice_mode:
                self.input_box.hint_text = "Ask Medha anything..."
                self._page.update()
                return
            
            # Handle both empty and non-empty responses
            if text and text.strip() != "":
                # Stop any ongoing speech immediately when new input detected
                self.voice.stop_speaking()
                
                # Show what was heard
                self.input_box.value = text
                self._page.update()
                
                # Check for stop commands
                stop_words = ["stop listening", "stop mode", "बंद करो", "रुको", "stop", "exit"]
                if any(stop in text.lower() for stop in stop_words):
                    self.continuous_voice_mode = False
                    self.continuous_voice_button.icon_color = ft.Colors.PURPLE_400
                    self.continuous_voice_button.tooltip = "🎙️ Continuous Voice Mode"
                    self.add_chat_bubble("⏹️ Stopping continuous mode...", is_user=False)
                    self.input_box.hint_text = "Ask Medha anything..."
                    self._page.update()
                    return
                
                # Process the command with voice response (in separate thread)
                threading.Thread(target=lambda: self.send_message(None, use_voice=True), daemon=True).start()
            
            # ALWAYS continue listening - no matter what
            # This ensures true continuous mode like Gemini
            if self.continuous_voice_mode:
                def restart_listening():
                    # Wait a bit for the previous listener to release the lock
                    time.sleep(1) 
                    if self.continuous_voice_mode:
                         # Update UI to show we are listening again
                         self.input_box.hint_text = "✨ Listening... (Say 'Stop' to exit)"
                         self.input_box.update()
                         self.voice.listen(on_speech, language="hi-IN")
                
                # Run invisible thread to restart listening
                threading.Thread(target=restart_listening, daemon=True).start()
        
        self.voice.listen(on_speech, language="hi-IN")  # Hindi-India for better Hindi support

    def on_file_picked(self, e):
        """Handle file selection"""
        if not e.files:
            return
        
        file_path = e.files[0].path
        
        # Show processing message
        self.add_chat_bubble(f"📎 Processing file: {e.files[0].name}...", is_user=False)
        self._page.update()
        
        # Process file
        file_context = self.file_handler.process_file(file_path)
        self.current_file_context = file_context
        
        # Show file analysis
        self.add_chat_bubble(file_context, is_user=False)
        self.add_chat_bubble("✅ File loaded! You can now ask questions about this file.", is_user=False)
        self._page.update()

    def send_message(self, e, use_voice=False):
        user_text = self.input_box.value
        if not user_text:
            return
        
        # Increment request ID to invalidate previous requests
        self.current_request_id += 1
        request_id = self.current_request_id

        # Save to Session Manager (Title update handled)
        self.save_current_chat()
        
        # Check for wake word
        wake_words = ["hey medha", "hey meda", "hi medha", "hello medha"]
        is_wake_word = any(wake in user_text.lower() for wake in wake_words)
        
        # Add user message
        self.add_chat_bubble(user_text, is_user=True)
        self.input_box.value = ""
        self.save_current_chat() # Save context immediately
        self._page.update()
        
        # If already processing, the new request will make old ones stale
        if self.processing_request:
            print(f"🔄 New request received, skipping old request")
        
        self.processing_request = True
        
        # Build context with file if available
        context_text = user_text
        if self.current_file_context:
            context_text = f"""[Context: User has uploaded a file]
{self.current_file_context}

[User Question]: {user_text}

Please answer the user's question based on the file content above."""
        
        # Get AI Response (this is the slow part)
        response = self.brain.ask(context_text)
        
        # Check if this request is still valid (not interrupted by newer request)
        if request_id != self.current_request_id:
            print(f"⏭️ Skipping stale response (request {request_id}, current {self.current_request_id})")
            self.processing_request = False
            return None
        
        # Only show response if it's still the latest request
        self.add_chat_bubble(response, is_user=False)
        self.save_current_chat() # Save context after response
        self._page.update()
        self.processing_request = False
        
        # Voice output logic (only for latest request)
        if use_voice or is_wake_word:
            # For voice mode, speak the full response (or limit to reasonable length)
            speech_text = response if len(response) < 500 else response[:500] + "..."
            # Remove markdown formatting for cleaner speech
            speech_text = speech_text.replace("**", "").replace("*", "").replace("#", "")
            self.voice.speak(speech_text, lang='hi')  # Changed to 'hi' for Hindi
        
        return response
        
        return response  # Return response for continuous mode
    
    def clear_history(self, e):
        """Clear chat history to save API quota"""
        self.chat_history.controls.clear()
        self.brain.chat_history.clear()
        self.add_chat_bubble("💬 Chat history cleared! Fresh start.", is_user=False)
        self._page.update()

    def add_chat_bubble(self, text, is_user):
        current_theme = theme.get_theme()
        bubble_color = current_theme["accent"] if is_user else current_theme["bg_secondary"]
        # Make user bubble slightly darker than accent for better contrast if needed, or stick to accent
        # Actually user bubble is typically distinction. Let's use accent for user, and a secondary bg for AI?
        # Standard: User right (Accent), AI left (Secondary BG or Surface)
        
        if is_user:
            bubble_color = current_theme["accent"]
            text_color = ft.Colors.WHITE # Assuming accent is usually dark/vibrant
        else:
            bubble_color = current_theme["bg_secondary"]
            text_color = current_theme["text_primary"]

        align = ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START
        
        # Create message content with text wrapping
        message_content = ft.Container(
            content=ft.Markdown(
                text, 
                selectable=True, 
                extension_set="gitHubWeb",
                code_theme="atom-one-dark",
                code_style=ft.TextStyle(font_family="Roboto Mono"),
            ),
            padding=15,
            bgcolor=bubble_color,
            border_radius=ft.BorderRadius.only(
                top_left=15, top_right=15, 
                bottom_left=15 if is_user else 0,
                bottom_right=0 if is_user else 15
            ),
            width=None,  # Allow flexible width
        )
        
        # For AI messages, add a speak button
        if not is_user:
            # Create a speaker button that can be clicked again to stop
            speaker_button = ft.IconButton(
                icon=ft.Icons.VOLUME_UP,
                icon_color=current_theme["accent"],
                icon_size=20,
                tooltip="🔊 Speak / Stop",
                data={"speaking": False}  # Track state
            )
            
            def toggle_speak(e):
                if speaker_button.data["speaking"]:
                    # Stop speaking
                    self.voice.stop_speaking()
                    speaker_button.icon = ft.Icons.VOLUME_UP
                    speaker_button.icon_color = current_theme["accent"]
                    speaker_button.data["speaking"] = False
                    speaker_button.update()
                else:
                    # Start speaking
                    speech_text = text.replace("**", "").replace("*", "").replace("#", "")
                    speaker_button.icon = ft.Icons.STOP
                    speaker_button.icon_color = current_theme["error"] if "error" in current_theme else ft.Colors.RED_400
                    speaker_button.data["speaking"] = True
                    speaker_button.update()
                    
                    # Speak in thread and reset button when done
                    import threading
                    def speak_and_reset():
                        self.voice.speak(speech_text, lang='hi')
                        speaker_button.icon = ft.Icons.VOLUME_UP
                        speaker_button.icon_color = current_theme["accent"]
                        speaker_button.data["speaking"] = False
                        try:
                            speaker_button.update()
                        except:
                            pass
                    threading.Thread(target=speak_and_reset, daemon=True).start()
            
            speaker_button.on_click = toggle_speak
            
            bubble = ft.Row(
                [
                    ft.Column(
                        [
                            message_content,
                            ft.Container(
                                content=speaker_button,
                                padding=ft.padding.only(left=10, top=5)
                            )
                        ],
                        spacing=0,
                        horizontal_alignment=ft.CrossAxisAlignment.START
                    )
                ],
                alignment=align,
                wrap=True,  # Enable text wrapping
            )
        else:
            # User messages don't need speak button
            bubble = ft.Row(
                [message_content],
                alignment=align,
                wrap=True,  # Enable text wrapping
            )
        
        self.chat_history.controls.append(bubble)
