class NextBestActionEngine:
    """
    JARVIS Next-Best-Action Engine

    Recommends the most useful unfinished task based on:
    - goal
    - context
    - project status
    - previous actions
    """

    def __init__(self):
        self.actions = [
            {
                "action": "Complete Voice Control",
                "priority": "HIGH",
                "keywords": [
                    "voice",
                    "speech",
                    "microphone",
                    "voice control",
                    "voice module",
                    "voice command"
                ],
                "reason": "Voice control is an important unfinished multimodal component."
            },
            {
                "action": "Complete Vision Integration",
                "priority": "HIGH",
                "keywords": [
                    "vision",
                    "camera",
                    "webcam",
                    "visual"
                ],
                "reason": "Vision adds multimodal visual understanding to JARVIS."
            },
            {
                "action": "Review Coding Agent",
                "priority": "MEDIUM",
                "keywords": [
                    "coding",
                    "code",
                    "debug",
                    "programming",
                    "coding agent"
                ],
                "reason": "The Coding Agent should be tested and verified before the final demo."
            },
            {
                "action": "Review Project Modules",
                "priority": "MEDIUM",
                "keywords": [
                    "project",
                    "module",
                    "development"
                ],
                "reason": "Reviewing incomplete modules helps move the project toward completion."
            },
            {
                "action": "Prepare Project Demo",
                "priority": "MEDIUM",
                "keywords": [
                    "demo",
                    "presentation",
                    "showcase"
                ],
                "reason": "A working demo is important for demonstrating JARVIS."
            }
        ]

    def recommend(
        self,
        goal="",
        context="",
        project_status="",
        previous_actions=None
    ):
        goal = (goal or "").lower()
        context = (context or "").lower()
        project_status = (project_status or "").lower()
        previous_actions = previous_actions or []

        combined_text = (
            goal + " " +
            context + " " +
            project_status
        )

        candidates = []

        for item in self.actions:
            score = 0

            # Strong match for specific action keywords.
            for keyword in item["keywords"]:
                if keyword in combined_text:
                    score += 5

            # Strongly prioritize explicitly unfinished work.
            unfinished_words = [
                "incomplete",
                "unfinished",
                "pending",
                "not done",
                "missing",
                "remaining",
                "needs work",
                "needs to be completed"
            ]

            if any(word in combined_text for word in unfinished_words):
                for keyword in item["keywords"]:
                    if keyword in combined_text:
                        score += 12

            # High-priority actions get a small bonus.
            if item["priority"] == "HIGH":
                score += 3
            else:
                score += 1

            # Do not recommend something already completed.
            already_done = any(
                item["action"].lower() in action.lower()
                for action in previous_actions
            )

            if already_done:
                score -= 20

            candidates.append({
                "action": item["action"],
                "priority": item["priority"],
                "reason": item["reason"],
                "score": score
            })

        candidates.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        best = candidates[0]

        confidence = min(
            95,
            max(
                60,
                70 + best["score"] * 3
            )
        )

        return {
            "action": best["action"],
            "priority": best["priority"],
            "reason": best["reason"],
            "confidence": confidence,
            "score": best["score"]
        }

    def format_recommendation(self, result):
        return (
            "🎯 NEXT BEST ACTION\n\n"
            f"Action: {result['action']}\n"
            f"Priority: {result['priority']}\n"
            f"Confidence: {result['confidence']}%\n\n"
            f"Reason: {result['reason']}"
        )


if __name__ == "__main__":
    engine = NextBestActionEngine()

    result = engine.recommend(
        goal="Complete my JARVIS project",
        context="The voice control module is incomplete.",
        project_status="Dashboard and coding agent are working.",
        previous_actions=[
            "Complete dashboard",
            "Complete coding agent"
        ]
    )

    print(engine.format_recommendation(result))
