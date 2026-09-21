from datetime import datetime


class ToolRegistry:
    """
    JARVIS Universal Tool Registry

    Maintains the capabilities available to the agent and allows
    the planner/executor to discover the appropriate tool.
    """

    def __init__(self):
        self.tools = {}

        self.register_default_tools()

    # ---------------------------------------------------------
    # REGISTER TOOL
    # ---------------------------------------------------------

    def register_tool(
        self,
        name,
        description,
        capabilities,
        risk_level="LOW",
        requires_permission=False,
    ):
        self.tools[name] = {
            "name": name,
            "description": description,
            "capabilities": capabilities,
            "risk_level": risk_level,
            "requires_permission": requires_permission,
            "available": True,
        }

    # ---------------------------------------------------------
    # DEFAULT TOOLS
    # ---------------------------------------------------------

    def register_default_tools(self):

        self.register_tool(
            name="voice_control",
            description="Listen to and process spoken user commands.",
            capabilities=["voice", "input"],
            risk_level="LOW",
        )

        self.register_tool(
            name="vision_engine",
            description="Analyze camera and visual information.",
            capabilities=["vision", "visual"],
            risk_level="LOW",
        )

        self.register_tool(
            name="ocr_engine",
            description="Extract text from images or visual content.",
            capabilities=["vision", "ocr", "document"],
            risk_level="LOW",
        )

        self.register_tool(
            name="computer_control",
            description="Open applications and perform computer interactions.",
            capabilities=["computer_control", "application"],
            risk_level="MEDIUM",
            requires_permission=True,
        )

        self.register_tool(
            name="coding_agent",
            description="Analyze, debug, fix, execute, and verify code.",
            capabilities=["coding", "development"],
            risk_level="MEDIUM",
        )

        self.register_tool(
            name="memory_store",
            description="Store and retrieve information from JARVIS memory.",
            capabilities=["memory", "recall"],
            risk_level="LOW",
        )

        self.register_tool(
            name="research_engine",
            description="Research information and compare relevant findings.",
            capabilities=["research", "web", "information"],
            risk_level="LOW",
        )

        self.register_tool(
            name="document_engine",
            description="Create, analyze, and process documents.",
            capabilities=["document", "files"],
            risk_level="MEDIUM",
        )

        self.register_tool(
            name="task_manager",
            description="Create, track, update, and complete tasks.",
            capabilities=["planning", "tasks", "productivity"],
            risk_level="LOW",
        )

    # ---------------------------------------------------------
    # GET TOOL
    # ---------------------------------------------------------

    def get_tool(self, name):

        return self.tools.get(name)

    # ---------------------------------------------------------
    # FIND TOOLS BY CAPABILITY
    # ---------------------------------------------------------

    def find_tools_for_capability(self, capability):

        matches = []

        for tool in self.tools.values():

            if capability in tool["capabilities"]:
                matches.append(tool)

        return matches

    # ---------------------------------------------------------
    # SELECT TOOLS FOR GOAL
    # ---------------------------------------------------------

    def select_tools_for_goal(self, goal):

        if not goal or not goal.get("success"):
            return []

        required_capabilities = goal.get(
            "required_capabilities",
            []
        )

        selected = []
        selected_names = set()

        for capability in required_capabilities:

            candidates = self.find_tools_for_capability(
                capability
            )

            for tool in candidates:

                if tool["name"] not in selected_names:

                    selected.append(tool)
                    selected_names.add(tool["name"])

        return selected

    # ---------------------------------------------------------
    # ENABLE / DISABLE TOOL
    # ---------------------------------------------------------

    def set_tool_availability(
        self,
        name,
        available
    ):

        if name not in self.tools:
            return False

        self.tools[name]["available"] = bool(
            available
        )

        return True

    # ---------------------------------------------------------
    # AVAILABLE TOOLS
    # ---------------------------------------------------------

    def get_available_tools(self):

        return [
            tool
            for tool in self.tools.values()
            if tool["available"]
        ]

    # ---------------------------------------------------------
    # TOOL COUNT
    # ---------------------------------------------------------

    def count(self):

        return len(self.tools)

    # ---------------------------------------------------------
    # SYSTEM STATUS
    # ---------------------------------------------------------

    def status(self):

        available = len(
            self.get_available_tools()
        )

        return {
            "total_tools": len(self.tools),
            "available_tools": available,
            "timestamp": datetime.now().isoformat(),
        }


# -------------------------------------------------------------
# TEST
# -------------------------------------------------------------

if __name__ == "__main__":

    from goal_engine import GoalEngine

    goal_engine = GoalEngine()
    registry = ToolRegistry()

    test_goal = (
        "I have a project presentation tomorrow "
        "and I haven't prepared anything."
    )

    goal = goal_engine.understand_goal(
        test_goal
    )

    selected_tools = registry.select_tools_for_goal(
        goal
    )

    print("\n" + "=" * 70)
    print("JARVIS TOOL REGISTRY TEST")
    print("=" * 70)

    print("\nREGISTERED TOOLS:")

    for tool in registry.get_available_tools():

        print(
            f"• {tool['name']}"
            f" | Risk: {tool['risk_level']}"
            f" | Permission: {tool['requires_permission']}"
        )

    print("\nTOOLS SELECTED FOR GOAL:")

    for tool in selected_tools:

        print(
            f"→ {tool['name']}"
            f" | {tool['description']}"
        )

    print("\nSYSTEM STATUS:")
    print(registry.status())

    print("\nTOOL COUNT:")
    print(registry.count())

    print("\nREGISTRY STATUS:")
    print(
        "PASS"
        if len(selected_tools) > 0
        else "FAIL"
    )

    print("=" * 70)