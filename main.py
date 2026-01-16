"""
Medha AI - Mobile App Entry Point (Kivy Version)
This is a simplified mobile version that works with Buildozer
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

# Set background color
Window.clearcolor = (0.1, 0.1, 0.15, 1)

class MedhaAI(App):
    def build(self):
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title
        title = Label(
            text='🤖 Medha AI Assistant',
            size_hint_y=0.1,
            font_size='24sp',
            color=(0.4, 0.5, 0.9, 1)
        )
        
        # Chat area
        self.chat_scroll = ScrollView(size_hint=(1, 0.7))
        self.chat_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
        self.chat_layout.bind(minimum_height=self.chat_layout.setter('height'))
        self.chat_scroll.add_widget(self.chat_layout)
        
        # Welcome message
        self.add_message("👋 Hi! I'm Medha. Ask me anything!", is_user=False)
        
        # Input area
        input_layout = BoxLayout(orientation='horizontal', size_hint_y=0.15, spacing=5)
        
        self.message_input = TextInput(
            hint_text='Type your message...',
            multiline=False,
            size_hint_x=0.75,
            background_color=(0.2, 0.2, 0.25, 1),
            foreground_color=(1, 1, 1, 1)
        )
        self.message_input.bind(on_text_validate=self.send_message)
        
        send_btn = Button(
            text='Send',
            size_hint_x=0.25,
            background_color=(0.4, 0.5, 0.9, 1)
        )
        send_btn.bind(on_press=self.send_message)
        
        input_layout.add_widget(self.message_input)
        input_layout.add_widget(send_btn)
        
        # Add all to main layout
        main_layout.add_widget(title)
        main_layout.add_widget(self.chat_scroll)
        main_layout.add_widget(input_layout)
        
        return main_layout
    
    def add_message(self, text, is_user=True):
        """Add message to chat"""
        color = (0.4, 0.5, 0.9, 1) if is_user else (0.3, 0.3, 0.35, 1)
        
        msg = Label(
            text=text,
            size_hint_y=None,
            height=100,
            text_size=(Window.width - 40, None),
            halign='left',
            valign='top',
            color=color,
            padding=(10, 10)
        )
        
        self.chat_layout.add_widget(msg)
        self.chat_scroll.scroll_y = 0
    
    def send_message(self, instance):
        """Send message"""
        message = self.message_input.text.strip()
        if not message:
            return
        
        # Add user message
        self.add_message(f"You: {message}", is_user=True)
        self.message_input.text = ''
        
        # Simple responses (AI integration will be added)
        responses = {
            'hello': 'Hi! How can I help you?',
            'hi': 'Hello! What can I do for you?',
            'help': 'I can help you with studying, quizzes, coding, and general questions!',
            'bye': 'Goodbye! Come back anytime! 👋'
        }
        
        # Get response
        response = responses.get(message.lower(), 
            f"I received: '{message}'. Full AI features coming soon! 🚀")
        
        self.add_message(f"Medha: {response}", is_user=False)

if __name__ == '__main__':
    MedhaAI().run()
