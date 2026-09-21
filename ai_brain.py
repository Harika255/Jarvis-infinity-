import csv
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


class JarvisBrain:

    def __init__(self):

        # ======================================================
        # LOAD DATASET
        # ======================================================

        base_dir = os.path.dirname(os.path.abspath(__file__))

        dataset_path = os.path.join(
            base_dir,
            "dataset",
            "jarvis_intents.csv"
        )

        self.training_sentences = []
        self.training_labels = []

        try:

            with open(
                dataset_path,
                "r",
                encoding="utf-8"
            ) as file:

                reader = csv.DictReader(file)

                for row in reader:

                    command = row["command"].strip()
                    intent = row["intent"].strip()

                    if command and intent:

                        self.training_sentences.append(command)
                        self.training_labels.append(intent)

        except FileNotFoundError:

            print("ERROR: Dataset file not found.")
            print("Expected location:")
            print(dataset_path)

        if len(self.training_sentences) == 0:

            raise ValueError(
                "Dataset is empty. "
                "Please check dataset/jarvis_intents.csv"
            )

        print("JARVIS DATASET LOADED")
        print("Samples:", len(self.training_sentences))
        print("Intents:", len(set(self.training_labels)))

        # ======================================================
        # TRAIN ML MODEL
        # ======================================================

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2)
        )

        X = self.vectorizer.fit_transform(
            self.training_sentences
        )

        self.model = LogisticRegression(
            max_iter=1000
        )

        self.model.fit(
            X,
            self.training_labels
        )

        # ======================================================
        # JARVIS CONTEXT MEMORY
        # ======================================================

        self.context = {

            "last_intent": None,
            "last_command": None,

            "project": None,
            "deadline": None,

            "completed_tasks": [],
            "pending_tasks": [],

            "last_recommendation": None,

            "user_approved_actions": 0,
            "user_denied_actions": 0
        }

        # ======================================================
        # PROJECT STATE
        # ======================================================

        self.project_state = {

            "dashboard": "COMPLETED",
            "dataset": "COMPLETED",
            "ai_brain": "COMPLETED",
            "intent_prediction": "COMPLETED",
            "planning": "COMPLETED",
            "safety_engine": "COMPLETED",
            "computer_control": "COMPLETED",

            "voice": "PENDING",
            "vision": "PENDING",
            "ocr": "PENDING",
            "integration_testing": "PENDING",
            "final_demo": "PENDING"
        }

    # ==========================================================
    # INTENT PREDICTION
    # ==========================================================

    def predict_intent(self, command):
        """Predict intent using clear command rules first, then ML."""

        command_lower = command.lower().strip()

        # ======================================================
        # HIGH-CONFIDENCE APPLICATION COMMANDS
        # ======================================================
        # These are deterministic commands, so do not let the
        # ML model reject an obvious request because of a low
        # probability score.
        if (
            ("open" in command_lower or
             "launch" in command_lower or
             "start" in command_lower)
            and (
                "vs code" in command_lower
                or "visual studio code" in command_lower
                or "vscode" in command_lower
                or "code editor" in command_lower
            )
        ):
            return "OPEN_APPLICATION", 0.99

        # ======================================================
        # NORMAL ML INTENT PREDICTION
        # ======================================================
        X = self.vectorizer.transform([command])

        prediction = self.model.predict(X)[0]

        probabilities = self.model.predict_proba(X)[0]

        confidence = max(probabilities)

        # Keep the threshold low enough for natural voice
        # variations, while still rejecting very uncertain input.
        if confidence < 0.30:
            prediction = "UNKNOWN"

        return prediction, confidence

    # ==========================================================
    # UPDATE CONTEXT
    # ==========================================================

    def update_context(self, command, intent):

        command_lower = command.lower()

        self.context["last_command"] = command
        self.context["last_intent"] = intent

        # Project detection

        if "project" in command_lower:

            self.context["project"] = "Current Project"

        # Deadline detection

        if "tomorrow" in command_lower:

            self.context["deadline"] = "Tomorrow"

        elif "today" in command_lower:

            self.context["deadline"] = "Today"

    # ==========================================================
    # CREATE PLAN
    # ==========================================================

    def create_plan(self, intent):

        if intent == "PROJECT_REVIEW":

            return [

                "Understand project requirements",
                "Check completed modules",
                "Identify incomplete sections",
                "Prepare important points",
                "Review final demonstration"

            ]

        elif intent == "CREATE_PLAN":

            return [

                "Understand the objective",
                "Break the task into smaller steps",
                "Prioritize important tasks",
                "Execute each step",
                "Verify the final result"

            ]

        elif intent == "TASK_STATUS":

            return [

                "Check pending tasks",
                "Prioritize unfinished tasks",
                "Complete high-priority tasks",
                "Verify progress"

            ]

        return []

    # ==========================================================
    # SAFETY CHECK
    # ==========================================================

    def safety_check(self, intent):

        low_risk = [

            "GREETING",
            "GENERAL_QUESTION",
            "TASK_STATUS",
            "CREATE_PLAN",
            "PROJECT_REVIEW"

        ]

        medium_risk = [

            "OPEN_APPLICATION"

        ]

        if intent in low_risk:

            return {

                "level": "LOW",
                "permission_required": False

            }

        elif intent in medium_risk:

            return {

                "level": "MEDIUM",
                "permission_required": True

            }

        return {

            "level": "HIGH",
            "permission_required": True

        }

    # ==========================================================
    # SITUATION AWARENESS ENGINE
    # ==========================================================

    def analyze_situation(self):

        pending = []

        completed = []

        # Separate completed and pending tasks

        for task, status in self.project_state.items():

            if status == "COMPLETED":

                completed.append(task)

            else:

                pending.append(task)

        # Determine highest priority

        if self.context["deadline"] in [
            "Today",
            "Tomorrow"
        ]:

            priority = "HIGH"

        elif len(pending) > 0:

            priority = "MEDIUM"

        else:

            priority = "LOW"

        # Determine recommended next action

        if self.project_state["voice"] == "PENDING":

            recommendation = "Complete the Voice Control module"

            reason = (
                "Voice is a major multimodal component "
                "and is currently incomplete."
            )

        elif self.project_state["vision"] == "PENDING":

            recommendation = "Implement Webcam Vision"

            reason = (
                "Vision is required to make JARVIS "
                "multimodal."
            )

        elif self.project_state["ocr"] == "PENDING":

            recommendation = "Implement OCR"

            reason = (
                "OCR will allow JARVIS to understand "
                "text from visual input."
            )

        elif self.project_state["integration_testing"] == "PENDING":

            recommendation = "Run Integration Testing"

            reason = (
                "The major modules are available and "
                "should now be tested together."
            )

        elif self.project_state["final_demo"] == "PENDING":

            recommendation = "Prepare Final Demonstration"

            reason = (
                "The core system is ready for final "
                "demonstration."
            )

        else:

            recommendation = "All major tasks are complete"

            reason = (
                "No pending high-priority development "
                "tasks were detected."
            )

        # Save recommendation

        self.context["last_recommendation"] = recommendation

        return {

            "priority": priority,

            "completed_tasks": completed,

            "pending_tasks": pending,

            "recommended_action": recommendation,

            "reason": reason,

            "deadline": self.context["deadline"],

            "project": self.context["project"]

        }

    # ==========================================================
    # WHAT SHOULD I DO NEXT?
    # ==========================================================

    def what_should_i_do_next(self):

        situation = self.analyze_situation()

        return {

            "recommendation":
                situation["recommended_action"],

            "reason":
                situation["reason"],

            "priority":
                situation["priority"],

            "deadline":
                situation["deadline"]

        }

    # ==========================================================
    # COMPLETE TASK
    # ==========================================================

    def complete_task(self, task):

        task_key = task.lower().replace(" ", "_")

        if task_key in self.project_state:

            self.project_state[task_key] = "COMPLETED"

            if task_key not in self.context["completed_tasks"]:

                self.context["completed_tasks"].append(
                    task_key
                )

            return True

        return False

    # ==========================================================
    # MAIN PROCESS
    # ==========================================================

    def process(self, command):

        intent, confidence = self.predict_intent(
            command
        )

        self.update_context(
            command,
            intent
        )

        safety = self.safety_check(
            intent
        )

        plan = self.create_plan(
            intent
        )

        situation = self.analyze_situation()

        return {

            "command": command,

            "intent": intent,

            "confidence": confidence,

            "context": self.context.copy(),

            "safety": safety,

            "plan": plan,

            "situation": situation

        }