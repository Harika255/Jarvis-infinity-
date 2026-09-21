class VerificationEngine:
    """
    JARVIS Infinity Verification Engine

    Checks whether an executed action appears to have
    succeeded based on the execution result.
    """

    def __init__(self):
        self.success_keywords = [
            "success",
            "successful",
            "opened",
            "created",
            "completed",
            "done",
            "started",
            "running",
            "generated",
            "saved",
            "connected",
            "approved",
        ]

        self.failure_keywords = [
            "failed",
            "failure",
            "error",
            "unable",
            "couldn't",
            "cannot",
            "not found",
            "denied",
            "blocked",
        ]

    def verify(self, action, execution_result):
        action = (action or "").strip()
        result = (execution_result or "").strip()

        lower_result = result.lower()

        # Check failure indicators first
        for keyword in self.failure_keywords:
            if keyword in lower_result:
                return {
                    "action": action,
                    "status": "FAILED",
                    "verified": False,
                    "confidence": 95,
                    "reason": (
                        "Execution result contains failure "
                        f"indicator: {keyword}"
                    ),
                }

        # Check success indicators
        for keyword in self.success_keywords:
            if keyword in lower_result:
                return {
                    "action": action,
                    "status": "SUCCESS",
                    "verified": True,
                    "confidence": 95,
                    "reason": (
                        "Execution result contains success "
                        f"indicator: {keyword}"
                    ),
                }

        # Unknown result
        return {
            "action": action,
            "status": "UNCERTAIN",
            "verified": False,
            "confidence": 50,
            "reason": (
                "The execution result does not provide "
                "enough evidence to verify success."
            ),
        }

    def format_verification(self, verification):
        status = verification["status"]

        if status == "SUCCESS":
            icon = "✅"
        elif status == "FAILED":
            icon = "❌"
        else:
            icon = "⚠️"

        return (
            f"{icon} VERIFICATION RESULT\n\n"
            f"Action: {verification['action']}\n"
            f"Status: {verification['status']}\n"
            f"Verified: "
            f"{'YES' if verification['verified'] else 'NO'}\n"
            f"Confidence: {verification['confidence']}%\n\n"
            f"Reason: {verification['reason']}"
        )


if __name__ == "__main__":
    verifier = VerificationEngine()

    tests = [
        (
            "Open Notepad",
            "notepad.exe opened successfully."
        ),
        (
            "Open Chrome",
            "Chrome failed to open."
        ),
        (
            "Create project file",
            "The result could not be determined."
        ),
    ]

    for action, result in tests:
        verification = verifier.verify(
            action,
            result
        )

        print(
            verifier.format_verification(
                verification
            )
        )

        print("=" * 60)