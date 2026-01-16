import flet as ft
from core.session_manager import SessionManager

class SessionHistoryView(ft.Container):
    def __init__(self, section, current_session_id, on_session_select, on_new_chat):
        super().__init__()
        self.section = section
        self.manager = SessionManager()
        self.on_session_select = on_session_select
        self.on_new_chat = on_new_chat
        self.current_session_id = current_session_id
        
        self.width = 250
        self.bgcolor = ft.Colors.with_opacity(0.05, ft.Colors.WHITE)
        self.border_radius = 10
        self.padding = 10
        
        # UI Lists
        self.session_list = ft.ListView(expand=True, spacing=5)
        # Don't call refresh_list() here - it will be called after control is added to page
        
        self.content = ft.Column([
            ft.Text("🕒 History", size=14, weight="bold", color=ft.Colors.WHITE54),
            ft.OutlinedButton(
                "New Chat", 
                icon=ft.Icons.ADD, 
                on_click=self._handle_new_chat,
                style=ft.ButtonStyle(
                    color=ft.Colors.CYAN_200,
                    side={"": ft.BorderSide(1, ft.Colors.CYAN_200)}
                )
            ),
            ft.Divider(color=ft.Colors.WHITE10),
            self.session_list
        ])

    def refresh_list(self):
        sessions = self.manager.load_sessions(self.section)
        self.session_list.controls.clear()
        
        if not sessions:
            self.session_list.controls.append(
                ft.Text("No history yet.", size=12, italic=True, color=ft.Colors.WHITE24)
            )
        
        for sess in sessions:
            is_active = sess['id'] == self.current_session_id
            bg_color = ft.Colors.WHITE10 if is_active else ft.Colors.TRANSPARENT
            
            self.session_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CHAT_BUBBLE_OUTLINE, size=14, color=ft.Colors.WHITE54),
                        ft.Text(sess['title'], size=12, no_wrap=True, expand=True, color=ft.Colors.WHITE if is_active else ft.Colors.WHITE70),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE, 
                            icon_size=14, 
                            icon_color=ft.Colors.RED_300,
                            data=sess['id'],
                            on_click=self._delete_session,
                            tooltip="Delete"
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=8,
                    border_radius=5,
                    bgcolor=bg_color,
                    on_click=lambda e, sid=sess['id']: self.on_session_select(sid),
                    ink=True
                )
            )
        if self.page:
            try:
                self.update()
            except Exception:
                pass # Suppress update errors if control isn't ready

    def _handle_new_chat(self, e):
        self.on_new_chat()

    def _delete_session(self, e):
        sid = e.control.data
        self.manager.delete_session(self.section, sid)
        # If deleted active, new chat
        if sid == self.current_session_id:
            self.on_new_chat()
        else:
            self.refresh_list()
