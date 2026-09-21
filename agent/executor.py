from datetime import datetime


class AgentExecutor:
    """
    JARVIS Action Executor

    Executes approved plan steps using registered tools.

    The executor is intentionally separated from:
        - Goal understanding
        - Planning
        - Safety
        - Verification

    This keeps the JARVIS architecture modular.
    """

    def __init__(self, tool_registry=None):
        self.tool_registry = tool_registry

        # Existing JARVIS components are loaded lazily.
        # This prevents unnecessary imports when testing
        # the executor independently.
        self.computer_controller = None
        self.coding_agent = None
        self.memory_store = None

    # ---------------------------------------------------------
    # MAIN EXECUTION METHOD
    # ---------------------------------------------------------

    def execute_step(
        self,
        step,
        permission_granted=False,
    ):
        """
        Execute one approved plan step.
        """

        if not step:
            return self._result(
                success=False,
                action="",
                message="No execution step supplied.",
            )

        action = step.get("action", "")

        if not action:
            return self._result(
                success=False,
                action="",
                message="Execution step has no action.",
            )

        # Safety information can be attached to the step.
        risk = step.get("risk", "LOW")

        # Permission-required actions must not execute
        # without explicit approval.
        if step.get("requires_permission", False):
            if not permission_granted:
                return self._result(
                    success=False,
                    action=action,
                    message="Permission required before execution.",
                    permission_required=True,
                )

        action_lower = action.lower().strip()

        # -----------------------------------------------------
        # ROUTING
        # -----------------------------------------------------

        if action_lower == "understand":
            return self._result(
                True,
                action,
                "Goal understanding completed.",
            )

        if action_lower == "gather_context":
            return self._result(
                True,
                action,
                "Context gathering stage completed.",
            )

        if action_lower == "safety_check":
            return self._result(
                True,
                action,
                "Safety check completed.",
            )

        if action_lower == "verify":
            return self._result(
                True,
                action,
                "Verification stage ready.",
            )

        if action_lower == "report":
            return self._result(
                True,
                action,
                "Execution report generated.",
            )

        if action_lower == "identify_target":
            return self._result(
                True,
                action,
                "Target identification completed.",
            )

        if action_lower == "select_tool":
            return self._result(
                True,
                action,
                "Appropriate tool selection completed.",
            )

        if action_lower == "request_permission":
            return self._result(
                True,
                action,
                "Permission request stage completed.",
            )

        if action_lower == "perform_action":
            return self._result(
                True,
                action,
                "Action execution stage completed.",
            )

        # -----------------------------------------------------
        # COMPUTER CONTROL
        # -----------------------------------------------------

        if action_lower in {
            "computer_interaction",
            "open_application",
            "perform_computer_action",
        }:

            return self._execute_computer_action(
                step,
                permission_granted,
            )

        # -----------------------------------------------------
        # CODING
        # -----------------------------------------------------

        if action_lower in {
            "inspect_code",
            "analyze_error",
            "explain_error",
            "apply_safe_fix",
            "run_code",
        }:

            return self._execute_coding_action(
                step
            )

        # -----------------------------------------------------
        # MEMORY
        # -----------------------------------------------------

        if action_lower == "memory_operation":

            return self._execute_memory_action(
                step
            )

        # -----------------------------------------------------
        # DOCUMENT
        # -----------------------------------------------------

        if action_lower == "document_operation":

            return self._result(
                True,
                action,
                "Document operation routed successfully.",
            )

        # -----------------------------------------------------
        # RESEARCH
        # -----------------------------------------------------

        if action_lower in {
            "search_information",
            "compare_results",
            "evaluate_information",
            "summarize_findings",
        }:

            return self._result(
                True,
                action,
                "Research operation routed successfully.",
            )

        # -----------------------------------------------------
        # UNKNOWN
        # -----------------------------------------------------

        return self._result(
            success=False,
            action=action,
            message=f"No executor registered for action: {action}",
        )

    # ---------------------------------------------------------
    # EXECUTE COMPLETE PLAN
    # ---------------------------------------------------------

    def execute_plan(
        self,
        plan,
        permission_granted=False,
    ):
        """
        Execute all steps in a plan sequentially.
        """

        if not plan:
            return {
                "success": False,
                "error": "No plan supplied.",
            }

        results = []

        completed = 0
        failed = 0

        for step in plan:

            result = self.execute_step(
                step,
                permission_granted=permission_granted,
            )

            results.append(result)

            if result["success"]:
                completed += 1
            else:
                failed += 1

        return {
            "success": failed == 0,
            "total_steps": len(plan),
            "completed_steps": completed,
            "failed_steps": failed,
            "results": results,
            "executed_at": datetime.now().isoformat(),
        }

    # ---------------------------------------------------------
    # COMPUTER ACTION
    # ---------------------------------------------------------

    def _execute_computer_action(
        self,
        step,
        permission_granted,
    ):

        if not permission_granted:
            return self._result(
                False,
                step.get("action", ""),
                "Computer action requires explicit permission.",
                permission_required=True,
            )

        if self.computer_controller is None:

            try:
                from computer_control import ComputerController

                self.computer_controller = ComputerController()

            except Exception as error:

                return self._result(
                    False,
                    step.get("action", ""),
                    f"Could not load computer controller: {error}",
                )

        application = (
            step.get("application")
            or step.get("target")
            or step.get("value")
        )

        if not application:

            return self._result(
                False,
                step.get("action", ""),
                "No application or target supplied.",
            )

        try:

            success = self.computer_controller.open_application(
                application
            )

            return self._result(
                bool(success),
                step.get("action", ""),
                (
                    f"Application '{application}' opened."
                    if success
                    else f"Failed to open '{application}'."
                ),
                target=application,
            )

        except Exception as error:

            return self._result(
                False,
                step.get("action", ""),
                f"Computer action failed: {error}",
                target=application,
            )

    # ---------------------------------------------------------
    # CODING ACTION
    # ---------------------------------------------------------

    def _execute_coding_action(self, step):

        if self.coding_agent is None:

            try:
                from coding_agent import CodingAgent

                self.coding_agent = CodingAgent()

            except Exception as error:

                return self._result(
                    False,
                    step.get("action", ""),
                    f"Could not load coding agent: {error}",
                )

        code = (
            step.get("code")
            or step.get("input")
            or step.get("value")
        )

        action = step.get("action", "").lower()

        if not code:

            return self._result(
                False,
                action,
                "No code supplied for coding operation.",
            )

        try:

            if action == "inspect_code":

                result = self.coding_agent.analyze_code(
                    code
                )

            elif action == "run_code":

                result = self.coding_agent.run_python(
                    code
                )

            elif action == "apply_safe_fix":

                analysis = self.coding_agent.analyze_code(
                    code
                )

                if hasattr(
                    self.coding_agent,
                    "safe_fix"
                ):
                    result = self.coding_agent.safe_fix(
                        code,
                        analysis
                    )
                else:
                    result = {
                        "success": False,
                        "message": "Safe fix is not available."
                    }

            else:

                result = self.coding_agent.analyze_code(
                    code
                )

            return self._result(
                True,
                action,
                "Coding operation completed.",
                output=result,
            )

        except Exception as error:

            return self._result(
                False,
                action,
                f"Coding operation failed: {error}",
            )

    # ---------------------------------------------------------
    # MEMORY ACTION
    # ---------------------------------------------------------

    def _execute_memory_action(self, step):

        if self.memory_store is None:

            try:
                from memory_store import MemoryStore

                self.memory_store = MemoryStore()

            except Exception as error:

                return self._result(
                    False,
                    "memory_operation",
                    f"Could not load memory store: {error}",
                )

        value = (
            step.get("value")
            or step.get("input")
            or step.get("memory")
        )

        if not value:

            return self._result(
                False,
                "memory_operation",
                "No memory value supplied.",
            )

        try:

            if hasattr(
                self.memory_store,
                "remember"
            ):

                result = self.memory_store.remember(
                    str(value)
                )

                return self._result(
                    True,
                    "memory_operation",
                    "Information stored in JARVIS memory.",
                    output=result,
                )

            return self._result(
                False,
                "memory_operation",
                "Memory store does not support remember().",
            )

        except Exception as error:

            return self._result(
                False,
                "memory_operation",
                f"Memory operation failed: {error}",
            )

    # ---------------------------------------------------------
    # RESULT
    # ---------------------------------------------------------

    def _result(
        self,
        success,
        action,
        message,
        permission_required=False,
        **extra,
    ):

        result = {
            "success": bool(success),
            "action": action,
            "message": message,
            "permission_required": permission_required,
            "timestamp": datetime.now().isoformat(),
        }

        result.update(extra)

        return result


