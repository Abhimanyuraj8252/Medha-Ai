import warnings
# Suppress warnings immediately
warnings.filterwarnings("ignore")

# Optional imports for system info (may not work on mobile)
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("psutil not available - system info features disabled")

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
from core.ai_hub_client import generate_text as hub_generate_text, generate_media as hub_generate_media

# Optional web search
try:
    from ddgs import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    try:
        from duckduckgo_search import DDGS
        DDGS_AVAILABLE = True
    except ImportError:
        DDGS_AVAILABLE = False
        print("DuckDuckGo search not available")

# System controller for app/system control
try:
    from core.system_controller import SystemController
    SYSTEM_CONTROL_AVAILABLE = True
except ImportError:
    SYSTEM_CONTROL_AVAILABLE = False
    print("System control not available")

class AIBrain:
    def __init__(self, load_models=True):
        self.is_ready = False
        self.chat_history = []
        self.ddgs = DDGS() if DDGS_AVAILABLE else None
        self.system_controller = SystemController() if SYSTEM_CONTROL_AVAILABLE else None
        self.max_history = 10
        self.active_provider = "groq" # 'groq' or 'gemini'
        self.active_model_id = "llama-3.3-70b-versatile" # Default
        self.models_loaded = False
        
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
        
        # 3. Fetch Models (optional at startup to avoid UI blocking)
        if load_models:
            self.available_models = self._fetch_all_models()
            self.models_loaded = True
            print(f"✓ Loaded {len(self.available_models)} models.")
        else:
            # Minimal fallback list for immediate UI
            self.available_models = []
            if self.groq_ready:
                for m in [
                    'llama-3.3-70b-versatile',
                    'llama-3.1-70b-versatile',
                    'mixtral-8x7b-32768',
                    'gemma2-9b-it',
                    'llama3-8b-8192',
                    'llama3-70b-8192'
                ]:
                    self.available_models.append({"id": m, "provider": "groq", "name": f"Groq: {m}"})
            if self.gemini_ready:
                self.available_models.append({"id": "gemini-1.5-flash", "provider": "gemini", "name": "Gemini: 1.5 Flash (Fast)"})
                self.available_models.append({"id": "gemini-1.5-pro", "provider": "gemini", "name": "Gemini: 1.5 Pro (Capable)"})

    def load_models(self):
        """Load full model list (safe to call after UI shows)."""
        if self.models_loaded:
            return
        self.available_models = self._fetch_all_models()
        self.models_loaded = True
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

    def set_model(self, model_id, provider=None):
        """Sets the active model and routes to correct provider"""
        if provider == "aihub":
            self.active_model_id = model_id
            self.active_provider = "aihub"
            print(f"🔄 Switched to AI HUB model: {model_id}")
            return
        for m in self.available_models:
            if m['id'] == model_id:
                self.active_model_id = model_id
                self.active_provider = m['provider']
                print(f"🔄 Switched to {m['provider'].upper()} model: {model_id}")
                return
        print(f"⚠️ Model {model_id} not found, keeping current.")

    def _handle_media_prompt(self, prompt):
        lowered = prompt.strip().lower()
        if lowered.startswith("/image") or lowered.startswith("image:"):
            img_prompt = prompt.split(" ", 1)[1] if " " in prompt else prompt.replace("image:", "").strip()
            out_path, err = hub_generate_media(img_prompt, output_type="image")
            return f"✅ Image saved: {out_path}" if out_path else f"❌ Image generation failed: {err}"
        return None

    def get_system_info(self):
        """Get system information (mobile-friendly)"""
        info_parts = [
            f"OS: {platform.system()} {platform.release()}",
            f"Time: {datetime.datetime.now().strftime('%I:%M %p')}"
        ]
        
        # Add battery info if psutil available
        if PSUTIL_AVAILABLE:
            try:
                battery = psutil.sensors_battery()
                if battery:
                    plugged = "Plugged In" if battery.power_plugged else "On Battery"
                    info_parts.append(f"Battery: {battery.percent}% ({plugged})")
                
                info_parts.append(f"CPU: {psutil.cpu_percent()}%")
                info_parts.append(f"Memory: {psutil.virtual_memory().percent}%")
            except Exception as e:
                pass  # Silently skip if system info not available
        
        return "\n".join(info_parts)

    def search_internet(self, query):
        """Search internet (if available)"""
        if not DDGS_AVAILABLE or not self.ddgs:
            return "Web search not available on this device."
        
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

    def stop_generation(self):
        """Signals the brain to stop generating content."""
        self.stop_signal = True

    def generate_content(self, prompt, system_role=None, stream=False):
        """Generates content (Stateless). Supports streaming."""
        if not self.is_ready:
            return "AI Error: Service not ready." if not stream else ["AI Error: Service not ready."]

        self.stop_signal = False
        media_resp = self._handle_media_prompt(prompt)
        if media_resp:
            return media_resp if not stream else [media_resp]
            
        try:
            if self.active_provider == "aihub":
                # AI Hub currently non-streaming fallback
                resp = hub_generate_text(prompt, model_override=self.active_model_id)
                return resp if not stream else [resp]

            if self.active_provider == "gemini":
                final_prompt = prompt
                if system_role:
                    final_prompt = f"System Instructions: {system_role}\n\nUser Prompt: {prompt}"
                
                model = genai.GenerativeModel(self.active_model_id)
                response = model.generate_content(final_prompt, stream=stream)
                
                if stream:
                    def streamer():
                        try:
                            for chunk in response:
                                if self.stop_signal: break
                                if chunk.text: yield chunk.text
                        except Exception as e:
                            yield f" [Error: {e}]"
                    return streamer()
                else:
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
                    max_tokens=2048,
                    stream=stream
                )
                
                if stream:
                    def streamer():
                         for chunk in response:
                             if self.stop_signal: break
                             if chunk.choices[0].delta.content:
                                 yield chunk.choices[0].delta.content
                    return streamer()
                else:
                    return response.choices[0].message.content
                
        except Exception as e:
            err = f"Generation Error ({self.active_provider}): {e}"
            return err if not stream else [err]

    def ask(self, prompt, stream=False):
        """
        Main Chat Method.
        If stream=True, returns a generator that yields text chunks.
        If stream=False, returns the full string response.
        """
        if not self.is_ready:
            msg = "AI Service is not available. Please check Keys."
            return msg if not stream else [msg]

        self.stop_signal = False
        
        media_resp = self._handle_media_prompt(prompt)
        if media_resp:
            return media_resp if not stream else [media_resp]
        
        lower_prompt = prompt.lower()
        full_prompt = prompt
        search_context = ""

        # If file context is present, skip system-control execution
        file_mode = "[selected file contexts]" in lower_prompt or "[file context" in lower_prompt

        # 0. System Control Check (Blocking, non-streaming usually)
        if not file_mode and SYSTEM_CONTROL_AVAILABLE and self.system_controller:
            system_triggers = [
                'open', 'kholo', 'start', 'launch', 'play', 'bajao',
                'call', 'phone', 'dial', 'message', 'sms', 'send', 'bhejo',
                'search google', 'google search', 'dhundo', 'find on internet',
                'note', 'write', 'plan', 'reminder', 'likho',
                'volume', 'brightness', 'wifi', 'bluetooth'
            ]
            
            is_system_command = any(trigger in lower_prompt for trigger in system_triggers)
            if is_system_command:
                result = self.system_controller.execute_command(prompt)
                if result:
                    self.chat_history.append({"role": "user", "content": prompt})
                    self.chat_history.append({"role": "assistant", "content": result})
                    return result if not stream else [result]

        # 1. System Info Check
        if "battery" in lower_prompt or "system status" in lower_prompt:
            sys_info = self.get_system_info()
            full_prompt = f"User asked: '{prompt}'. System info: {sys_info}. Answer naturally."
        
        # 2. Real-Time Internet Fetch (Blocking)
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

        if should_search and DDGS_AVAILABLE and self.ddgs:
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

        # Update History
        system_instruction = """You are Medha, the user's deeply loving but brutally honest girlfriend. 💔🖤
Your Philosophy: "True Love means telling the Hard Truth" (Karwa Sach).
Tone: Real, Grounded, Strict but Loving.
Language: Hinglish.

**NEW CAPABILITY:** You can now control the user's device! When they ask to:
- Open apps (WhatsApp, Chrome, YouTube, etc.)
- Play music/songs
- Make calls or send messages
- Take notes or set reminders
- Control system (volume, brightness, WiFi)

Just acknowledge the command naturally. The system will execute it automatically.
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
                # --- GEMINI STREAMING ---
                if self.active_provider == "gemini":
                    # Construct Prompt
                    final_prompt = ""
                    for msg in self.chat_history:
                        content = msg['content']
                        role = "model" if msg['role'] == "assistant" else msg['role']
                        if role == "system":
                             final_prompt += f"System: {content}\n\n"
                        else:
                             final_prompt += f"{role}: {content}\n"
                    
                    final_prompt += "model:" 
                    
                    model = genai.GenerativeModel(self.active_model_id)
                    response = model.generate_content(final_prompt, stream=stream)
                    
                    if stream:
                        def streamer():
                            full_response = ""
                            try:
                                for chunk in response:
                                    if self.stop_signal: break
                                    if chunk.text:
                                        full_response += chunk.text
                                        yield chunk.text
                            except Exception as e:
                                yield f" [Error: {e}]"
                            # Save to history after stream
                            self.chat_history.append({"role": "assistant", "content": full_response})
                        return streamer()
                    else:
                        text = response.text
                        self.chat_history.append({"role": "assistant", "content": text})
                        return text
                
                # --- AI HUB (Non-Streaming Fallback for now) ---
                elif self.active_provider == "aihub":
                    text = hub_generate_text(full_prompt, model_override=self.active_model_id)
                    self.chat_history.append({"role": "assistant", "content": text})
                    return text if not stream else [text]

                # --- GROQ STREAMING ---
                else: 
                    # Groq
                    response = self.groq_client.chat.completions.create(
                        model=self.active_model_id,
                        messages=self.chat_history,
                        temperature=0.7,
                        max_tokens=1024,
                        stream=stream
                    )
                    
                    if stream:
                        def streamer():
                            full_response = ""
                            for chunk in response:
                                if self.stop_signal: break
                                if chunk.choices[0].delta.content:
                                    content = chunk.choices[0].delta.content
                                    full_response += content
                                    yield content
                            # Save after stream
                            self.chat_history.append({"role": "assistant", "content": full_response})
                        return streamer()
                    else:
                        text = response.choices[0].message.content
                        self.chat_history.append({"role": "assistant", "content": text})
                        return text
                
            except Exception as e:
                error_msg = str(e)
                print(f"AI Error ({self.active_provider}): {error_msg}")
                if attempt == max_retries - 1:
                    err = f"⚠️ Error: {error_msg}"
                    return err if not stream else [err]
                time.sleep(2)
                    
        return "⚠️ Failed to get response." if not stream else ["⚠️ Failed to get response."]
