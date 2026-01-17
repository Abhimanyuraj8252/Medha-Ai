"""
Chat Exporter for Medha AI
Export chat history to TXT and PDF formats
"""
import os
from datetime import datetime
from pathlib import Path

class ChatExporter:
    """Export chat history to various formats"""
    
    def __init__(self):
        self.export_dir = Path.home() / "Documents" / "Medha AI Exports"
        self._ensure_export_dir()
    
    def _ensure_export_dir(self):
        """Create export directory if not exists"""
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def export_to_txt(self, messages: list, title: str = "Chat") -> str:
        """Export chat to TXT file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Medha_Chat_{timestamp}.txt"
        filepath = self.export_dir / filename
        
        content = f"{'='*50}\n"
        content += f"  MEDHA AI - Chat Export\n"
        content += f"  {title}\n"
        content += f"  Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += f"{'='*50}\n\n"
        
        for msg in messages:
            role = "🧑 You" if msg.get('role') == 'user' else "🤖 Medha"
            if msg.get('role') == 'system':
                continue
            content += f"{role}:\n{msg.get('content', '')}\n\n{'-'*40}\n\n"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(filepath)
    
    def export_to_html(self, messages: list, title: str = "Chat") -> str:
        """Export chat to HTML file (prettier than PDF without extra deps)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Medha_Chat_{timestamp}.html"
        filepath = self.export_dir / filename
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Medha AI - {title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #1a1a2e; color: #eee; }}
        .header {{ text-align: center; padding: 20px; background: linear-gradient(135deg, #00d4ff, #7b2cbf); border-radius: 10px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0; color: white; }}
        .message {{ margin: 15px 0; padding: 15px; border-radius: 10px; }}
        .user {{ background: #16213e; border-left: 4px solid #00d4ff; }}
        .assistant {{ background: #1f1f3d; border-left: 4px solid #7b2cbf; }}
        .role {{ font-weight: bold; margin-bottom: 10px; }}
        .user .role {{ color: #00d4ff; }}
        .assistant .role {{ color: #7b2cbf; }}
        .content {{ line-height: 1.6; white-space: pre-wrap; }}
        .footer {{ text-align: center; margin-top: 30px; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 Medha AI Chat</h1>
        <p>{title} | Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
"""
        
        for msg in messages:
            if msg.get('role') == 'system':
                continue
            role_class = msg.get('role', 'assistant')
            role_name = "🧑 You" if role_class == 'user' else "🤖 Medha"
            content = msg.get('content', '').replace('<', '&lt;').replace('>', '&gt;')
            html += f"""
    <div class="message {role_class}">
        <div class="role">{role_name}</div>
        <div class="content">{content}</div>
    </div>
"""
        
        html += """
    <div class="footer">
        <p>Exported from Medha AI | Made with ❤️</p>
    </div>
</body>
</html>"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return str(filepath)
    
    def get_export_dir(self) -> str:
        """Get export directory path"""
        return str(self.export_dir)

# Global instance
chat_exporter = ChatExporter()
