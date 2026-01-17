"""
Multi-language Support for Medha AI
Supports Hindi, English, Tamil, Telugu, Bengali, Marathi
"""
import json
from pathlib import Path

LANGUAGES = {
    "en": "English",
    "hi": "हिंदी",
    "ta": "தமிழ்",
    "te": "తెలుగు",
    "bn": "বাংলা",
    "mr": "मराठी"
}

# UI Strings in different languages
STRINGS = {
    "en": {
        "app_name": "Medha AI",
        "chat": "Chat",
        "study_notes": "Study Notes",
        "quiz_mode": "Quiz Mode",
        "coder_mode": "Coder Mode",
        "settings": "Settings",
        "clear_history": "Clear History",
        "ask_anything": "Ask Medha anything...",
        "send": "Send",
        "voice_input": "Voice Input",
        "export_chat": "Export Chat",
        "language": "Language",
        "theme": "Theme",
        "usage_stats": "Usage Stats",
        "check_updates": "Check for Updates",
        "api_calls": "API Calls",
        "tokens_used": "Tokens Used",
        "session_time": "Session Time",
        "new_chat": "New Chat",
        "history": "History",
        "listening": "Listening...",
        "processing": "Processing...",
        "error": "Error",
        "success": "Success",
        "welcome": "Hi! I'm Medha. How can I help you today? ❤️"
    },
    "hi": {
        "app_name": "मेधा AI",
        "chat": "चैट",
        "study_notes": "अध्ययन नोट्स",
        "quiz_mode": "क्विज़ मोड",
        "coder_mode": "कोडर मोड",
        "settings": "सेटिंग्स",
        "clear_history": "इतिहास साफ़ करें",
        "ask_anything": "मेधा से कुछ भी पूछें...",
        "send": "भेजें",
        "voice_input": "आवाज़ इनपुट",
        "export_chat": "चैट निर्यात करें",
        "language": "भाषा",
        "theme": "थीम",
        "usage_stats": "उपयोग आँकड़े",
        "check_updates": "अपडेट जाँचें",
        "api_calls": "API कॉल्स",
        "tokens_used": "टोकन उपयोग",
        "session_time": "सत्र समय",
        "new_chat": "नई चैट",
        "history": "इतिहास",
        "listening": "सुन रहे हैं...",
        "processing": "प्रोसेस हो रहा है...",
        "error": "त्रुटि",
        "success": "सफल",
        "welcome": "नमस्ते! मैं मेधा हूं। आज मैं आपकी कैसे मदद कर सकती हूं? ❤️"
    },
    "ta": {
        "app_name": "மேதா AI",
        "chat": "அரட்டை",
        "study_notes": "படிப்பு குறிப்புகள்",
        "quiz_mode": "வினாடி வினா",
        "coder_mode": "கோடர் பயன்முறை",
        "settings": "அமைப்புகள்",
        "clear_history": "வரலாற்றை அழி",
        "ask_anything": "மேதாவிடம் எதையும் கேளுங்கள்...",
        "send": "அனுப்பு",
        "voice_input": "குரல் உள்ளீடு",
        "export_chat": "அரட்டையை ஏற்றுமதி செய்",
        "language": "மொழி",
        "theme": "தீம்",
        "usage_stats": "பயன்பாட்டு புள்ளிவிவரங்கள்",
        "check_updates": "புதுப்பிப்புகளைச் சரிபார்க்கவும்",
        "api_calls": "API அழைப்புகள்",
        "tokens_used": "டோக்கன்கள் பயன்படுத்தப்பட்டன",
        "session_time": "அமர்வு நேரம்",
        "new_chat": "புதிய அரட்டை",
        "history": "வரலாறு",
        "listening": "கேட்கிறேன்...",
        "processing": "செயலாக்குகிறது...",
        "error": "பிழை",
        "success": "வெற்றி",
        "welcome": "வணக்கம்! நான் மேதா. இன்று நான் உங்களுக்கு எப்படி உதவ முடியும்? ❤️"
    },
    "te": {
        "app_name": "మేధా AI",
        "chat": "చాట్",
        "study_notes": "అధ్యయన నోట్స్",
        "quiz_mode": "క్విజ్ మోడ్",
        "coder_mode": "కోడర్ మోడ్",
        "settings": "సెట్టింగ్‌లు",
        "clear_history": "చరిత్రను తొలగించు",
        "ask_anything": "మేధాను ఏదైనా అడగండి...",
        "send": "పంపు",
        "voice_input": "వాయిస్ ఇన్‌పుట్",
        "export_chat": "చాట్ ఎగుమతి చేయండి",
        "language": "భాష",
        "theme": "థీమ్",
        "usage_stats": "వినియోగ గణాంకాలు",
        "check_updates": "అప్‌డేట్‌లను తనిఖీ చేయండి",
        "api_calls": "API కాల్స్",
        "tokens_used": "టోకెన్లు ఉపయోగించబడ్డాయి",
        "session_time": "సెషన్ సమయం",
        "new_chat": "కొత్త చాట్",
        "history": "చరిత్ర",
        "listening": "వింటున్నాను...",
        "processing": "ప్రాసెస్ చేస్తోంది...",
        "error": "లోపం",
        "success": "విజయం",
        "welcome": "హలో! నేను మేధా. ఈరోజు మీకు ఎలా సహాయం చేయగలను? ❤️"
    },
    "bn": {
        "app_name": "মেধা AI",
        "chat": "চ্যাট",
        "study_notes": "অধ্যয়ন নোট",
        "quiz_mode": "কুইজ মোড",
        "coder_mode": "কোডার মোড",
        "settings": "সেটিংস",
        "clear_history": "ইতিহাস মুছুন",
        "ask_anything": "মেধাকে কিছু জিজ্ঞাসা করুন...",
        "send": "পাঠান",
        "voice_input": "ভয়েস ইনপুট",
        "export_chat": "চ্যাট এক্সপোর্ট করুন",
        "language": "ভাষা",
        "theme": "থিম",
        "usage_stats": "ব্যবহারের পরিসংখ্যান",
        "check_updates": "আপডেট চেক করুন",
        "api_calls": "API কল",
        "tokens_used": "টোকেন ব্যবহৃত",
        "session_time": "সেশন সময়",
        "new_chat": "নতুন চ্যাট",
        "history": "ইতিহাস",
        "listening": "শুনছি...",
        "processing": "প্রক্রিয়াকরণ হচ্ছে...",
        "error": "ত্রুটি",
        "success": "সফল",
        "welcome": "হ্যালো! আমি মেধা। আজ আমি আপনাকে কীভাবে সাহায্য করতে পারি? ❤️"
    },
    "mr": {
        "app_name": "मेधा AI",
        "chat": "चॅट",
        "study_notes": "अभ्यास नोट्स",
        "quiz_mode": "क्विझ मोड",
        "coder_mode": "कोडर मोड",
        "settings": "सेटिंग्ज",
        "clear_history": "इतिहास साफ करा",
        "ask_anything": "मेधाला काहीही विचारा...",
        "send": "पाठवा",
        "voice_input": "व्हॉइस इनपुट",
        "export_chat": "चॅट एक्सपोर्ट करा",
        "language": "भाषा",
        "theme": "थीम",
        "usage_stats": "वापर आकडेवारी",
        "check_updates": "अपडेट तपासा",
        "api_calls": "API कॉल्स",
        "tokens_used": "टोकन वापरले",
        "session_time": "सेशन वेळ",
        "new_chat": "नवीन चॅट",
        "history": "इतिहास",
        "listening": "ऐकत आहे...",
        "processing": "प्रक्रिया होत आहे...",
        "error": "त्रुटी",
        "success": "यशस्वी",
        "welcome": "नमस्कार! मी मेधा आहे. आज मी तुम्हाला कशी मदत करू शकते? ❤️"
    }
}

class LanguageManager:
    """Manages language preferences and translations"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".medha_ai"
        self.config_file = self.config_dir / "language.json"
        self.current_lang = self._load_preference()
        
    def _load_preference(self) -> str:
        """Load saved language preference"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    return data.get("lang", "en")
        except:
            pass
        return "en"
    
    def save_preference(self, lang_code: str):
        """Save language preference"""
        self.config_dir.mkdir(exist_ok=True)
        self.current_lang = lang_code
        with open(self.config_file, 'w') as f:
            json.dump({"lang": lang_code}, f)
    
    def get(self, key: str) -> str:
        """Get translated string"""
        return STRINGS.get(self.current_lang, STRINGS["en"]).get(key, key)
    
    def get_all_languages(self) -> dict:
        """Get all available languages"""
        return LANGUAGES
    
    def get_current_language(self) -> str:
        """Get current language code"""
        return self.current_lang

# Global instance
lang = LanguageManager()
