class SafetyEngine:
    """
    JARVIS Infinity Safety + Permission Engine

    Classifies actions by risk and determines whether
    user permission is required before execution.
    """

    def __init__(self):
        self.risk_levels = {
            "LOW": 1,
            "MEDIUM": 2,
            "HIGH": 3,
        }

        self.high_risk_keywords = [
            "delete",
            "remove",
            "shutdown",
            "restart",
            "format",
            "install",
            "uninstall",
            "send email",
            "send message",
            "publish",
            "upload",
            "download",
            "modify system",
        ]

        self.medium_risk_keywords = [
            "open",
            "launch",
            "run",
            "execute",
            "change",
            "edit",
            "create file",
            "write file",
        ]

    def assess_action(self, action):
        """
        Determine the risk level of an action.
        """

        action = (action or "").strip()
        lower = action.lower()

        # High-risk actions
        for keyword in self.high_risk_keywords:
            if keyword in lower:
                return {
                    "action": action,
                    "risk": "HIGH",
                    "permission_required": True,
                    "reason": f"Action contains high-risk operation: {keyword}",
                }

        # Medium-risk actions
        for keyword in self.medium_risk_keywords:
            if keyword in lower:
                return {
                    "action": action,
                    "risk": "MEDIUM",
                    "permission_required": True,
                    "reason": f"Action may modify or interact with the computer: {keyword}",
                }

        # Safe actions
        return {
            "action": action,
            "risk": "LOW",
            "permission_required": False,
            "reason": "Action is considered low risk.",
        }

    def request_permission(self, assessment):
        """
        Create a permission request for actions requiring approval.
        """

        if not assessment["permission_required"]:
            return {
                "approved": True,
                "message": "Permission is not required for this action.",
            }

        return {
            "approved": False,
            "message": (
                f"⚠️ PERMISSION REQUIRED\n\n"
                f"Action: {assessment['action']}\n"
                f"Risk Level: {assessment['risk']}\n"
                f"Reason: {assessment['reason']}\n\n"
                f"JARVIS is waiting for your approval."
            ),
        }

    def format_assessment(self, assessment):
        """
        Format safety information for the dashboard.
        """

        return (
            "🛡️ SAFETY CHECK\n\n"
            f"Action: {assessment['action']}\n"
            f"Risk: {assessment['risk']}\n"
            f"Permission Required: "
            f"{'YES' if assessment['permission_required'] else 'NO'}\n"
            f"Reason: {assessment['reason']}"
        )


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    safety = SafetyEngine()

    test_actions = [
        "Open Notepad",
        "Create a project file",
        "Delete an old file",
    ]

    for action in test_actions:

        assessment = safety.assess_action(action)

        print(safety.format_assessment(assessment))
        print()

        permission = safety.request_permission(assessment)

        print(permission["message"])
        print("=" * 50)