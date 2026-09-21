class SafetyEngine:
    """
    JARVIS Infinity Safety Engine

    Responsible for:
    - Risk classification
    - Permission handling
    - Blocking dangerous actions
    - Allowing safe internal agent operations
    """

    RISK_ORDER = {
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3,
        "CRITICAL": 4,
        "BLOCKED": 5,
    }

    # Actions that are internal reasoning/control operations.
    # These do NOT require user permission.
    INTERNAL_ACTIONS = {
        "UNDERSTAND",
        "GATHER_CONTEXT",
        "DEFINE_OUTPUT",
        "IDENTIFY_RESOURCES",
        "IDENTIFY_STUDY_SCOPE",
        "PRIORITIZE_TOPICS",
        "CREATE_STUDY_SCHEDULE",
        "PREPARE_MATERIAL",
        "INSPECT_CODE",
        "ANALYZE_ERROR",
        "EXPLAIN_ERROR",
        "RUN_CODE",
        "DEFINE_RESEARCH_QUESTION",
        "SEARCH_INFORMATION",
        "COMPARE_RESULTS",
        "EVALUATE_INFORMATION",
        "SUMMARIZE_FINDINGS",
        "IDENTIFY_TARGET",
        "SELECT_TOOL",
        "BREAK_INTO_TASKS",
        "ORDER_TASKS",
        "QUALITY_CHECK",
        "SAFETY_CHECK",
        "EXECUTE",
        "VERIFY",
        "REPORT",
        "ANALYZE",
        "PLAN",
        "REASON",
        "CONTEXT",
    }

    # Actions that can affect the user's computer,
    # files, communication, or external systems.
    PERMISSION_ACTIONS = {
        "OPEN_APPLICATION",
        "COMPUTER_INTERACTION",
        "SEND_EMAIL",
        "SEND_MESSAGE",
        "DELETE_FILE",
        "MODIFY_FILE",
        "INSTALL_SOFTWARE",
        "EXECUTE_EXTERNAL_COMMAND",
        "WRITE_FILE",
        "CREATE_FILE",
        "DELETE_APPLICATION",
        "SYSTEM_CHANGE",
    }

    # Actions that JARVIS must never perform.
    BLOCKED_ACTIONS = {
        "DELETE_SYSTEM_FILES",
        "FORMAT_DRIVE",
        "DISABLE_SECURITY",
        "STEAL_CREDENTIALS",
        "BYPASS_SECURITY",
        "DISABLE_ANTIVIRUS",
        "REMOVE_SECURITY_CONTROLS",
        "ACCESS_PRIVATE_CREDENTIALS",
    }

    def __init__(self):
        self.last_decision = None

    def normalize_action(self, action):
        if action is None:
            return ""

        return str(action).strip().upper().replace(" ", "_")

    def normalize_risk(self, risk_level):
        if risk_level is None:
            return "LOW"

        risk = str(risk_level).strip().upper()

        if risk not in self.RISK_ORDER:
            return "LOW"

        return risk

    def requires_permission(self, action, risk_level="LOW"):
        """
        Determine whether an action requires user permission.
        """

        action = self.normalize_action(action)
        risk = self.normalize_risk(risk_level)

        # Internal JARVIS operations never require permission.
        if action in self.INTERNAL_ACTIONS:
            return False

        # Explicit external actions require permission.
        if action in self.PERMISSION_ACTIONS:
            return True

        # High/critical unknown actions require permission.
        if risk in {"HIGH", "CRITICAL"}:
            return True

        return False

    def evaluate_action(
        self,
        action,
        risk_level="LOW",
        permission_granted=False
    ):
        """
        Evaluate a single action.

        Returns:
            APPROVED
            CAUTION
            PERMISSION_REQUIRED
            BLOCKED
        """

        action = self.normalize_action(action)
        risk = self.normalize_risk(risk_level)

        # Empty action is invalid.
        if not action:
            result = {
                "status": "BLOCKED",
                "action": action,
                "risk": "BLOCKED",
                "requires_permission": False,
                "message": "No valid action was provided."
            }

            self.last_decision = result
            return result

        # Dangerous actions are always blocked.
        if action in self.BLOCKED_ACTIONS:
            result = {
                "status": "BLOCKED",
                "action": action,
                "risk": "BLOCKED",
                "requires_permission": False,
                "message": (
                    f"Action '{action}' is blocked by the JARVIS "
                    "safety policy."
                )
            }

            self.last_decision = result
            return result

        # Internal reasoning/control actions are automatically safe.
        if action in self.INTERNAL_ACTIONS:
            result = {
                "status": "APPROVED",
                "action": action,
                "risk": "LOW",
                "requires_permission": False,
                "message": (
                    f"Internal action '{action}' approved "
                    "automatically."
                )
            }

            self.last_decision = result
            return result

        # External actions require explicit permission.
        if action in self.PERMISSION_ACTIONS:

            if not permission_granted:
                result = {
                    "status": "PERMISSION_REQUIRED",
                    "action": action,
                    "risk": risk,
                    "requires_permission": True,
                    "message": (
                        f"JARVIS requires user permission "
                        f"before performing '{action}'."
                    )
                }

                self.last_decision = result
                return result

            result = {
                "status": "APPROVED",
                "action": action,
                "risk": risk,
                "requires_permission": True,
                "message": (
                    f"Permission granted. Action '{action}' "
                    "is approved."
                )
            }

            self.last_decision = result
            return result

        # Medium-risk unknown actions.
        if risk == "MEDIUM":

            if not permission_granted:
                result = {
                    "status": "PERMISSION_REQUIRED",
                    "action": action,
                    "risk": risk,
                    "requires_permission": True,
                    "message": (
                        f"Action '{action}' has medium risk "
                        "and requires user permission."
                    )
                }

                self.last_decision = result
                return result

            result = {
                "status": "APPROVED",
                "action": action,
                "risk": risk,
                "requires_permission": True,
                "message": (
                    f"Permission granted. Medium-risk "
                    f"action '{action}' approved."
                )
            }

            self.last_decision = result
            return result

        # Low-risk unknown actions can proceed.
        result = {
            "status": "APPROVED",
            "action": action,
            "risk": "LOW",
            "requires_permission": False,
            "message": (
                f"Low-risk action '{action}' approved."
            )
        }

        self.last_decision = result
        return result

    def evaluate_plan(
        self,
        plan,
        permission_granted=False
    ):
        """
        Evaluate an entire JARVIS plan.

        The plan can contain dictionaries like:

        {
            "action": "OPEN_APPLICATION",
            "risk": "MEDIUM"
        }

        Returns the first blocked or permission-required
        action, otherwise APPROVED.
        """

        if not plan:
            result = {
                "status": "APPROVED",
                "requires_permission": False,
                "message": "Empty plan is safe."
            }

            self.last_decision = result
            return result

        decisions = []

        for step in plan:

            if isinstance(step, dict):
                action = (
                    step.get("action")
                    or step.get("name")
                    or step.get("stage")
                    or ""
                )

                risk = (
                    step.get("risk")
                    or step.get("risk_level")
                    or "LOW"
                )

            else:
                action = str(step)
                risk = "LOW"

            decision = self.evaluate_action(
                action,
                risk,
                permission_granted
            )

            decisions.append(decision)

            # Dangerous action → stop immediately.
            if decision["status"] == "BLOCKED":
                result = {
                    "status": "BLOCKED",
                    "requires_permission": False,
                    "message": decision["message"],
                    "decisions": decisions
                }

                self.last_decision = result
                return result

            # External action without permission → stop.
            if decision["status"] == "PERMISSION_REQUIRED":
                result = {
                    "status": "PERMISSION_REQUIRED",
                    "requires_permission": True,
                    "message": decision["message"],
                    "action": decision["action"],
                    "risk": decision["risk"],
                    "decisions": decisions
                }

                self.last_decision = result
                return result

        result = {
            "status": "APPROVED",
            "requires_permission": False,
            "message": "All plan steps passed the safety check.",
            "decisions": decisions
        }

        self.last_decision = result
        return result


