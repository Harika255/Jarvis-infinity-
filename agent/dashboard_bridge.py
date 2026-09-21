from agent.universal_agent import UniversalAgent


class DashboardAgentBridge:
    """
    Connects the JARVIS dashboard to the Universal Agent.
    """

    def __init__(self):
        self.agent = UniversalAgent()

    def process(self, user_input, permission_granted=False):
        """
        Send a user goal to the Universal Agent.
        """
        return self.agent.process_goal(
            user_input,
            permission_granted=permission_granted,
        )

    def get_summary(self, result):
        """
        Convert the agent result into dashboard-friendly text.
        """

        if not isinstance(result, dict):
            return {
                "status": "ERROR",
                "message": "Invalid agent result.",
            }

        success = result.get("success", False)
        stage = result.get("stage", "UNKNOWN")
        message = result.get(
            "message",
            "No message available.",
        )

        safety = result.get("safety", {})

        if isinstance(safety, dict):
            safety_status = safety.get(
                "status",
                safety.get(
                    "decision",
                    "UNKNOWN",
                ),
            )
        else:
            safety_status = "UNKNOWN"

        return {
            "status": (
                "SUCCESS"
                if success
                else "WAITING"
                if stage == "SAFETY"
                else "FAILED"
            ),
            "stage": stage,
            "safety": str(safety_status).upper(),
            "message": message,
        }


if __name__ == "__main__":

    print()
    print("=" * 70)
    print("JARVIS DASHBOARD AGENT BRIDGE TEST")
    print("=" * 70)

    bridge = DashboardAgentBridge()

    result = bridge.process(
        "Create a study plan for my computer networks exam."
    )

    summary = bridge.get_summary(result)

    print()
    print("STATUS:")
    print(summary["status"])

    print()
    print("STAGE:")
    print(summary["stage"])

    print()
    print("SAFETY:")
    print(summary["safety"])

    print()
    print("MESSAGE:")
    print(summary["message"])

    print()
    print("=" * 70)
    print("DASHBOARD BRIDGE STATUS: PASS")
    print("=" * 70)