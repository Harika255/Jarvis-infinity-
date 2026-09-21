class SituationAwareness:

    def analyze(self, screen_text):

        text = (screen_text or "").lower()

        situation = {
            "application": "Unknown",
            "activity": "Unknown",
            "project": None,
            "recommendation": None,
            "confidence": 0.0
        }

        # Detect VS Code
        if (
            "visual studio code" in text
            or "explorer" in text
            or "terminal" in text
            or "jarvis-infinity" in text
        ):
            situation["application"] = "Visual Studio Code"
            situation["confidence"] = 0.85

        # Detect JARVIS project
        if "jarvis-infinity" in text:
            situation["project"] = "JARVIS Infinity"
            situation["activity"] = "Software development"
            situation["recommendation"] = (
                "Continue developing and testing the JARVIS project."
            )

        # Detect Python development
        if (
            ".py" in text
            or "python" in text
            or "venv" in text
        ):
            situation["activity"] = "Python development"

        return situation


if __name__ == "__main__":

    sample_screen = """
    jarvis-infinity
    Visual Studio Code
    screen_capture.py
    python.exe
    venv
    """

    engine = SituationAwareness()

    result = engine.analyze(sample_screen)

    print("\nJARVIS SITUATION AWARENESS")
    print("--------------------------")

    for key, value in result.items():
        print(f"{key}: {value}")