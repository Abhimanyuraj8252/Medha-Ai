"""
System Controller - Full system automation for Medha AI
Controls apps, plays music, makes calls, sends messages, etc.
Works on both Windows and Android
"""

import subprocess
import os
import platform
import webbrowser
import re
from pathlib import Path

class SystemController:
    def __init__(self):
        self.system = platform.system()
        self.is_mobile = hasattr(__builtins__, 'android') or 'ANDROID_ROOT' in os.environ
        
        # Common app paths (Windows)
        self.windows_apps = {
            'chrome': r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            'edge': r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'paint': 'mspaint.exe',
            'explorer': 'explorer.exe',
            'whatsapp': r'C:\Users\{}\AppData\Local\WhatsApp\WhatsApp.exe',
            'spotify': r'C:\Users\{}\AppData\Roaming\Spotify\Spotify.exe',
            'vlc': r'C:\Program Files\VideoLAN\VLC\vlc.exe',
        }
        
        # Android package names
        self.android_packages = {
            'whatsapp': 'com.whatsapp',
            'chrome': 'com.android.chrome',
            'youtube': 'com.google.android.youtube',
            'spotify': 'com.spotify.music',
            'gmail': 'com.google.android.gm',
            'keep': 'com.google.android.keep',
            'maps': 'com.google.android.apps.maps',
            'photos': 'com.google.android.apps.photos',
            'camera': 'com.android.camera',
            'gallery': 'com.google.android.apps.photos',
            'settings': 'com.android.settings',
            'calculator': 'com.google.android.calculator',
            'calendar': 'com.google.android.calendar',
        }
    
    def execute_command(self, user_text):
        """Main entry point - analyze command and execute"""
        text = user_text.lower()
        
        # App opening commands
        if any(word in text for word in ['open', 'kholo', 'start', 'launch']):
            return self.open_app(text)
        
        # Music/Media commands
        if any(word in text for word in ['play', 'song', 'music', 'bajao', 'gaana']):
            return self.play_music(text)
        
        # Call commands
        if any(word in text for word in ['call', 'phone', 'dial', 'call karo']):
            return self.make_call(text)
        
        # Message commands
        if any(word in text for word in ['message', 'sms', 'text', 'bhejo', 'send']):
            return self.send_message(text)
        
        # WhatsApp commands
        if 'whatsapp' in text:
            return self.open_whatsapp(text)
        
        # Search commands
        if any(word in text for word in ['search', 'google', 'dhundo', 'find']):
            return self.search_web(text)
        
        # Note taking
        if any(word in text for word in ['note', 'write', 'plan', 'reminder', 'likho']):
            return self.create_note(text)
        
        # System control
        if any(word in text for word in ['volume', 'brightness', 'wifi', 'bluetooth']):
            return self.system_control(text)
        
        return None  # Command not recognized
    
    def open_app(self, text):
        """Open applications"""
        # Detect app name
        app_name = None
        
        # Common app keywords
        app_keywords = {
            'chrome': ['chrome', 'browser'],
            'whatsapp': ['whatsapp', 'whatsup'],
            'youtube': ['youtube', 'video'],
            'spotify': ['spotify', 'music'],
            'notepad': ['notepad', 'editor'],
            'calculator': ['calculator', 'calc'],
            'keep': ['keep', 'notes', 'note'],
            'gmail': ['gmail', 'email', 'mail'],
            'camera': ['camera', 'photo'],
            'settings': ['settings', 'setting'],
            'maps': ['maps', 'map', 'navigation'],
        }
        
        for app, keywords in app_keywords.items():
            if any(keyword in text for keyword in keywords):
                app_name = app
                break
        
        if not app_name:
            return "❌ App not recognized. Please specify the app name."
        
        try:
            if self.is_mobile:
                # Android: Use intents
                return self.open_android_app(app_name)
            else:
                # Windows: Use subprocess
                return self.open_windows_app(app_name)
        except Exception as e:
            return f"❌ Failed to open {app_name}: {str(e)}"
    
    def open_windows_app(self, app_name):
        """Open app on Windows"""
        if app_name in self.windows_apps:
            app_path = self.windows_apps[app_name]
            # Replace username placeholder
            if '{}' in app_path:
                app_path = app_path.format(os.getenv('USERNAME'))
            
            if os.path.exists(app_path):
                subprocess.Popen([app_path])
                return f"✅ Opening {app_name.title()}..."
            else:
                # Try system command
                try:
                    subprocess.Popen([app_name])
                    return f"✅ Opening {app_name.title()}..."
                except:
                    return f"❌ {app_name.title()} not found on your system."
        
        # Try as system command
        try:
            subprocess.Popen([app_name])
            return f"✅ Opening {app_name.title()}..."
        except:
            return f"❌ Unable to find {app_name.title()}."
    
    def open_android_app(self, app_name):
        """Open app on Android using intents"""
        if app_name in self.android_packages:
            package = self.android_packages[app_name]
            try:
                # Try using android module if available
                import android
                android.app_start_intent(package)
                return f"✅ Opening {app_name.title()}..."
            except:
                # Fallback: Use adb-like intent
                return f"📱 Please open {app_name.title()} manually (Android intent: {package})"
        
        return f"❌ {app_name.title()} not found."
    
    def play_music(self, text):
        """Play music"""
        # Extract song name if provided
        song_patterns = [
            r'play\s+(.+?)(?:\s+song|\s+music|$)',
            r'bajao\s+(.+?)(?:\s+gaana|$)',
            r'song\s+(.+)',
        ]
        
        song_name = None
        for pattern in song_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                song_name = match.group(1).strip()
                break
        
        if self.is_mobile:
            # Android: Open Spotify or YouTube Music
            if song_name:
                return f"🎵 Opening music app to play: {song_name}"
            else:
                return self.open_android_app('spotify')
        else:
            # Windows: Open Spotify or YouTube
            if song_name:
                # Search on YouTube
                webbrowser.open(f"https://www.youtube.com/results?search_query={song_name.replace(' ', '+')}")
                return f"🎵 Searching for: {song_name} on YouTube"
            else:
                return self.open_windows_app('spotify')
    
    def make_call(self, text):
        """Make phone call"""
        # Extract phone number or contact name
        number_match = re.search(r'\d{10}', text)
        
        if self.is_mobile:
            if number_match:
                number = number_match.group()
                return f"📞 Dialing {number}... (Android dialer intent)"
            else:
                return "📞 Opening phone app..."
        else:
            return "📞 Phone calls require mobile device or apps like WhatsApp/Skype."
    
    def send_message(self, text):
        """Send message"""
        # Extract message content
        msg_match = re.search(r'(?:message|sms|text|bhejo)\s+(.+?)(?:\s+to|\s+ko|$)', text, re.IGNORECASE)
        
        if 'whatsapp' in text:
            return self.open_whatsapp(text)
        
        if self.is_mobile:
            return "💬 Opening messaging app..."
        else:
            return "💬 Messages require mobile device. Use WhatsApp Web?"
    
    def open_whatsapp(self, text):
        """Open WhatsApp"""
        # Extract contact name or number
        contact_match = re.search(r'(?:to|ko)\s+(.+?)(?:\s+message|$)', text, re.IGNORECASE)
        
        if self.is_mobile:
            return self.open_android_app('whatsapp')
        else:
            # Open WhatsApp Web
            webbrowser.open('https://web.whatsapp.com')
            return "💬 Opening WhatsApp Web..."
    
    def search_web(self, text):
        """Search on Google"""
        # Extract search query
        query_patterns = [
            r'search\s+(?:for\s+)?(.+)',
            r'google\s+(.+)',
            r'dhundo\s+(.+)',
            r'find\s+(.+)',
        ]
        
        query = None
        for pattern in query_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                query = match.group(1).strip()
                break
        
        if query:
            webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
            return f"🔍 Searching for: {query}"
        
        webbrowser.open("https://www.google.com")
        return "🔍 Opening Google..."
    
    def create_note(self, text):
        """Create note in Keep Notes or Notepad"""
        # Extract note content
        note_patterns = [
            r'(?:write|note|plan|likho)\s+(.+)',
            r'create\s+(?:a\s+)?note\s+(.+)',
        ]
        
        note_content = None
        for pattern in note_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                note_content = match.group(1).strip()
                break
        
        if self.is_mobile:
            # Open Keep Notes
            if note_content:
                return f"📝 Opening Keep Notes to write: {note_content}"
            else:
                return self.open_android_app('keep')
        else:
            # Open Notepad with content
            if note_content:
                # Create temp note file
                note_file = os.path.join(os.getenv('TEMP'), 'medha_note.txt')
                with open(note_file, 'w', encoding='utf-8') as f:
                    f.write(note_content)
                subprocess.Popen(['notepad.exe', note_file])
                return f"📝 Created note in Notepad: {note_content[:50]}..."
            else:
                subprocess.Popen(['notepad.exe'])
                return "📝 Opening Notepad..."
    
    def system_control(self, text):
        """Control system settings"""
        if 'volume' in text:
            if 'up' in text or 'increase' in text or 'badha' in text:
                return self.adjust_volume('up')
            elif 'down' in text or 'decrease' in text or 'kam' in text:
                return self.adjust_volume('down')
            elif 'mute' in text or 'band' in text:
                return self.adjust_volume('mute')
        
        if 'brightness' in text:
            return "💡 Brightness control coming soon!"
        
        if 'wifi' in text or 'bluetooth' in text:
            if self.is_mobile:
                return self.open_android_app('settings')
            else:
                subprocess.Popen(['ms-settings:network'])
                return "⚙️ Opening network settings..."
        
        return "⚙️ System control feature coming soon!"
    
    def adjust_volume(self, action):
        """Adjust system volume"""
        try:
            if self.system == 'Windows':
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                
                if action == 'up':
                    current = volume.GetMasterVolumeLevelScalar()
                    volume.SetMasterVolumeLevelScalar(min(1.0, current + 0.1), None)
                    return "🔊 Volume increased"
                elif action == 'down':
                    current = volume.GetMasterVolumeLevelScalar()
                    volume.SetMasterVolumeLevelScalar(max(0.0, current - 0.1), None)
                    return "🔉 Volume decreased"
                elif action == 'mute':
                    volume.SetMute(1, None)
                    return "🔇 Volume muted"
            else:
                return "🔊 Volume control not available on this platform"
        except:
            return "❌ Volume control requires pycaw library. Install: pip install pycaw comtypes"
