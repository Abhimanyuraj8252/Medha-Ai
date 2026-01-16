import json
import os
import uuid
from datetime import datetime
import shutil

class SessionManager:
    def __init__(self, app_name="MedhaAI"):
        # Base data path
        self.base_path = os.path.join(os.getcwd(), "user_data", "sessions")
        os.makedirs(self.base_path, exist_ok=True)
        
    def _get_session_file(self, section):
        """Get the path for the specific section's session file (chat, study, etc)"""
        return os.path.join(self.base_path, f"{section}_sessions.json")

    def load_sessions(self, section):
        """Load list of session headers for a section"""
        file_path = self._get_session_file(section)
        if not os.path.exists(file_path):
            return []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Sort by timestamp desc
                return sorted(data, key=lambda x: x.get('timestamp', ''), reverse=True)
        except Exception as e:
            print(f"Error loading sessions for {section}: {e}")
            return []

    def save_session(self, section, session_id, title, messages, extra_data=None):
        """Save a new or update existing session"""
        file_path = self._get_session_file(section)
        sessions = self.load_sessions(section)
        
        # Check if session exists
        existing_index = next((index for (index, d) in enumerate(sessions) if d["id"] == session_id), None)
        
        timestamp = datetime.now().isoformat()
        
        entry = {
            "id": session_id,
            "title": title if title else "New Chat",
            "timestamp": timestamp,
            "preview": messages[-1]['content'][:50] + "..." if messages else "Empty",
            "messages": messages
        }
        
        if extra_data:
            entry.update(extra_data)
        
        if existing_index is not None:
             # Preserve existing fields if not overwritten, though we rebuild entry mostly.
             # Actually, simpler to just overwrite.
            sessions[existing_index] = entry
        else:
            sessions.append(entry)
            
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(sessions, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False

    def delete_session(self, section, session_id):
        sessions = self.load_sessions(section)
        sessions = [s for s in sessions if s['id'] != session_id]
        
        file_path = self._get_session_file(section)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(sessions, f, indent=4)
            return True
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False
            
    def get_session_content(self, section, session_id):
        sessions = self.load_sessions(section)
        session = next((s for s in sessions if s['id'] == session_id), None)
        return session if session else None

    def create_new_session_id(self):
        return str(uuid.uuid4())
