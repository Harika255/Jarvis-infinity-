import os
import re
import json
import webbrowser
from urllib.parse import quote_plus
from typing import Any, Dict, Optional

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from memory_store import JarvisMemory
from task_manager import RealWorldTaskManager
from agent_tools import AgentTools


class JarvisLLM:
    """General-purpose JARVIS AI brain with safe local tools."""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.model = os.getenv("JARVIS_MODEL", "gpt-5.6-luna").strip()

        self.enabled = bool(self.api_key and OpenAI)

        self.client = (
            OpenAI(api_key=self.api_key)
            if self.enabled
            else None
        )

        self.previous_response_id: Optional[str] = None

        self.memory = JarvisMemory()
        self.tasks = RealWorldTaskManager()
        self.tools = AgentTools()

        self.pending_action: Optional[Dict[str, Any]] = None

        self.instructions = """
You are JARVIS Infinity 2026, a practical desktop AI assistant.

Your job is to understand natural language naturally, like a modern AI assistant.

Do NOT require the user to use predefined commands.
Do NOT behave like a command parser.
Do NOT say a request is unsupported simply because the wording is new.

You can:
- Answer general questions
- Explain technical and non-technical concepts
- Help with programming
- Write and debug code
- Help with college studies
- Help with productivity
- Create and manage tasks
- Remember information when explicitly asked
- Recall saved information
- Inspect JARVIS project status
- Open approved desktop applications after user permission
- Use web search for current information when available

IMPORTANT:
You have access to local tools. Use them when they are genuinely useful.

SAFETY RULES:

1. Never claim an action happened unless the corresponding tool reports success.

2. Opening a desktop application is a MEDIUM-RISK action.
   It requires explicit user approval through the JARVIS desktop UI.

3. Never expose:
   - API keys
   - passwords
   - credentials
   - secrets
   - private system information

4. Do not perform:
   - destructive file deletion
   - credential changes
   - financial transactions
   - dangerous system modifications
   - other high-impact actions

5. If the user's request is ambiguous, ask a short clarification.

6. For current or time-sensitive information, use web search when available.

7. Do not reveal hidden chain-of-thought.
   Give concise explanations, decisions, tool status, and results only.

STYLE:

- Natural
- Intelligent
- Helpful
- Concise by default
- Friendly but professional
- Understand conversational language
- Do not force predefined commands
- For complex tasks, provide a practical plan
""".strip()

    # ==============================================================
    # TOOL DEFINITIONS
    # ==============================================================

    def tool_definitions(self):
        """
        Tools available to the JARVIS AI brain.

        IMPORTANT:
        Because strict=True is used, every property MUST appear
        in the required list.
        """

        return [

            # ------------------------------------------------------
            # WEB SEARCH
            # ------------------------------------------------------

            {
                "type": "web_search"
            },

            # ------------------------------------------------------
            # REMEMBER
            # ------------------------------------------------------

            {
                "type": "function",
                "name": "remember",
                "description": (
                    "Store a fact, preference, goal, or note that "
                    "the user explicitly wants JARVIS to remember."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "value": {
                            "type": "string",
                            "description": "Information to remember."
                        },
                        "category": {
                            "type": "string",
                            "description": "Category of the memory."
                        }
                    },

                    # FIXED:
                    # Both properties are required.
                    "required": [
                        "value",
                        "category"
                    ],

                    "additionalProperties": False
                },
                "strict": True
            },

            # ------------------------------------------------------
            # RECALL MEMORY
            # ------------------------------------------------------

            {
                "type": "function",
                "name": "recall_memory",
                "description": (
                    "Retrieve recent saved memories relevant to "
                    "the current conversation."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 20,
                            "description": (
                                "Maximum number of memories to retrieve."
                            )
                        }
                    },

                    # FIXED:
                    # limit must be required for strict schema.
                    "required": [
                        "limit"
                    ],

                    "additionalProperties": False
                },
                "strict": True
            },

            # ------------------------------------------------------
            # CREATE TASK
            # ------------------------------------------------------

            {
                "type": "function",
                "name": "create_task",
                "description": (
                    "Create a practical task for the user when "
                    "they ask JARVIS to track, remember, schedule, "
                    "or add work to their task list."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {

                        "title": {
                            "type": "string",
                            "description": "Task title."
                        },

                        "priority": {
                            "type": "string",
                            "enum": [
                                "HIGH",
                                "MEDIUM",
                                "LOW"
                            ],
                            "description": "Task priority."
                        },

                        "deadline": {
                            "type": [
                                "string",
                                "null"
                            ],
                            "description": (
                                "Task deadline or null if there is "
                                "no deadline."
                            )
                        },

                        "category": {
                            "type": "string",
                            "description": "Task category."
                        }
                    },

                    "required": [
                        "title",
                        "priority",
                        "deadline",
                        "category"
                    ],

                    "additionalProperties": False
                },
                "strict": True
            },

            # ------------------------------------------------------
            # LIST TASKS
            # ------------------------------------------------------

            {
                "type": "function",
                "name": "list_tasks",
                "description": (
                    "List the user's pending tasks ordered "
                    "by priority and deadline."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                    "additionalProperties": False
                },
                "strict": True
            },

            # ------------------------------------------------------
            # COMPLETE TASK
            # ------------------------------------------------------

            {
                "type": "function",
                "name": "complete_task",
                "description": (
                    "Mark one pending task as completed "
                    "using its task ID."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "ID of the task to complete."
                        }
                    },

                    "required": [
                        "task_id"
                    ],

                    "additionalProperties": False
                },
                "strict": True
            },

            # ------------------------------------------------------
            # OPEN APPLICATION
            # ------------------------------------------------------

            {
                "type": "function",
                "name": "open_application",
                "description": (
                    "Open an allowlisted desktop application. "
                    "This always requires explicit user approval "
                    "in the JARVIS UI before execution."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "application": {
                            "type": "string",
                            "enum": [
                                "vscode",
                                "notepad",
                                "calculator"
                            ],
                            "description": "Application to open."
                        }
                    },

                    "required": [
                        "application"
                    ],

                    "additionalProperties": False
                },
                "strict": True
            },

            # ------------------------------------------------------
            # PROJECT STATUS
            # ------------------------------------------------------

            {
                "type": "function",
                "name": "get_project_status",
                "description": (
                    "Inspect the known JARVIS Infinity project "
                    "module status and identify useful next work."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                    "additionalProperties": False
                },
                "strict": True
            }
        ]

    # ==============================================================
    # TOOL EXECUTION
    # ==============================================================

    def _execute_tool(
        self,
        name: str,
        args: Dict[str, Any]
    ) -> Dict[str, Any]:

        # ----------------------------------------------------------
        # REMEMBER
        # ----------------------------------------------------------

        if name == "remember":

            value = str(
                args.get("value", "")
            ).strip()

            category = str(
                args.get("category", "USER_NOTE")
            ).strip()

            if not value:
                return {
                    "success": False,
                    "message": "There is no information to remember."
                }

            self.memory.remember(
                category,
                "user_memory",
                value
            )

            return {
                "success": True,
                "message": f"Remembered: {value}"
            }

        # ----------------------------------------------------------
        # RECALL MEMORY
        # ----------------------------------------------------------

        if name == "recall_memory":

            try:
                limit = int(args.get("limit", 10))
            except (TypeError, ValueError):
                limit = 10

            limit = max(1, min(limit, 20))

            memories = self.memory.recall(
                limit=limit
            )

            return {
                "success": True,
                "memories": memories
            }

        # ----------------------------------------------------------
        # CREATE TASK
        # ----------------------------------------------------------

        if name == "create_task":

            task = self.tasks.add_task(
                title=args["title"],
                priority=args["priority"],
                deadline=args["deadline"],
                category=args["category"]
            )

            return {
                "success": True,
                "task": task
            }

        # ----------------------------------------------------------
        # LIST TASKS
        # ----------------------------------------------------------

        if name == "list_tasks":

            try:
                tasks = self.tasks.prioritize()
            except Exception as exc:
                return {
                    "success": False,
                    "message": f"Could not retrieve tasks: {exc}"
                }

            return {
                "success": True,
                "tasks": tasks
            }

        # ----------------------------------------------------------
        # COMPLETE TASK
        # ----------------------------------------------------------

        if name == "complete_task":

            task_id = args.get("task_id")

            try:
                task_id = int(task_id)
            except (TypeError, ValueError):
                return {
                    "success": False,
                    "message": "Invalid task ID."
                }

            task = self.tasks.complete_task(
                task_id
            )

            if not task:

                return {
                    "success": False,
                    "message": "Task was not found."
                }

            return {
                "success": True,
                "task": task
            }

        # ----------------------------------------------------------
        # OPEN APPLICATION
        # ----------------------------------------------------------

        if name == "open_application":

            # IMPORTANT:
            # Never execute directly.
            # Store it until the user approves it.

            self.pending_action = {
                "name": name,
                "args": args,
                "risk": "MEDIUM"
            }

            return {
                "success": False,
                "approval_required": True,
                "message": (
                    "User approval is required before this "
                    "computer action can execute."
                )
            }

        # ----------------------------------------------------------
        # PROJECT STATUS
        # ----------------------------------------------------------

        if name == "get_project_status":

            try:

                from ai_brain import JarvisBrain

                brain = JarvisBrain()

                status = brain.analyze_situation()

                return {
                    "success": True,
                    "status": status
                }

            except Exception as exc:

                return {
                    "success": False,
                    "message": str(exc)
                }

        # ----------------------------------------------------------
        # UNKNOWN TOOL
        # ----------------------------------------------------------

        return {
            "success": False,
            "message": f"Unknown tool: {name}"
        }

    # ==============================================================
    # RESPONSE TEXT EXTRACTION
    # ==============================================================

    def _response_text(self, response) -> str:

        text = getattr(
            response,
            "output_text",
            None
        )

        if text:
            return text.strip()

        pieces = []

        for item in (
            getattr(response, "output", [])
            or []
        ):

            if getattr(
                item,
                "type",
                ""
            ) != "message":
                continue

            for content in (
                getattr(item, "content", [])
                or []
            ):

                value = getattr(
                    content,
                    "text",
                    None
                )

                if value:
                    pieces.append(
                        value
                    )

        return "\n".join(
            pieces
        ).strip()

    # ==============================================================
    # SMART LOCAL WEB ROUTER
    # ============================================================== 

    WEBSITE_ALIASES = {
        "youtube": "https://www.youtube.com/",
        "google": "https://www.google.com/",
        "gmail": "https://mail.google.com/",
        "google drive": "https://drive.google.com/",
        "google docs": "https://docs.google.com/",
        "google sheets": "https://sheets.google.com/",
        "google meet": "https://meet.google.com/",
        "github": "https://github.com/",
        "linkedin": "https://www.linkedin.com/",
        "microsoft": "https://www.microsoft.com/",
        "microsoft learn": "https://learn.microsoft.com/",
        "stackoverflow": "https://stackoverflow.com/",
        "stack overflow": "https://stackoverflow.com/",
        "reddit": "https://www.reddit.com/",
        "instagram": "https://www.instagram.com/",
        "facebook": "https://www.facebook.com/",
        "x": "https://x.com/",
        "twitter": "https://x.com/",
        "chatgpt": "https://chatgpt.com/",
        "canva": "https://www.canva.com/",
        "figma": "https://www.figma.com/",
        "coursera": "https://www.coursera.org/",
        "kaggle": "https://www.kaggle.com/",
        "geeksforgeeks": "https://www.geeksforgeeks.org/",
        "geeks for geeks": "https://www.geeksforgeeks.org/",
        "w3schools": "https://www.w3schools.com/",
        "npm": "https://www.npmjs.com/",
        "pypi": "https://pypi.org/",
        "openai": "https://openai.com/",
        "vercel": "https://vercel.com/",
        "netlify": "https://www.netlify.com/",
    }

    def _local_web_action(self, text: str) -> Optional[Dict[str, Any]]:
        """Handle common website navigation/search locally, without API usage."""
        raw = (text or "").strip()
        lower = raw.lower()

        if not raw:
            return None

        # ----------------------------------------------------------
        # Bare website names
        # ----------------------------------------------------------
        bare_target = re.sub(r"[.!?]+$", "", raw).strip().lower()
        if bare_target in self.WEBSITE_ALIASES:
            url = self.WEBSITE_ALIASES[bare_target]
            webbrowser.open_new_tab(url)
            return {
                "success": True,
                "configured": True,
                "local_action": True,
                "message": f"Opening {bare_target.title()} in your browser.",
            }

        # ----------------------------------------------------------
        # Search a specific website
        # Examples:
        #   search YouTube for Python tutorials
        #   find Python on Google
        #   search GitHub for face recognition
        # ----------------------------------------------------------
        search_match = re.match(
            r"^(?:please\s+)?(?:search|find|look\s+up)\s+(.+?)\s+(?:on|in)\s+(.+?)\s*(?:for)?\s*$",
            raw,
            re.IGNORECASE,
        )

        # More reliable form: "search <site> for <query>"
        site_first = re.match(
            r"^(?:please\s+)?(?:search|find|look\s+up)\s+(.+?)\s+(?:for|about)\s+(.+)$",
            raw,
            re.IGNORECASE,
        )

        if site_first:
            first = site_first.group(1).strip().lower()
            query = site_first.group(2).strip()

            # Prefer an exact known website in the first phrase.
            site_key = None
            for alias in sorted(self.WEBSITE_ALIASES, key=len, reverse=True):
                if first == alias or first.endswith(" " + alias):
                    site_key = alias
                    break

            if site_key and query:
                base = self.WEBSITE_ALIASES[site_key]

                if site_key == "youtube":
                    url = "https://www.youtube.com/results?search_query=" + quote_plus(query)
                elif site_key in {"google", "gmail"}:
                    url = "https://www.google.com/search?q=" + quote_plus(query)
                elif site_key in {"github"}:
                    url = "https://github.com/search?q=" + quote_plus(query)
                elif site_key in {"stackoverflow", "stack overflow"}:
                    url = "https://stackoverflow.com/search?q=" + quote_plus(query)
                elif site_key == "reddit":
                    url = "https://www.reddit.com/search/?q=" + quote_plus(query)
                else:
                    url = base

                webbrowser.open_new_tab(url)
                return {
                    "success": True,
                    "configured": True,
                    "local_action": True,
                    "message": f"Opening {site_key.title()} and searching for {query}.",
                }

        # ----------------------------------------------------------
        # Open a known website
        # Examples:
        #   open YouTube
        #   launch Gmail
        #   go to GitHub
        #   take me to Google
        # ----------------------------------------------------------
        open_match = re.match(
            r"^(?:please\s+)?(?:open|launch|start|visit|go\s+to|take\s+me\s+to)\s+(.+?)\s*$",
            raw,
            re.IGNORECASE,
        )

        if open_match:
            target = open_match.group(1).strip().lower()
            target = re.sub(r"[.!?]+$", "", target).strip()

            # Remove conversational words while preserving site names.
            target = re.sub(r"^(the)\s+", "", target)

            if target in self.WEBSITE_ALIASES:
                url = self.WEBSITE_ALIASES[target]
                webbrowser.open_new_tab(url)
                return {
                    "success": True,
                    "configured": True,
                    "local_action": True,
                    "message": f"Opening {target.title()} in your browser.",
                }

            # Allow explicit safe web addresses such as "open example.com".
            if re.fullmatch(r"(?:https?://)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?", target):
                url = target if target.startswith("http") else "https://" + target
                webbrowser.open_new_tab(url)
                return {
                    "success": True,
                    "configured": True,
                    "local_action": True,
                    "message": "Opening the requested website in your browser.",
                }

        # ----------------------------------------------------------
        # Generic web search
        # Example: "search for Python decorators"
        # ----------------------------------------------------------
        generic_search = re.match(
            r"^(?:please\s+)?(?:search|google)\s+(?:for\s+)?(.+)$",
            raw,
            re.IGNORECASE,
        )

        if generic_search:
            query = generic_search.group(1).strip()
            if query:
                url = "https://www.google.com/search?q=" + quote_plus(query)
                webbrowser.open_new_tab(url)
                return {
                    "success": True,
                    "configured": True,
                    "local_action": True,
                    "message": f"Searching Google for {query}.",
                }

        return None

    # ==============================================================
    # MAIN AI REQUEST
    # ==============================================================

    def ask(
        self,
        user_text: str
    ) -> Dict[str, Any]:
        """Ask JARVIS and allow it to use safe tools."""

        user_text = (
            user_text or ""
        ).strip()

        if not user_text:

            return {
                "success": False,
                "configured": True,
                "message": "Please tell me what you need."
            }

        # ------------------------------------------------------
        # SMART LOCAL ROUTING
        # ------------------------------------------------------
        # Website navigation/search happens locally and consumes
        # ZERO OpenAI tokens. This is checked before any API call.
        local_result = self._local_web_action(user_text)
        if local_result:
            return local_result

        # Only non-local requests need the OpenAI API.
        if not self.enabled:
            return {
                "success": False,
                "configured": False,
                "message": (
                    "My general AI brain is not configured yet. "
                    "Local website and desktop actions are still available."
                )
            }

        self.pending_action = None

        try:

            # ------------------------------------------------------
            # FIRST AI REQUEST
            # ------------------------------------------------------

            response = self.client.responses.create(
                model=self.model,
                instructions=self.instructions,
                input=user_text,
                tools=self.tool_definitions(),
                previous_response_id=self.previous_response_id,
                max_output_tokens=1200
            )

            # ------------------------------------------------------
            # TOOL LOOP
            # ------------------------------------------------------

            for _ in range(6):

                calls = [
                    item
                    for item in (
                        getattr(
                            response,
                            "output",
                            []
                        )
                        or []
                    )
                    if getattr(
                        item,
                        "type",
                        ""
                    ) == "function_call"
                ]

                # --------------------------------------------------
                # NO TOOL CALL
                # --------------------------------------------------

                if not calls:

                    self.previous_response_id = response.id

                    message = self._response_text(
                        response
                    )

                    return {
                        "success": True,
                        "configured": True,
                        "message": message,
                        "response_id": response.id
                    }

                outputs = []

                approval_required = None

                # --------------------------------------------------
                # EXECUTE TOOL CALLS
                # --------------------------------------------------

                for call in calls:

                    try:

                        args = json.loads(
                            getattr(
                                call,
                                "arguments",
                                "{}"
                            )
                            or "{}"
                        )

                    except json.JSONDecodeError:

                        args = {}

                    result = self._execute_tool(
                        call.name,
                        args
                    )

                    # ----------------------------------------------
                    # APPROVAL REQUIRED
                    # ----------------------------------------------

                    if result.get(
                        "approval_required"
                    ):

                        approval_required = {
                            "response_id": response.id,
                            "call_id": call.call_id,
                            "name": call.name,
                            "args": args,
                            "risk": "MEDIUM"
                        }

                        break

                    # ----------------------------------------------
                    # NORMAL TOOL RESULT
                    # ----------------------------------------------

                    outputs.append(
                        {
                            "type": "function_call_output",
                            "call_id": call.call_id,
                            "output": json.dumps(
                                result,
                                ensure_ascii=False
                            )
                        }
                    )

                # --------------------------------------------------
                # PAUSE FOR USER APPROVAL
                # --------------------------------------------------

                if approval_required:

                    self.previous_response_id = response.id

                    self.pending_action = (
                        approval_required
                    )

                    return {
                        "success": True,
                        "configured": True,
                        "approval_required": True,
                        "message": self._approval_message(
                            approval_required
                        ),
                        "action": approval_required,
                        "response_id": response.id
                    }

                # --------------------------------------------------
                # SEND TOOL RESULTS BACK TO MODEL
                # --------------------------------------------------

                response = self.client.responses.create(
                    model=self.model,
                    instructions=self.instructions,
                    previous_response_id=response.id,
                    input=outputs,
                    tools=self.tool_definitions(),
                    max_output_tokens=1200
                )

            # ------------------------------------------------------
            # TOOL LOOP LIMIT
            # ------------------------------------------------------

            return {
                "success": False,
                "configured": True,
                "message": (
                    "I reached the action limit for this request. "
                    "Please try again."
                )
            }

        except Exception as exc:

            return {
                "success": False,
                "configured": True,
                "message": f"JARVIS AI error: {exc}"
            }

    # ==============================================================
    # APPROVAL MESSAGE
    # ==============================================================

    def _approval_message(
        self,
        action: Dict[str, Any]
    ) -> str:

        app = (
            action
            .get("args", {})
            .get(
                "application",
                "application"
            )
        )

        return (
            f"I can open {app}, but this is a medium-risk "
            "computer action. Please approve it before I continue."
        )

    # ==============================================================
    # APPROVE ACTION
    # ==============================================================

    def approve_pending_action(
        self
    ) -> Dict[str, Any]:

        action = self.pending_action

        if not action:

            return {
                "success": False,
                "message": "There is no pending action."
            }

        if action["name"] != "open_application":

            return {
                "success": False,
                "message": "Unsupported pending action."
            }

        app = action["args"]["application"]

        # ----------------------------------------------------------
        # ACTUALLY EXECUTE ALLOWLISTED APPLICATION
        # ----------------------------------------------------------

        ok, message = (
            self.tools.open_application(
                app
            )
        )

        output = {
            "type": "function_call_output",
            "call_id": action["call_id"],
            "output": json.dumps(
                {
                    "success": ok,
                    "message": message
                }
            )
        }

        try:

            response = self.client.responses.create(
                model=self.model,
                instructions=self.instructions,
                previous_response_id=action["response_id"],
                input=[output],
                tools=self.tool_definitions(),
                max_output_tokens=1200
            )

            self.previous_response_id = response.id

            self.pending_action = None

            return {
                "success": True,
                "message": self._response_text(
                    response
                ),
                "action_success": ok
            }

        except Exception as exc:

            self.pending_action = None

            return {
                "success": False,
                "message": (
                    "Could not continue the AI turn: "
                    f"{exc}"
                )
            }

    # ==============================================================
    # DENY ACTION
    # ==============================================================

    def deny_pending_action(
        self
    ) -> Dict[str, Any]:

        action = self.pending_action

        if not action:

            return {
                "success": False,
                "message": "There is no pending action."
            }

        output = {
            "type": "function_call_output",
            "call_id": action["call_id"],
            "output": json.dumps(
                {
                    "success": False,
                    "message": (
                        "The user denied this action."
                    )
                }
            )
        }

        try:

            response = self.client.responses.create(
                model=self.model,
                instructions=self.instructions,
                previous_response_id=action["response_id"],
                input=[output],
                tools=self.tool_definitions(),
                max_output_tokens=1200
            )

            self.previous_response_id = response.id

            self.pending_action = None

            return {
                "success": True,
                "message": self._response_text(
                    response
                )
            }

        except Exception as exc:

            self.pending_action = None

            return {
                "success": False,
                "message": (
                    "Could not continue the AI turn: "
                    f"{exc}"
                )
            }