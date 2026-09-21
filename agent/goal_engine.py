import re
from datetime import datetime, timedelta


class GoalEngine:
    """
    JARVIS Goal Understanding Engine

    Converts natural-language user requests into a structured
    representation that can be passed to the planning engine.
    """

    def __init__(self):
        self.priority_keywords = {
            "urgent": "CRITICAL",
            "emergency": "CRITICAL",
            "critical": "CRITICAL",
            "asap": "HIGH",
            "immediately": "HIGH",
            "important": "HIGH",
            "soon": "HIGH",
            "deadline": "HIGH",
            "normal": "MEDIUM",
            "later": "LOW",
            "whenever": "LOW",
        }

        self.capability_keywords = {
            "voice": [
                "listen",
                "speak",
                "voice",
                "say",
                "talk",
                "hear",
            ],
            "vision": [
                "camera",
                "see",
                "look",
                "image",
                "photo",
                "screen",
                "visual",
            ],
            "computer_control": [
                "open",
                "launch",
                "close",
                "start",
                "run",
                "click",
                "application",
                "app",
                "software",
            ],
            "coding": [
                "code",
                "coding",
                "program",
                "python",
                "javascript",
                "debug",
                "bug",
                "error",
                "function",
                "developer",
            ],
            "research": [
                "research",
                "find information",
                "search",
                "investigate",
                "compare",
                "analyze",
            ],
            "planning": [
                "plan",
                "planning",
                "schedule",
                "organize",
                "steps",
                "roadmap",
            ],
            "memory": [
                "remember",
                "memorize",
                "save",
                "recall",
                "forget",
            ],
            "document": [
                "document",
                "report",
                "ppt",
                "presentation",
                "slides",
                "pdf",
                "resume",
            ],
            "study": [
                "study",
                "exam",
                "learn",
                "revision",
                "revise",
                "question",
                "subject",
            ],
            "communication": [
                "email",
                "message",
                "send",
                "reply",
                "mail",
            ],
        }

    # ---------------------------------------------------------
    # MAIN METHOD
    # ---------------------------------------------------------

    def understand_goal(self, user_input):
        """
        Convert a natural-language request into a structured goal.
        """

        if not user_input or not user_input.strip():
            return {
                "success": False,
                "error": "No user goal provided.",
            }

        text = user_input.strip()

        deadline = self.extract_deadline(text)
        priority = self.detect_priority(text)
        capabilities = self.detect_capabilities(text)

        goal_type = self.classify_goal(text, capabilities)

        return {
            "success": True,
            "raw_goal": text,
            "normalized_goal": self.normalize_goal(text),
            "goal_type": goal_type,
            "priority": priority,
            "deadline": deadline,
            "required_capabilities": capabilities,
            "constraints": self.extract_constraints(text),
            "created_at": datetime.now().isoformat(),
        }

    # ---------------------------------------------------------
    # GOAL NORMALIZATION
    # ---------------------------------------------------------

    def normalize_goal(self, text):
        """
        Remove unnecessary whitespace and normalize the request.
        """

        text = re.sub(r"\s+", " ", text)
        return text.strip()

    # ---------------------------------------------------------
    # PRIORITY DETECTION
    # ---------------------------------------------------------

    def detect_priority(self, text):
        """
        Determine the urgency of a goal.
        """

        text_lower = text.lower()

        for keyword, priority in self.priority_keywords.items():
            if keyword in text_lower:
                return priority

        # Deadline-related goals are automatically important.
        if self.extract_deadline(text) is not None:
            return "HIGH"

        return "MEDIUM"

    # ---------------------------------------------------------
    # DEADLINE DETECTION
    # ---------------------------------------------------------

    def extract_deadline(self, text):
        """
        Detect common natural-language deadlines.
        """

        text_lower = text.lower()

        now = datetime.now()

        if "today" in text_lower:
            return {
                "type": "DATE",
                "description": "Today",
                "date": now.strftime("%Y-%m-%d"),
            }

        if "tomorrow" in text_lower:
            tomorrow = now + timedelta(days=1)

            return {
                "type": "DATE",
                "description": "Tomorrow",
                "date": tomorrow.strftime("%Y-%m-%d"),
            }

        if "day after tomorrow" in text_lower:
            future = now + timedelta(days=2)

            return {
                "type": "DATE",
                "description": "Day after tomorrow",
                "date": future.strftime("%Y-%m-%d"),
            }

        # "in 3 days"
        match = re.search(
            r"in\s+(\d+)\s+days?",
            text_lower
        )

        if match:
            days = int(match.group(1))
            future = now + timedelta(days=days)

            return {
                "type": "DATE",
                "description": f"In {days} days",
                "date": future.strftime("%Y-%m-%d"),
            }

        # "in 2 hours"
        match = re.search(
            r"in\s+(\d+)\s+hours?",
            text_lower
        )

        if match:
            hours = int(match.group(1))
            future = now + timedelta(hours=hours)

            return {
                "type": "TIME",
                "description": f"In {hours} hours",
                "datetime": future.isoformat(),
            }

        return None

    # ---------------------------------------------------------
    # CAPABILITY DETECTION
    # ---------------------------------------------------------

    def detect_capabilities(self, text):
        """
        Determine which JARVIS capabilities may be required.
        """

        text_lower = text.lower()

        capabilities = []

        for capability, keywords in self.capability_keywords.items():

            for keyword in keywords:

                if keyword in text_lower:
                    capabilities.append(capability)
                    break

        # Every goal requires planning at some level.
        if "planning" not in capabilities:
            capabilities.append("planning")

        return capabilities

    # ---------------------------------------------------------
    # GOAL CLASSIFICATION
    # ---------------------------------------------------------

    def classify_goal(self, text, capabilities):
        """
        Classify the broad type of goal.
        """

        text_lower = text.lower()

        if any(
            word in text_lower
            for word in [
                "study",
                "exam",
                "learn",
                "revision",
            ]
        ):
            return "STUDY"

        if any(
            word in text_lower
            for word in [
                "debug",
                "bug",
                "error",
                "fix code",
                "fix this code",
            ]
        ):
            return "DEBUG"

        if any(
            word in text_lower
            for word in [
                "research",
                "investigate",
                "find information",
            ]
        ):
            return "RESEARCH"

        if any(
            word in text_lower
            for word in [
                "create",
                "make",
                "build",
                "develop",
                "prepare",
            ]
        ):
            return "CREATE"

        if any(
            word in text_lower
            for word in [
                "open",
                "launch",
                "start",
                "run",
            ]
        ):
            return "ACTION"

        if "planning" in capabilities:
            return "PLAN"

        return "GENERAL"

    # ---------------------------------------------------------
    # CONSTRAINT EXTRACTION
    # ---------------------------------------------------------

    def extract_constraints(self, text):
        """
        Extract simple constraints from a natural-language goal.
        """

        text_lower = text.lower()

        constraints = []

        if "without internet" in text_lower:
            constraints.append("OFFLINE_ONLY")

        if "offline" in text_lower:
            constraints.append("OFFLINE_ONLY")

        if "no internet" in text_lower:
            constraints.append("NO_INTERNET")

        if "do not open" in text_lower:
            constraints.append("DO_NOT_OPEN_APPLICATION")

        if "don't open" in text_lower:
            constraints.append("DO_NOT_OPEN_APPLICATION")

        if "ask me first" in text_lower:
            constraints.append("REQUIRE_PERMISSION")

        if "with permission" in text_lower:
            constraints.append("REQUIRE_PERMISSION")

        return constraints


# -------------------------------------------------------------
# SIMPLE TEST
# -------------------------------------------------------------

if __name__ == "__main__":

    engine = GoalEngine()

    test_goals = [
        "I have a project presentation tomorrow and I haven't prepared anything.",
        "Debug my Python program.",
        "Open VS Code.",
        "Help me create a study plan for my CN exam.",
        "Research the best way to organize my project.",
        "Remember that I need to submit my report tomorrow.",
    ]

    print("\n" + "=" * 60)
    print("JARVIS GOAL ENGINE TEST")
    print("=" * 60)

    for goal in test_goals:

        result = engine.understand_goal(goal)

        print("\nUSER GOAL:")
        print(goal)

        print("\nUNDERSTANDING:")
        print(result)

        print("-" * 60)