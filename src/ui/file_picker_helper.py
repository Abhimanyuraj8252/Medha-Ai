import os
import flet as ft


class FilePickerHelper:
    def __init__(self, file_handler):
        self.file_handler = file_handler
        self.selected_files = []
        self.page = None
        self.is_mobile = False
        self.file_picker = None

        self.preview_list = ft.Column(spacing=6)
        self.preview_container = ft.Container(
            content=self.preview_list,
            padding=8,
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
            border_radius=10,
            visible=False,
        )

    def attach(self, page: ft.Page, is_mobile: bool):
        self.page = page
        self.is_mobile = is_mobile
        if self.is_mobile:
            self.file_picker = ft.FilePicker()
            self.file_picker.on_result = self._on_result
            if self.file_picker not in self.page.overlay:
                self.page.overlay.append(self.file_picker)

    def open_picker(self):
        if self.is_mobile and self.file_picker:
            self.file_picker.pick_files(
                allowed_extensions=["jpg", "jpeg", "png", "gif", "pdf", "txt", "doc", "docx", "mp3", "mp4", "wav"],
                allow_multiple=True,
            )
            return

        if not self._open_desktop_dialog():
            self._show_manual_input()

    def _on_result(self, e):
        if not e.files:
            return
        self._add_selected_files(e.files)

    def _open_desktop_dialog(self):
        try:
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            file_paths = filedialog.askopenfilenames(
                title="Select files",
                filetypes=[
                    ("All supported", "*.jpg *.jpeg *.png *.gif *.pdf *.txt *.doc *.docx *.mp3 *.mp4 *.wav"),
                    ("Images", "*.jpg *.jpeg *.png *.gif"),
                    ("Documents", "*.pdf *.txt *.doc *.docx"),
                    ("Audio", "*.mp3 *.wav"),
                    ("Video", "*.mp4"),
                    ("All files", "*.*"),
                ],
            )
            root.destroy()
            if file_paths:
                files = [type("obj", (object,), {"path": p, "name": os.path.basename(p)}) for p in file_paths]
                self._add_selected_files(files)
                return True
            return False
        except Exception:
            return False

    def _show_manual_input(self):
        if not self.page:
            return

        def close_dialog(e):
            dialog.open = False
            self.page.update()

        def submit_path(e):
            raw = path_input.value or ""
            paths = [p.strip() for p in raw.replace("\n", ";").split(";") if p.strip()]
            valid_paths = [p for p in paths if os.path.exists(p)]
            if valid_paths:
                dialog.open = False
                self.page.update()
                files = [type("obj", (object,), {"path": p, "name": os.path.basename(p)}) for p in valid_paths]
                self._add_selected_files(files)
            else:
                error_text.value = "❌ File not found!"
                error_text.visible = True
                self.page.update()

        path_input = ft.TextField(
            label="File Path(s)",
            hint_text="Enter full paths separated by ; or new lines",
            width=500,
            multiline=True,
            min_lines=2,
            max_lines=4,
            on_submit=submit_path,
        )
        error_text = ft.Text("", color=ft.Colors.RED_400, visible=False)
        dialog = ft.AlertDialog(
            title=ft.Text("📎 Select Files"),
            content=ft.Column(
                [
                    ft.Text("Enter the full path(s) to your file(s):"),
                    path_input,
                    error_text,
                    ft.Text("Supported: PDF, Images, Text, Audio, Video, Documents", size=10, color=ft.Colors.WHITE_54),
                ],
                tight=True,
                spacing=10,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.TextButton("Open", on_click=submit_path),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _add_selected_files(self, files):
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
                "type": self._guess_file_type(f.name),
            })

        if new_files:
            self.selected_files.extend(new_files)
        if len(self.selected_files) > 50:
            self.selected_files = self.selected_files[:50]

        self._refresh_preview()
        if self.page:
            self.page.update()

    def _remove_selected_file(self, path):
        self.selected_files = [f for f in self.selected_files if f["path"] != path]
        self._refresh_preview()
        if self.page:
            self.page.update()

    def clear(self, e=None):
        self.selected_files = []
        self._refresh_preview()
        if self.page:
            self.page.update()

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
            "file": ft.Icons.INSERT_DRIVE_FILE,
        }.get(ftype, ft.Icons.INSERT_DRIVE_FILE)

    def _refresh_preview(self):
        self.preview_list.controls.clear()
        if not self.selected_files:
            self.preview_container.visible = False
            return

        header = ft.Row([
            ft.Text(f"Selected files ({len(self.selected_files)}/50)", size=12, color=ft.Colors.CYAN_400),
            ft.Container(expand=True),
            ft.TextButton("Clear all", on_click=self.clear),
        ])
        self.preview_list.controls.append(header)

        for f in self.selected_files:
            row = ft.Row([
                ft.Icon(self._file_type_icon(f["type"]), size=16, color=ft.Colors.CYAN_200),
                ft.Text(f["name"], size=12, overflow=ft.TextOverflow.ELLIPSIS, max_lines=1, expand=True),
                ft.IconButton(icon=ft.Icons.CLOSE, icon_size=16, on_click=lambda e, p=f["path"]: self._remove_selected_file(p)),
            ], spacing=6)
            self.preview_list.controls.append(row)

        self.preview_container.visible = True

    def build_prompt_with_files(self, user_prompt: str):
        user_prompt = (user_prompt or "").strip()
        if not user_prompt:
            user_prompt = "Summarize the selected files briefly."

        if not self.selected_files:
            return user_prompt

        file_contexts = []
        for f in self.selected_files:
            try:
                fc = self.file_handler.process_file(f["path"])
                file_contexts.append(f"[File: {f['name']}]\n{fc}")
            except Exception as ex:
                file_contexts.append(f"[File: {f['name']}]\n❌ Error: {ex}")

        return f"""[Selected File Contexts]
{chr(10).join(file_contexts)}

[User Question]: {user_prompt}

Please answer based on the selected file contents above."""
