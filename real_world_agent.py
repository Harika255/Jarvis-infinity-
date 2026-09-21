"""Compatibility facade for the new general-purpose JARVIS AI brain.

The desktop app now routes natural language through llm_manager.JarvisLLM.
This class is kept so older scripts/tests importing RealWorldAgent continue to
work without maintaining a hard-coded command dictionary.
"""

from llm_manager import JarvisLLM


class RealWorldAgent:
    def __init__(self):
        self.brain = JarvisLLM()

    def handle(self, text):
        result = self.brain.ask(text)
        if result.get("configured"):
            return result
        return {
            "intent": "GENERAL_AI_NOT_CONFIGURED",
            "message": result.get("message", "General AI is not configured."),
        }