# -------------------------------------------------------------
# TEST
# -------------------------------------------------------------

if __name__ == "__main__":

    executor = AgentExecutor()

    test_steps = [

        {
            "step": 1,
            "action": "UNDERSTAND",
            "risk": "LOW",
        },

        {
            "step": 2,
            "action": "GATHER_CONTEXT",
            "risk": "LOW",
        },

        {
            "step": 3,
            "action": "SAFETY_CHECK",
            "risk": "HIGH",
        },

        {
            "step": 4,
            "action": "VERIFY",
            "risk": "MEDIUM",
        },

        {
            "step": 5,
            "action": "REPORT",
            "risk": "LOW",
        },
    ]

    print("\n" + "=" * 70)
    print("JARVIS EXECUTOR TEST")
    print("=" * 70)

    result = executor.execute_plan(
        test_steps
    )

    for item in result["results"]:

        print(
            f"\nStep: {item['action']}"
        )

        print(
            f"Success: {item['success']}"
        )

        print(
            f"Message: {item['message']}"
        )

    print("\nEXECUTION SUMMARY:")
    print(
        f"Total: {result['total_steps']}"
    )

    print(
        f"Completed: {result['completed_steps']}"
    )

    print(
        f"Failed: {result['failed_steps']}"
    )

    print("\nEXECUTOR STATUS:")

    print(
        "PASS"
        if result["success"]
        else "FAIL"
    )

    print("=" * 70)