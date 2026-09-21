class ActionPlanner:
    """
    JARVIS Infinity Action Planner

    Converts a recommended next action into a practical
    step-by-step execution plan.
    """

    def __init__(self):
        self.plans = {
            "Complete Voice Control": [
                "Test microphone input",
                "Test voice recognition",
                "Test application control",
                "Test voice-to-intent integration",
                "Verify successful command execution",
            ],

            "Complete Vision Integration": [
                "Initialize webcam",
                "Test face detection",
                "Test visual input processing",
                "Connect vision results to JARVIS context",
                "Verify visual understanding",
            ],

            "Review Coding Agent": [
                "Test Python code generation",
                "Test Java code generation",
                "Test JavaScript code generation",
                "Test HTML and CSS generation",
                "Test debugging and verification",
            ],

            "Review Project Modules": [
                "Check all JARVIS modules",
                "Identify incomplete components",
                "Test module communication",
                "Fix critical issues",
                "Run complete system verification",
            ],

            "Prepare Project Demo": [
                "Verify dashboard",
                "Verify voice control",
                "Verify computer control",
                "Verify Next-Best-Action engine",
                "Run complete JARVIS demonstration",
            ],
        }

    def create_plan(self, action):
        """Create a step-by-step plan for the selected action."""

        action = (action or "").strip()

        if action in self.plans:
            steps = self.plans[action]
        else:
            steps = [
                f"Analyze the task: {action}",
                "Identify required components",
                "Execute the required steps",
                "Verify the result",
            ]

        return {
            "action": action,
            "steps": steps,
            "total_steps": len(steps),
        }

    def format_plan(self, plan):
        """Format the plan as a JARVIS response."""

        lines = [
            "📋 ACTION PLAN",
            "",
            f"Goal: {plan['action']}",
            f"Steps: {plan['total_steps']}",
            "",
        ]

        for index, step in enumerate(plan["steps"], start=1):
            lines.append(f"{index}. {step}")

        lines.extend([
            "",
            "Would you like me to start this plan?"
        ])

        return "\n".join(lines)


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    planner = ActionPlanner()

    plan = planner.create_plan("Complete Voice Control")

    print(planner.format_plan(plan))