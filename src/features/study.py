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

        self.stop_button = ft.IconButton(
            ft.Icons.STOP_CIRCLE_OUTLINED,
            tooltip="Stop Generation",
            icon_color=current_theme["error"],
            visible=False,
            on_click=self.stop_generation_click
        )
        
        self.send_button = ft.IconButton(ft.Icons.SEND, on_click=self.handle_chat_submit, icon_color=current_theme["accent"])

        # Config Controls
        # Config Controls (Grouped in ExpansionTile)
        self.purpose_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("General Study"),
                ft.dropdown.Option("Exam Prep"),
                ft.dropdown.Option("Placement/Interview"),
                ft.dropdown.Option("Deep Dive Research"),
            ],
            value="General Study",
            expand=True,
            label="Purpose",
            height=40,
            content_padding=10,
            text_size=12,
            label_style=ft.TextStyle(size=10, color=current_theme["text_secondary"]),
            text_style=ft.TextStyle(size=12, color=current_theme["text_primary"]),
            border_color=ft.Colors.with_opacity(0.2, current_theme["text_primary"]),
        )
        
        self.level_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("Beginner"),
                ft.dropdown.Option("Intermediate"),
                ft.dropdown.Option("Advanced"),
                ft.dropdown.Option("Extreme/PhD"),
            ],
            value="Intermediate",
            expand=True,
            label="Level",
            height=40,
            content_padding=10,
            text_size=12,
            label_style=ft.TextStyle(size=10, color=current_theme["text_secondary"]),
            text_style=ft.TextStyle(size=12, color=current_theme["text_primary"]),
            border_color=ft.Colors.with_opacity(0.2, current_theme["text_primary"]),
        )

        self.lang_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("English"),
                ft.dropdown.Option("Hindi (Pure)"),
                ft.dropdown.Option("Hinglish (Mix)"),
                ft.dropdown.Option("Simple English"),
                ft.dropdown.Option("Marathi"),
                ft.dropdown.Option("Bengali"),
                ft.dropdown.Option("Tamil"),
                ft.dropdown.Option("Telugu"),
                ft.dropdown.Option("Kannada"),
                ft.dropdown.Option("Spanish"),
                ft.dropdown.Option("French"),
                ft.dropdown.Option("German"),
            ],
            value="English",
            expand=True,
            label="Language",
            height=40,
            content_padding=10,
            text_size=12,
            label_style=ft.TextStyle(size=10, color=current_theme["text_secondary"]),
            text_style=ft.TextStyle(size=12, color=current_theme["text_primary"]),
            border_color=ft.Colors.with_opacity(0.2, current_theme["text_primary"]),
        )

        self.pages_input = ft.TextField(
            value="3",
            width=80,
            label="Pages",
            height=40,
            content_padding=10,
            text_size=12,
            keyboard_type=ft.KeyboardType.NUMBER,
            label_style=ft.TextStyle(size=10, color=current_theme["text_secondary"]),
            text_style=ft.TextStyle(size=12, color=current_theme["text_primary"]),
            border_radius=5,
            border_color=ft.Colors.with_opacity(0.2, current_theme["text_primary"]),
            bgcolor=ft.Colors.with_opacity(0.1, current_theme["text_primary"]),
        )

        self.config_tile = ft.ExpansionTile(
            title=ft.Text("⚙️ Study Configuration", size=14, weight="bold", color=current_theme["text_primary"]),
            subtitle=ft.Text("Customize purpose, level, language & length", size=11, color=current_theme["text_secondary"]),
            collapsed_text_color=current_theme["text_secondary"],
            text_color=current_theme["accent"],
            icon_color=current_theme["accent"],
            controls=[
                ft.Container(
                    content=ft.Column([
                        ft.Row([self.purpose_dropdown, self.level_dropdown], spacing=10),
                        ft.Row([self.lang_dropdown, self.pages_input], spacing=10),
                    ]),
                    padding=10,
                )
            ]
        )

        self.chat_area_container = ft.Container(
            content=ft.Column([
                self.config_tile,
                ft.Divider(height=1, color=ft.Colors.with_opacity(0.1, current_theme["text_primary"])),
                ft.Container(content=self.chat_list, expand=True, bgcolor=ft.Colors.with_opacity(0.05, current_theme["text_primary"]), border_radius=10, padding=10),
                self.file_helper.preview_container,
                ft.Row([
                    self.file_button, 
                    self.chat_input, 
                    self.stop_button,
                    self.send_button
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ]),
            expand=4,
            padding=10
        )
        
        self.processing_request = False

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
        
        # Update Config Dropdowns
        for ctrl in [self.purpose_dropdown, self.level_dropdown, self.lang_dropdown, self.pages_input]:
             ctrl.text_style.color = current_theme["text_primary"]
             ctrl.label_style.color = current_theme["text_secondary"]
             ctrl.border_color = ft.Colors.with_opacity(0.2, current_theme["text_primary"])
             if isinstance(ctrl, ft.Dropdown):
                 pass # Dropdown specific text color handled by theme generally, or we set usage
             else:
                 ctrl.bgcolor = ft.Colors.with_opacity(0.1, current_theme["text_primary"])
        
        self.file_button.icon_color = current_theme["text_primary"]
        self.toggle_btn.icon_color = current_theme["text_primary"]
        self.header_text.color = current_theme["accent"]
        self.history_drawer.bgcolor = current_theme["bg_secondary"]
        
        if self.page:
             self.chat_area_container.content.controls[2].bgcolor = ft.Colors.with_opacity(0.05, current_theme["text_primary"])
             # Update Tile Colors
             self.config_tile.title.color = current_theme["text_primary"]
             self.config_tile.subtitle.color = current_theme["text_secondary"]
             self.config_tile.collapsed_text_color = current_theme["text_secondary"]
             self.config_tile.text_color = current_theme["accent"]
             self.config_tile.icon_color = current_theme["accent"]
        
        # Update send button color
        self.send_button.icon_color = current_theme["accent"]

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

    # ... (did_mount to save_current_session identical) ...
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
        self.chat_list.controls.clear()
        for msg in self.chat_history:
             is_user = msg['role'] == 'user'
             self.add_chat_bubble(msg['content'], is_user=is_user, run_update=False)
             self.chat_history.pop() # Remove duplicate
        
        self.history_view.current_session_id = session_id
        self.history_view.refresh_list()
        if self.page:
            self.update()

    def save_current_session(self):
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
    # ...

    def stop_generation_click(self, e):
        """Stops the current AI generation"""
        if self.processing_request:
            self.brain.stop_generation()
            self.processing_request = False
            self.toggle_send_stop_buttons(is_generating=False)
            self.add_chat_bubble("⏹️ Generation Stopped.", is_user=False)

    def toggle_send_stop_buttons(self, is_generating):
        self.send_button.visible = not is_generating
        self.stop_button.visible = is_generating
        if self.page:
            self.chat_area_container.update()

    def handle_chat_submit(self, e):
        prompt = self.chat_input.value
        if not prompt and not self.file_helper.selected_files:
            return
        
        self.chat_input.value = ""
        if prompt:
            self.add_chat_bubble(prompt, is_user=True)
            self.chat_list.update() # Ensure user msg is seen

        # Image generation shortcut
        if prompt.strip().lower().startswith("/image") or prompt.strip().lower().startswith("image:"):
            resp = self.brain.generate_content(prompt)
            self.add_chat_bubble(resp, is_user=False)
            return

        if self.file_helper.selected_files:
            self.add_chat_bubble("📎 Processing selected files...", is_user=False)
            prompt = self.file_helper.build_prompt_with_files(prompt)
        
        self.processing_request = True
        self.toggle_send_stop_buttons(is_generating=True)
        
        if not self.current_notes:
            self.generate_new_notes(prompt)
        else:
            self.refine_notes(prompt)
            
        self.processing_request = False
        self.toggle_send_stop_buttons(is_generating=False)

    def generate_new_notes(self, topic):
        # 1. Get Config Values
        purpose = self.purpose_dropdown.value
        level = self.level_dropdown.value
        language = self.lang_dropdown.value
        try:
            pages = int(self.pages_input.value)
        except: 
            pages = 3
        
        target_words = pages * 500
        
        self.add_chat_bubble(f"🔍 Researching '{topic}' for {level} level {purpose} notes ({language})...", is_user=False)
        
        # 2. Deep Research
        research_context = ""
        try:
            self.notes_display.value = "⏳ conducted deep research on the web..."
            if self.page: self.update()
            
            if not self.processing_request: return

            research = self.brain.deep_research(topic)
            if research:
                research_context = research.get('context', '')
                self.add_chat_bubble(f"✅ Found {len(research.get('results', []))} citations...", is_user=False)
            else:
                self.add_chat_bubble("⚠️ Web search limited, utilizing internal knowledge base.", is_user=False)
        except Exception:
             self.add_chat_bubble("⚠️ Research module unavailable.", is_user=False)

        if not self.processing_request: return

        # 3. Advanced Prompt
        lang_instruction = ""
        if language == "Hindi (Pure)":
            lang_instruction = "Write completely in Hindi using Devanagari script (e.g., 'नमस्ते', not 'Namaste'). Do NOT use English script at all. Use formal/standard Hindi terms."
        elif language == "Hinglish (Mix)":
            lang_instruction = "Write in Hinglish: Use English script (Latin alphabet) for Hindi words. Easy to understand for Indian students. Example: 'Photoelectric effect mein electrons emit hote hain...' not 'प्रकाशवैद्युत प्रभाव'"
        elif language == "Simple English":
            lang_instruction = "Write in very simple, easy-to-understand English. Avoid complex jargon. Use analogies."
        elif language in ["Marathi", "Bengali", "Tamil", "Telugu", "Kannada"]:
            lang_instruction = f"Write completely in {language} using its native script. Do NOT use English script."
        elif language in ["Spanish", "French", "German"]:
            lang_instruction = f"Write completely in {language}. Use standard academic {language}."
        else:
            lang_instruction = "Write in standard academic English."

        system_prompt = f"""You are a World-Class Professor and Expert Tutor.
        
Topic: {topic}
Purpose: {purpose}
Difficulty Level: {level}
Language: {lang_instruction}
Target Length: Approx {pages} A4 Pages ({target_words} words).

Context from Internet: {research_context[:15000]}

Your Task: Create the ULTIMATE STUDY GUIDE.
1. Coverage: Cover A-Z of the topic. Start from basics, go to advanced.
2. Structure:
   - **Title & Overview**: Brief summary.
   - **Concepts (In-Depth)**: Explain every sub-topic in detail.
   - **Key Terms/Formulas**: Highlight important data.
   - **Examples/Analogies**: Use real-world examples to make it super clear ("Ek baar mein samajh aa jaye").
   - **Summary/Cheatsheet**: For quick revision.

Style Guide:
- Use clear Headings, Bullet Points, and Bold text.
- If 'Exam Prep': Focus on likely questions and marking points.
- If 'Placement': Focus on interview questions and technical depth.
- If 'Ph.D': Use academic rigor and citations.
- EXPLAIN SO WELL THAT A STUDENT UNDERSTANDS IMMEDITELY.
"""
        
        self.current_notes = ""
        # 4. UI Setup: Clear previous and add new container
        self.notes_contrainer.content.controls.clear()
        
        current_theme = theme.get_theme()
        
        # Create active markdown control
        active_markdown = ft.Markdown(
            "",
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            on_tap_link=lambda e: self.launch_url(e.data),
            code_theme="atom-one-dark"
        )
        
        # Wrap in a card-like container
        note_card = ft.Container(
            content=active_markdown,
            bgcolor=ft.Colors.with_opacity(0.05, current_theme["text_primary"]),
            padding=20,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, current_theme["text_primary"]))
        )
        
        self.notes_contrainer.content.controls.append(note_card)
        self.notes_contrainer.update()
        
        try:
            response_generator = self.brain.generate_content(topic, system_role=system_prompt, stream=True)
            
            import types
            if isinstance(response_generator, types.GeneratorType):
                for chunk in response_generator:
                    if not self.processing_request: break
                    self.current_notes += chunk
                    # Update ONLY the active markdown control with new chunk
                    # Note: We rebuild the value for this specific control
                    active_markdown.value = self.current_notes + " 🖊️"
                    active_markdown.update()
                
                active_markdown.value = self.current_notes
                active_markdown.update()
            else:
                self.current_notes = response_generator
                active_markdown.value = self.current_notes
                active_markdown.update()
                
        except Exception as e:
            self.add_chat_bubble(f"❌ Error: {e}", is_user=False)
            return

        self.save_current_session()
        self.add_chat_bubble("✅ Guide generated!", is_user=False)

    def refine_notes(self, instruction):
        self.add_chat_bubble("✍️ Adding to notes...", is_user=False)
        
        # Determine language for context
        language = self.lang_dropdown.value
        lang_instruction = ""
        if language == "Hindi (Pure)":
             lang_instruction = "Write in Hindi (Devanagari). Do NOT use English script."
        elif language == "Hinglish (Mix)":
             lang_instruction = "Write in Hinglish (English script for Hindi)."
        else:
             lang_instruction = f"Write in {language}."

        system_prompt = f"""You are an Expert Tutor. 
        User Instruction: {instruction}
        Context: The user is asking a follow-up question or requesting more details on the previous topic.
        Language: {lang_instruction}
        Task: Provide a detailed answer/addition. Do NOT rewrite the old notes. Just generate the NEW content.
        Style: Markdown with headers/bullets.
        """
        
        # Append separator
        separator = "\n\n---\n\n### ➕ Additional Notes\n\n"
        self.current_notes += separator
        
        # UI: Create NEW container for follow-up
        current_theme = theme.get_theme()
        
        follow_up_markdown = ft.Markdown(
            "",
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            on_tap_link=lambda e: self.launch_url(e.data),
            code_theme="atom-one-dark"
        )
        
        follow_up_card = ft.Container(
            content=follow_up_markdown,
            bgcolor=ft.Colors.with_opacity(0.05, current_theme["text_primary"]),
            padding=20,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, current_theme["text_primary"])),
            margin=ft.margin.only(top=10)
        )
        
        self.notes_contrainer.content.controls.append(follow_up_card)
        self.notes_contrainer.update()
        
        # Temp buffer for new content display
        new_content_buffer = "" 
        
        try:
            response_generator = self.brain.generate_content("Follow-up: " + instruction, system_role=system_prompt, stream=True)
            
            import types
            if isinstance(response_generator, types.GeneratorType):
                for chunk in response_generator:
                     if not self.processing_request: break
                     new_content_buffer += chunk
                     # Update logic memory
                     # Note: we don't add chunk to self.current_notes here yet to avoid double counting if logic changes
                     # Actually we should.
                     
                     # Update UI: Only show NEW buffer
                     follow_up_markdown.value = new_content_buffer + " 🖊️"
                     follow_up_markdown.update()
                
                # Finalize
                self.current_notes += new_content_buffer # Update history
                follow_up_markdown.value = new_content_buffer
                follow_up_markdown.update()
            else:
                 self.current_notes += response_generator
                 follow_up_markdown.value = response_generator
                 follow_up_markdown.update()
                 
        except Exception as e:
            self.add_chat_bubble(f"❌ Error: {e}", is_user=False)

        self.save_current_session()
        self.add_chat_bubble("✅ Notes expanded!", is_user=False)
