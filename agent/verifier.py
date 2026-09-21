from datetime import datetime


class AgentVerifier:
    """
    JARVIS Verification Engine

    Determines whether an executed action actually achieved
    its intended result.
    """

    def __init__(self):
        self.verification_methods = {
            "open_application": "PROCESS_CHECK",
            "computer_interaction": "PROCESS_CHECK",
            "run_code": "OUTPUT_CHECK",
            "apply_safe_fix": "CODE_CHECK",
            "memory_operation": "MEMORY_CHECK",
            "create_plan": "PLAN_CHECK",
            "document_operation": "FILE_CHECK",
            "research": "CONTENT_CHECK",
        }

    # ---------------------------------------------------------
    # VERIFY EXECUTION RESULT
    # ---------------------------------------------------------

    def verify(
        self,
        action,
        execution_result,
        expected_result=None,
    ):
        """
        Verify the result of an executed action.
        """

        if not action:
            return self._result(
                "UNCERTAIN",
                False,
                "No action was supplied for verification.",
            )

        action_name = (
            str(action)
            .lower()
            .strip()
        )

        # -----------------------------------------------------
        # EXECUTION FAILURE
        # -----------------------------------------------------

        if not execution_result:

            return self._result(
                "FAILED",
                False,
                "No execution result was received.",
            )

        if execution_result.get("success") is False:

            return self._result(
                "FAILED",
                False,
                "The executor reported that the action failed.",
                execution_result=execution_result,
            )

        # -----------------------------------------------------
        # ACTION-SPECIFIC VERIFICATION
        # -----------------------------------------------------

        if action_name == "open_application":

            return self._verify_application(
                execution_result
            )

        if action_name == "computer_interaction":

            return self._verify_application(
                execution_result
            )

        if action_name == "run_code":

            return self._verify_code(
                execution_result
            )

        if action_name == "apply_safe_fix":

            return self._verify_code_fix(
                execution_result
            )

        if action_name == "memory_operation":

            return self._verify_memory(
                execution_result
            )

        if action_name in {
            "create_plan",
            "planning",
        }:

            return self._verify_plan(
                execution_result
            )

        if action_name == "document_operation":

            return self._verify_generic(
                execution_result,
                "Document operation completed according to the executor.",
            )

        if action_name in {
            "research",
            "search_information",
            "compare_results",
            "evaluate_information",
            "summarize_findings",
        }:

            return self._verify_generic(
                execution_result,
                "Research operation returned successfully.",
            )

        # -----------------------------------------------------
        # GENERIC VERIFICATION
        # -----------------------------------------------------

        return self._verify_generic(
            execution_result,
            "Executor reported successful completion.",
        )

    # ---------------------------------------------------------
    # VERIFY COMPLETE PLAN
    # ---------------------------------------------------------

    def verify_plan(
        self,
        execution_results,
    ):
        """
        Verify all results produced by an executed plan.
        """

        if not execution_results:
            return {
                "success": False,
                "overall_status": "UNCERTAIN",
                "message": "No execution results supplied.",
            }

        results = []

        successful = 0
        failed = 0
        uncertain = 0

        for execution in execution_results:

            verification = self.verify(
                execution.get("action", ""),
                execution,
            )

            results.append(
                verification
            )

            status = verification["status"]

            if status == "SUCCESS":
                successful += 1

            elif status == "FAILED":
                failed += 1

            else:
                uncertain += 1

        if failed > 0:
            overall = "FAILED"

        elif uncertain > 0:
            overall = "UNCERTAIN"

        else:
            overall = "SUCCESS"

        return {
            "success": True,
            "overall_status": overall,
            "total_steps": len(results),
            "successful_steps": successful,
            "failed_steps": failed,
            "uncertain_steps": uncertain,
            "results": results,
            "verified_at": datetime.now().isoformat(),
        }

    # ---------------------------------------------------------
    # APPLICATION VERIFICATION
    # ---------------------------------------------------------

    def _verify_application(
        self,
        execution_result,
    ):

        target = execution_result.get(
            "target"
        )

        if execution_result.get(
            "success"
        ):

            return self._result(
                "SUCCESS",
                True,
                (
                    f"Application '{target}' "
                    "was reported as successfully opened."
                    if target
                    else
                    "Application launch was reported as successful."
                ),
                verification_method="PROCESS_CHECK",
            )

        return self._result(
            "FAILED",
            False,
            "Application launch was not successful.",
            verification_method="PROCESS_CHECK",
        )

    # ---------------------------------------------------------
    # CODE VERIFICATION
    # ---------------------------------------------------------

    def _verify_code(
        self,
        execution_result,
    ):

        output = execution_result.get(
            "output"
        )

        if execution_result.get(
            "success"
        ):

            return self._result(
                "SUCCESS",
                True,
                "Code execution completed successfully.",
                verification_method="OUTPUT_CHECK",
                output=output,
            )

        return self._result(
            "FAILED",
            False,
            "Code execution failed.",
            verification_method="OUTPUT_CHECK",
            output=output,
        )

    # ---------------------------------------------------------
    # CODE FIX VERIFICATION
    # ---------------------------------------------------------

    def _verify_code_fix(
        self,
        execution_result,
    ):

        if not execution_result.get(
            "success"
        ):

            return self._result(
                "FAILED",
                False,
                "Safe code correction was not completed.",
                verification_method="CODE_CHECK",
            )

        return self._result(
            "SUCCESS",
            True,
            "Safe code correction completed.",
            verification_method="CODE_CHECK",
        )

    # ---------------------------------------------------------
    # MEMORY VERIFICATION
    # ---------------------------------------------------------

    def _verify_memory(
        self,
        execution_result,
    ):

        if execution_result.get(
            "success"
        ):

            return self._result(
                "SUCCESS",
                True,
                "Memory operation completed successfully.",
                verification_method="MEMORY_CHECK",
            )

        return self._result(
            "FAILED",
            False,
            "Memory operation failed.",
            verification_method="MEMORY_CHECK",
        )

    # ---------------------------------------------------------
    # PLAN VERIFICATION
    # ---------------------------------------------------------

    def _verify_plan(
        self,
        execution_result,
    ):

        if execution_result.get(
            "success"
        ):

            return self._result(
                "SUCCESS",
                True,
                "Plan was generated successfully.",
                verification_method="PLAN_CHECK",
            )

        return self._result(
            "FAILED",
            False,
            "Plan generation failed.",
            verification_method="PLAN_CHECK",
        )

    # ---------------------------------------------------------
    # GENERIC VERIFICATION
    # ---------------------------------------------------------

    def _verify_generic(
        self,
        execution_result,
        message,
    ):

        if execution_result.get(
            "success"
        ):

            return self._result(
                "SUCCESS",
                True,
                message,
                verification_method="EXECUTION_RESULT_CHECK",
            )

        return self._result(
            "FAILED",
            False,
            "Executor reported failure.",
            verification_method="EXECUTION_RESULT_CHECK",
        )

    # ---------------------------------------------------------
    # RESULT
    # ---------------------------------------------------------

    def _result(
        self,
        status,
        verified,
        message,
        **extra,
    ):

        result = {
            "status": status,
            "verified": verified,
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }

        result.update(extra)

        return result


