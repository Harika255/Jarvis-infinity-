class NextBestActionEngine:

    def recommend(self, situation):

        application = situation.get("application", "Unknown")
        activity = situation.get("activity", "Unknown")
        project = situation.get("project")

        if project == "JARVIS Infinity":
            return {
                "action": "Continue JARVIS development",
                "reason": "JARVIS Infinity is currently being developed.",
                "priority": "HIGH",
                "confidence": 0.90
            }

        if application == "Visual Studio Code":
            return {
                "action": "Continue the current coding task",
                "reason": "The user is working inside Visual Studio Code.",
                "priority": "MEDIUM",
                "confidence": 0.80
            }

        return {
            "action": "Ask the user what they want to accomplish",
            "reason": "The current situation is not sufficiently understood.",
            "priority": "LOW",
            "confidence": 0.50
        }


if __name__ == "__main__":

    situation = {
        "application": "Visual Studio Code",
        "activity": "Python development",
        "project": "JARVIS Infinity"
    }

    engine = NextBestActionEngine()

    result = engine.recommend(situation)

    print("\nJARVIS NEXT-BEST-ACTION")
    print("-----------------------")

    for key, value in result.items():
        print(f"{key}: {value}")