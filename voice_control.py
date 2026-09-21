import speech_recognition as sr


class VoiceController:
    def __init__(self):
        self.recognizer = sr.Recognizer()

        # Working Airdopes 141 microphone
        self.microphone_index = 1

        # Tuned from our successful test
        self.recognizer.energy_threshold = 100
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.5

    def listen(self):
        microphone = None

        try:
            print("\n" + "=" * 50)
            print("🎤 JARVIS VOICE CONTROL")
            print("=" * 50)
            print("🎧 Microphone: Airdopes 141")
            print("🎙️ JARVIS is listening...")
            print("👉 Speak now!")

            microphone = sr.Microphone(
                device_index=self.microphone_index
            )

            with microphone as source:
                audio = self.recognizer.listen(
                    source,
                    timeout=8,
                    phrase_time_limit=8
                )

            print("🧠 Processing your voice...")

            command = self.recognizer.recognize_google(audio)

            print("✅ You said:")
            print(command)
            print("=" * 50)

            return command.strip()

        except sr.WaitTimeoutError:
            print("⏱️ No speech detected.")
            return ""

        except sr.UnknownValueError:
            print("❌ I heard you, but could not understand.")
            return ""

        except sr.RequestError as error:
            print("❌ Speech recognition service error:")
            print(error)
            return ""

        except OSError as error:
            print("❌ Microphone error:")
            print(error)
            return ""

        except Exception as error:
            print("❌ Voice error:")
            print(repr(error))
            return ""

        finally:
            microphone = None