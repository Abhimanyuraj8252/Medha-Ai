import flet as ft
import json
from ui.model_selector import ModelSelector
from core.session_manager import SessionManager
from ui.history_view import SessionHistoryView
from core.file_handler import FileHandler
from ui.file_picker_helper import FilePickerHelper
from core.themes import theme

class QuizView(ft.Column):
    def __init__(self, brain):
        super().__init__()
        self.brain = brain
        self.expand = True
        self.quiz_data = [] # List of dicts {question, options, answer, explanation}
        self.user_answers = {}
        
        self.session_manager = SessionManager()
        self.current_session_id = self.session_manager.create_new_session_id()
        self.chat_history_data = [] # Store local chat history data

        self.file_helper = FilePickerHelper(FileHandler())
        
        # Get Current Theme
        current_theme = theme.get_theme()
        
        # --- UI COMPONENTS ---
        
        # 1. Quiz Display (Left Side)
        self.quiz_list = ft.ListView(expand=True, spacing=20, padding=20)
        self.quiz_container = ft.Container(
            content=self.quiz_list,
            expand=6,
            bgcolor=ft.Colors.with_opacity(0.05, current_theme["text_primary"]),
            border_radius=10,
        )

        # 2. Chat Area (Right Side)
        self.chat_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)
        self.chat_input = ft.TextField(
            hint_text="Topic? (e.g. 'Space', 'Python Hard Mode')...",
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
            section="quiz",
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
            tooltip="Quiz History",
            icon_color=current_theme["text_primary"]
        )

        self.header_text = ft.Text("🧠 Interactive Quiz Master", size=24, weight=ft.FontWeight.BOLD, color=current_theme["accent"])

        # Quiz Controls
        self.diff_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("Easy"),
                ft.dropdown.Option("Medium"),
                ft.dropdown.Option("Hard"),
                ft.dropdown.Option("Expert"),
            ],
            value="Medium",
            expand=True,
            label="Difficulty",
            height=40,
            content_padding=10,
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
            border_radius=5,
            border_color=ft.Colors.with_opacity(0.2, current_theme["text_primary"]),
        )

        self.count_input = ft.TextField(
            value="10",
            width=80,
            label="Count",
            height=40,
            content_padding=10,
            keyboard_type=ft.KeyboardType.NUMBER,
            text_style=ft.TextStyle(size=12, color=current_theme["text_primary"]),
            label_style=ft.TextStyle(size=10, color=current_theme["text_secondary"]),
            border_radius=5,
            bgcolor=ft.Colors.with_opacity(0.1, current_theme["text_primary"]),
            border_color=ft.Colors.with_opacity(0.2, current_theme["text_primary"]),
        )

        self.config_tile = ft.ExpansionTile(
            title=ft.Text("⚙️ Quiz Configuration", size=14, weight="bold", color=current_theme["text_primary"]),
            subtitle=ft.Text("Customize difficulty, language & count", size=11, color=current_theme["text_secondary"]),
            collapsed_text_color=current_theme["text_secondary"],
            text_color=current_theme["accent"],
            icon_color=current_theme["accent"],
            controls=[
                ft.Container(
                    content=ft.Column([
                        ft.Row([self.diff_dropdown, self.lang_dropdown], spacing=10),
                        ft.Row([self.count_input], spacing=10),
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
                    # Left: Quiz (60%)
                    self.quiz_container,
                    # Right: Chat (40%)
                    self.chat_area_container
                ], expand=True),
                expand=True
            )
        ]
        
    def update_theme(self):
        """Update colors based on current theme"""
        current_theme = theme.get_theme()
        
        self.quiz_container.bgcolor = ft.Colors.with_opacity(0.05, current_theme["text_primary"])
        self.chat_input.bgcolor = ft.Colors.with_opacity(0.1, current_theme["text_primary"])
        self.chat_input.color = current_theme["text_primary"]
        self.chat_input.hint_style.color = current_theme["text_secondary"]
        
        # Update dropdowns
        for ctrl in [self.diff_dropdown, self.count_input]:
             ctrl.text_style.color = current_theme["text_primary"]
             ctrl.label_style.color = current_theme["text_secondary"]
             ctrl.border_color = ft.Colors.with_opacity(0.2, current_theme["text_primary"])
        
        self.file_button.icon_color = current_theme["text_primary"]
        self.toggle_btn.icon_color = current_theme["text_primary"]
        self.header_text.color = current_theme["accent"]
        self.history_drawer.bgcolor = current_theme["bg_secondary"]
        
        # Update Chat Area Background
        if len(self.chat_area_container.content.controls) > 1:
             self.chat_area_container.content.controls[1].bgcolor = ft.Colors.with_opacity(0.05, current_theme["text_primary"])
             # Header row text
             self.chat_area_container.content.controls[0].controls[0].color = current_theme["text_primary"]
        
        # Update send button color
        row_controls = self.chat_area_container.content.controls[3].controls
        if len(row_controls) > 2:
             row_controls[2].icon_color = current_theme["accent"]

        # Update Model Selector
        self.model_dropdown.update_theme()
        
        # Update existing chat bubbles
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
        
        # Re-render Quiz Cards to update theme
        self.render_quiz(update_theme_only=True)
        
        if self.page:
            self.update()

    def did_mount(self):
        """Called when control is added to page"""
        if self.page:
            is_mobile = self.page.platform in [ft.PagePlatform.ANDROID, ft.PagePlatform.IOS]
            self.file_helper.attach(self.page, is_mobile)
        self.add_chat_bubble("👋 Ready to test your knowledge? Give me a topic!", is_user=False, run_update=False)
        self.history_view.refresh_list()
        if self.page:
            self.update()

    def open_file_picker(self, e):
        self.file_helper.open_picker()

    def toggle_history(self, e=None):
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
        self.quiz_data = []
        self.user_answers = {}
        self.chat_history_data = []
        self.chat_list.controls.clear()
        self.quiz_list.controls.clear()
        self.history_view.current_session_id = self.current_session_id
        self.history_view.refresh_list()
        self.add_chat_bubble("👋 Ready to test your knowledge? Give me a topic!", is_user=False)
        if self.page:
            self.update()

    def load_session(self, session_id):
        data = self.session_manager.get_session_content("quiz", session_id)
        if not data: return
        
        self.current_session_id = session_id
        self.quiz_data = data.get('quiz_data', [])
        self.user_answers = data.get('user_answers', {})
        self.chat_history_data = data.get('messages', [])
        
        # Rebuild Chat UI
        self.chat_list.controls.clear()
        for msg in self.chat_history_data:
             is_user = msg['role'] == 'user'
             self.add_chat_bubble(msg['content'], is_user=is_user, run_update=False, record_history=False)

        # Rebuild Quiz UI (Assuming render_quiz exists below)
        if hasattr(self, 'render_quiz'):
            self.render_quiz()
        
        self.history_view.current_session_id = session_id
        self.history_view.refresh_list()
        if self.page:
            self.update()

    def save_current_session(self):
        title = "New Quiz"
        for msg in self.chat_history_data:
            if msg['role'] == 'user':
                title = msg['content'][:30]
                break
        
        self.session_manager.save_session(
            "quiz",
            self.current_session_id,
            title,
            self.chat_history_data,
            extra_data={"quiz_data": self.quiz_data, "user_answers": self.user_answers}
        )

    def add_chat_bubble(self, text, is_user=False, run_update=True, record_history=True):
        current_theme = theme.get_theme()
        
        bubble = ft.Container(
            content=ft.Column([
                ft.Text("You" if is_user else "QuizMaster", size=10, color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE) if is_user else current_theme["text_secondary"]),
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
        # Add to history
        if record_history:
             self.chat_history_data.append({"role": "user" if is_user else "assistant", "content": text})
             self.save_current_session()
        
        if run_update and self.page:
            self.update()

    def handle_chat_submit(self, e):
        prompt = self.chat_input.value
        if not prompt and not self.file_helper.selected_files:
            return
        
        self.chat_input.value = ""
        if prompt:
            self.add_chat_bubble(prompt, is_user=True)

        # Image generation shortcut
        if prompt.strip().lower().startswith("/image") or prompt.strip().lower().startswith("image:"):
            resp = self.brain.generate_content(prompt)
            self.add_chat_bubble(resp, is_user=False)
            return

        if self.file_helper.selected_files:
            self.add_chat_bubble("📎 Processing selected files...", is_user=False)
            prompt = self.file_helper.build_prompt_with_files(prompt)
        
        if not self.quiz_data:
            self.generate_new_quiz(prompt)
        else:
            self.refine_quiz(prompt)

    def generate_new_quiz(self, topic):
        try:
            count = int(self.count_input.value)
            if count < 1: count = 5
            # No limit check here as requested by user
        except ValueError:
            count = 5 # Default
            
        difficulty = self.diff_dropdown.value
        language = self.lang_dropdown.value
        
        self.add_chat_bubble(f"🎲 Generating {count} {difficulty} questions on '{topic}' in {language}...", is_user=False)
        
        # 1. Research for accuracy
        research_context = ""
        try:
             # Force research for better quality
            res = self.brain.deep_research(topic) 
            if res:
                research_context = res.get('context', '')
        except:
            pass

        if language == "Hindi (Pure)":
            lang_instruction = "Write completely in Hindi using Devanagari script (e.g., 'नमस्ते'). Do NOT use English script."
        elif language == "Hinglish (Mix)":
            lang_instruction = "Write in Hinglish: Use English script (Latin) for Hindi words (e.g., 'Kya haal hai?')."
        elif language == "Simple English":
            lang_instruction = "Write in simple English."
        elif language in ["Marathi", "Bengali", "Tamil", "Telugu", "Kannada"]:
            lang_instruction = f"Write completely in {language} using its native script."
        else:
            lang_instruction = f"Write in standard {language}."

        # 2. Generate Content with Streaming
        system_prompt = f"""You are a Quiz Generator.
Topic: {topic}
Difficulty: {difficulty}
Language: {language}
Context: {research_context[:3000] if research_context else "None"}

Task: Stream {count} multiple choice questions one by one.
Format: JSON Object per line. Separate each object with '@@@'.
Example:
@@@ {{"id": 1, "question": "...", "options": ["..."], "correct_index": 0, "explanation": "..."}} @@@
@@@ {{"id": 2, ...}} @@@

Rules:
- "id": integer
- "options": list of 4 strings (No A/B prefixes)
- "correct_index": 0-3
- "explanation": concise string
- NO Markdown code blocks. Just raw text/json with @@@ separators.
- LANGUAGE INSTRUCTION: {lang_instruction}
"""
        
        self.toggle_history() # Close history to show quiz
        
        self.quiz_data = [] 
        self.quiz_list.controls.clear()
        self.quiz_list.update()
        
        # Streaming Loop
        buffer = ""
        try:
            response_gen = self.brain.generate_content(topic, system_role=system_prompt, stream=True)
            
            # Check if response is string (error)
            if isinstance(response_gen, str):
                self.add_chat_bubble(f"❌ Error: {response_gen}", is_user=False)
                return

            question_count = 0
            
            for chunk in response_gen:
                buffer += chunk
                
                if "@@@" in buffer:
                    parts = buffer.split("@@@")
                    buffer = parts.pop()
                    
                    for part in parts:
                        part = part.strip()
                        if not part: continue
                        
                        try:
                            # Clean potential markdown
                            if part.startswith("json"): part = part[4:] 
                            if part.startswith("```"): part = part.replace("```", "")
                            
                            q_data = json.loads(part)
                            
                            self.quiz_data.append(q_data)
                            self.add_quiz_card(q_data)
                            question_count += 1
                            self.quiz_list.update()
                            try:
                                self.quiz_list.scroll_to(offset=-1, duration=500)
                            except: pass
                            
                        except json.JSONDecodeError:
                            pass
                            
            if buffer.strip():
                try:
                    clean = buffer.strip().replace("@@@", "").replace("```json", "").replace("```", "")
                    if clean:
                        q_data = json.loads(clean)
                        self.quiz_data.append(q_data)
                        self.add_quiz_card(q_data)
                        self.quiz_list.update()
                except: pass
                
        except Exception as e:
            self.add_chat_bubble(f"⚠️ Error during streaming: {str(e)}", is_user=False)

        if len(self.quiz_data) == 0:
             self.add_chat_bubble("⚠️ No questions were generated. Try a simpler topic.", is_user=False)
        else:
             self.add_chat_bubble(f"✅ Generated {len(self.quiz_data)} questions!", is_user=False)

    def refine_quiz(self, instruction):
        self.add_chat_bubble("✍️ Adding more questions...", is_user=False)
        
        # Get current config
        difficulty = self.diff_dropdown.value
        language = self.lang_dropdown.value
        
        # Determine strict language prompt
        if language == "Hindi (Pure)":
            lang_instruction = "Write completely in Hindi using Devanagari script. Do NOT use English script."
        elif language == "Hinglish (Mix)":
             lang_instruction = "Write in Hinglish (English script for Hindi)."
        else:
             lang_instruction = f"Write in {language}."

        # Start ID for new questions
        start_id = len(self.quiz_data) + 1
        count = 5 # Default for refinement

        system_prompt = f"""You are a Quiz Generator.
        User Request: {instruction}
        Difficulty: {difficulty}
        Language: {language}
        
        Task: Generate {count} NEW additional multiple choice questions.
        Format: JSON Object per line. Separate with '@@@'.
        
        Rules:
        - Start IDs from {start_id}.
        - "options": list of 4 strings.
        - "correct_index": 0-3.
        - NO Markdown.
        - LANGUAGE INSTRUCTION: {lang_instruction}
        """
        
        # Streaming Logic (Reuse/Duplicate for simplicity or refactor later)
        buffer = ""
        questions_added = 0
        try:
            response_gen = self.brain.generate_content("Add questions", system_role=system_prompt, stream=True)
            
            # Check if response is string (error)
            if isinstance(response_gen, str):
                self.add_chat_bubble(f"❌ Error: {response_gen}", is_user=False)
                return

            for chunk in response_gen:
                buffer += chunk
                if "@@@" in buffer:
                    parts = buffer.split("@@@")
                    buffer = parts.pop()
                    for part in parts:
                        part = part.strip()
                        if not part: continue
                        try:
                            if part.startswith("json"): part = part[4:] 
                            if part.startswith("```"): part = part.replace("```", "")
                            q_data = json.loads(part)
                            
                            # Append to existing data
                            self.quiz_data.append(q_data)
                            self.add_quiz_card(q_data)
                            questions_added += 1
                            self.quiz_list.update()
                            try:
                                self.quiz_list.scroll_to(offset=-1, duration=500)
                            except: pass
                        except json.JSONDecodeError: pass
            
            # Handle remainder
            if buffer.strip():
                 try:
                    clean = buffer.strip().replace("@@@", "").replace("```json", "").replace("```", "")
                    if clean:
                        q_data = json.loads(clean)
                        self.quiz_data.append(q_data)
                        self.add_quiz_card(q_data)
                        questions_added += 1
                        self.quiz_list.update()
                 except: pass

            self.add_chat_bubble(f"✅ Added {questions_added} new questions!", is_user=False)
            
        except Exception as e:
            self.add_chat_bubble(f"❌ Error adding questions: {e}", is_user=False)

    def process_quiz_json(self, response):
        pass # Deprecated/Unused now that we use streaming in refine_quiz

    def render_quiz(self, update_theme_only=False):
        self.quiz_list.controls.clear()
        # Note: We must NOT clear user_answers if we are just updating theme
        if not update_theme_only:
             self.user_answers = {}
        
        for q in self.quiz_data:
            self.quiz_list.controls.append(self.build_question_card(q))
        
        if self.quiz_data:
            current_theme = theme.get_theme()
            self.quiz_list.controls.append(
                ft.Row([
                    ft.ElevatedButton("Submit & Check Results", icon=ft.Icons.CHECK_CIRCLE, on_click=self.check_results, bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE)
                ], alignment=ft.MainAxisAlignment.CENTER)
            )
        if self.page:
            self.update()

    def build_question_card(self, q):
        q_id = q.get('id', 0)
        current_theme = theme.get_theme()
        
        # Helper to handle radio change
        def on_change(e):
            self.user_answers[str(q_id)] = e.control.value # Value is index string "0", "1" etc

        # Create options with index as value
        radios = []
        for i, opt in enumerate(q['options']):
            radios.append(ft.Radio(
                value=str(i), 
                label=opt,
                fill_color=current_theme["accent"]
            ))

        rg = ft.RadioGroup(
            content=ft.Column(radios),
            value=self.user_answers.get(str(q_id)), # Restore selection if exists
            on_change=on_change
        )
        
        card = ft.Container(
            content=ft.Column([
                ft.Text(f"Q{q_id}. {q['question']}", size=16, weight=ft.FontWeight.BOLD, color=current_theme["text_primary"]),
                rg
            ]),
            bgcolor=ft.Colors.with_opacity(0.1, current_theme["text_primary"]),
            padding=15,
            border_radius=10
        )
        return card

    def check_results(self, e):
        score = 0
        total = len(self.quiz_data)
        current_theme = theme.get_theme()
        
        self.quiz_list.controls.clear()
        
        for q in self.quiz_data:
            q_id = q.get('id', 0)
            user_val = self.user_answers.get(str(q_id), None)
            user_ans_idx = int(user_val) if user_val is not None else -1
            correct_idx = q['correct_index']
            
            is_correct = user_ans_idx == correct_idx
            if is_correct: score += 1
            
            # Rebuild card with feedback
            options_col = ft.Column()
            for i, opt in enumerate(q['options']):
                color = current_theme["text_primary"]
                icon = None
                weight = ft.FontWeight.NORMAL
                
                if i == correct_idx:
                    color = ft.Colors.GREEN_400
                    icon = ft.Icons.CHECK
                    weight = ft.FontWeight.BOLD
                elif i == user_ans_idx and not is_correct:
                    color = ft.Colors.RED_400
                    icon = ft.Icons.CLOSE
                
                options_col.controls.append(
                    ft.Row([
                        ft.Icon(icon, color=color, size=16) if icon else ft.Container(width=16),
                        ft.Text(opt, color=color, weight=weight)
                    ])
                )
            
            card = ft.Container(
                content=ft.Column([
                    ft.Text(f"Q{q_id}. {q['question']}", size=16, weight="bold", color=current_theme["text_primary"]),
                    options_col,
                    ft.Container(
                        content=ft.Text(f"💡 {q.get('explanation', '')}", size=12, italic=True, color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.BLUE_900 if not is_correct else ft.Colors.TRANSPARENT,
                        padding=5,
                        border_radius=5
                    )
                ]),
                bgcolor=ft.Colors.with_opacity(0.1, current_theme["text_primary"]),
                padding=15,
                border_radius=10,
                border=ft.border.all(1, ft.Colors.GREEN_400 if is_correct else ft.Colors.RED_400)
            )
            self.quiz_list.controls.append(card)
            
        self.add_chat_bubble(f"🏆 You scored {score}/{total}!", is_user=False)
        
        # Add a "Next Quiz" button?
        self.quiz_list.controls.append(
            ft.Row([
               ft.ElevatedButton("New Quiz", icon=ft.Icons.REFRESH, on_click=lambda e: self.render_empty(), bgcolor=current_theme["accent"], color=ft.Colors.WHITE) 
            ], alignment=ft.MainAxisAlignment.CENTER)
        )
        self.update()

    def render_empty(self):
        self.quiz_data = []
        self.quiz_list.controls.clear()
        self.add_chat_bubble("Give me a new topic!", is_user=False)
        self.update()
