from agent.goal_engine import GoalEngine
from agent.planner import DynamicPlanner
from agent.tool_registry import ToolRegistry
from agent.safety_engine import SafetyEngine
from agent.executor import AgentExecutor
from agent.verifier import AgentVerifier


class UniversalAgent:
    """
    JARVIS INFINITY Universal Agent

    Pipeline:

    USER GOAL
        ↓
    GOAL ENGINE
        ↓
    DYNAMIC PLANNER
        ↓
    TOOL REGISTRY
        ↓
    SAFETY ENGINE
        ↓
    EXECUTOR
        ↓
    VERIFIER
        ↓
    FINAL RESULT
    """

    PROTECTED_ACTIONS = {
        "OPEN_APPLICATION",
        "COMPUTER_INTERACTION",
        "PERFORM_COMPUTER_ACTION",
        "PERFORM_ACTION",
        "APPLY_SAFE_FIX",
        "MODIFY_FILE",
        "WRITE_FILE",
        "CREATE_FILE",
        "DELETE_FILE",
        "SEND_EMAIL",
        "SEND_MESSAGE",
        "INSTALL_SOFTWARE",
        "EXECUTE_EXTERNAL_COMMAND",
        "SYSTEM_CHANGE",
    }

    def __init__(self):
        self.goal_engine = GoalEngine()
        self.planner = DynamicPlanner()
        self.tool_registry = ToolRegistry()
        self.safety_engine = SafetyEngine()
        self.executor = AgentExecutor(self.tool_registry)
        self.verifier = AgentVerifier()

    # ==============================================================
    # MAIN PIPELINE
    # ==============================================================

    def process_goal(self, user_input, permission_granted=False):

        if not user_input or not str(user_input).strip():
            return {
                "success": False,
                "stage": "INPUT",
                "message": "No user goal was provided.",
            }

        user_input = str(user_input).strip()

        # ----------------------------------------------------------
        # 1. UNDERSTAND GOAL
        # ----------------------------------------------------------

        goal = self.goal_engine.understand_goal(user_input)

        if not goal.get("success", False):
            return {
                "success": False,
                "stage": "GOAL_ENGINE",
                "goal": goal,
                "message": "JARVIS could not understand the goal.",
            }

        # ----------------------------------------------------------
        # 2. CREATE PLAN
        # ----------------------------------------------------------

        plan_result = self.planner.create_plan(goal)

        if not plan_result.get("success", False):
            return {
                "success": False,
                "stage": "PLANNER",
                "goal": goal,
                "message": "JARVIS could not create a plan.",
            }

        plan = plan_result.get("plan", [])

        # ----------------------------------------------------------
        # 3. SELECT TOOLS
        # ----------------------------------------------------------

        selected_tools = self.tool_registry.select_tools_for_goal(goal)

        # ----------------------------------------------------------
        # 4. PREPARE PLAN
        # ----------------------------------------------------------

        prepared_plan = self._prepare_plan(
            plan,
            goal,
            selected_tools,
        )

        # ----------------------------------------------------------
        # 5. SAFETY CHECK
        # ----------------------------------------------------------

        safety_result = self.safety_engine.evaluate_plan(
            prepared_plan,
            permission_granted=permission_granted,
        )

        safety_status = self._get_safety_status(safety_result)

        # Permission required
        if safety_status == "PERMISSION_REQUIRED":
            return {
                "success": False,
                "stage": "SAFETY",
                "goal": goal,
                "plan": prepared_plan,
                "tools": selected_tools,
                "safety": safety_result,
                "message": (
                    "JARVIS requires user permission before "
                    "performing one or more actions."
                ),
            }

        # Block unsafe actions
        if safety_status == "BLOCKED":
            return {
                "success": False,
                "stage": "SAFETY",
                "goal": goal,
                "plan": prepared_plan,
                "tools": selected_tools,
                "safety": safety_result,
                "message": (
                    "JARVIS blocked the requested action for safety."
                ),
            }

        # Unknown safety state
        if safety_status not in {
            "APPROVED",
            "SAFE",
            "PASS",
        }:
            return {
                "success": False,
                "stage": "SAFETY",
                "goal": goal,
                "plan": prepared_plan,
                "tools": selected_tools,
                "safety": safety_result,
                "message": (
                    "JARVIS could not establish a safe "
                    "execution state."
                ),
            }

        # ----------------------------------------------------------
        # 6. EXECUTE
        # ----------------------------------------------------------

        try:
            execution_result = self.executor.execute_plan(
                prepared_plan,
                permission_granted=permission_granted,
            )

        except TypeError:
            # Compatibility with older Executor versions.
            execution_result = self.executor.execute_plan(
                prepared_plan
            )

        # ----------------------------------------------------------
        # 7. VERIFY
        # ----------------------------------------------------------

        verification_input = execution_result

        if isinstance(execution_result, dict):
            verification_input = execution_result.get(
                "results",
                execution_result.get(
                    "execution_results",
                    execution_result,
                ),
            )

        verification_result = self.verifier.verify_plan(
            verification_input
        )

        verification_success = self._verification_success(
            verification_result
        )

        # ----------------------------------------------------------
        # 8. FINAL RESULT
        # ----------------------------------------------------------

        return {
            "success": verification_success,
            "stage": (
                "COMPLETE"
                if verification_success
                else "VERIFICATION"
            ),
            "goal": goal,
            "plan": prepared_plan,
            "tools": selected_tools,
            "safety": safety_result,
            "execution": execution_result,
            "verification": verification_result,
            "message": (
                "JARVIS completed and verified the task."
                if verification_success
                else
                "JARVIS executed the plan, but verification "
                "was not successful."
            ),
        }

    # ==============================================================
    # PLAN PREPARATION
    # ==============================================================

    def _prepare_plan(self, plan, goal, selected_tools):

        prepared_plan = []

        if not isinstance(plan, list):
            return prepared_plan

        for step in plan:

            if not isinstance(step, dict):
                continue

            new_step = dict(step)

            action = str(
                new_step.get("action", "")
            ).strip().upper()

            description = str(
                new_step.get("description", "")
            )

            # ------------------------------------------------------
            # Detect application
            # ------------------------------------------------------

            application = self._extract_application_name(
                goal.get(
                    "normalized_goal",
                    "",
                )
            )

            if application:
                new_step["application"] = application

            # ------------------------------------------------------
            # Attach selected tools
            # ------------------------------------------------------

            if selected_tools:
                new_step["selected_tools"] = selected_tools

            # ------------------------------------------------------
            # Permission
            # ------------------------------------------------------

            if action in self.PROTECTED_ACTIONS:
                new_step["requires_permission"] = True
            else:
                new_step["requires_permission"] = False

            # ------------------------------------------------------
            # Goal context
            # ------------------------------------------------------

            new_step["goal_type"] = goal.get(
                "goal_type",
                "GENERAL",
            )

            new_step["goal_priority"] = goal.get(
                "priority",
                "MEDIUM",
            )

            new_step["goal_description"] = description

            prepared_plan.append(new_step)

        return prepared_plan

    # ==============================================================
    # APPLICATION EXTRACTION
    # ==============================================================

    def _extract_application_name(self, text):

        if not text:
            return None

        text_lower = str(text).lower()

        aliases = [
            ("visual studio code", "vscode"),
            ("vs code", "vscode"),
            ("vscode", "vscode"),
            ("code editor", "vscode"),

            ("notepad", "notepad"),
            ("note pad", "notepad"),

            ("calculator", "calculator"),
            ("calc", "calculator"),

            ("google chrome", "chrome"),
            ("chrome", "chrome"),

            ("spotify", "spotify"),

            ("microsoft word", "word"),
            ("word", "word"),

            ("microsoft powerpoint", "powerpoint"),
            ("power point", "powerpoint"),
            ("powerpoint", "powerpoint"),

            ("microsoft excel", "excel"),
            ("excel", "excel"),

            ("file explorer", "explorer"),
            ("windows explorer", "explorer"),
            ("explorer", "explorer"),

            ("command prompt", "cmd"),
            ("cmd", "cmd"),

            ("powershell", "powershell"),
        ]

        for phrase, application in aliases:

            if phrase in text_lower:
                return application

        return None

    # ==============================================================
    # SAFETY STATUS
    # ==============================================================

    def _get_safety_status(self, safety_result):

        if not isinstance(safety_result, dict):
            return "UNKNOWN"

        for key in (
            "status",
            "decision",
            "result",
        ):

            value = safety_result.get(key)

            if value:
                return str(value).strip().upper()

        return "UNKNOWN"

    # ==============================================================
    # VERIFICATION
    # ==============================================================

    def _verification_success(self, verification_result):

        if not isinstance(verification_result, dict):
            return False

        # AgentVerifier normally uses overall_status.
        status = verification_result.get(
            "overall_status"
        )

        if status:
            status = str(status).strip().upper()

        # Compatibility with other verifier versions.
        if status != "SUCCESS":

            status = str(
                verification_result.get(
                    "status",
                    "",
                )
            ).strip().upper()

        if status == "SUCCESS":
            return True

        if verification_result.get("success") is True:
            return True

        if verification_result.get("verified") is True:
            return True

        return False


# ==================================================================
# TEST PROGRAM
# ==================================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("JARVIS INFINITY — UNIVERSAL AGENT TEST")
    print("=" * 70)

    agent = UniversalAgent()

    test_goals = [
        "Create a study plan for my computer networks exam.",
        "Research the best technologies for building an AI assistant.",
        "Open VS Code.",
    ]

    for number, test_goal in enumerate(
        test_goals,
        start=1,
    ):

        print()
        print("-" * 70)
        print(f"TEST {number}")
        print("-" * 70)

        print()
        print("USER GOAL:")
        print(test_goal)

        result = agent.process_goal(
            test_goal,
            permission_granted=False,
        )

        print()
        print("STAGE:")
        print(result.get("stage"))

        print()
        print("MESSAGE:")
        print(result.get("message"))

        print()
        print("SUCCESS:")
        print(result.get("success"))

        print()
        print("SAFETY:")

        safety = result.get("safety")

        if isinstance(safety, dict):

            print(
                safety.get(
                    "status",
                    safety.get(
                        "decision",
                        "UNKNOWN",
                    ),
                )
            )

        else:
            print("UNKNOWN")

    print()
    print("=" * 70)
    print("UNIVERSAL AGENT TEST COMPLETE")
    print("=" * 70)
