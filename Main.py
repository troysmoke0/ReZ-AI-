from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.core.text import LabelBase
from datetime import datetime
import pyttsx3
import threading
import random
import speech_recognition as sr
import requests
import json

# ==================================================
# 🔐 YOUR SETTINGS — EDIT THESE DIRECTLY
# ==================================================
VERIFICATION_KEY = "Juniour123"       # Your secret key
OWNER_NAME = "Boss JID"               # What REZ calls you
AI_NAME = "REZ"
VOICE_RATE = 142                      # Henry voice speed
VOICE_VOLUME = 0.95

# 👇 PASTE YOUR API KEY HERE 👇
YOUR_AI_API_KEY = "apf_nsjxwp8w8o0efn3murp9xons"   # <--- ENCODE YOUR KEY HERE
YOUR_AI_API_URL = "https://apifreellm.com/api/v1/chat"  # <--- Your API endpoint

# Register modern font
LabelBase.register(name='SegoeUI', fn_regular='SegoeUI.ttf')

# ==================================================
# 🎤 HENRY VOICE ENGINE
# ==================================================
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for v in voices:
    if 'English' in v.name and ('David' in v.name or 'Male' in v.name or 'Henry' in v.name):
        engine.setProperty('voice', v.id)
        break
engine.setProperty('rate', VOICE_RATE)
engine.setProperty('volume', VOICE_VOLUME)

# ==================================================
# 🧠 GLOBAL STATE
# ==================================================
LISTENING = False
VERIFIED = False  # Will become True only after correct key
CONVERSATION_HISTORY = []  # For real back-and-forth talk

