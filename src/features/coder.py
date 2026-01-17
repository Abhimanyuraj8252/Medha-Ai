import flet as ft
import os
import webbrowser
import re
import json
from datetime import datetime
from ui.model_selector import ModelSelector
from core.session_manager import SessionManager
from ui.history_view import SessionHistoryView
from core.file_handler import FileHandler
from ui.file_picker_helper import FilePickerHelper
from core.themes import theme

class CoderView(ft.Column):
    def __init__(self, brain):
        super().__init__()
        self.brain = brain
        self.expand = True
        self.current_code = {}  # {filename: content}
        self.project_path = None
        self.chat_history = []  # For the coding conversation
        
        self.session_manager = SessionManager()
        self.current_session_id = self.session_manager.create_new_session_id()

        self.file_helper = FilePickerHelper(FileHandler())
        
        # Get Current Theme
        current_theme = theme.get_theme()
        
        # --- UI COMPONENTS ---
        
        # 1. Editor Area (Custom Tabs Implementation)
        self.active_file = None
        self.tab_headers = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=5)
        self.tab_body = ft.Container(
            content=ft.Text("No Files Created", color=current_theme["text_secondary"], italic=True),
            expand=True,
            bgcolor=ft.Colors.with_opacity(0.02, current_theme["text_primary"]),
            border_radius=5,
            padding=10
        )
        
        # 2. Chat Area (For refining code)
        self.chat_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)
        self.chat_input = ft.TextField(
            hint_text="Ask to change code... (e.g. 'Make background blue', 'Add login form')",
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
        
        # 3. Control Bar
        self.controls_bar = ft.Row([
            ft.IconButton(ft.Icons.PLAY_ARROW_ROUNDED, tooltip="Preview Website", icon_color=ft.Colors.GREEN_400, on_click=self.preview_project),
            ft.IconButton(ft.Icons.FOLDER_OPEN, tooltip="Open Folder", icon_color=ft.Colors.AMBER_400, on_click=self.open_folder),
            ft.IconButton(ft.Icons.DELETE_SWEEP, tooltip="Reset Project", icon_color=current_theme["error"] if "error" in current_theme else ft.Colors.RED_400, on_click=self.reset_project),
        ])

        # Model Selector
        self.model_dropdown = ModelSelector(self.brain)
        
        # History View
        self.history_view = SessionHistoryView(
            section="coder",
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
            tooltip="Project History",
            icon_color=current_theme["text_primary"]
        )

        self.header_text = ft.Text("🚀 Medha Coder Pro", size=24, weight=ft.FontWeight.BOLD, color=current_theme["accent"])
        
        self.editor_container = ft.Container(
             content=ft.Column([
                 self.tab_headers,
                 ft.Divider(height=1, color=ft.Colors.with_opacity(0.1, current_theme["text_primary"])),
                 self.tab_body
             ], spacing=0),
             expand=6,
             bgcolor=ft.Colors.with_opacity(0.05, current_theme["text_primary"]),
             border_radius=10,
             padding=10
        )

        self.chat_area_container = ft.Container(
            content=ft.Column([
                ft.Text("⚡ Project Assistant", size=16, weight="bold", color=current_theme["text_primary"]),
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

        # --- MAIN LAYOUT ---
        self.controls = [
            ft.Row([
                self.header_text,
                ft.Container(expand=True),
                self.toggle_btn,
                self.model_dropdown,
                ft.VerticalDivider(width=10, color=ft.Colors.TRANSPARENT),
                self.controls_bar
            ]),
            ft.Divider(color=ft.Colors.with_opacity(0.1, current_theme["text_primary"])),
            ft.Container(
                content=ft.Row([
                    self.history_drawer,
                    # Left Side: Editor (60%)
                    self.editor_container,
                    # Right Side: Chat/Prompt (40%)
                    self.chat_area_container
                ], expand=True),
                expand=True
            )
        ]
        
        # Initial Welcome Message (will be added after page is ready)
        self._init_messages = [
            "👋 Hi! Describe your dream website or app. I'll build it for you!",
            "💡 Tip: You can ask me to research tech stacks or use specific frameworks."
        ]
        
    def update_theme(self):
        """Update colors based on current theme"""
        current_theme = theme.get_theme()
        
        self.editor_container.bgcolor = ft.Colors.with_opacity(0.05, current_theme["text_primary"])
        self.editor_container.content.controls[1].color = ft.Colors.with_opacity(0.1, current_theme["text_primary"]) # Divider
        
        # Update Tab Body background if no file
        if not self.active_file:
             self.tab_body.bgcolor = ft.Colors.with_opacity(0.02, current_theme["text_primary"])
             if isinstance(self.tab_body.content, ft.Text):
                  self.tab_body.content.color = current_theme["text_secondary"]
        else:
             # Make sure code editor contrast is okay
             pass 

        self.chat_input.bgcolor = ft.Colors.with_opacity(0.1, current_theme["text_primary"])
        self.chat_input.color = current_theme["text_primary"]
        self.chat_input.hint_style.color = current_theme["text_secondary"]
        
        self.file_button.icon_color = current_theme["text_primary"]
        self.toggle_btn.icon_color = current_theme["text_primary"]
        self.header_text.color = current_theme["accent"]
        self.history_drawer.bgcolor = current_theme["bg_secondary"]
        
        # Reset Icon Color
        self.controls_bar.controls[2].icon_color = current_theme["error"] if "error" in current_theme else ft.Colors.RED_400

        # Update Chat Area Background
        if len(self.chat_area_container.content.controls) > 1:
             self.chat_area_container.content.controls[1].bgcolor = ft.Colors.with_opacity(0.05, current_theme["text_primary"])
             self.chat_area_container.content.controls[0].color = current_theme["text_primary"] # Header
        
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
        
        # Update Tab Headers
        self.update_editor_tabs(theme_update=True)
        
        if self.page:
            self.update()
    
    def did_mount(self):
        """Called when control is added to page"""
        if self.page:
            is_mobile = self.page.platform in [ft.PagePlatform.ANDROID, ft.PagePlatform.IOS]
            self.file_helper.attach(self.page, is_mobile)
        # Add initial messages
        for msg in self._init_messages:
            self.add_chat_bubble(msg, is_user=False, run_update=False, record_history=False)
        # Initialize history
        self.history_view.refresh_list()
        if self.page:
            self.update()

    def add_chat_bubble(self, text, is_user=False, run_update=True, record_history=True):
        current_theme = theme.get_theme()
        
        bubble = ft.Container(
            content=ft.Column([
                ft.Text("You" if is_user else "Medha Coder", size=10, color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE) if is_user else current_theme["text_secondary"]),
                ft.Markdown(text, selectable=True, code_theme="atom-one-dark")
            ]),
            bgcolor=current_theme["accent"] if is_user else ft.Colors.with_opacity(0.1, current_theme["text_primary"]),
            padding=10,
            border_radius=10,
            width=None if is_user else 400
        )
        self.chat_list.controls.append(
            ft.Row([bubble], alignment=ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START)
        )
        if record_history:
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
        self.current_code = {}
        self.active_file = None
        self.chat_history = []
        self.chat_list.controls.clear()
        
        self.tab_headers.controls.clear()
        self.tab_body.content = ft.Text("No Files Created", color=ft.Colors.WHITE54, italic=True)
        
        self.history_view.current_session_id = self.current_session_id
        self.history_view.refresh_list()
        if self.page:
            self.update()

    def load_session(self, session_id):
        data = self.session_manager.get_session_content("coder", session_id)
        if not data: return
        
        self.current_session_id = session_id
        self.current_code = data.get('current_code', {})
        self.chat_history = data.get('messages', [])
        
        # Restore Chat
        self.chat_list.controls.clear()
        for msg in self.chat_history:
             is_user = msg['role'] == 'user'
             self.add_chat_bubble(msg['content'], is_user=is_user, run_update=False, record_history=False)

        # Restore Tabs
        self.tab_headers.controls.clear()
        for filename in self.current_code:
            # We don't have create_tab, so we just rely on update_editor_tabs
            pass
            
        # Select first file if any
        if self.current_code:
            first_file = list(self.current_code.keys())[0]
            self.select_tab(first_file)
        else:
             self.tab_body.content = ft.Text("No Files Created", color=ft.Colors.WHITE54, italic=True)

        self.history_view.current_session_id = session_id
        self.history_view.refresh_list()
        if self.page:
            self.update()

    def save_current_session(self):
        title = "New Project"
        for msg in self.chat_history:
            if msg['role'] == 'user':
                title = msg['content'][:30]
                break
        
        self.session_manager.save_session(
            "coder",
            self.current_session_id,
            title,
            self.chat_history,
            extra_data={"current_code": self.current_code}
        )
        
    def select_tab(self, filename):
        self.active_file = filename
        code = self.current_code.get(filename, "")
        self.tab_body.content = ft.Column([
            ft.Text(f"📄 {filename}", size=12, color=ft.Colors.CYAN_100),
            ft.Markdown(f"```python\n{code}\n```" if filename.endswith(".py") else f"```\n{code}\n```", 
                       selectable=True, extension_set=ft.MarkdownExtensionSet.GITHUB_WEB, code_theme="atom-one-dark")
        ], scroll=ft.ScrollMode.AUTO)
        self.update_editor_tabs() # To update styles (active tab highlight)
        self.update()

    def handle_chat_submit(self, e):
        prompt = self.chat_input.value
        if not prompt and not self.file_helper.selected_files:
            return
        
        self.chat_input.value = ""
        if prompt:
            self.add_chat_bubble(prompt, is_user=True, record_history=True)
        self.update()

        # Image generation shortcut
        if prompt.strip().lower().startswith("/image") or prompt.strip().lower().startswith("image:"):
            resp = self.brain.generate_content(prompt)
            self.add_chat_bubble(resp, is_user=False)
            return

        if self.file_helper.selected_files:
            self.add_chat_bubble("📎 Processing selected files...", is_user=False, record_history=True)
            prompt = self.file_helper.build_prompt_with_files(prompt)
        
        if not self.current_code:
            # Case 1: New Project Generation
            self.generate_new_project(prompt)
        else:
            # Case 2: Edit/Refine Existing Code
            self.refine_existing_project(prompt)

    def open_file_picker(self, e):
        self.file_helper.open_picker()

    def generate_new_project(self, prompt):
        self.add_chat_bubble("🔍 Researching & Planning project structrure... please wait...", is_user=False)
        
        # 1. Research Step
        research_data = self.brain.deep_research(f"best web technology stack, libraries and design trends for {prompt} in 2026")
        research_context = research_data['context'] if research_data else "No specific research found, using general best practices."
        if research_data:
             self.add_chat_bubble(f"📚 **Research Insights:**\n{research_data['display'][:300]}...\n*(Applying this knowledge)*", is_user=False)

        # 2. Generation Prompt
        system_prompt = f"""You are an Expert Developer.
        Task: Create a complete, production-ready web project based on user request.
        Research Context: {research_context}
        
        Rules:
        1. Output MUST be valid JSON string mapping filenames to content. 
           Example: {{ "index.html": "<html>...</html>", "style.css": "..." }}
        2. Create multiple files (HTML, CSS, JS) for a complete solution.
        3. Use modern frameworks (Tailwind, Bootstrap, Vue) via CDN if applicable.
        4. Code must be clean, commented, and working.
        
        Output format: JSON ONLY. No markdown blocks like ```json. Just raw JSON string.
        """
        
        response = self.brain.generate_content(prompt, system_role=system_prompt)
        self.process_ai_response(response)

    def refine_existing_project(self, prompt):
        self.add_chat_bubble("🛠️ Updating code...", is_user=False)
        
        # Serialize current code state for AI
        code_context = json.dumps(self.current_code, indent=2)
        
        system_prompt = f"""You are an Expert Developer refining an existing project.
        Current Project State (JSON files):
        {code_context}
        
        User Request: {prompt}
        
        Rules:
        1. Return the COMPLETE content of ONLY the files that need to change.
        2. If a new file is needed, include it.
        3. Output MUST be a JSON object {{ "filename": "new content" }}.
        4. Do not return files that didn't change (to save tokens).
        
        Output format: JSON ONLY.
        """
        
        response = self.brain.generate_content("Update the code.", system_role=system_prompt)
        self.process_ai_response(response, is_update=True)

    def process_ai_response(self, response, is_update=False):
        try:
            # Clean possible markdown
            clean_json = response.replace("```json", "").replace("```", "").strip()
            # Sometimes AI adds text before/after
            start = clean_json.find('{')
            end = clean_json.rfind('}') + 1
            if start != -1 and end != -1:
                clean_json = clean_json[start:end]
            
            new_files = json.loads(clean_json)
            
            # Update state
            self.current_code.update(new_files)
            
            # Save logic
            self.save_project_to_disk()
            
            # Update UI Editors
            self.update_editor_tabs()
            
            msg = "✨ Project created!" if not is_update else f"✨ Updated {len(new_files)} files!"
            self.add_chat_bubble(msg, is_user=False)
            
        except json.JSONDecodeError as e:
            self.add_chat_bubble(f"❌ AI Error: Invalid JSON response. {e}", is_user=False)
            print(response) # Debug

    def update_editor_tabs(self, theme_update=False):
        current_theme = theme.get_theme()
        
        self.tab_headers.controls.clear()
        
        if not self.current_code:
            self.tab_body.content = ft.Text("No Files Created", color=current_theme["text_secondary"], italic=True)
            if not theme_update and self.page: self.update()
            return

        # If no active file or active file deleted, set to first
        if not self.active_file or self.active_file not in self.current_code:
            self.active_file = list(self.current_code.keys())[0]

        for filename in self.current_code.keys():
            is_active = filename == self.active_file
            
            # Create a button for the tab
            btn = ft.Container(
                content=ft.Text(
                    filename, 
                    color=current_theme["accent"] if is_active else current_theme["text_secondary"],
                    weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL
                ),
                padding=10,
                border_radius=ft.border_radius.only(top_left=5, top_right=5),
                bgcolor=ft.Colors.with_opacity(0.1, current_theme["text_primary"]) if is_active else ft.Colors.TRANSPARENT,
                on_click=lambda e, f=filename: self.switch_tab(f),
                ink=True
            )
            self.tab_headers.controls.append(btn)
        
        if not theme_update:
             # Set body content
             content = self.current_code.get(self.active_file, "")
             self.tab_body.content = ft.TextField(
                 value=content,
                 multiline=True,
                 read_only=True,
                 text_style=ft.TextStyle(font_family="Consolas", size=12, color=current_theme["text_primary"]),
                 bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLACK), 
                 border_color=ft.Colors.TRANSPARENT,
                 expand=True
             )
             self.update()

    def switch_tab(self, filename):
        self.active_file = filename
        self.update_editor_tabs()

    def save_project_to_disk(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not self.project_path:
             self.project_path = os.path.abspath(f"medha_coder_project_{timestamp}")
             os.makedirs(self.project_path, exist_ok=True)
        
        for fname, content in self.current_code.items():
            full_path = os.path.join(self.project_path, fname)
            # Handle folders in filenames "css/style.css"
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
                
    def preview_project(self, e):
        if not self.project_path: return
        # Find index.html
        for fname in self.current_code:
            if fname.endswith(".html"):
                webbrowser.open(f"file:///{os.path.join(self.project_path, fname)}")
                self.add_chat_bubble("🌐 Opening preview...", is_user=False)
                return
        self.add_chat_bubble("⚠️ No HTML file found to preview.", is_user=False)

    def open_folder(self, e):
        if self.project_path: os.startfile(self.project_path)

    def reset_project(self, e):
        self.current_code = {}
        self.project_path = None
        self.chat_history = []
        self.update_editor_tabs()
        self.chat_list.controls.clear()
        self.add_chat_bubble("🗑️ Project reset. What shall we build next?", is_user=False)
        if self.page:
            self.update()
