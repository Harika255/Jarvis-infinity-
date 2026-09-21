from datetime import datetime


class DynamicPlanner:
    """
    JARVIS INFINITY Dynamic Planning Engine

    Converts a structured goal from GoalEngine into an
    ordered, explainable execution plan.
    """

    def __init__(self):
        self.step_counter = 0

    # =========================================================
    # MAIN PLANNER
    # =========================================================

    def create_plan(self, goal):
        """
        Create a dynamic execution plan from a GoalEngine result.
        """

        if not isinstance(goal, dict) or not goal.get("success", False):
            return {
                "success": False,
                "error": "Invalid goal provided to planner.",
            }

        self.step_counter = 0

        goal_type = str(
            goal.get("goal_type", "GENERAL")
        ).upper()

        capabilities = goal.get(
            "required_capabilities",
            []
        )

        if not isinstance(capabilities, list):
            capabilities = []

        plan_steps = []

        # -----------------------------------------------------
        # Every task starts with understanding the goal.
        # -----------------------------------------------------

        plan_steps.append(
            self._create_step(
                "UNDERSTAND",
                "Understand the user's goal and required outcome.",
                "LOW",
            )
        )

        # -----------------------------------------------------
        # Gather context.
        # -----------------------------------------------------

        plan_steps.append(
            self._create_step(
                "GATHER_CONTEXT",
                "Gather the information and resources required for the task.",
                "LOW",
            )
        )

        # -----------------------------------------------------
        # Goal-specific planning.
        # -----------------------------------------------------

        if goal_type == "STUDY":
            plan_steps.extend(
                self._study_plan()
            )

        elif goal_type == "DEBUG":
            plan_steps.extend(
                self._debug_plan()
            )

        elif goal_type == "RESEARCH":
            plan_steps.extend(
                self._research_plan()
            )

        elif goal_type == "CREATE":
            plan_steps.extend(
                self._create_task_plan()
            )

        elif goal_type == "ACTION":
            plan_steps.extend(
                self._action_plan()
            )

        elif goal_type == "PLAN":
            plan_steps.extend(
                self._planning_plan()
            )

        else:
            plan_steps.extend(
                self._general_plan(capabilities)
            )

        # -----------------------------------------------------
        # Safety check.
        # -----------------------------------------------------

        plan_steps.append(
            self._create_step(
                "SAFETY_CHECK",
                "Evaluate whether the planned actions are safe and whether permission is required.",
                "HIGH",
            )
        )

        # -----------------------------------------------------
        # Execute approved actions.
        #
        # EXECUTE itself is an internal planning stage.
        # Actual protected actions are handled separately.
        # -----------------------------------------------------

        plan_steps.append(
            self._create_step(
                "EXECUTE",
                "Execute approved actions using the appropriate JARVIS tools.",
                "MEDIUM",
            )
        )

        # -----------------------------------------------------
        # Verification.
        # -----------------------------------------------------

        plan_steps.append(
            self._create_step(
                "VERIFY",
                "Verify whether the intended result was successfully achieved.",
                "MEDIUM",
            )
        )

        # -----------------------------------------------------
        # Report.
        # -----------------------------------------------------

        plan_steps.append(
            self._create_step(
                "REPORT",
                "Explain what JARVIS completed and identify any remaining work.",
                "LOW",
            )
        )

        return {
            "success": True,
            "goal": goal,
            "plan": plan_steps,
            "step_count": len(plan_steps),
            "generated_at": datetime.now().isoformat(),
        }

    # =========================================================
    # STEP CREATOR
    # =========================================================

    def _create_step(
        self,
        action,
        description,
        risk,
    ):
        self.step_counter += 1

        return {
            "step": self.step_counter,
            "action": str(action).strip().upper(),
            "description": description,
            "risk": str(risk).strip().upper(),
            "status": "PENDING",
        }

    # =========================================================
    # STUDY PLAN
    # =========================================================

    def _study_plan(self):
        return [
            self._create_step(
                "IDENTIFY_STUDY_SCOPE",
                "Identify the subject, topics, exam requirements, and available study time.",
                "LOW",
            ),
            self._create_step(
                "PRIORITIZE_TOPICS",
                "Prioritize topics according to importance, difficulty, and deadline.",
                "LOW",
            ),
            self._create_step(
                "CREATE_STUDY_SCHEDULE",
                "Generate a realistic study schedule based on the available time.",
                "LOW",
            ),
            self._create_step(
                "PREPARE_MATERIAL",
                "Prepare or organize the required study material.",
                "LOW",
            ),
        ]

    # =========================================================
    # DEBUG PLAN
    # =========================================================

    def _debug_plan(self):
        return [
            self._create_step(
                "INSPECT_CODE",
                "Inspect the provided program and understand its structure.",
                "LOW",
            ),
            self._create_step(
                "ANALYZE_ERROR",
                "Identify syntax, runtime, or logical problems.",
                "LOW",
            ),
            self._create_step(
                "EXPLAIN_ERROR",
                "Explain the detected problem and its likely cause.",
                "LOW",
            ),
            self._create_step(
                "APPLY_SAFE_FIX",
                "Apply a safe deterministic correction when possible.",
                "MEDIUM",
            ),
            self._create_step(
                "RUN_CODE",
                "Run the corrected program in a controlled environment.",
                "MEDIUM",
            ),
        ]

    # =========================================================
    # RESEARCH PLAN
    # =========================================================

    def _research_plan(self):
        return [
            self._create_step(
                "DEFINE_RESEARCH_QUESTION",
                "Identify exactly what information needs to be discovered.",
                "LOW",
            ),
            self._create_step(
                "SEARCH_INFORMATION",
                "Search relevant information sources.",
                "LOW",
            ),
            self._create_step(
                "COMPARE_RESULTS",
                "Compare relevant findings and identify useful differences.",
                "LOW",
            ),
            self._create_step(
                "EVALUATE_INFORMATION",
                "Evaluate the reliability and relevance of the findings.",
                "LOW",
            ),
            self._create_step(
                "SUMMARIZE_FINDINGS",
                "Create a concise evidence-based summary.",
                "LOW",
            ),
        ]

    # =========================================================
    # CREATE PLAN
    # =========================================================

    def _create_task_plan(self):
        return [
            self._create_step(
                "DEFINE_OUTPUT",
                "Determine the required final output.",
                "LOW",
            ),
            self._create_step(
                "IDENTIFY_RESOURCES",
                "Identify files, tools, information, and capabilities required.",
                "LOW",
            ),
            self._create_step(
                "BUILD_OUTPUT",
                "Create the requested output.",
                "MEDIUM",
            ),
            self._create_step(
                "QUALITY_CHECK",
                "Check the generated result for completeness and correctness.",
                "LOW",
            ),
        ]

    # =========================================================
    # ACTION PLAN
    # =========================================================

    def _action_plan(self):
        return [
            self._create_step(
                "IDENTIFY_TARGET",
                "Identify the application, file, or system involved in the requested action.",
                "LOW",
            ),
            self._create_step(
                "SELECT_TOOL",
                "Select the appropriate computer-control tool.",
                "LOW",
            ),
            self._create_step(
                "REQUEST_PERMISSION",
                "Request user permission when the action requires approval.",
                "HIGH",
            ),
            self._create_step(
                "PERFORM_ACTION",
                "Perform the approved computer interaction.",
                "MEDIUM",
            ),
        ]

    # =========================================================
    # PLANNING PLAN
    # =========================================================

    def _planning_plan(self):
        return [
            self._create_step(
                "UNDERSTAND_REQUIREMENTS",
                "Identify the desired outcome and constraints.",
                "LOW",
            ),
            self._create_step(
                "BREAK_INTO_TASKS",
                "Break the goal into manageable tasks.",
                "LOW",
            ),
            self._create_step(
                "ORDER_TASKS",
                "Determine the most effective execution order.",
                "LOW",
            ),
        ]

    # =========================================================
    # GENERAL PLAN
    # =========================================================

    def _general_plan(self, capabilities):
        steps = []

        capability_set = {
            str(item).strip().lower()
            for item in capabilities
        }

        if "voice" in capability_set:
            steps.append(
                self._create_step(
                    "VOICE_INPUT",
                    "Process the user's voice input.",
                    "LOW",
                )
            )

        if "vision" in capability_set:
            steps.append(
                self._create_step(
                    "VISION_INPUT",
                    "Analyze available visual information.",
                    "LOW",
                )
            )

        if "computer_control" in capability_set:
            steps.append(
                self._create_step(
                    "COMPUTER_INTERACTION",
                    "Interact with the computer using an appropriate tool.",
                    "MEDIUM",
                )
            )

        if "memory" in capability_set:
            steps.append(
                self._create_step(
                    "MEMORY_OPERATION",
                    "Store or retrieve relevant information from JARVIS memory.",
                    "LOW",
                )
            )

        if "document" in capability_set:
            steps.append(
                self._create_step(
                    "DOCUMENT_OPERATION",
                    "Process or create the required document.",
                    "MEDIUM",
                )
            )

        if "coding" in capability_set:
            steps.append(
                self._create_step(
                    "CODING_OPERATION",
                    "Analyze or process the required programming task.",
                    "LOW",
                )
            )

        if "research" in capability_set:
            steps.append(
                self._create_step(
                    "RESEARCH_OPERATION",
                    "Gather and evaluate information relevant to the goal.",
                    "LOW",
                )
            )

        if "planning" in capability_set:
            steps.append(
                self._create_step(
                    "PLANNING_OPERATION",
                    "Develop an appropriate plan for the user's goal.",
                    "LOW",
                )
            )

        return steps


# =============================================================
# TEST
# =============================================================

if __name__ == "__main__":
    from agent.goal_engine import GoalEngine

    engine = GoalEngine()
    planner = DynamicPlanner()

    test_goal = (
        "I have a project presentation tomorrow "
        "and I haven't prepared anything."
    )

    goal = engine.understand_goal(test_goal)

    result = planner.create_plan(goal)

    print()
    print("=" * 70)
    print("JARVIS DYNAMIC PLANNER TEST")
    print("=" * 70)

    print()
    print("USER GOAL:")
    print(test_goal)

    if not result.get("success", False):
        print()
        print("PLANNER ERROR:")
        print(
            result.get(
                "error",
                "Unknown planner error.",
            )
        )

        print()
        print("PLANNER STATUS:")
        print("FAIL")

    else:
        print()
        print("GENERATED PLAN:")

        for step in result.get("plan", []):
            print(
                f"{step['step']}. "
                f"[{step['risk']}] "
                f"{step['action']} "
                f"-> {step['description']}"
            )

        print()
        print("TOTAL STEPS:")
        print(result.get("step_count", 0))

        print()
        print("PLANNER STATUS:")
        print("PASS")

    print("=" * 70)
