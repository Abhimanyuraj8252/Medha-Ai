import flet as ft
import json
from ui.model_selector import ModelSelector
from core.session_manager import SessionManager
from ui.history_view import SessionHistoryView
from core.file_handler import FileHandler
from ui.file_picker_helper import FilePickerHelper

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
        
        # --- UI COMPONENTS ---
        
        # 1. Quiz Display (Left Side)
        self.quiz_list = ft.ListView(expand=True, spacing=20, padding=20)
        self.quiz_container = ft.Container(
            content=self.quiz_list,
            expand=6,
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
            border_radius=10,
        )

        # 2. Chat Area (Right Side)
        self.chat_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)
        self.chat_input = ft.TextField(
            hint_text="Topic? (e.g. 'Space', 'Python Hard Mode')...",
            expand=True,
            border_radius=20,
            on_submit=self.handle_chat_submit
        )
        self.file_button = ft.IconButton(ft.Icons.ATTACH_FILE, tooltip="Attach File(s)", on_click=self.open_file_picker)

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
            bgcolor=ft.Colors.BLACK_54
        )
        
        toggle_btn = ft.IconButton(ft.Icons.HISTORY, on_click=self.toggle_history, tooltip="Quiz History")

        self.controls = [
            ft.Row([
                ft.Text("🧠 Interactive Quiz Master", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_400),
                ft.Container(expand=True),
                toggle_btn,
                self.model_dropdown
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(color=ft.Colors.WHITE_24),
            ft.Container(
                content=ft.Row([
                    self.history_drawer,
                    # Left: Quiz (60%)
                    self.quiz_container,
                    # Right: Chat (40%)
                    ft.Container(
                        content=ft.Column([
                            ft.Text("💬 Quiz Config", size=16, weight="bold"),
                            ft.Container(content=self.chat_list, expand=True, bgcolor=ft.Colors.BLACK_12, border_radius=10, padding=10),
                            self.file_helper.preview_container,
                            ft.Row([self.file_button, self.chat_input, ft.IconButton(ft.Icons.SEND, on_click=self.handle_chat_submit)])
                        ]),
                        expand=4,
                        padding=10
                    )
                ], expand=True),
                expand=True
            )
        ]
    
    def did_mount(self):
        """Called when control is added to page"""
        if self.page:
            is_mobile = self.page.platform in [ft.PagePlatform.ANDROID, ft.PagePlatform.IOS]
            self.file_helper.attach(self.page, is_mobile)
        self.add_chat_bubble("👋 Ready to test your knowledge? Give me a topic!", is_user=False, run_update=False)
        self.history_view.refresh_list()
        self.update()

    def open_file_picker(self, e):
        self.file_helper.open_picker()

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
             bubble = ft.Container(
                content=ft.Column([
                    ft.Text("You" if is_user else "Quiz Master", size=10, color=ft.Colors.WHITE_54),
                    ft.Markdown(msg['content'])
                ]),
                bgcolor=ft.Colors.PURPLE_900 if is_user else ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                padding=10,
                border_radius=10,
                width=None if is_user else 300
            )
             self.chat_list.controls.append(
                ft.Row([bubble], alignment=ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START)
            )

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

    def add_chat_bubble(self, text, is_user=False, run_update=True):
        bubble = ft.Container(
            content=ft.Column([
                ft.Text("You" if is_user else "QuizMaster", size=10, color=ft.Colors.WHITE_54),
                ft.Markdown(text)
            ]),
            bgcolor=ft.Colors.PURPLE_900 if is_user else ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
            padding=10,
            border_radius=10,
            width=None if is_user else 300
        )
        self.chat_list.controls.append(
            ft.Row([bubble], alignment=ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START)
        )
        # Add to history
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
        # Update called in add_chat_bubble

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
        self.add_chat_bubble(f"🎲 Researching & Generating quiz on '{topic}'...", is_user=False)
        
        # 1. Research for accuracy (User requested real-time everything)
        research_context = ""
        try:
            # We use a broad search to ensure we have facts even for historical topics
            res = self.brain.deep_research(topic) 
            if res:
                research_context = res.get('context', '')
        except:
            pass # Fallback to internal knowledge

        # 2. Generate Content
        # We use strict JSON prompting.
        system_prompt = f"""You are a Quiz Generator.
        Topic: {topic}
        Context from Internet: {research_context[:2000] if research_context else "None"}
        
        Task: Generate 5 multiple choice questions based on the topic/context.
        Format: JSON Array.
        [
          {{
            "id": 1,
            "question": "...",
            "options": ["...", "...", "...", "..."],
            "correct_index": 0,
            "explanation": "..."
          }}
        ]
        
        Format Rules:
        - "id" is integer 1 to 5.
        - "options" is a list of 4 strings. DO NOT prefix with A), B) etc, just the text.
        - "correct_index" is 0-3.
        - "explanation" explains why the answer is right.
        - JSON ONLY. No markdown blocks.
        """
        
        response = self.brain.generate_content(topic, system_role=system_prompt)
        self.process_quiz_json(response)

    def refine_quiz(self, instruction):
        self.add_chat_bubble("🔄 Updating quiz...", is_user=False)
        current_state = json.dumps(self.quiz_data)
        
        system_prompt = f"""You are a Quiz Generator.
        Current Quiz: {current_state}
        User Request: {instruction}
        
        Task: Return a NEW JSON Array with the modified questions.
        Maintain the exact same JSON structure as before.
        """
        response = self.brain.generate_content("Update the quiz", system_role=system_prompt)
        self.process_quiz_json(response)

    def process_quiz_json(self, response):
        try:
            clean_json = response.replace("```json", "").replace("```", "").strip()
            # Handle potential outer text
            start = clean_json.find('[')
            end = clean_json.rfind(']') + 1
            if start != -1 and end != -1:
                clean_json = clean_json[start:end]
                
            self.quiz_data = json.loads(clean_json)
            self.render_quiz()
            self.add_chat_bubble("✅ Quiz Ready! Good luck!", is_user=False)
        except Exception as e:
            self.add_chat_bubble(f"❌ Error generating quiz: {e}\nRaw: {response[:100]}...", is_user=False)

    def render_quiz(self):
        self.quiz_list.controls.clear()
        self.user_answers = {}
        
        for q in self.quiz_data:
            self.quiz_list.controls.append(self.build_question_card(q))
        
        if self.quiz_data:
            self.quiz_list.controls.append(
                ft.Row([
                    ft.ElevatedButton("Submit & Check Results", icon=ft.Icons.CHECK_CIRCLE, on_click=self.check_results, bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE)
                ], alignment=ft.MainAxisAlignment.CENTER)
            )
        self.update()

    def build_question_card(self, q):
        q_id = q.get('id', 0)
        
        # Helper to handle radio change
        def on_change(e):
            self.user_answers[str(q_id)] = e.control.value # Value is index string "0", "1" etc

        # Create options with index as value
        radios = []
        for i, opt in enumerate(q['options']):
            radios.append(ft.Radio(value=str(i), label=opt))

        rg = ft.RadioGroup(
            content=ft.Column(radios),
            on_change=on_change
        )
        
        card = ft.Container(
            content=ft.Column([
                ft.Text(f"Q{q_id}. {q['question']}", size=16, weight="bold"),
                rg
            ]),
            bgcolor=ft.Colors.BLACK26,
            padding=15,
            border_radius=10
        )
        return card

    def check_results(self, e):
        score = 0
        total = len(self.quiz_data)
        
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
                color = ft.Colors.WHITE
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
                    ft.Text(f"Q{q_id}. {q['question']}", size=16, weight="bold"),
                    options_col,
                    ft.Container(
                        content=ft.Text(f"💡 {q.get('explanation', '')}", size=12, italic=True),
                        bgcolor=ft.Colors.BLUE_900 if not is_correct else ft.Colors.TRANSPARENT,
                        padding=5,
                        border_radius=5
                    )
                ]),
                bgcolor=ft.Colors.BLACK45,
                padding=15,
                border_radius=10,
                border=ft.border.all(1, ft.Colors.GREEN_400 if is_correct else ft.Colors.RED_400)
            )
            self.quiz_list.controls.append(card)
            
        self.add_chat_bubble(f"🏆 You scored {score}/{total}!", is_user=False)
        
        # Add a "Next Quiz" button?
        self.quiz_list.controls.append(
            ft.Row([
               ft.ElevatedButton("New Quiz", icon=ft.Icons.REFRESH, on_click=lambda e: self.render_empty(), bgcolor=ft.Colors.PURPLE_600) 
            ], alignment=ft.MainAxisAlignment.CENTER)
        )
        self.update()

    def render_empty(self):
        self.quiz_data = []
        self.quiz_list.controls.clear()
        self.add_chat_bubble("Give me a new topic!", is_user=False)
        self.update()
