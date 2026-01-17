import flet as ft
from ui.model_selector import ModelSelector
from core.session_manager import SessionManager
from ui.history_view import SessionHistoryView
from core.file_handler import FileHandler
from ui.file_picker_helper import FilePickerHelper
from core.themes import theme

class StudyNotesView(ft.Column):
    def __init__(self, brain):
        super().__init__()
        self.brain = brain
        self.expand = True
        self.current_notes = ""
        self.chat_history = []
        
        self.session_manager = SessionManager()
        self.current_session_id = self.session_manager.create_new_session_id()

        self.file_helper = FilePickerHelper(FileHandler())
        
        # Get Current Theme
        current_theme = theme.get_theme()
        
        # --- UI COMPONENTS ---
        
        # 1. Notes Display (Left Side)
        self.notes_display = ft.Markdown(
            "📚 **Welcome to Smart Study!**\n\nEnter a topic on the right side to generate comprehensive notes.\nI can research online to get you the latest information.",
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            on_tap_link=lambda e: self.launch_url(e.data),
            code_theme="atom-one-dark"
        )
        
        self.notes_contrainer = ft.Container(
            content=ft.Column([self.notes_display], scroll=ft.ScrollMode.AUTO),
            expand=True,
            bgcolor=ft.Colors.with_opacity(0.05, current_theme["text_primary"]),
            border_radius=10,
            padding=20
        )

        # 2. Chat Area (Right Side)
        self.chat_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)
        self.chat_input = ft.TextField(
            hint_text="Enter topic or ask for changes...",
            expand=True,
            border_radius=20,
            on_submit=self.handle_chat_submit,
            border_color=ft.Colors.TRANSPARENT,
            bgcolor=ft.Colors.with_opacity(0.1, current_theme["text_primary"]),
            color=current_theme["text_primary"],
            hint_style=ft.TextStyle(color=current_theme["text_secondary"])
        )
        self.file_button = ft.IconButton(
            ft.Icons.ATTACH_FILE, 
            tooltip="Attach File(s)", 
            on_click=self.open_file_picker,
            icon_color=current_theme["text_primary"]
        )

        # --- MAIN LAYOUT ---
        # Model Selector
        self.model_dropdown = ModelSelector(self.brain)
        
        # History View
        self.history_view = SessionHistoryView(
            section="study",
            current_session_id=self.current_session_id,
            on_session_select=self.load_session,
            on_new_chat=self.start_new_session
        )
        
        self.history_drawer = ft.Container(
            content=self.history_view,
            width=0, opacity=0,
            animate=300,
            bgcolor=current_theme["bg_secondary"]
        )
        
        self.toggle_btn = ft.IconButton(
            ft.Icons.HISTORY, 
            on_click=self.toggle_history, 
            tooltip="Study History",
            icon_color=current_theme["text_primary"]
        )

        self.header_text = ft.Text("🎓 Advanced Study Companion", size=24, weight=ft.FontWeight.BOLD, color=current_theme["accent"])

        self.chat_area_container = ft.Container(
            content=ft.Column([
                ft.Text("💬 Study Assistant", size=16, weight="bold", color=current_theme["text_primary"]),
                ft.Container(content=self.chat_list, expand=True, bgcolor=ft.Colors.with_opacity(0.05, current_theme["text_primary"]), border_radius=10, padding=10),
                self.file_helper.preview_container,
                ft.Row([
                    self.file_button, 
                    self.chat_input, 
                    ft.IconButton(ft.Icons.SEND, on_click=self.handle_chat_submit, icon_color=current_theme["accent"])
                ])
            ]),
            expand=4,
            padding=10
        )

        self.controls = [
            ft.Row([
                self.header_text,
                ft.Container(expand=True),
                self.toggle_btn,
                self.model_dropdown
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(color=ft.Colors.with_opacity(0.1, current_theme["text_primary"])),
            ft.Container(
                content=ft.Row([
                    self.history_drawer,
                    # Left: Notes (60%)
                    ft.Container(content=self.notes_contrainer, expand=6),
                    # Right: Chat (40%)
                    self.chat_area_container
                ], expand=True),
                expand=True
            )
        ]
    
    def update_theme(self):
        """Update colors based on current theme"""
        current_theme = theme.get_theme()
        
        self.notes_contrainer.bgcolor = ft.Colors.with_opacity(0.05, current_theme["text_primary"])
        self.chat_input.bgcolor = ft.Colors.with_opacity(0.1, current_theme["text_primary"])
        self.chat_input.color = current_theme["text_primary"]
        self.chat_input.hint_style.color = current_theme["text_secondary"]
        
        self.file_button.icon_color = current_theme["text_primary"]
        self.toggle_btn.icon_color = current_theme["text_primary"]
        self.header_text.color = current_theme["accent"]
        self.history_drawer.bgcolor = current_theme["bg_secondary"]
        
        # Update Chat Area Background
        # The container holding chat_list (2nd child of chat_area_container's Column)
        if len(self.chat_area_container.content.controls) > 1:
             self.chat_area_container.content.controls[1].bgcolor = ft.Colors.with_opacity(0.05, current_theme["text_primary"])
             self.chat_area_container.content.controls[0].color = current_theme["text_primary"] # Header text
        
        # Update send button color
        row_controls = self.chat_area_container.content.controls[3].controls
        if len(row_controls) > 2:
             row_controls[2].icon_color = current_theme["accent"]

        # Update Model Selector
        self.model_dropdown.update_theme()
        
        # Update existing bubbles
        for row in self.chat_list.controls:
             if isinstance(row, ft.Row) and len(row.controls) > 0:
                  bubble = row.controls[0]
                  is_user = row.alignment == ft.MainAxisAlignment.END
                  bubble.bgcolor = current_theme["accent"] if is_user else ft.Colors.with_opacity(0.1, current_theme["text_primary"])
                  # Update Text Color inside bubble if needed
                  content_col = bubble.content
                  if isinstance(content_col, ft.Column) and len(content_col.controls) > 0:
                       header_text = content_col.controls[0]
                       header_text.color = ft.Colors.with_opacity(0.7, ft.Colors.WHITE) if is_user else current_theme["text_secondary"]

        if self.page:
            self.update()

    def did_mount(self):
        """Called when control is added to page"""
        if self.page:
            is_mobile = self.page.platform in [ft.PagePlatform.ANDROID, ft.PagePlatform.IOS]
            self.file_helper.attach(self.page, is_mobile)
        self.add_chat_bubble("👋 Hi! What subject are we mastering today?", is_user=False, run_update=False)
        self.history_view.refresh_list()
        if self.page:
            self.update()

    def open_file_picker(self, e):
        self.file_helper.open_picker()

    def launch_url(self, url):
        # Open links if any
        pass

    def add_chat_bubble(self, text, is_user=False, run_update=True):
        current_theme = theme.get_theme()
        
        bubble = ft.Container(
            content=ft.Column([
                ft.Text("You" if is_user else "Medha Tutor", size=10, color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE) if is_user else current_theme["text_secondary"]),
                ft.Markdown(text, code_theme="atom-one-dark")
            ]),
            bgcolor=current_theme["accent"] if is_user else ft.Colors.with_opacity(0.1, current_theme["text_primary"]),
            padding=10,
            border_radius=10,
            width=None if is_user else 300
        )
        self.chat_list.controls.append(
            ft.Row([bubble], alignment=ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START)
        )
        # Store in history
        self.chat_history.append({"role": "user" if is_user else "assistant", "content": text})
        
        self.save_current_session()
        
        if run_update and self.page:
            self.update()

    def toggle_history(self, e):
        if self.history_drawer.width == 0:
            self.history_drawer.width = 250
            self.history_drawer.opacity = 1
            self.history_view.refresh_list()
        else:
            self.history_drawer.width = 0
            self.history_drawer.opacity = 0
        if self.page:
            self.update()

    def start_new_session(self):
        self.current_session_id = self.session_manager.create_new_session_id()
        self.current_notes = ""
        self.notes_display.value = "📚 **Welcome to Smart Study!**..."
        self.chat_history = []
        self.chat_list.controls.clear()
        self.history_view.current_session_id = self.current_session_id
        self.history_view.refresh_list()
        if self.page:
            self.update()

    def load_session(self, session_id):
        data = self.session_manager.get_session_content("study", session_id)
        if not data: return
        
        self.current_session_id = session_id
        self.current_notes = data.get('notes_content', "")
        self.notes_display.value = self.current_notes if self.current_notes else "No notes content."
        
        self.chat_history = data.get('messages', [])
        # Rebuild Chat
        self.chat_list.controls.clear()
        for msg in self.chat_history:
             is_user = msg['role'] == 'user'
             self.add_chat_bubble(msg['content'], is_user=is_user, run_update=False)
             self.chat_history.pop() # Remove duplicate caused by add_chat_bubble
        
        self.history_view.current_session_id = session_id
        self.history_view.refresh_list()
        if self.page:
            self.update()

    def save_current_session(self):
        # Infer title
        title = "New Study Session"
        for msg in self.chat_history:
            if msg['role'] == 'user':
                title = msg['content'][:30]
                break
        
        self.session_manager.save_session(
            "study",
            self.current_session_id,
            title,
            self.chat_history,
            extra_data={"notes_content": self.current_notes}
        )

    def handle_chat_submit(self, e):
        prompt = self.chat_input.value
        if not prompt and not self.file_helper.selected_files:
            return
        
        self.chat_input.value = ""
        if prompt:
            self.add_chat_bubble(prompt, is_user=True)
        # update() called inside

        # Image generation shortcut
        if prompt.strip().lower().startswith("/image") or prompt.strip().lower().startswith("image:"):
            resp = self.brain.generate_content(prompt)
            self.add_chat_bubble(resp, is_user=False)
            return

        if self.file_helper.selected_files:
            self.add_chat_bubble("📎 Processing selected files...", is_user=False)
            prompt = self.file_helper.build_prompt_with_files(prompt)
        
        if not self.current_notes:
            self.generate_new_notes(prompt)
        else:
            self.refine_notes(prompt)

    def generate_new_notes(self, topic):
        self.add_chat_bubble(f"🔍 Researching '{topic}'...", is_user=False)
        
        # 1. Deep Research
        research = self.brain.deep_research(topic)
        context = research['context'] if research else "Use general knowledge."
        
        if research:
            self.add_chat_bubble(f"found {len(research['results'])} sources. Writing notes...", is_user=False)

        # 2. Generate Content
        system_prompt = f"""You are an Expert Tutor.
        Task: Create comprehensive study notes on the user's topic.
        Research Base: {context}
        
        Format: Markdown.
        Structure:
        - Title & Overview
        - Key Concepts (Bullet points)
        - Detailed Explanations
        - Examples / Analogies
        - Summary
        """
        
        response = self.brain.generate_content(topic, system_role=system_prompt)
        self.current_notes = response
        self.notes_display.value = response
        self.save_current_session() # Save notes
        self.update()
        self.add_chat_bubble("✅ Notes generated! You can ask me to simplify, expand, or add quiz questions.", is_user=False)

    def refine_notes(self, instruction):
        self.add_chat_bubble("✍️ Refining notes...", is_user=False)
        
        system_prompt = f"""You are an Expert Tutor.
        Current Notes:
        {self.current_notes}
        
        User Instruction: {instruction}
        
        Task: Rewrite or Modify the notes based on the instruction. Return the FULL updated markdown.
        """
        
        response = self.brain.generate_content("Update the notes.", system_role=system_prompt)
        self.current_notes = response
        self.notes_display.value = response
        self.save_current_session() # Save notes
        self.update()
        self.add_chat_bubble("✅ Notes updated!", is_user=False)
