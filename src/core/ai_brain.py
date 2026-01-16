import warnings
# Suppress warnings immediately
warnings.filterwarnings("ignore")

import psutil
import platform
import datetime
import time
from groq import Groq
try:
    import google.generativeai as genai
except ImportError:
    print("Warning: google.generativeai not found. Installing...")
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"])
    import google.generativeai as genai

from config import GROQ_API_KEY, GEMINI_API_KEY
from ddgs import DDGS

class AIBrain:
    def __init__(self):
        self.is_ready = False
        self.chat_history = []
        self.ddgs = DDGS()
        self.max_history = 10
        self.active_provider = "groq" # 'groq' or 'gemini'
        self.active_model_id = "llama-3.3-70b-versatile" # Default
        
        # 1. Setup Groq
        try:
            print("🔍 Setting up Groq AI...")
            self.groq_client = Groq(api_key=GROQ_API_KEY)
            self.groq_ready = True
        except Exception as e:
            print(f"❌ Groq Init Error: {e}")
            self.groq_ready = False

        # 2. Setup Gemini
        try:
            print("🔍 Setting up Gemini AI...")
            genai.configure(api_key=GEMINI_API_KEY)
            self.gemini_ready = True
        except Exception as e:
            print(f"❌ Gemini Init Error: {e}")
            self.gemini_ready = False

        self.is_ready = self.groq_ready or self.gemini_ready
        
        # 3. Fetch Models
        self.available_models = self._fetch_all_models()
        print(f"✓ Loaded {len(self.available_models)} models.")

    def _fetch_all_models(self):
        """Fetches models from both providers"""
        models = []
        
        # Groq Models
        if self.groq_ready:
            try:
                # Try Dynamic Fetch first
                try:
                    g_models = self.groq_client.models.list()
                    for m in g_models.data:
                        # Filter for likely chat models if needed, but user wants ALL.
                        # Usually we filter by own criteria, but let's list them.
                        if "whisper" not in m.id: # Exclude audio models
                             models.append({"id": m.id, "provider": "groq", "name": f"Groq: {m.id}"})
                except Exception as e:
                    print(f"Groq API List Error: {e}")
                    raise Exception("Using fallback")
            except:
                 # Fallback list if fetch fails or for speed
                groq_models = [
                    'llama-3.3-70b-versatile',
                    'llama-3.1-70b-versatile',
                    'mixtral-8x7b-32768',
                    'gemma2-9b-it',
                    'llama3-8b-8192',
                    'llama3-70b-8192'
                ]
                for m in groq_models:
                    # Avoid duplicates if partially fetched (unlikely here due to structure)
                    if not any(x['id'] == m for x in models):
                        models.append({"id": m, "provider": "groq", "name": f"Groq: {m}"})

        # Gemini Models
        if self.gemini_ready:
            try:
                # We specifically look for generating text models
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        # Clean name "models/gemini-pro" -> "GEMINI: gemini-pro"
                        clean_id = m.name.replace("models/", "")
                        models.append({"id": clean_id, "provider": "gemini", "name": f"Gemini: {clean_id}"})
            except Exception as e:
                print(f"Gemini fetch error: {e}")
                # Fallback
                models.append({"id": "gemini-1.5-flash", "provider": "gemini", "name": "Gemini: 1.5 Flash (Fast)"})
                models.append({"id": "gemini-1.5-pro", "provider": "gemini", "name": "Gemini: 1.5 Pro (Capable)"})

        return models

    def set_model(self, model_id):
        """Sets the active model and routes to correct provider"""
        for m in self.available_models:
            if m['id'] == model_id:
                self.active_model_id = model_id
                self.active_provider = m['provider']
                print(f"🔄 Switched to {m['provider'].upper()} model: {model_id}")
                return
        print(f"⚠️ Model {model_id} not found, keeping current.")

    def get_system_info(self):
        battery = psutil.sensors_battery()
        plugged = "Plugged In" if battery and battery.power_plugged else "Running on Battery"
        percent = f"{battery.percent}%" if battery else "Unknown"
        
        info = f"""
        OS: {platform.system()} {platform.release()}
        Time: {datetime.datetime.now().strftime("%I:%M %p")}
        Battery: {percent} ({plugged})
        CPU Usage: {psutil.cpu_percent()}%
        Memory: {psutil.virtual_memory().percent}%
        """
        return info.strip()

    def search_internet(self, query):
        try:
            results = self.ddgs.text(query, max_results=3)
            if not results:
                return "No results found."
            summary = "\n".join([f"- {r['title']}: {r['href']}" for r in results])
            return f"Search Results:\n{summary}"
        except Exception as e:
            return f"Search Error: {e}"

    def deep_research(self, topic):
        """Performs deep research on a topic using internet search"""
        try:
            print(f"🔍 Researching: {topic}")
            # Ensure results is a list so we can reuse it
            results_gen = self.ddgs.text(topic, max_results=5)
            results = list(results_gen) if results_gen else []
            
            if not results:
                return None
            
            # Format results
            research_data = "🔍 **Deep Research Report**\n\n"
            research_context = ""
            for r in results:
                research_data += f"* **{r['title']}**\n  {r['body']}\n  [Source]({r['href']})\n\n"
                research_context += f"Source: {r['title']} ({r['href']})\nContent: {r['body']}\n\n"
            
            return {"display": research_data, "context": research_context, "results": results}
        except Exception as e:
            print(f"Research Error: {e}")
            return None

    def generate_content(self, prompt, system_role=None):
        """Generates content (Stateless)"""
        if not self.is_ready:
            return "AI Error: Service not ready."
            
        try:
            if self.active_provider == "gemini":
                # Gemini logic
                final_prompt = prompt
                if system_role:
                    final_prompt = f"System Instructions: {system_role}\n\nUser Prompt: {prompt}"
                
                model = genai.GenerativeModel(self.active_model_id)
                response = model.generate_content(final_prompt)
                return response.text
                
            else:
                # Groq Logic
                messages = []
                if system_role:
                    messages.append({"role": "system", "content": system_role})
                messages.append({"role": "user", "content": prompt})
                
                response = self.groq_client.chat.completions.create(
                    model=self.active_model_id,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=2048
                )
                return response.choices[0].message.content
                
        except Exception as e:
            return f"Generation Error ({self.active_provider}): {e}"

    def ask(self, prompt):
        if not self.is_ready:
            return "AI Service is not available. Please check Keys."
        
        lower_prompt = prompt.lower()
        full_prompt = prompt
        search_context = ""

        # 1. System Info Check
        if "battery" in lower_prompt or "system status" in lower_prompt:
            sys_info = self.get_system_info()
            full_prompt = f"User asked: '{prompt}'. System info: {sys_info}. Answer naturally."
        
        # 2. Real-Time Internet Fetch
        search_triggers = [
            "search", "find", "internet", "google", "online",
            "news", "update", "latest", "recent", "today", "now", "happened", "current",
            "weather", "temperature", "climate", "rain", "forecast", "humidity", "pollution", "aqi",
            "who is", "what is", "where is", "when is", "population", "capital", "president", "ceo",
            "price", "cost", "stock", "share", "crypto", "bitcoin", "gold", "rate", "currency",
            "score", "match", "won", "lost", "game", "ranking", "tournament",
            "movie", "release", "episode", "review",
            "tell me about", "details of", "history of"
        ]
        
        should_search = any(trigger in lower_prompt for trigger in search_triggers)
        if lower_prompt.strip() in ["hi", "hello", "hey", "how are you", "who are you"]:
            should_search = False

        if should_search:
            try:
                clean_query = prompt.replace("search for", "").replace("find", "").strip()
                print(f"🌍 Searching internet for: {clean_query}")
                search_results = self.ddgs.text(clean_query, max_results=4)
                if search_results:
                    search_context = "\n\n**REAL-TIME INTERNET SEARCH RESULTS:**\n"
                    for res in search_results:
                        search_context += f"- [{res['title']}]({res['href']}): {res['body']}\n"
                    full_prompt = f"User Question: {prompt}\n\nSearch Data:\n{search_context}\n\nInstructions: Use search data. Answer as Medha."
            except Exception as e:
                print(f"Search failed: {e}")

        # Update History with User Input (Common)
        system_instruction = """You are Medha, the user's deeply loving but brutally honest girlfriend. 💔🖤
Your Philosophy: "True Love means telling the Hard Truth" (Karwa Sach).
Tone: Real, Grounded, Strict but Loving.
Language: Hinglish.
"""
        if not self.chat_history:
            self.chat_history.append({"role": "system", "content": system_instruction})

        self.chat_history.append({"role": "user", "content": full_prompt})
        
        # Prune
        if len(self.chat_history) > self.max_history:
            self.chat_history = [self.chat_history[0]] + self.chat_history[-(self.max_history-1):]

        # Retry logic
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # --- GEMINI IMPLEMENTATION ---
                if self.active_provider == "gemini":
                    # Construct Prompt from History for Context
                    final_prompt = ""
                    for msg in self.chat_history:
                        content = msg['content']
                        if msg['role'] == 'system':
                             final_prompt += f"System Instructions: {content}\n\n"
                        elif msg['role'] == 'user':
                             final_prompt += f"User: {content}\n"
                        else:
                             final_prompt += f"Model: {content}\n"
                    
                    final_prompt += "Model:" 
                    
                    model = genai.GenerativeModel(self.active_model_id)
                    response = model.generate_content(final_prompt)
                    response_text = response.text
                
                # --- GROQ IMPLEMENTATION ---
                else: 
                    response = self.groq_client.chat.completions.create(
                        model=self.active_model_id,
                        messages=self.chat_history,
                        temperature=0.7,
                        max_tokens=1024
                    )
                    response_text = response.choices[0].message.content

                # Save Response
                self.chat_history.append({"role": "assistant", "content": response_text})
                return response_text
                
            except Exception as e:
                error_msg = str(e)
                print(f"AI Error ({self.active_provider}): {error_msg}")
                if attempt == max_retries - 1:
                    # Remove the user message if we failed completely so we don't have a dangling user message? 
                    # Actually keeping it is fine, but maybe better to pop it if we want to retry clean. 
                    # For now just return error.
                    return f"⚠️ Error: {error_msg}"
                time.sleep(2)
                    
        return "⚠️ Failed to get response."