# Compatibility alias
JarvisSafetyEngine = SafetyEngine


if __name__ == "__main__":

    print("=" * 70)
    print("JARVIS SAFETY ENGINE TEST")
    print("=" * 70)

    engine = SafetyEngine()

    print("\nTEST 1 — INTERNAL ACTION")
    result = engine.evaluate_action(
        "SAFETY_CHECK",
        "HIGH"
    )
    print("Status:", result["status"])
    print("Message:", result["message"])

    print("\nTEST 2 — STUDY ACTION")
    result = engine.evaluate_action(
        "CREATE_STUDY_SCHEDULE",
        "LOW"
    )
    print("Status:", result["status"])
    print("Message:", result["message"])

    print("\nTEST 3 — OPEN APPLICATION WITHOUT PERMISSION")
    result = engine.evaluate_action(
        "OPEN_APPLICATION",
        "MEDIUM",
        permission_granted=False
    )
    print("Status:", result["status"])
    print("Permission Required:", result["requires_permission"])

    print("\nTEST 4 — OPEN APPLICATION WITH PERMISSION")
    result = engine.evaluate_action(
        "OPEN_APPLICATION",
        "MEDIUM",
        permission_granted=True
    )
    print("Status:", result["status"])

    print("\nTEST 5 — BLOCKED ACTION")
    result = engine.evaluate_action(
        "FORMAT_DRIVE",
        "CRITICAL"
    )
    print("Status:", result["status"])

    print("\n" + "=" * 70)

    if (
        engine.evaluate_action("SAFETY_CHECK", "HIGH")["status"]
        == "APPROVED"
        and
        engine.evaluate_action(
            "OPEN_APPLICATION",
            "MEDIUM",
            False
        )["status"]
        == "PERMISSION_REQUIRED"
        and
        engine.evaluate_action(
            "FORMAT_DRIVE",
            "CRITICAL"
        )["status"]
        == "BLOCKED"
    ):
        print("SAFETY ENGINE STATUS:")
        print("PASS")

    print("=" * 70)