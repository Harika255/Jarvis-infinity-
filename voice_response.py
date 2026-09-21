import pyttsx3
import queue
import threading
import time


class JarvisSpeaker:
    """Reliable Windows TTS for repeated JARVIS responses."""

    def __init__(self):
        self.rate = 170
        self.volume = 1.0

        self.speech_queue = queue.Queue()
        self.running = True

        self.worker = threading.Thread(
            target=self._speech_loop,
            daemon=True,
            name="JARVIS-TTS"
        )

        self.worker.start()

    def _create_engine(self):
        """Create a fresh Windows speech engine."""
        try:
            engine = pyttsx3.init("sapi5")

            engine.setProperty("rate", self.rate)
            engine.setProperty("volume", self.volume)

            voices = engine.getProperty("voices")

            if voices:
                engine.setProperty("voice", voices[0].id)

            return engine

        except Exception as error:
            print("❌ Could not create TTS engine:", repr(error))
            return None

    def _speak_once(self, text):
        """Speak one response using a fresh engine."""
        engine = None

        try:
            engine = self._create_engine()

            if engine is None:
                return

            print("🔊 JARVIS:", text)

            engine.say(str(text))
            engine.runAndWait()

        except Exception as error:
            print("❌ TTS playback error:", repr(error))

        finally:
            if engine is not None:
                try:
                    engine.stop()
                except Exception:
                    pass

            # Give Windows SAPI a tiny moment to release the engine.
            time.sleep(0.15)

    def _speech_loop(self):
        """Continuously process every speech request."""
        print("✅ JARVIS voice worker started")

        while self.running:

            try:
                text = self.speech_queue.get()

                if text is None:
                    self.speech_queue.task_done()
                    break

                self._speak_once(text)

                self.speech_queue.task_done()

            except Exception as error:
                print("❌ Voice worker error:", repr(error))

                try:
                    self.speech_queue.task_done()
                except Exception:
                    pass

        print("🛑 JARVIS voice worker stopped")

    def speak(self, text):
        """Add every response to the speech queue."""
        if not text:
            return

        if not self.running:
            return

        self.speech_queue.put(str(text))

    def stop(self):
        """Safely stop the speech worker."""
        if not self.running:
            return

        self.running = False
        self.speech_queue.put(None)