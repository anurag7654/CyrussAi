import threading
import webbrowser
import queue
import time
import tempfile
from gtts import gTTS
from playsound import playsound
from ai_handler import get_ai_response
from config import SITES
import speech_recognition as sr
import os

# Speech queue system
speech_queue = queue.Queue()
stop_speech_thread = False


def speak(text):
    """Convert text to speech using gTTS (Google's TTS API)"""
    try:
        # Create a temporary MP3 file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as fp:
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(fp.name)
            fp.close()  # Ensure file is written before playback

            # Play the audio
            playsound(fp.name)

        # Clean up
        os.unlink(fp.name)

    except Exception as e:
        print(f"🔇 Speech Error: {e}")


def speech_worker():
    """Dedicated thread for non-blocking speech"""
    while not stop_speech_thread:
        text = speech_queue.get()
        if text is None:  # Exit signal
            break
        try:
            print(f"\n🔊 Speaking: {text[:100]}...")  # Log first 100 chars
            speak(text)
        except Exception as e:
            print(f"Speech error: {e}")
        finally:
            speech_queue.task_done()


# Start speech thread
speech_thread = threading.Thread(target=speech_worker, daemon=True)
speech_thread.start()


def speak_async(text):
    """Add speech to queue without blocking"""
    if text.strip():  # Only queue non-empty text
        speech_queue.put(text)


def listen():
    """Listen to microphone input with enhanced reliability"""
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 4000
    recognizer.pause_threshold = 0.8

    with sr.Microphone() as source:
        print("\n🔇 Calibrating microphone...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("🎤 Speak now...")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
            command = recognizer.recognize_google(audio)
            print(f"\n🗣️ You said: {command}")
            return command.lower()
        except sr.WaitTimeoutError:
            print("(No speech detected)")
            return ""
        except sr.UnknownValueError:
            print("(Speech not understood)")
            return ""
        except sr.RequestError as e:
            print(f"(API Error: {e})")
            return ""


def handle_command(command):
    """Process user commands"""
    if not command.strip():
        return

    # Website commands
    for name, url in SITES:
        if f"open {name}" in command:
            speak_async(f"Opening {name}")
            webbrowser.open(url)
            return

    # AI queries
    print("\n🤖 Processing with Gemini...")
    try:
        response = get_ai_response(command)
        if response:
            # Clean response for speech
            clean_response = ' '.join(response.split())
            clean_response = clean_response.replace('*', '').replace('_', '')

            print(f"\n💡 Full Response:\n{clean_response}\n")

            # Split long responses into chunks
            max_chunk_size = 500  # Characters per chunk
            if len(clean_response) > max_chunk_size:
                chunks = [clean_response[i:i + max_chunk_size]
                          for i in range(0, len(clean_response), max_chunk_size)]
                for chunk in chunks:
                    speak_async(chunk)
                    time.sleep(0.3)  # Pause between chunks
            else:
                speak_async(clean_response)
        else:
            speak_async("I didn't get a response. Please try again.")
    except Exception as e:
        print(f"Error: {e}")
        speak_async("Sorry, I encountered an error.")


if __name__ == "__main__":
    print("🚀 Starting Cyruss AI...")
    speak_async("Hello, I'm Cyruss AI. How can I help you today?")

    try:
        while True:
            command = listen()
            if command:
                handle_command(command)
            time.sleep(0.3)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        stop_speech_thread = True
        speech_queue.put(None)
        speech_thread.join()
        print("System stopped.")