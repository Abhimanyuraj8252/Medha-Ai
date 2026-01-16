import flet as ft
import threading
import time
from core.ai_brain import AIBrain
from ui.model_selector import ModelSelector

from features.study import StudyNotesView
from features.quiz import QuizView
from features.coder import CoderView
from core.voice_handler import VoiceHandler
from core.file_handler import FileHandler
from core.session_manager import SessionManager
from ui.history_view import SessionHistoryView

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
        
        # Init Views
        self.sidebar = self.build_sidebar()
        self.chat_view = self.build_chat_area()
        self.study_view = StudyNotesView(self.brain)
        self.quiz_view = QuizView(self.brain)
        self.coder_view = CoderView(self.brain)
        
        # Default View
        self.content_area = ft.Container(
            content=self.chat_view,
            expand=True,
            bgcolor=ft.Colors.with_opacity(0.9, ft.Colors.BLACK),
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
            bgcolor=ft.Colors.BLACK54
        )

        self.controls = [
            self.sidebar,
            self.history_container,
            self.content_area
        ]

    def build_sidebar(self):
        return ft.Container(
            width=250,
            bgcolor=ft.Colors.with_opacity(0.8, "#1a1a1a"),
            padding=10,
            content=ft.Column(
                controls=[
                    ft.Text("Medha AI", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_400),
                    ft.Divider(color=ft.Colors.WHITE24),
                    self.sidebar_button("Chat", ft.Icons.CHAT_BUBBLE, lambda e: self.navigate_to(self.chat_view)),
                    self.sidebar_button("Study Notes", ft.Icons.BOOK, lambda e: self.navigate_to(self.study_view)),
                    self.sidebar_button("Quiz Mode", ft.Icons.QUIZ, lambda e: self.navigate_to(self.quiz_view)),
                    self.sidebar_button("Coder Mode", ft.Icons.CODE, lambda e: self.navigate_to(self.coder_view)),
                    ft.Divider(color=ft.Colors.WHITE24),
                    ft.TextButton(
                        "Clear Chat History",
                        icon=ft.Icons.DELETE_OUTLINE,
                        on_click=self.clear_history,
                        style=ft.ButtonStyle(color=ft.Colors.RED_300)
                    ),
                    ft.Container(expand=True),
                    ft.Text("v1.0.0", size=10, color=ft.Colors.WHITE54)
                ]
            )
        )

    def navigate_to(self, view_control):
        self.content_area.content = view_control
        self.content_area.update()

    def sidebar_button(self, text, icon, on_click_handler):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=ft.Colors.WHITE54),
                ft.Text(text, color=ft.Colors.WHITE54)
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
        self.chat_history = ft.ListView(
            expand=True,
            spacing=10,
            auto_scroll=True
        )
        
        self.input_box = ft.TextField(
            hint_text="Ask Medha anything...",
            border_color=ft.Colors.TRANSPARENT,
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
            border_radius=20,
            expand=True,
            on_submit=self.send_message
        )
        
        # Model Selector
        self.model_dropdown = ModelSelector(self.brain, width=220)
        
        # History Toggle
        self.history_btn = ft.IconButton(
            icon=ft.Icons.HISTORY,
            tooltip="Chat History",
            on_click=self.toggle_history
        )
        
        # Continuous voice mode state
        self.continuous_voice_mode = False
        self.continuous_voice_mode = False
        
        self.mic_button = ft.IconButton(
            icon=ft.Icons.MIC,
            icon_color=ft.Colors.RED_400,
            tooltip="🎤 Voice Input (Hindi/English)",
            on_click=self.start_listening
        )
        
        self.continuous_voice_button = ft.IconButton(
            icon=ft.Icons.RECORD_VOICE_OVER,
            icon_color=ft.Colors.PURPLE_400,
            tooltip="🎙️ Continuous Voice Mode",
            on_click=self.toggle_continuous_voice
        )
        
        return ft.Column([
            ft.Row([
                self.history_btn, 
                ft.Container(expand=True), 
                self.model_dropdown
            ], alignment=ft.MainAxisAlignment.END), # Header
            self.chat_history,
            ft.Container(
                content=ft.Row([
                    self.input_box,
                    self.mic_button,
                    self.continuous_voice_button,
                    ft.IconButton(
                        icon=ft.Icons.SEND_ROUNDED, 
                        icon_color=ft.Colors.CYAN_400,
                        tooltip="Send Message",
                        on_click=self.send_message
                    )
                ]),
                padding=10,
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
                border_radius=25
            )
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
        bubble_color = ft.Colors.CYAN_900 if is_user else "#2b2b2b"
        align = ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START
        
        # Create message content with text wrapping
        message_content = ft.Container(
            content=ft.Markdown(text, selectable=True),
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
                icon_color=ft.Colors.CYAN_400,
                icon_size=20,
                tooltip="🔊 Speak / Stop",
                data={"speaking": False}  # Track state
            )
            
            def toggle_speak(e):
                if speaker_button.data["speaking"]:
                    # Stop speaking
                    self.voice.stop_speaking()
                    speaker_button.icon = ft.Icons.VOLUME_UP
                    speaker_button.icon_color = ft.Colors.CYAN_400
                    speaker_button.data["speaking"] = False
                    speaker_button.update()
                else:
                    # Start speaking
                    speech_text = text.replace("**", "").replace("*", "").replace("#", "")
                    speaker_button.icon = ft.Icons.STOP
                    speaker_button.icon_color = ft.Colors.RED_400
                    speaker_button.data["speaking"] = True
                    speaker_button.update()
                    
                    # Speak in thread and reset button when done
                    import threading
                    def speak_and_reset():
                        self.voice.speak(speech_text, lang='hi')
                        speaker_button.icon = ft.Icons.VOLUME_UP
                        speaker_button.icon_color = ft.Colors.CYAN_400
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
