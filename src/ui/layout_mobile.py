import flet as ft
import threading
import time
import os
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

class MainLayout(ft.Column):
    """
    Mobile-Responsive Layout for Medha AI
    - Bottom navigation for mobile
    - Collapsible sidebar for tablet/desktop
    - Touch-optimized buttons
    """
    def __init__(self, page: ft.Page, is_mobile=False):
        super().__init__()
        self._page = page
        self.is_mobile = is_mobile
        self.expand = True
        self.spacing = 0
        
        # Initialize AI Brain and Session Manager (lazy models to avoid UI blocking)
        self.brain = AIBrain(load_models=False)
        self.session_manager = SessionManager()
        self.current_session_id = self.session_manager.create_new_session_id()
        
        self.voice = VoiceHandler(page)
        self.file_handler = FileHandler()
        self.current_file_context = None
        self.selected_files = []
        
        # Request tracking for interruption handling
        self.current_request_id = 0
        self.processing_request = False
        
        # Track current view
        self.current_view_name = "chat"
        
        # Init Views
        self.chat_view = self.build_chat_area()
        self.study_view = StudyNotesView(self.brain)
        self.quiz_view = QuizView(self.brain)
        self.coder_view = CoderView(self.brain)
        self.ai_hub_view = AIHubView()
        
        # Initialize FilePicker only for mobile to avoid desktop control mismatch
        if is_mobile:
            self.file_picker = ft.FilePicker()
            self.file_picker.on_result = self.on_file_picked
        else:
            self.file_picker = None
        
        # Main Content Area
        self.content_area = ft.Container(
            content=self.chat_view,
            expand=True,
            bgcolor=ft.Colors.with_opacity(0.95, ft.Colors.BLACK),
            padding=10 if is_mobile else 20,
        )

        # History Sidebar (overlay style for mobile)
        self.history_view = SessionHistoryView(
            section="chat",
            current_session_id=self.current_session_id,
            on_session_select=self.load_session,
            on_new_chat=self.start_new_chat
        )
        
        # Build layout based on device type
        if is_mobile:
            # Mobile layout: Top bar + Content + Bottom Nav
            self.top_bar = self.build_mobile_top_bar()
            self.bottom_nav = self.build_bottom_navigation()
            
            self.controls = [
                self.top_bar,
                self.content_area,
                self.bottom_nav
            ]
        else:
            # Desktop/Tablet layout: Sidebar + Content
            self.sidebar = self.build_sidebar()
            self.history_container = ft.Container(
                content=self.history_view,
                width=0, 
                opacity=0,
                animate=300,
                bgcolor=ft.Colors.BLACK_54
            )
            
            # Convert to Row for desktop
            self.expand = True
            desktop_row = ft.Row(
                [
                    self.sidebar,
                    self.history_container,
                    self.content_area
                ],
                expand=True,
                spacing=0
            )
            self.controls = [desktop_row]
        
        # Add FilePicker to page overlay after layout is built (mobile only)
        if self.file_picker and self.file_picker not in self._page.overlay:
            self._page.overlay.append(self.file_picker)

        # Ensure initial chat is saved on startup
        if not self.brain.chat_history and len(self.chat_history.controls) == 0:
            greeting = "Hi! I'm Medha. How can I help you? ❤️"
            self.add_chat_bubble(greeting, False, record_history=True, save=True)

        # Load full model list in background and refresh dropdown
        threading.Thread(target=self._load_models_async, daemon=True).start()

    def _load_models_async(self):
        try:
            self.brain.load_models()
            if hasattr(self.model_dropdown, "refresh_options"):
                def _refresh_ui():
                    try:
                        self.model_dropdown.refresh_options()
                    except Exception:
                        pass
                if hasattr(self._page, "call_from_thread"):
                    self._page.call_from_thread(_refresh_ui)
                else:
                    _refresh_ui()
        except Exception:
            pass

    def build_mobile_top_bar(self):
        """Top app bar for mobile with menu and history"""
        self.menu_sheet = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Row([
                            ft.Text("Menu", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_400),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE,
                                on_click=lambda e: self.toggle_menu()
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=ft.padding.only(left=10, right=5, top=10, bottom=5)
                    ),
                    ft.Divider(color=ft.Colors.WHITE24),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.CHAT_BUBBLE, color=ft.Colors.CYAN_400),
                        title=ft.Text("Chat", size=18),
                        on_click=lambda e: self.navigate_to("chat")
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.BOOK, color=ft.Colors.BLUE_400),
                        title=ft.Text("Study Notes", size=18),
                        on_click=lambda e: self.navigate_to("study")
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.QUIZ, color=ft.Colors.PURPLE_400),
                        title=ft.Text("Quiz Mode", size=18),
                        on_click=lambda e: self.navigate_to("quiz")
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.CODE, color=ft.Colors.GREEN_400),
                        title=ft.Text("Coder Mode", size=18),
                        on_click=lambda e: self.navigate_to("coder")
                    ),
                    ft.Divider(color=ft.Colors.WHITE24),
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.DELETE_OUTLINE, color=ft.Colors.RED_300),
                        title=ft.Text("Clear History", size=18, color=ft.Colors.RED_300),
                        on_click=self.clear_history
                    ),
                ]),
                padding=20,
                bgcolor="#1a1a1a"
            ),
            open=False
        )
        self._page.overlay.append(self.menu_sheet)
        
        return ft.Container(
            content=ft.Row([
                ft.IconButton(
                    icon=ft.Icons.MENU,
                    icon_color=ft.Colors.CYAN_400,
                    icon_size=28,
                    tooltip="Menu",
                    on_click=lambda e: self.toggle_menu()
                ),
                ft.Text(
                    "Medha AI", 
                    size=20, 
                    weight=ft.FontWeight.BOLD, 
                    color=ft.Colors.CYAN_400
                ),
                ft.Container(expand=True)
            ]),
            bgcolor=ft.Colors.with_opacity(0.95, "#1a1a1a"),
            padding=ft.padding.symmetric(horizontal=10, vertical=12),
        )

    def toggle_menu(self):
        """Toggle menu bottom sheet"""
        self.menu_sheet.open = not self.menu_sheet.open
        self.menu_sheet.update()

    def build_bottom_navigation(self):
        """Bottom navigation bar for mobile"""
        return ft.Container(
            content=ft.Row([
                ft.IconButton(
                    icon=ft.Icons.CHAT_BUBBLE,
                    icon_color=ft.Colors.CYAN_400 if self.current_view_name == "chat" else ft.Colors.WHITE_54,
                    icon_size=28,
                    tooltip="Chat",
                    on_click=lambda e: self.navigate_to("chat")
                ),
                ft.IconButton(
                    icon=ft.Icons.BOOK,
                    icon_color=ft.Colors.CYAN_400 if self.current_view_name == "study" else ft.Colors.WHITE_54,
                    icon_size=28,
                    tooltip="Study",
                    on_click=lambda e: self.navigate_to("study")
                ),
                ft.IconButton(
                    icon=ft.Icons.QUIZ,
                    icon_color=ft.Colors.CYAN_400 if self.current_view_name == "quiz" else ft.Colors.WHITE_54,
                    icon_size=28,
                    tooltip="Quiz",
                    on_click=lambda e: self.navigate_to("quiz")
                ),
                ft.IconButton(
                    icon=ft.Icons.CODE,
                    icon_color=ft.Colors.CYAN_400 if self.current_view_name == "coder" else ft.Colors.WHITE_54,
                    icon_size=28,
                    tooltip="Code",
                    on_click=lambda e: self.navigate_to("coder")
                ),
                ft.IconButton(
                    icon=ft.Icons.AUTO_AWESOME,
                    icon_color=ft.Colors.CYAN_400 if self.current_view_name == "ai_hub" else ft.Colors.WHITE_54,
                    icon_size=28,
                    tooltip="AI Hub",
                    on_click=lambda e: self.navigate_to("ai_hub")
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
            bgcolor=ft.Colors.with_opacity(0.95, "#1a1a1a"),
            padding=10,
        )

    def build_sidebar(self):
        """Desktop sidebar"""
        return ft.Container(
            width=250,
            bgcolor=ft.Colors.with_opacity(0.8, "#1a1a1a"),
            padding=10,
            content=ft.Column(
                controls=[
                    ft.Text("Medha AI", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_400),
                    ft.Divider(color=ft.Colors.WHITE24),
                    self.sidebar_button("Chat", ft.Icons.CHAT_BUBBLE, lambda e: self.navigate_to("chat")),
                    self.sidebar_button("Study Notes", ft.Icons.BOOK, lambda e: self.navigate_to("study")),
                    self.sidebar_button("Quiz Mode", ft.Icons.QUIZ, lambda e: self.navigate_to("quiz")),
                    self.sidebar_button("Coder Mode", ft.Icons.CODE, lambda e: self.navigate_to("coder")),
                    self.sidebar_button("AI Hub", ft.Icons.AUTO_AWESOME, lambda e: self.navigate_to("ai_hub")),
                    ft.Divider(color=ft.Colors.WHITE24),
                    ft.TextButton(
                        "Clear Chat History",
                        icon=ft.Icons.DELETE_OUTLINE,
                        on_click=self.clear_history,
                        style=ft.ButtonStyle(color=ft.Colors.RED_300)
                    ),
                    ft.Container(expand=True),
                    ft.Text("v2.0.0 Mobile", size=10, color=ft.Colors.WHITE_54)
                ]
            )
        )

    def navigate_to(self, view_name):
        """Navigate between views"""
        self.current_view_name = view_name
        
        view_map = {
            "chat": self.chat_view,
            "study": self.study_view,
            "quiz": self.quiz_view,
            "coder": self.coder_view,
            "ai_hub": self.ai_hub_view
        }
        
        self.content_area.content = view_map.get(view_name, self.chat_view)
        
        # Close menu if mobile
        if self.is_mobile and hasattr(self, 'menu_sheet'):
            self.menu_sheet.open = False
            self.menu_sheet.update()
        
        # Update bottom nav colors
        if self.is_mobile:
            self.update()
        else:
            self.content_area.update()

    def sidebar_button(self, text, icon, on_click_handler):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=ft.Colors.WHITE_54),
                ft.Text(text, color=ft.Colors.WHITE_54)
            ]),
            padding=10,
            border_radius=10,
            ink=True,
            on_click=on_click_handler
        )

    def build_chat_area(self):
        """Build responsive chat interface"""
        self.chat_history = ft.ListView(
            expand=True,
            spacing=10,
            auto_scroll=True,
            padding=10
        )
        
        # Responsive input
        input_height = 45 if self.is_mobile else 50
        button_size = 35 if self.is_mobile else 40
        
        self.input_box = ft.TextField(
            hint_text="Ask Medha...",
            border_color=ft.Colors.TRANSPARENT,
            bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
            border_radius=25,
            expand=True,
            multiline=False,
            height=input_height,
            text_size=14 if self.is_mobile else 16,
            on_submit=self.send_message,
            content_padding=ft.Padding(left=20, right=20, top=10, bottom=10)
        )
        
        # Model Selector
        self.model_dropdown = ModelSelector(self.brain, width=150 if self.is_mobile else 220)
        
        # Voice buttons
        self.continuous_voice_mode = False
        
        self.mic_button = ft.IconButton(
            icon=ft.Icons.MIC,
            icon_color=ft.Colors.RED_400,
            icon_size=button_size,
            tooltip="Voice",
            on_click=self.start_listening
        )
        
        self.file_button = ft.IconButton(
            icon=ft.Icons.ATTACH_FILE,
            icon_color=ft.Colors.GREEN_400,
            icon_size=button_size,
            tooltip="Attach File",
            on_click=lambda e: self._open_file_picker()
        )
        
        self.continuous_voice_button = ft.IconButton(
            icon=ft.Icons.RECORD_VOICE_OVER,
            icon_color=ft.Colors.PURPLE_400,
            icon_size=button_size,
            tooltip="Continuous",
            on_click=self.toggle_continuous_voice
        )
        
        # File preview area
        self.file_preview_list = ft.Column(spacing=6)
        self.file_preview_container = ft.Container(
            content=self.file_preview_list,
            padding=8,
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
            border_radius=10,
            visible=False
        )

        # Build input row based on screen size
        if self.is_mobile:
            # Mobile: Compact input with file picker
            input_row = ft.Row([
                self.file_button,
                self.input_box,
                self.mic_button,
                ft.IconButton(
                    icon=ft.Icons.SEND_ROUNDED, 
                    icon_color=ft.Colors.CYAN_400,
                    icon_size=button_size,
                    tooltip="Send",
                    on_click=self.send_message
                )
            ], spacing=5)
            
            # Mobile: Simple header with history and model selector (right aligned)
            header_row = ft.Container(
                content=ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.HISTORY,
                        icon_color=ft.Colors.CYAN_400,
                        icon_size=24,
                        tooltip="History",
                        on_click=self.toggle_history
                    ),
                    ft.Container(expand=True),
                    ft.Container(
                        content=self.model_dropdown,
                        padding=ft.padding.only(right=5)
                    )
                ]),
                padding=ft.padding.only(bottom=5, top=5, left=5, right=5)
            )
        else:
            # Desktop: Full controls with file picker
            input_row = ft.Row([
                self.file_button,
                self.input_box,
                self.mic_button,
                self.continuous_voice_button,
                ft.IconButton(
                    icon=ft.Icons.SEND_ROUNDED, 
                    icon_color=ft.Colors.CYAN_400,
                    icon_size=button_size,
                    tooltip="Send",
                    on_click=self.send_message
                )
            ], spacing=5)
            
            # Desktop: Header with history and model selector
            header_row = ft.Container(
                content=ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.HISTORY,
                        icon_color=ft.Colors.CYAN_400,
                        tooltip="History",
                        on_click=self.toggle_history
                    ),
                    ft.Container(expand=True),
                    self.model_dropdown
                ]),
                padding=ft.Padding(bottom=10)
            )
        
        return ft.Column([
            header_row,
            self.chat_history,
            self.file_preview_container,
            ft.Container(
                content=input_row,
                padding=10,
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
                border_radius=25
            )
        ], expand=True)

    def toggle_history(self, e):
        """Toggle history sidebar/sheet"""
        if self.is_mobile:
            # Show as bottom sheet on mobile
            history_sheet = ft.BottomSheet(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("Chat History", size=20, weight=ft.FontWeight.BOLD),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE,
                                on_click=lambda e: self.close_history_sheet()
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Divider(),
                        ft.Container(
                            content=self.history_view,
                            height=400,
                        )
                    ]),
                    padding=20
                ),
                open=True
            )
            self._page.overlay.append(history_sheet)
            self._page.update()
        else:
            # Toggle sidebar on desktop
            if not hasattr(self, 'history_container'):
                return
            if self.history_container.width == 0:
                self.history_container.width = 250
                self.history_container.opacity = 1
                if getattr(self.history_view, "uid", None):
                    self.history_view.refresh_list()
            else:
                self.history_container.width = 0
                self.history_container.opacity = 0
            self.update()

    def close_history_sheet(self):
        if self._page.overlay:
            self._page.overlay.clear()
            self._page.update()

    def start_new_chat(self):
        self.current_session_id = self.session_manager.create_new_session_id()
        self.brain.chat_history = []
        self.chat_history.controls.clear()
        
        greeting = "Hi! I'm Medha. How can I help you? ❤️"
        self.add_chat_bubble(greeting, False, record_history=True, save=True)
        
        self.history_view.current_session_id = self.current_session_id
        if getattr(self.history_view, "uid", None):
            self.history_view.refresh_list()
        self.update()

    def load_session(self, session_id):
        self.current_session_id = session_id
        session_data = self.session_manager.get_session_content("chat", session_id)
        messages = session_data.get('messages', []) if session_data else []
        
        self.brain.chat_history = messages
        self.chat_history.controls.clear()
        for msg in messages:
            if msg['role'] != 'system':
                self.add_chat_bubble(msg['content'], msg['role'] == 'user', record_history=False, save=False)
        
        self.history_view.current_session_id = session_id
        if getattr(self.history_view, "uid", None):
            self.history_view.refresh_list()
        self.update()

    def save_current_chat(self):
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
        if self.history_view and getattr(self.history_view, "uid", None):
            self.history_view.refresh_list()

    def on_file_picked(self, e):
        """Handle file selection"""
        try:
            if not e.files:
                return

            self._add_selected_files(e.files)
        except Exception as e:
            print(f"Error in on_file_picked: {e}")
            self.add_chat_bubble(f"❌ File picker error: {str(e)}", is_user=False)
            self._page.update()
    
    def _open_file_picker(self):
        """Open file picker with proper error handling"""
        try:
            print("Opening file picker...")
            
            # Desktop: use native file dialog
            if not self.is_mobile:
                if not self._open_desktop_file_dialog():
                    self._show_manual_file_input()
                return

            # Mobile: use FilePicker control
            if self.file_picker:
                self.file_picker.pick_files(
                    allowed_extensions=["jpg", "jpeg", "png", "gif", "pdf", "txt", "doc", "docx", "mp3", "mp4", "wav"],
                    allow_multiple=True
                )
        except Exception as e:
            print(f"Error opening file picker: {e}")
            self.add_chat_bubble(f"❌ Cannot open file picker: {str(e)}", is_user=False)
            self._page.update()

    def _open_desktop_file_dialog(self):
        """Open native file dialog on desktop. Returns True if a file was selected."""
        try:
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            file_paths = filedialog.askopenfilenames(
                title="Select file",
                filetypes=[
                    ("All supported", "*.jpg *.jpeg *.png *.gif *.pdf *.txt *.doc *.docx *.mp3 *.mp4 *.wav"),
                    ("Images", "*.jpg *.jpeg *.png *.gif"),
                    ("Documents", "*.pdf *.txt *.doc *.docx"),
                    ("Audio", "*.mp3 *.wav"),
                    ("Video", "*.mp4"),
                    ("All files", "*.*")
                ]
            )
            root.destroy()

            if file_paths:
                class MockEvent:
                    def __init__(self, paths):
                        self.files = [type('obj', (object,), {'path': p, 'name': os.path.basename(p)}) for p in paths]

                self.on_file_picked(MockEvent(file_paths))
                return True
            return False
        except Exception as e:
            print(f"Desktop file dialog error: {e}")
            return False

    def _add_selected_files(self, files):
        """Add selected files (max 50)."""
        if not files:
            return

        existing_paths = {f["path"] for f in self.selected_files}
        new_files = []

        for f in files:
            if len(self.selected_files) + len(new_files) >= 50:
                break
            if f.path in existing_paths:
                continue
            new_files.append({
                "path": f.path,
                "name": f.name,
                "type": self._guess_file_type(f.name)
            })

        if not new_files and len(self.selected_files) >= 50:
            self.add_chat_bubble("⚠️ You can select up to 50 files.", is_user=False)
        else:
            self.selected_files.extend(new_files)
            if len(self.selected_files) > 50:
                self.selected_files = self.selected_files[:50]
                self.add_chat_bubble("⚠️ Only first 50 files kept.", is_user=False)

        self._refresh_file_preview()
        self._page.update()

    def _remove_selected_file(self, path):
        self.selected_files = [f for f in self.selected_files if f["path"] != path]
        self._refresh_file_preview()
        self._page.update()

    def _clear_selected_files(self, e=None):
        self.selected_files = []
        self._refresh_file_preview()
        self._page.update()

    def _guess_file_type(self, filename):
        ext = os.path.splitext(filename)[1].lower()
        if ext in [".jpg", ".jpeg", ".png", ".gif"]:
            return "image"
        if ext in [".mp4", ".mov", ".avi", ".mkv"]:
            return "video"
        if ext in [".mp3", ".wav", ".m4a", ".aac"]:
            return "audio"
        if ext in [".pdf"]:
            return "pdf"
        if ext in [".doc", ".docx", ".txt", ".md"]:
            return "document"
        return "file"

    def _file_type_icon(self, ftype):
        return {
            "image": ft.Icons.IMAGE,
            "video": ft.Icons.VIDEO_FILE,
            "audio": ft.Icons.AUDIO_FILE,
            "pdf": ft.Icons.PICTURE_AS_PDF,
            "document": ft.Icons.DESCRIPTION,
            "file": ft.Icons.INSERT_DRIVE_FILE
        }.get(ftype, ft.Icons.INSERT_DRIVE_FILE)

    def _refresh_file_preview(self):
        self.file_preview_list.controls.clear()

        if not self.selected_files:
            self.file_preview_container.visible = False
            return

        header = ft.Row([
            ft.Text(f"Selected files ({len(self.selected_files)}/50)", size=12, color=ft.Colors.CYAN_400),
            ft.Container(expand=True),
            ft.TextButton("Clear all", on_click=self._clear_selected_files)
        ])
        self.file_preview_list.controls.append(header)

        for f in self.selected_files:
            row = ft.Row([
                ft.Icon(self._file_type_icon(f["type"]), size=16, color=ft.Colors.CYAN_200),
                ft.Text(f["name"], size=12, overflow=ft.TextOverflow.ELLIPSIS, max_lines=1, expand=True),
                ft.IconButton(icon=ft.Icons.CLOSE, icon_size=16, on_click=lambda e, p=f["path"]: self._remove_selected_file(p))
            ], spacing=6)
            self.file_preview_list.controls.append(row)

        self.file_preview_container.visible = True
    
    def _show_manual_file_input(self):
        """Show manual file path input for desktop"""
        def close_dialog(e):
            dialog.open = False
            self._page.update()
        
        def submit_path(e):
            raw = path_input.value or ""
            paths = [p.strip() for p in raw.replace("\n", ";").split(";") if p.strip()]
            valid_paths = [p for p in paths if os.path.exists(p)]

            if valid_paths:
                dialog.open = False
                self._page.update()
                class MockEvent:
                    def __init__(self, paths):
                        self.files = [type('obj', (object,), {'path': p, 'name': os.path.basename(p)}) for p in paths]
                self.on_file_picked(MockEvent(valid_paths))
            else:
                error_text.value = "❌ File not found!"
                error_text.visible = True
                self._page.update()
        
        path_input = ft.TextField(
            label="File Path(s)",
            hint_text="Enter full paths separated by ; or new lines",
            width=500,
            multiline=True,
            min_lines=2,
            max_lines=4,
            on_submit=submit_path
        )
        
        error_text = ft.Text("", color=ft.Colors.RED_400, visible=False)
        
        dialog = ft.AlertDialog(
            title=ft.Text("📎 Select File"),
            content=ft.Column([
                ft.Text("Enter the full path to your file:"),
                path_input,
                error_text,
                ft.Text("Supported: PDF, Images, Text, Audio, Video, Documents", size=10, color=ft.Colors.WHITE_54)
            ], tight=True, spacing=10),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.TextButton("Open", on_click=submit_path)
            ]
        )
        
        self._page.dialog = dialog
        dialog.open = True
        self._page.update()

    def start_listening(self, e):
        """Voice input"""
        self.input_box.hint_text = "🎤 Listening..."
        self.input_box.disabled = True
        self._page.update()
        
        def on_speech(text):
            self.input_box.disabled = False
            self.input_box.hint_text = "Ask Medha..."
            
            if not text or text.strip() == "":
                self.input_box.update()
                return
                
            self.input_box.value = text
            self.input_box.update()
            self.send_message(None, use_voice=True)
            
        self.voice.listen(on_speech, language="hi-IN")
    
    def toggle_continuous_voice(self, e):
        """Continuous voice mode"""
        self.continuous_voice_mode = not self.continuous_voice_mode
        
        if self.continuous_voice_mode:
            self.continuous_voice_button.icon_color = ft.Colors.GREEN_400
            self.add_chat_bubble("🎙️ Continuous Mode ON!", is_user=False)
            self._page.update()
            self._continuous_listen()
        else:
            self.continuous_voice_button.icon_color = ft.Colors.PURPLE_400
            self.add_chat_bubble("⏹️ Continuous Mode OFF", is_user=False)
            self._page.update()
    
    def _continuous_listen(self):
        """Continuous listening loop"""
        if not self.continuous_voice_mode:
            return
        
        self.input_box.hint_text = "🎙️ CONTINUOUS MODE..."
        self._page.update()
        
        def on_speech(text):
            if not self.continuous_voice_mode:
                self.input_box.hint_text = "Ask Medha..."
                self._page.update()
                return
            
            if text and text.strip() != "":
                self.voice.stop_speaking()
                self.input_box.value = text
                self._page.update()
                
                stop_words = ["stop listening", "stop mode", "बंद करो", "stop"]
                if any(stop in text.lower() for stop in stop_words):
                    self.continuous_voice_mode = False
                    self.continuous_voice_button.icon_color = ft.Colors.PURPLE_400
                    self.add_chat_bubble("⏹️ Stopping...", is_user=False, record_history=False, save=False)
                    self.input_box.hint_text = "Ask Medha..."
                    self._page.update()
                    return
                
                threading.Thread(target=lambda: self.send_message(None, use_voice=True), daemon=True).start()
            
            if self.continuous_voice_mode:
                def restart_listening():
                    time.sleep(1) 
                    if self.continuous_voice_mode:
                         self.input_box.hint_text = "✨ Listening..."
                         self.input_box.update()
                         self.voice.listen(on_speech, language="hi-IN")
                
                threading.Thread(target=restart_listening, daemon=True).start()
        
        self.voice.listen(on_speech, language="hi-IN")

    def send_message(self, e, use_voice=False):
        user_text = self.input_box.value
        if not user_text and not self.selected_files:
            return
        
        self.current_request_id += 1
        request_id = self.current_request_id
        
        if user_text:
            self.add_chat_bubble(user_text, is_user=True, record_history=True, save=True)
        self.input_box.value = ""
        self._page.update()
        
        self.processing_request = True
        
        # Build context with selected files (up to 50)
        user_prompt = user_text.strip() if user_text else ""
        if not user_prompt:
            user_prompt = "Summarize the selected files briefly." 
        if self.selected_files:
            self.add_chat_bubble("📎 Processing selected files...", is_user=False, record_history=False, save=False)
            self._page.update()

            file_contexts = []
            for f in self.selected_files:
                try:
                    fc = self.file_handler.process_file(f["path"])
                    file_contexts.append(f"[File: {f['name']}]\n{fc}")
                except Exception as ex:
                    file_contexts.append(f"[File: {f['name']}]\n❌ Error: {ex}")

            context_text = f"""[Selected File Contexts]
{chr(10).join(file_contexts)}

[User Question]: {user_prompt}

Please answer based on the selected file contents above."""
        else:
            context_text = user_prompt
        
        response = self.brain.ask(context_text)
        
        if request_id != self.current_request_id:
            self.processing_request = False
            return None
        
        self.add_chat_bubble(response, is_user=False, record_history=True, save=True)
        self._page.update()
        self.processing_request = False
        
        if use_voice:
            speech_text = response[:500] if len(response) < 500 else response[:500] + "..."
            speech_text = speech_text.replace("**", "").replace("*", "").replace("#", "")
            self.voice.speak(speech_text, lang='hi')
        
        return response
        
    def clear_history(self, e):
        """Clear chat"""
        self.chat_history.controls.clear()
        self.brain.chat_history.clear()
        self.add_chat_bubble("💬 History cleared!", is_user=False)
        
        # Close menu if open
        if self.is_mobile and hasattr(self, 'menu_sheet'):
            self.menu_sheet.open = False
            self.menu_sheet.update()
        
        self._page.update()

    def add_chat_bubble(self, text, is_user, record_history=True, save=True):
        """Add responsive chat bubble"""
        bubble_color = ft.Colors.CYAN_900 if is_user else "#2b2b2b"
        align = ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START
        
        # Responsive bubble width
        max_width = 300 if self.is_mobile else 600
        
        message_content = ft.Container(
            content=ft.Markdown(
                text,
                selectable=True,
                extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                on_tap_link=lambda e: self._page.launch_url(e.data)
            ),
            padding=12 if self.is_mobile else 15,
            bgcolor=bubble_color,
            border_radius=ft.BorderRadius.only(
                top_left=15, top_right=15, 
                bottom_left=15 if is_user else 5,
                bottom_right=5 if is_user else 15
            ),
            width=max_width,
        )
        
        # Speaker button for AI messages
        if not is_user and not self.is_mobile:  # Skip speaker on mobile to save space
            speaker_button = ft.IconButton(
                icon=ft.Icons.VOLUME_UP,
                icon_color=ft.Colors.CYAN_400,
                icon_size=18,
                data={"speaking": False}
            )
            
            def toggle_speak(e):
                if speaker_button.data["speaking"]:
                    self.voice.stop_speaking()
                    speaker_button.icon = ft.Icons.VOLUME_UP
                    speaker_button.data["speaking"] = False
                    speaker_button.update()
                else:
                    speech_text = text.replace("**", "").replace("*", "")
                    speaker_button.icon = ft.Icons.STOP
                    speaker_button.data["speaking"] = True
                    speaker_button.update()
                    
                    def speak_and_reset():
                        self.voice.speak(speech_text, lang='hi')
                        speaker_button.icon = ft.Icons.VOLUME_UP
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
                        [message_content, speaker_button],
                        spacing=5,
                        horizontal_alignment=ft.CrossAxisAlignment.START
                    )
                ],
                alignment=align
            )
        else:
            bubble = ft.Row([message_content], alignment=align)
        
        self.chat_history.controls.append(bubble)

        if record_history:
            self.brain.chat_history.append({"role": "user" if is_user else "assistant", "content": text})
            if save:
                self.save_current_chat()