# ==================================================
# 🖥️ MAIN INTERFACE
# ==================================================
class REZInterface(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 12
        self.bg_color = (0.1, 0.1, 0.18, 1)

        # --- HEADER ---
        self.header = Label(
            text="✨ REZ • ULTIMATE AI",
            font_name='SegoeUI',
            font_size=26,
            color=(0, 0.98, 0.83, 1),
            size_hint_y=0.11,
            bold=True
        )
        self.add_widget(self.header)

        # --- STATUS ---
        self.status = Label(
            text="🔒 VERIFICATION REQUIRED",
            font_name='SegoeUI',
            font_size=15,
            color=(1, 0.3, 0.3, 1),
            size_hint_y=0.05
        )
        self.add_widget(self.status)

        # --- TIME & DATE ---
        self.time_label = Label(
            text="",
            font_name='SegoeUI',
            font_size=17,
            color=(0.94, 0.36, 0.71, 1),
            size_hint_y=0.07
        )
        self.add_widget(self.time_label)
        Clock.schedule_interval(self.update_time, 1)

        # --- CHAT BOX ---
        self.chat_box = TextInput(
            text="REZ: Welcome! I am locked. Please enter your verification key to activate me.\n",
            font_name='SegoeUI',
            font_size=14,
            background_color=(0.08, 0.13, 0.22, 1),
            foreground_color=(0.88, 0.88, 0.88, 1),
            readonly=True,
            size_hint_y=0.55,
            padding=(15,15)
        )
        self.add_widget(self.chat_box)

        # --- INPUT FIELD ---
        self.input_field = TextInput(
            hint_text="Enter key or type message here...",
            font_name='SegoeUI',
            font_size=15,
            background_color=(0.04, 0.2, 0.38, 1),
            foreground_color=(1,1,1,1),
            hint_text_color=(0.7,0.7,0.7,1),
            size_hint_y=0.09,
            multiline=False
        )
        self.input_field.bind(on_text_validate=self.handle_text_input)
        self.add_widget(self.input_field)

        # --- BUTTONS ROW ---
        self.btn_row = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.11)

        self.send_btn = Button(
            text="SEND",
            font_name='SegoeUI',
            font_size=16,
            background_color=(0, 0.98, 0.83, 1),
            color=(0,0,0,1),
            bold=True
        )
        self.send_btn.bind(on_press=self.handle_text_input)
        self.btn_row.add_widget(self.send_btn)

        self.voice_btn = Button(
            text="🎤 TALK",
            font_name='SegoeUI',
            font_size=16,
            background_color=(1, 0.2, 0.4, 1),
            color=(1,1,1,1),
            bold=True,
            disabled_color=(0.5,0.5,0.5,1)
        )
        self.voice_btn.bind(on_press=self.start_voice_listen)
        self.btn_row.add_widget(self.voice_btn)

        self.add_widget(self.btn_row)

    # ==================================================
    # ⏱️ TIME UPDATE
    # ==================================================
    def update_time(self, dt):
        now = datetime.now().strftime("%A | %d %B %Y | %H:%M:%S")
        self.time_label.text = now

    # ==================================================
    # 💬 ADD TEXT TO CHAT
    # ==================================================
    def append(self, text):
        self.chat_box.text += text
        self.chat_box.cursor = (0, len(self.chat_box.text))

    # ==================================================
    # 🎤 VOICE OUTPUT (HENRY)
    # ==================================================
    def speak(self, text):
        def talk():
            engine.say(text)
            engine.runAndWait()
        threading.Thread(target=talk, daemon=True).start()
        self.append(f"REZ: {text}\n")

    # ==================================================
    # 🔐 VERIFICATION SYSTEM
    # ==================================================
    def verify_user(self, key_input):
        global VERIFIED
        if key_input.strip() == VERIFICATION_KEY:
            VERIFIED = True
            self.status.text = f"🟢 ONLINE | Welcome {OWNER_NAME}"
            self.status.color = (0.2, 1, 0.5, 1)
            self.voice_btn.disabled = False  # Enable voice
            self.speak(f"Verification successful. Hello {OWNER_NAME}! I am fully activated. You can talk or type freely. I remember everything we say.")
            self.append("\n✅ SYSTEM UNLOCKED — Full access granted\n")
            return True
        else:
            self.speak("Invalid key. Access denied.")
            return False

    # ==================================================
    # 📝 TYPING INPUT
    # ==================================================
    def handle_text_input(self, instance):
        txt = self.input_field.text.strip()
        if not txt:
            return
        self.append(f"YOU: {txt}\n")
        self.input_field.text = ""

        if not VERIFIED:
            self.verify_user(txt)
            return

        self.process_command(txt)

    # ==================================================
    # 🎤 VOICE INPUT
    # ==================================================
    def start_voice_listen(self, instance):
        if not VERIFIED or LISTENING:
            return
        global LISTENING
        LISTENING = True
        self.status.text = "🎤 LISTENING... Speak now"
        self.status.color = (1, 0.5, 0, 1)
        threading.Thread(target=self.listen_voice, daemon=True).start()

    def listen_voice(self):
        global LISTENING
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source, timeout=5)
        try:
            spoken_text = r.recognize_google(audio).lower()
            self.append(f"YOU: {spoken_text}\n")
            self.process_command(spoken_text)
        except:
            self.speak("Sorry I didn't catch that, please repeat or type.")
        LISTENING = False
        Clock.schedule_once(lambda dt: self.reset_status(), 0.5)

    # ==================================================
    # 🧠 MAIN AI LOGIC + FREE CONVERSATION + PHONE CONTROL
    # ==================================================
    def process_command(self, user_text):
        user_low = user_text.lower()

        # --- REACT TO NAME ---
        if AI_NAME.lower() in user_low:
            self.status.text = "⚡ ACTIVATED ⚡"
            self.status.color = (1, 0, 0.33, 1)
            Clock.schedule_once(lambda dt: self.reset_status(), 1.5)
            self.speak(f"Yes {OWNER_NAME}? I'm right here.")
            return

        # --- PHONE CONTROL COMMANDS ---
        if "open settings" in user_low:
            self.speak("Opening phone settings now.")
            # Add Android intent code here if needed
            return
        elif "open browser" in user_low or "internet" in user_low:
            self.speak("Opening web browser.")
            return
        elif "what time is it" in user_low:
            t = datetime.now().strftime("%H:%M")
            self.speak(f"It's {t} {OWNER_NAME}.")
            return
        elif "what is the date" in user_low:
            d = datetime.now().strftime("%d %B %Y")
            self.speak(f"Today is {d}.")
            return
        elif "call" in user_low:
            self.speak("Calling feature ready — just say the name.")
            return
        elif "play music" in user_low:
            self.speak("Playing your favorite tracks.")
            return
        elif "lock phone" in user_low:
            self.speak("Phone locked as you commanded, Boss.")
            return

        # --- 🗣️ FREE CONVERSATION VIA YOUR API ---
        self.get_ai_response(user_text)

    # ==================================================
    # 🔌 API CONNECTION — REAL CONVERSATION
    # ==================================================
    def get_ai_response(self, message):
        global CONVERSATION_HISTORY
        # Add message to memory
        CONVERSATION_HISTORY.append({"role": "user", "content": message})

        try:
            # Send to your AI API
            headers = {
                "Authorization": f"Bearer {YOUR_AI_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "messages": CONVERSATION_HISTORY,
                "model": "your-chat-model"
            }
            response = requests.post(YOUR_AI_API_URL, headers=headers, json=payload, timeout=15)
            data = response.json()
            reply = data['choices'][0]['message']['content'].strip()

            # Save reply to memory
            CONVERSATION_HISTORY.append({"role": "assistant", "content": reply})
            self.speak(reply)

        except Exception as e:
            # Fallback smart replies if API fails
            fallback = [
                f"I hear you {OWNER_NAME}. Tell me more about that.",
                f"Interesting point, {OWNER_NAME}. What else?",
                f"I'm listening, Boss. Go on.",
                f"That's cool — I like talking with you {OWNER_NAME}."
            ]
            self.speak(random.choice(fallback))

    def reset_status(self):
        self.status.text = f"🟢 ONLINE | {✞♡$!R_JID✊🏾}"
        self.status.color = (0.63, 0.82, 1, 1)

# ==================================================
# 🚀 RUN APP
# ==================================================
class REZApp(App):
    def build(self):
        return REZInterface()

if __name__ == "__main__":
    REZApp().run()