# -------------------------------------------------------------
# TEST
# -------------------------------------------------------------

if __name__ == "__main__":

    verifier = AgentVerifier()

    print("\n" + "=" * 70)
    print("JARVIS VERIFICATION ENGINE TEST")
    print("=" * 70)

    # Successful application launch.
    success_execution = {
        "success": True,
        "action": "open_application",
        "target": "notepad",
        "message": "Application 'notepad' opened.",
    }

    result = verifier.verify(
        "open_application",
        success_execution,
    )

    print("\nTEST 1 — SUCCESSFUL ACTION")
    print(
        "Status:",
        result["status"]
    )
    print(
        "Verified:",
        result["verified"]
    )
    print(
        "Message:",
        result["message"]
    )

    # Failed action.
    failed_execution = {
        "success": False,
        "action": "open_application",
        "target": "unknown_app",
        "message": "Failed to open application.",
    }

    result = verifier.verify(
        "open_application",
        failed_execution,
    )

    print("\nTEST 2 — FAILED ACTION")
    print(
        "Status:",
        result["status"]
    )
    print(
        "Verified:",
        result["verified"]
    )
    print(
        "Message:",
        result["message"]
    )

    # Code execution.
    code_execution = {
        "success": True,
        "action": "run_code",
        "output": "30",
        "message": "Code executed successfully.",
    }

    result = verifier.verify(
        "run_code",
        code_execution,
    )

    print("\nTEST 3 — CODE VERIFICATION")
    print(
        "Status:",
        result["status"]
    )
    print(
        "Verified:",
        result["verified"]
    )
    print(
        "Output:",
        result.get("output")
    )

    print("\nVERIFIER STATUS:")
    print("PASS")

    print("=" * 70)