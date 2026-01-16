import threading
import flet as ft
import tempfile
import os
import time
import asyncio
import edge_tts

# Try importing Voice Dependencies safely
try:
    import speech_recognition as sr
    from gtts import gTTS
    import pygame
    VOICE_AVAILABLE = True
    AUDIO_ENGINE = "pygame"
except ImportError:
    try:
        import speech_recognition as sr
        from gtts import gTTS
        from playsound import playsound
        VOICE_AVAILABLE = True
        AUDIO_ENGINE = "playsound"
        pygame = None
    except ImportError:
        try:
            import speech_recognition as sr
            from gtts import gTTS
            import winsound
            VOICE_AVAILABLE = True
            AUDIO_ENGINE = "winsound"
            pygame = None
        except ImportError as e:
            print(f"Voice Warning: Dependencies missing ({e}). Voice disabled.")
            VOICE_AVAILABLE = False
            AUDIO_ENGINE = None
            sr = None
            gTTS = None
            pygame = None

class VoiceHandler:
    def __init__(self, page: ft.Page):
        self.page = page
        # self.audio_player = ft.Audio(autoplay=True) # Removed: Not supported in this Flet version
        # self.page.overlay.append(self.audio_player)
        self.is_listening = False
        self.is_speaking = False  # Track if currently speaking
        
        # Initialize mixer
        if VOICE_AVAILABLE and pygame:
            try:
                pygame.mixer.init()
            except Exception as e:
                print(f"Pygame Init Error: {e}")
        
        # Initialize recognizer only if available
        if VOICE_AVAILABLE and sr:
            self.recognizer = sr.Recognizer()
        else:
            self.recognizer = None
    
    def stop_speaking(self):
        """Stop current speech"""
        self.is_speaking = False
        if AUDIO_ENGINE == "pygame" and pygame:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
            except:
                pass


    def speak(self, text, lang='en'):
        """Converts text to speech and plays it using Edge TTS for Anime voice."""
        if not VOICE_AVAILABLE:
            print("Voice Output not available.")
            return

        def _speak():
            try:
                self.is_speaking = True
                
                # Create a temp file
                fd, temp_path = tempfile.mkstemp(suffix=".mp3")
                os.close(fd)
                
                # --- Edge TTS Generation (Anime Style) ---
                async def generate_anime_voice():
                    try:
                        # "hi-IN-SwaraNeural" with Sweet & Emotional tuning
                        # Pitch: +15Hz (Soft sweetness, avoiding child-like squeak)
                        # Rate: -10% (Slower pace feels more emotional and caring)
                        voice = "hi-IN-SwaraNeural"
                        communicate = edge_tts.Communicate(text, voice, pitch="+15Hz", rate="-10%")
                        await communicate.save(temp_path)
                        return True
                    except Exception as e:
                        print(f"EdgeTTS Error: {e}")
                        return False

                # Run Async Code
                try:
                    # Windows ProactorEventLoop is needed for some subprocesses, 
                    # but simple async gen is file I/O bound.
                    # Create a new loop for this thread.
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    success = loop.run_until_complete(generate_anime_voice())
                    loop.close()
                except Exception as e:
                     print(f"Async Loop Error: {e}")
                     # Fallback to just gTTS immediately if async loop fails
                     success = False

                # --- Fallback to gTTS if EdgeTTS failed ---
                if not success:
                    print("Falling back to gTTS...")
                    if gTTS:
                        if lang == 'hi':
                            tts = gTTS(text=text, lang='hi', slow=False, tld='co.in')
                        else:
                            tts = gTTS(text=text, lang='en', slow=False, tld='co.in')
                        tts.save(temp_path)
                    else:
                        print("No TTS engine available")
                        return

                # --- Play Audio ---
                played = False
                
                # 1. Try Pygame (Most reliable for control)
                if AUDIO_ENGINE == "pygame" and pygame and self.is_speaking:
                    try:
                        # Unload previous music to free file lock if any
                        try:
                             pygame.mixer.music.unload()
                        except: pass
                        
                        pygame.mixer.music.load(temp_path)
                        pygame.mixer.music.play()
                        
                        # Wait for playback to finish OR stop signal
                        while pygame.mixer.music.get_busy() and self.is_speaking: 
                            time.sleep(0.1)
                            
                        # If stopped manually, actual stop command
                        if not self.is_speaking:
                             pygame.mixer.music.stop()
                             
                        pygame.mixer.music.unload()
                        played = True
                    except Exception as e:
                        print(f"Pygame error: {e}")
                
                # 2. Native Fallback
                if not played:
                    try:
                        if os.name == 'nt':
                            os.startfile(temp_path)
                            # Wait heuristic (imperfect)
                            time.sleep(min(len(text)/5, 15)) 
                    except:
                        pass
                
                # Cleanup
                try:
                    # Small delay to ensure file handle is released
                    time.sleep(0.2)
                    os.remove(temp_path)
                except:
                    pass
                
            except Exception as e:
                print(f"Voice generation error: {e}")
            finally:
                self.is_speaking = False

        threading.Thread(target=_speak, daemon=True).start()


    def listen(self, callback, language="en-IN"):
        """Listens to microphone and calls callback with text."""
        if not VOICE_AVAILABLE or not self.recognizer:
            # Silent return - don't spam console
            callback("")
            return

        if self.is_listening:
            return
            
        self.is_listening = True
        
        def _listen():
            try:
                # Check for PyAudio availability before attempting to use microphone
                try:
                    import pyaudio
                except ImportError:
                    # Silent - PyAudio not available
                    callback("")
                    self.is_listening = False
                    return
                
                # Check if Microphone class is available
                if not hasattr(sr, 'Microphone'):
                    raise ImportError("PyAudio not properly linked to SpeechRecognition")

                with sr.Microphone() as source:
                    print("🎤 Listening... Speak now!")
                    # Reduce noise adjustment time for faster response
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    audio = self.recognizer.listen(source, timeout=8, phrase_time_limit=15)
                    
                # Try recognition with error handling
                try:
                    text = self.recognizer.recognize_google(audio, language=language)
                    print(f"✓ Heard: {text}")
                    callback(text)
                except sr.UnknownValueError:
                    print("Could not understand audio - please speak clearly")
                    callback("")
                except sr.RequestError as e:
                    print(f"Speech recognition service error: {e}")
                    callback("")
                
            except sr.WaitTimeoutError:
                print("⏱️ No speech detected - please try again")
                callback("")
            except (OSError, ImportError) as e:
                # Silently handle - don't spam console
                callback("")
            except Exception as e:
                # Only log unexpected errors (not PyAudio related)
                if "PyAudio" not in str(e) and "pyaudio" not in str(e).lower():
                    print(f"[ERROR] Unexpected microphone error: {e}")
                callback("")
            finally:
                self.is_listening = False

        threading.Thread(target=_listen, daemon=True).start()
