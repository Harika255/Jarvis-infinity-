import ast
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


class CodingAgent:
    """
    Universal local code debugger for JARVIS Infinity.

    Supports:
    - Language detection
    - Static code analysis
    - Safe automatic fixes
    - Code verification
    - Python execution
    - Task-aware code generation
    """

    LANGUAGE_ALIASES = {
        "python": "python",
        "py": "python",
        "java": "java",
        "javascript": "javascript",
        "js": "javascript",
        "typescript": "typescript",
        "ts": "typescript",
        "c": "c",
        "cpp": "cpp",
        "c++": "cpp",
        "cxx": "cpp",
        "csharp": "csharp",
        "c#": "csharp",
        "html": "html",
        "css": "css",
        "sql": "sql",
        "json": "json",
        "rust": "rust",
        "rs": "rust",
        "go": "go",
        "golang": "go",
        "php": "php",
    }

    EXTENSIONS = {
        ".py": "python",
        ".java": "java",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".c": "c",
        ".h": "c",
        ".cpp": "cpp",
        ".cc": "cpp",
        ".cxx": "cpp",
        ".cs": "csharp",
        ".html": "html",
        ".htm": "html",
        ".css": "css",
        ".sql": "sql",
        ".json": "json",
        ".rs": "rust",
        ".go": "go",
        ".php": "php",
    }

    def __init__(self):
        self.project_root = Path(__file__).resolve().parent

    # ================================================================
    # LANGUAGE DETECTION
    # ================================================================

    def detect_language(self, code):
        if not code:
            return None

        text = code.strip()

        if not text:
            return None

        # HTML
        if re.search(
            r"^\s*(?:<!DOCTYPE\s+html|<html\b|<head\b|<body\b)",
            text,
            re.IGNORECASE,
        ):
            return "html"

        if re.search(
            r"<\s*(?:p|div|section|main|h1|h2|title)\b",
            text,
            re.IGNORECASE,
        ):
            return "html"

        # CSS
        if (
            re.search(
                r"^\s*[.#]?[A-Za-z_-][\w-]*\s*\{",
                text,
                re.MULTILINE,
            )
            and re.search(
                r"\b(?:width|height|margin|padding|color|background|"
                r"display|font|border|position|grid|flex)\s*:",
                text,
                re.IGNORECASE,
            )
        ):
            return "css"

        # JSON
        if text.startswith("{") or text.startswith("["):
            try:
                json.loads(text)
                return "json"
            except json.JSONDecodeError:
                pass

        # Java
        if re.search(r"\bpublic\s+class\s+\w+", text):
            return "java"

        if re.search(r"\bSystem\.out\.println\s*\(", text):
            return "java"

        # C++
        if (
            re.search(r"#include\s*<iostream>", text)
            or "std::" in text
            or re.search(r"\busing\s+namespace\s+std\b", text)
            or re.search(r"\bcout\s*<<", text)
            or re.search(r"\bcin\s*>>", text)
        ):
            return "cpp"

        # C
        if re.search(
            r"#include\s*<(?:stdio|stdlib|string|math)\.h>",
            text,
        ):
            return "c"

        if re.search(r"\b(?:printf|scanf)\s*\(", text):
            return "c"

        # C#
        if re.search(r"\busing\s+System\s*;", text):
            return "csharp"

        if re.search(r"\bConsole\.WriteLine\s*\(", text):
            return "csharp"

        # Rust
        if re.search(r"\bfn\s+main\s*\(", text):
            return "rust"

        if "println!(" in text:
            return "rust"

        # Go
        if re.search(r"\bpackage\s+main\b", text):
            return "go"

        if re.search(r"\bfunc\s+main\s*\(", text):
            return "go"

        # PHP
        if re.search(r"<\?php\b", text, re.IGNORECASE):
            return "php"

        # SQL
        if re.search(
            r"\b(?:SELECT|INSERT\s+INTO|UPDATE|DELETE\s+FROM|"
            r"CREATE\s+TABLE|ALTER\s+TABLE|DROP\s+TABLE|WITH)\b",
            text,
            re.IGNORECASE,
        ):
            return "sql"

        # JavaScript / TypeScript
        if (
            re.search(r"\b(?:function|const|let|var)\b", text)
            or "console.log(" in text
            or "=>" in text
        ):
            if re.search(
                r":\s*(?:string|number|boolean|any|unknown)\b",
                text,
            ):
                return "typescript"

            return "javascript"

        # Python
        if (
            re.search(r"\b(?:def|import|from)\s+\w+", text)
            or re.search(r"\bprint\s*\(", text)
            or re.search(
                r"\bif\s+.+:\s*$",
                text,
                re.MULTILINE,
            )
            or re.search(
                r"\bfor\s+\w+\s+in\s+.+:",
                text,
            )
        ):
            return "python"

        return None

    # ================================================================
    # ACTION DETECTION
    # ================================================================

    def detect_action(self, command):
        text = (command or "").lower()

        if any(
            word in text
            for word in (
                "debug",
                "fix",
                "find error",
                "find bug",
                "correct",
            )
        ):
            return "DEBUG"

        if any(
            word in text
            for word in (
                "explain",
                "analyze",
                "analyse",
            )
        ):
            return "ANALYZE"

        if any(
            word in text
            for word in (
                "run",
                "execute",
            )
        ):
            return "RUN"

        return "DEBUG"

    # ================================================================
    # HELPERS
    # ================================================================

    def _error(
        self,
        kind,
        severity,
        line,
        message,
        suggestion=None,
    ):
        item = {
            "type": kind,
            "severity": severity,
            "line": line,
            "message": message,
        }

        if suggestion:
            item["suggestion"] = suggestion

        return item

    def _base(self):
        return {
            "errors": [],
            "warnings": [],
            "valid": True,
        }

    def _balanced(self, code, opening, closing):
        return code.count(opening) == code.count(closing)

    # ================================================================
    # CODE ANALYSIS
    # ================================================================

    def analyze_code(self, code, language=None):
        language = language or self.detect_language(code)

        if not language:
            return {
                "language": None,
                "errors": [
                    self._error(
                        "language",
                        "error",
                        1,
                        "Could not confidently detect the programming language.",
                        "Specify the programming language or provide more code.",
                    )
                ],
                "warnings": [],
                "valid": False,
            }

        language = self.LANGUAGE_ALIASES.get(
            language.lower(),
            language.lower(),
        )

        analyzers = {
            "python": self._analyze_python,
            "java": self._analyze_java,
            "javascript": self._analyze_javascript,
            "typescript": self._analyze_javascript,
            "c": self._analyze_c,
            "cpp": self._analyze_cpp,
            "csharp": self._analyze_csharp,
            "html": self._analyze_html,
            "css": self._analyze_css,
            "sql": self._analyze_sql,
            "json": self._analyze_json,
            "rust": self._analyze_rust,
            "go": self._analyze_go,
            "php": self._analyze_php,
        }

        analyzer = analyzers.get(
            language,
            self._analyze_generic,
        )

        result = analyzer(code)

        result["language"] = language

        result.setdefault(
            "warnings",
            [],
        )

        result["valid"] = not any(
            error.get("severity") == "error"
            for error in result.get("errors", [])
        )

        return result

    # ================================================================
    # PYTHON ANALYSIS
    # ================================================================

    def _analyze_python(self, code):
        result = self._base()

        try:
            ast.parse(code)
        except SyntaxError as error:
            result["errors"].append(
                self._error(
                    "syntax",
                    "error",
                    error.lineno or 1,
                    error.msg,
                    "Fix the Python syntax at this line.",
                )
            )

            return result

        if re.search(
            r"\b(?:TODO|pass)\b",
            code,
            re.IGNORECASE,
        ):
            result["warnings"].append(
                {
                    "line": 1,
                    "message": (
                        "The Python code contains TODO/pass-style "
                        "placeholder logic."
                    ),
                    "suggestion": (
                        "Replace placeholder logic with the required implementation."
                    ),
                }
            )

        return result

    # ================================================================
    # SEMICOLON CHECK
    # ================================================================

    def _check_semicolons(self, code, result):
        for number, line in enumerate(
            code.splitlines(),
            1,
        ):
            stripped = line.strip()

            if not stripped:
                continue

            if stripped.startswith(
                (
                    "//",
                    "#",
                )
            ):
                continue

            if stripped.endswith(
                (
                    "{",
                    "}",
                    ";",
                    ":",
                )
            ):
                continue

            if re.match(
                r"^(?:int|float|double|char|long|short|byte|"
                r"boolean|String|bool|auto)\s+\w+",
                stripped,
            ) and "=" in stripped:

                result["errors"].append(
                    self._error(
                        "syntax",
                        "error",
                        number,
                        "Statement appears to be missing a semicolon.",
                        "Add ';' at the end of the statement.",
                    )
                )

    # ================================================================
    # JAVA ANALYSIS
    # ================================================================

    def _analyze_java(self, code):
        result = self._base()

        self._check_semicolons(
            code,
            result,
        )

        if not self._balanced(
            code,
            "{",
            "}",
        ):
            result["errors"].append(
                self._error(
                    "syntax",
                    "error",
                    1,
                    "Unbalanced curly braces.",
                    "Check that every '{' has a matching '}'.",
                )
            )

        for number, line in enumerate(
            code.splitlines(),
            1,
        ):
            if "System.out.println(" in line:
                if not line.rstrip().endswith(";"):
                    result["errors"].append(
                        self._error(
                            "syntax",
                            "error",
                            number,
                            "Missing semicolon after System.out.println.",
                            "Add ';' at the end.",
                        )
                    )

        return result

    # ================================================================
    # JAVASCRIPT ANALYSIS
    # ================================================================

    def _analyze_javascript(self, code):
        result = self._base()

        if not self._balanced(
            code,
            "{",
            "}",
        ):
            result["errors"].append(
                self._error(
                    "syntax",
                    "error",
                    1,
                    "Unbalanced curly braces.",
                    "Check the opening and closing braces.",
                )
            )

        if not self._balanced(
            code,
            "(",
            ")",
        ):
            result["errors"].append(
                self._error(
                    "syntax",
                    "error",
                    1,
                    "Unbalanced parentheses.",
                    "Check the opening and closing parentheses.",
                )
            )

        for number, line in enumerate(
            code.splitlines(),
            1,
        ):
            stripped = line.strip()

            if (
                stripped.startswith("console.log(")
                and not stripped.endswith(
                    (
                        ";",
                        "}",
                    )
                )
            ):
                result["warnings"].append(
                    {
                        "line": number,
                        "message": (
                            "Statement has no semicolon. "
                            "This is usually valid JavaScript."
                        ),
                    }
                )

        return result

    # ================================================================
    # C ANALYSIS
    # ================================================================

    def _analyze_c(self, code):
        result = self._base()

        self._check_semicolons(
            code,
            result,
        )

        if not self._balanced(
            code,
            "{",
            "}",
        ):
            result["errors"].append(
                self._error(
                    "syntax",
                    "error",
                    1,
                    "Unbalanced curly braces.",
                    "Check the C block structure.",
                )
            )

        return result

    # ================================================================
    # C++ ANALYSIS
    # ================================================================

    def _analyze_cpp(self, code):
        result = self._base()

        self._check_semicolons(
            code,
            result,
        )

        if not self._balanced(
            code,
            "{",
            "}",
        ):
            result["errors"].append(
                self._error(
                    "syntax",
                    "error",
                    1,
                    "Unbalanced curly braces.",
                    "Check the C++ block structure.",
                )
            )

        return result

    # ================================================================
    # C# ANALYSIS
    # ================================================================

    def _analyze_csharp(self, code):
        result = self._base()

        self._check_semicolons(
            code,
            result,
        )

        if not self._balanced(
            code,
            "{",
            "}",
        ):
            result["errors"].append(
                self._error(
                    "syntax",
                    "error",
                    1,
                    "Unbalanced curly braces.",
                    "Check the C# block structure.",
                )
            )

        return result

    # ================================================================
    # HTML ANALYSIS
    # ================================================================

    def _analyze_html(self, code):
        result = self._base()

        void_tags = {
            "area",
            "base",
            "br",
            "col",
            "embed",
            "hr",
            "img",
            "input",
            "link",
            "meta",
            "param",
            "source",
            "track",
            "wbr",
        }

        stack = []

        token_re = re.compile(
            r"<\s*(/?)\s*([A-Za-z][\w-]*)\b[^>]*>",
            re.IGNORECASE,
        )

        for match in token_re.finditer(code):
            closing = bool(match.group(1))
            tag = match.group(2).lower()
            full = match.group(0)

            if (
                tag in void_tags
                or full.rstrip().endswith("/>")
            ):
                continue

            line = (
                code[:match.start()].count("\n")
                + 1
            )

            if closing:
                if not stack or stack[-1][0] != tag:
                    result["errors"].append(
                        self._error(
                            "markup",
                            "error",
                            line,
                            f"Unexpected closing </{tag}> tag.",
                            f"Check the matching opening <{tag}> tag.",
                        )
                    )
                else:
                    stack.pop()

            else:
                stack.append(
                    (
                        tag,
                        line,
                    )
                )

        for tag, line in stack:
            result["errors"].append(
                self._error(
                    "markup",
                    "error",
                    line,
                    f"Unclosed <{tag}> tag.",
                    f"Add </{tag}>.",
                )
            )

        return result

    # ================================================================
    # CSS ANALYSIS
    # ================================================================

    def _analyze_css(self, code):
        result = self._base()

        if not self._balanced(
            code,
            "{",
            "}",
        ):
            result["errors"].append(
                self._error(
                    "syntax",
                    "error",
                    1,
                    "Unbalanced CSS braces.",
                    "Check every selector block.",
                )
            )

        if not self._balanced(
            code,
            "(",
            ")",
        ):
            result["errors"].append(
                self._error(
                    "syntax",
                    "error",
                    1,
                    "Unbalanced CSS parentheses.",
                    "Check CSS functions such as calc() or rgb().",
                )
            )

        if "background-colour:" in code:
            line = (
                code.find("background-colour:")
            )

            line = (
                code[:line].count("\n")
                + 1
            )

            result["errors"].append(
                self._error(
                    "property",
                    "error",
                    line,
                    "Unknown CSS property 'background-colour'.",
                    "Use 'background-color'.",
                )
            )

        return result

    # ================================================================
    # SQL ANALYSIS
    # ================================================================

    def _analyze_sql(self, code):
        result = self._base()

        text = code.strip()

        if not text:
            result["errors"].append(
                self._error(
                    "sql",
                    "error",
                    1,
                    "SQL code is empty.",
                )
            )

            return result

        if not re.match(
            r"^(?:SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|WITH)\b",
            text,
            re.IGNORECASE,
        ):
            result["errors"].append(
                self._error(
                    "sql",
                    "error",
                    1,
                    "SQL statement does not start with a recognized SQL command.",
                    (
                        "Start with SELECT, INSERT, UPDATE, DELETE, "
                        "CREATE, ALTER, DROP, or WITH."
                    ),
                )
            )

        return result

    # ================================================================
    # JSON ANALYSIS
    # ================================================================

    def _analyze_json(self, code):
        result = self._base()

        try:
            json.loads(code)
        except json.JSONDecodeError as error:
            result["errors"].append(
                self._error(
                    "json",
                    "error",
                    error.lineno,
                    error.msg,
                    "Fix the JSON syntax, commas, quotes, or brackets.",
                )
            )

        return result

    # ================================================================
    # RUST ANALYSIS
    # ================================================================

    def _analyze_rust(self, code):
        result = self._base()

        if not self._balanced(
            code,
            "{",
            "}",
        ):
            result["errors"].append(
                self._error(
                    "syntax",
                    "error",
                    1,
                    "Unbalanced curly braces.",
                    "Check the Rust block structure.",
                )
            )

        return result

    # ================================================================
    # GO ANALYSIS
    # ================================================================

    def _analyze_go(self, code):
        result = self._base()

        if not self._balanced(
            code,
            "{",
            "}",
        ):
            result["errors"].append(
                self._error(
                    "syntax",
                    "error",
                    1,
                    "Unbalanced curly braces.",
                    "Check the Go block structure.",
                )
            )

        return result

    # ================================================================
    # PHP ANALYSIS
    # ================================================================

    def _analyze_php(self, code):
        result = self._base()

        if not self._balanced(
            code,
            "{",
            "}",
        ):
            result["errors"].append(
                self._error(
                    "syntax",
                    "error",
                    1,
                    "Unbalanced curly braces.",
                    "Check the PHP block structure.",
                )
            )

        return result

    # ================================================================
    # GENERIC ANALYSIS
    # ================================================================

    def _analyze_generic(self, code):
        result = self._base()

        if not self._balanced(
            code,
            "{",
            "}",
        ):
            result["errors"].append(
                self._error(
                    "syntax",
                    "error",
                    1,
                    "Unbalanced curly braces.",
                    "Check matching braces.",
                )
            )

        return result

    # ================================================================
    # SAFE FIX
    # ================================================================

    def safe_fix(self, code, language=None):
        language = language or self.detect_language(code)

        if not language:
            return {
                "fixed": False,
                "fixed_code": code,
                "changes": [],
            }

        language = self.LANGUAGE_ALIASES.get(
            language.lower(),
            language.lower(),
        )

        if language == "python":
            return self._safe_fix_python(code)

        if language in {
            "java",
            "c",
            "cpp",
            "csharp",
            "rust",
        }:
            return self._safe_fix_c_family(
                code,
                language,
            )

        if language in {
            "javascript",
            "typescript",
        }:
            return self._safe_fix_javascript(code)

        if language == "html":
            return self._safe_fix_html(code)

        if language == "css":
            return self._safe_fix_css(code)

        if language == "json":
            return self._safe_fix_json(code)

        return {
            "fixed": False,
            "fixed_code": code,
            "changes": [],
        }

    # ================================================================
    # PYTHON SAFE FIX
    # ================================================================

    def _safe_fix_python(self, code):
        lines = code.splitlines()
        fixed_lines = []
        changes = []

        pattern = re.compile(
            r"^(\s*)def\s+\w+\s*\(.*\)\s*:?\s*$"
        )

        for number, line in enumerate(
            lines,
            1,
        ):
            match = pattern.match(line)

            if (
                match
                and not line.rstrip().endswith(":")
            ):
                new_line = line.rstrip() + ":"

                fixed_lines.append(
                    new_line
                )

                changes.append(
                    {
                        "line": number,
                        "description": (
                            "Added missing ':' "
                            "to the function definition."
                        ),
                    }
                )

            else:
                fixed_lines.append(line)

        fixed_code = "\n".join(
            fixed_lines
        )

        return {
            "fixed": fixed_code != code,
            "fixed_code": fixed_code,
            "changes": changes,
        }

    # ================================================================
    # C / C++ / JAVA / C# / RUST FIX
    # ================================================================

    def _safe_fix_c_family(
        self,
        code,
        language,
    ):
        lines = code.splitlines()
        fixed_lines = []
        changes = []

        for number, line in enumerate(
            lines,
            1,
        ):
            new_line = line
            stripped = line.strip()

            # Rust println!
            if (
                language == "rust"
                and stripped.startswith("println!(")
                and not stripped.endswith(";")
            ):
                new_line = line.rstrip() + ";"

                changes.append(
                    {
                        "line": number,
                        "description": (
                            "Added missing ';' after println!."
                        ),
                    }
                )

            # Java / C / C++ / C#
            elif language in {
                "java",
                "c",
                "cpp",
                "csharp",
            }:

                declaration = re.match(
                    r"^(\s*)(?:int|float|double|char|"
                    r"bool|boolean|String|long|short|auto)"
                    r"\s+\w+.*=\s*[^;{}]+$",
                    line,
                )

                if declaration:
                    new_line = line.rstrip() + ";"

                    changes.append(
                        {
                            "line": number,
                            "description": (
                                "Added missing semicolon."
                            ),
                        }
                    )

                if (
                    language == "java"
                    and "System.out.println(" in line
                    and not line.rstrip().endswith(";")
                ):
                    new_line = line.rstrip() + ";"

                    changes.append(
                        {
                            "line": number,
                            "description": (
                                "Added missing semicolon "
                                "to System.out.println."
                            ),
                        }
                    )

            fixed_lines.append(
                new_line
            )

        fixed_code = "\n".join(
            fixed_lines
        )

        return {
            "fixed": fixed_code != code,
            "fixed_code": fixed_code,
            "changes": changes,
        }

    # ================================================================
    # JAVASCRIPT SAFE FIX
    # ================================================================

    def _safe_fix_javascript(self, code):
        lines = code.splitlines()
        fixed_lines = []
        changes = []

        for number, line in enumerate(
            lines,
            1,
        ):
            stripped = line.strip()

            if (
                stripped.startswith("console.log(")
                and not stripped.endswith(
                    (
                        ";",
                        "}",
                    )
                )
            ):
                fixed_lines.append(
                    line.rstrip() + ";"
                )

                changes.append(
                    {
                        "line": number,
                        "description": (
                            "Added missing semicolon."
                        ),
                    }
                )

            else:
                fixed_lines.append(line)

        fixed_code = "\n".join(
            fixed_lines
        )

        if (
            fixed_code.count("{")
            > fixed_code.count("}")
        ):
            fixed_code += "\n}"

            changes.append(
                {
                    "line": len(fixed_lines) + 1,
                    "description": (
                        "Added missing closing '}'."
                    ),
                }
            )

        return {
            "fixed": fixed_code != code,
            "fixed_code": fixed_code,
            "changes": changes,
        }

    # ================================================================
    # HTML SAFE FIX
    # ================================================================

    def _safe_fix_html(self, code):
        fixed = code
        changes = []

        for tag in (
            "html",
            "head",
            "body",
            "main",
            "section",
            "div",
            "p",
        ):
            opening = len(
                re.findall(
                    rf"<{tag}\b",
                    fixed,
                    re.IGNORECASE,
                )
            )

            closing = len(
                re.findall(
                    rf"</{tag}>",
                    fixed,
                    re.IGNORECASE,
                )
            )

            if opening > closing:
                fixed += f"\n</{tag}>"

                changes.append(
                    {
                        "line": len(
                            fixed.splitlines()
                        ),
                        "description": (
                            f"Added missing </{tag}> "
                            "closing tag."
                        ),
                    }
                )

        return {
            "fixed": fixed != code,
            "fixed_code": fixed,
            "changes": changes,
        }

    # ================================================================
    # CSS SAFE FIX
    # ================================================================

    def _safe_fix_css(self, code):
        fixed = code.replace(
            "background-colour:",
            "background-color:",
        )

        changes = []

        if fixed != code:
            changes.append(
                {
                    "line": 1,
                    "description": (
                        "Changed invalid "
                        "'background-colour' "
                        "to 'background-color'."
                    ),
                }
            )

        return {
            "fixed": fixed != code,
            "fixed_code": fixed,
            "changes": changes,
        }

    # ================================================================
    # JSON SAFE FIX
    # ================================================================

    def _safe_fix_json(self, code):
        fixed = re.sub(
            r",(\s*[}\]])",
            r"\1",
            code,
        )

        changes = []

        if fixed != code:
            changes.append(
                {
                    "line": 1,
                    "description": (
                        "Removed trailing comma from JSON."
                    ),
                }
            )

        return {
            "fixed": fixed != code,
            "fixed_code": fixed,
            "changes": changes,
        }

    # ================================================================
    # VERIFICATION
    # ================================================================

    def verify_code(self, code, language=None):
        language = language or self.detect_language(code)

        if not language:
            return {
                "verified": False,
                "language": None,
                "errors": [
                    self._error(
                        "language",
                        "error",
                        1,
                        (
                            "I could not confidently "
                            "detect the programming language."
                        ),
                    )
                ],
                "warnings": [],
            }

        language = self.LANGUAGE_ALIASES.get(
            language.lower(),
            language.lower(),
        )

        # Python
        if language == "python":
            return self.verify_python(code)

        # JSON
        if language == "json":
            analysis = self._analyze_json(code)

            return {
                "verified": analysis["valid"],
                "language": language,
                "errors": analysis["errors"],
                "warnings": analysis["warnings"],
            }

        # C
        if language == "c":
            compiler_result = (
                self.verify_c_with_compiler(code)
            )

            if compiler_result["compiler_available"]:
                return {
                    "verified": compiler_result["verified"],
                    "language": "c",
                    "errors": compiler_result["errors"],
                    "warnings": compiler_result["warnings"],
                    "compiler": compiler_result["compiler"],
                    "compiler_stderr": compiler_result["stderr"],
                }

        # Other languages
        analysis = self.analyze_code(
            code,
            language,
        )

        return {
            "verified": analysis["valid"],
            "language": language,
            "errors": analysis["errors"],
            "warnings": analysis["warnings"],
        }

    # ================================================================
    # PYTHON VERIFICATION
    # ================================================================

    def verify_python(self, code):
        try:
            ast.parse(code)

            return {
                "verified": True,
                "language": "python",
                "errors": [],
                "warnings": [],
            }

        except SyntaxError as error:
            return {
                "verified": False,
                "language": "python",
                "errors": [
                    self._error(
                        "syntax",
                        "error",
                        error.lineno or 1,
                        error.msg,
                        "Fix the Python syntax at this line.",
                    )
                ],
                "warnings": [],
            }

    # ================================================================
    # C COMPILER
    # ================================================================

    def _find_c_compiler(self):
        """
        Find a local C compiler.

        Checks:
        - gcc
        - clang
        - cc
        """
        for name in (
            "gcc",
            "clang",
            "cc",
        ):
            compiler = shutil.which(name)

            if compiler:
                return compiler

        return None

    def verify_c_with_compiler(self, code):
        """
        Check C syntax using a local compiler.

        The C program is NOT executed.
        Only syntax checking is performed.
        """

        compiler = self._find_c_compiler()

        if not compiler:
            return {
                "verified": False,
                "compiler_available": False,
                "compiler": None,
                "stdout": "",
                "stderr": (
                    "No C compiler "
                    "(gcc/clang/cc) was found."
                ),
                "errors": [
                    self._error(
                        "compiler",
                        "error",
                        1,
                        (
                            "C compiler is not installed "
                            "or not available on PATH."
                        ),
                        (
                            "Install GCC or Clang "
                            "and reopen the terminal."
                        ),
                    )
                ],
                "warnings": [],
            }

        temp_path = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".c",
                delete=False,
                encoding="utf-8",
            ) as handle:
                handle.write(code)
                temp_path = handle.name

            result = subprocess.run(
                [
                    compiler,
                    "-fsyntax-only",
                    temp_path,
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            stdout = (
                result.stdout or ""
            ).strip()

            stderr = (
                result.stderr or ""
            ).strip()

            if result.returncode == 0:
                return {
                    "verified": True,
                    "compiler_available": True,
                    "compiler": compiler,
                    "stdout": stdout,
                    "stderr": stderr,
                    "errors": [],
                    "warnings": [],
                }

            errors = []

            compiler_pattern = re.compile(
                r":(?P<line>\d+)"
                r"(?::(?P<column>\d+))?:\s*"
                r"(?:fatal\s+)?error:\s*"
                r"(?P<message>.*)",
                re.IGNORECASE,
            )

            for compiler_line in stderr.splitlines():
                match = compiler_pattern.search(
                    compiler_line
                )

                if match:
                    errors.append(
                        self._error(
                            "compiler",
                            "error",
                            int(
                                match.group("line")
                            ),
                            match.group(
                                "message"
                            ).strip(),
                            "Fix the compiler error at this line.",
                        )
                    )

            if not errors:
                errors.append(
                    self._error(
                        "compiler",
                        "error",
                        1,
                        stderr or "C compilation failed.",
                        "Review the compiler output.",
                    )
                )

            return {
                "verified": False,
                "compiler_available": True,
                "compiler": compiler,
                "stdout": stdout,
                "stderr": stderr,
                "errors": errors,
                "warnings": [],
            }

        except subprocess.TimeoutExpired:
            return {
                "verified": False,
                "compiler_available": True,
                "compiler": compiler,
                "stdout": "",
                "stderr": (
                    "C syntax check timed out."
                ),
                "errors": [
                    self._error(
                        "compiler",
                        "error",
                        1,
                        "C syntax check timed out.",
                    )
                ],
                "warnings": [],
            }

        except Exception as error:
            return {
                "verified": False,
                "compiler_available": True,
                "compiler": compiler,
                "stdout": "",
                "stderr": str(error),
                "errors": [
                    self._error(
                        "compiler",
                        "error",
                        1,
                        str(error),
                    )
                ],
                "warnings": [],
            }

        finally:
            if temp_path:
                try:
                    Path(temp_path).unlink(
                        missing_ok=True
                    )
                except Exception:
                    pass

    # ================================================================
    # PYTHON EXECUTION
    # ================================================================

    def run_python(self, code):
        try:
            result = subprocess.run(
                [
                    "python",
                    "-c",
                    code,
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            return {
                "success": result.returncode == 0,
                "stdout": (
                    result.stdout or ""
                ).strip(),
                "stderr": (
                    result.stderr or ""
                ).strip(),
                "returncode": result.returncode,
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": (
                    "Python execution timed out "
                    "after 10 seconds."
                ),
                "returncode": -1,
            }

        except Exception as error:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(error),
                "returncode": -1,
            }

    # ================================================================
    # RUN FILE
    # ================================================================

    def run_file(self, path):
        path = Path(path)

        try:
            if path.suffix.lower() == ".py":
                return self.run_python(
                    path.read_text(
                        encoding="utf-8"
                    )
                )

            return {
                "success": False,
                "stdout": "",
                "stderr": (
                    f"Execution for {path.suffix} "
                    "is not enabled in the local safe runner."
                ),
                "returncode": -1,
            }

        except Exception as error:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(error),
                "returncode": -1,
            }

    # ================================================================
    # CODE GENERATION
    # ================================================================

    def generate_code(self, request):
        """
        Generate task-aware code.

        Supported:
        Python
        Java
        JavaScript
        HTML
        CSS
        """

        request = (request or "").strip()
        lower = request.lower()

        if not request:
            return {
                "success": False,
                "language": None,
                "code": "",
                "message": (
                    "Please provide a programming task."
                ),
            }

        # Detect requested language
        if re.search(
            r"\b(python|py)\b",
            lower,
        ):
            language = "python"

        elif re.search(
            r"\bjava\b",
            lower,
        ):
            language = "java"

        elif re.search(
            r"\b(javascript|js)\b",
            lower,
        ):
            language = "javascript"

        elif re.search(
            r"\bhtml\b",
            lower,
        ):
            language = "html"

        elif re.search(
            r"\bcss\b",
            lower,
        ):
            language = "css"

        else:
            return {
                "success": False,
                "language": None,
                "code": "",
                "message": (
                    "Please specify Python, Java, "
                    "JavaScript, HTML, or CSS."
                ),
            }

        code = ""

        # ============================================================
        # PYTHON
        # ============================================================

        if language == "python":

            if "prime" in lower:
                code = '''def is_prime(n):
    if n < 2:
        return False

    if n == 2:
        return True

    if n % 2 == 0:
        return False

    divisor = 3

    while divisor * divisor <= n:
        if n % divisor == 0:
            return False

        divisor += 2

    return True


def main():
    number = 17

    print(
        f"{number} is prime: "
        f"{is_prime(number)}"
    )


if __name__ == "__main__":
    main()
'''

            elif "factorial" in lower:
                code = '''def factorial(n):
    if n < 0:
        raise ValueError(
            "Factorial is not defined for negative numbers"
        )

    result = 1

    for value in range(2, n + 1):
        result *= value

    return result


def main():
    number = 5

    print(
        f"{number}! = "
        f"{factorial(number)}"
    )


if __name__ == "__main__":
    main()
'''

            elif "fibonacci" in lower:
                code = '''def fibonacci(n):
    sequence = []

    a = 0
    b = 1

    for _ in range(n):
        sequence.append(a)
        a, b = b, a + b

    return sequence


def main():
    print(fibonacci(10))


if __name__ == "__main__":
    main()
'''

            elif "palindrome" in lower:
                code = '''def is_palindrome(value):
    text = str(value)

    return text == text[::-1]


def main():
    value = "madam"

    print(
        f"{value} is palindrome: "
        f"{is_palindrome(value)}"
    )


if __name__ == "__main__":
    main()
'''

            elif "student" in lower:
                code = '''class Student:
    def __init__(self, name, marks):
        self.name = name
        self.marks = marks

    def average(self):
        return sum(self.marks) / len(self.marks)


def main():
    student = Student(
        "Harika",
        [85, 90, 88]
    )

    print(
        f"Student: {student.name}"
    )

    print(
        f"Average: "
        f"{student.average():.2f}"
    )


if __name__ == "__main__":
    main()
'''

            elif (
                "calculator" in lower
                or "calculate" in lower
            ):
                code = '''def calculator(a, b, operator):
    if operator == "+":
        return a + b

    if operator == "-":
        return a - b

    if operator == "*":
        return a * b

    if operator == "/":
        if b == 0:
            raise ZeroDivisionError(
                "Cannot divide by zero"
            )

        return a / b

    raise ValueError(
        "Unsupported operator"
    )


def main():
    print(
        "10 * 5 =",
        calculator(10, 5, "*")
    )


if __name__ == "__main__":
    main()
'''

            elif (
                "reverse" in lower
                and (
                    "string" in lower
                    or "text" in lower
                )
            ):
                code = '''def reverse_text(text):
    return text[::-1]


def main():
    print(
        reverse_text("JARVIS")
    )


if __name__ == "__main__":
    main()
'''

            elif (
                "even" in lower
                and "odd" in lower
            ):
                code = '''def check_number(n):
    if n % 2 == 0:
        return "even"

    return "odd"


def main():
    number = 17

    print(
        f"{number} is "
        f"{check_number(number)}"
    )


if __name__ == "__main__":
    main()
'''

            else:
                return {
                    "success": False,
                    "language": "python",
                    "code": "",
                    "message": (
                        "I could not generate a reliable "
                        "Python solution. Please provide "
                        "the exact problem statement."
                    ),
                }

        # ============================================================
        # JAVA
        # ============================================================

        elif language == "java":

            if "prime" in lower:
                code = '''public class Main {

    static boolean isPrime(int n) {
        if (n < 2) {
            return false;
        }

        if (n == 2) {
            return true;
        }

        if (n % 2 == 0) {
            return false;
        }

        for (int d = 3; d * d <= n; d += 2) {
            if (n % d == 0) {
                return false;
            }
        }

        return true;
    }

    public static void main(String[] args) {
        int number = 17;

        System.out.println(
            number
            + " is prime: "
            + isPrime(number)
        );
    }
}
'''

            elif "factorial" in lower:
                code = '''public class Main {

    static long factorial(int n) {
        long result = 1;

        for (int i = 2; i <= n; i++) {
            result *= i;
        }

        return result;
    }

    public static void main(String[] args) {
        int number = 5;

        System.out.println(
            number
            + "! = "
            + factorial(number)
        );
    }
}
'''

            elif (
                "calculator" in lower
                or "calculate" in lower
            ):
                code = '''public class Main {

    public static void main(String[] args) {

        double a = 10;
        double b = 5;

        char operator = '*';

        double result;

        switch (operator) {

            case '+':
                result = a + b;
                break;

            case '-':
                result = a - b;
                break;

            case '*':
                result = a * b;
                break;

            case '/':
                if (b == 0) {
                    throw new ArithmeticException(
                        "Cannot divide by zero"
                    );
                }

                result = a / b;
                break;

            default:
                throw new IllegalArgumentException(
                    "Unsupported operator"
                );
        }

        System.out.println(
            a
            + " "
            + operator
            + " "
            + b
            + " = "
            + result
        );
    }
}
'''

            elif "student" in lower:
                code = '''public class Main {

    static class Student {

        String name;
        int[] marks;

        Student(
            String name,
            int[] marks
        ) {
            this.name = name;
            this.marks = marks;
        }

        double average() {

            int total = 0;

            for (int mark : marks) {
                total += mark;
            }

            return (double) total
                / marks.length;
        }
    }

    public static void main(
        String[] args
    ) {

        Student student =
            new Student(
                "Harika",
                new int[]{85, 90, 88}
            );

        System.out.println(
            "Student: "
            + student.name
        );

        System.out.printf(
            "Average: %.2f%n",
            student.average()
        );
    }
}
'''

            else:
                return {
                    "success": False,
                    "language": "java",
                    "code": "",
                    "message": (
                        "I could not generate a reliable "
                        "Java solution. Please provide "
                        "the exact problem statement."
                    ),
                }

        # ============================================================
        # JAVASCRIPT
        # ============================================================

        elif language == "javascript":

            if "prime" in lower:
                code = '''function isPrime(n) {

    if (n < 2) {
        return false;
    }

    if (n === 2) {
        return true;
    }

    if (n % 2 === 0) {
        return false;
    }

    for (
        let d = 3;
        d * d <= n;
        d += 2
    ) {
        if (n % d === 0) {
            return false;
        }
    }

    return true;
}

const number = 17;

console.log(
    `${number} is prime: ${isPrime(number)}`
);
'''

            elif "factorial" in lower:
                code = '''function factorial(n) {

    let result = 1;

    for (
        let i = 2;
        i <= n;
        i++
    ) {
        result *= i;
    }

    return result;
}

const number = 5;

console.log(
    `${number}! = ${factorial(number)}`
);
'''

            elif (
                "calculator" in lower
                or "calculate" in lower
            ):
                code = '''function calculator(
    a,
    b,
    operator
) {

    if (operator === "+") {
        return a + b;
    }

    if (operator === "-") {
        return a - b;
    }

    if (operator === "*") {
        return a * b;
    }

    if (operator === "/") {

        if (b === 0) {
            throw new Error(
                "Cannot divide by zero"
            );
        }

        return a / b;
    }

    throw new Error(
        "Unsupported operator"
    );
}

console.log(
    "10 * 5 =",
    calculator(10, 5, "*")
);
'''

            elif (
                "todo" in lower
                or "to-do" in lower
            ):
                code = '''const todos = [];

function addTodo(task) {

    todos.push({
        task: task,
        completed: false
    });
}

function completeTodo(index) {

    if (todos[index]) {
        todos[index].completed = true;
    }
}

addTodo(
    "Complete JARVIS project"
);

completeTodo(0);

console.log(todos);
'''

            else:
                return {
                    "success": False,
                    "language": "javascript",
                    "code": "",
                    "message": (
                        "I could not generate a reliable "
                        "JavaScript solution. Please provide "
                        "the exact problem statement."
                    ),
                }

        # ============================================================
        # HTML
        # ============================================================

        elif language == "html":

            if "portfolio" in lower:
                code = '''<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>Portfolio</title>
</head>

<body>

    <header>
        <h1>My Portfolio</h1>

        <p>
            Computer Science & Engineering Student
        </p>
    </header>

    <main>

        <section>
            <h2>About Me</h2>

            <p>
                Welcome to my portfolio.
            </p>
        </section>

        <section>
            <h2>Projects</h2>

            <p>
                JARVIS Infinity and other projects.
            </p>
        </section>

    </main>

</body>
</html>
'''

            elif "login" in lower:
                code = '''<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>Login</title>
</head>

<body>

    <main>

        <h1>Login</h1>

        <form>

            <label for="email">
                Email
            </label>

            <input
                id="email"
                type="email"
                required
            >

            <label for="password">
                Password
            </label>

            <input
                id="password"
                type="password"
                required
            >

            <button type="submit">
                Login
            </button>

        </form>

    </main>

</body>
</html>
'''

            else:
                code = '''<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>JARVIS Page</title>

</head>

<body>

    <main>

        <h1>
            JARVIS Infinity
        </h1>

        <p>
            Welcome to the JARVIS interface.
        </p>

    </main>

</body>
</html>
'''

        # ============================================================
        # CSS
        # ============================================================

        else:

            if "button" in lower:
                code = '''button {

    padding: 12px 20px;

    border: none;

    border-radius: 8px;

    cursor: pointer;

    font-size: 16px;
}

button:hover {

    transform: translateY(-1px);
}
'''

            else:
                code = '''.container {

    max-width: 1000px;

    margin: 0 auto;

    padding: 24px;
}

.card {

    padding: 20px;

    border-radius: 12px;
}
'''

        return {
            "success": True,
            "language": language,
            "code": code,
            "message": (
                "Task-aware code generated successfully."
            ),
        }

    # ================================================================
    # GENERATION FORMAT
    # ================================================================

    def format_generation(self, result):
        if not result:
            return (
                "❌ CODE GENERATION NOT COMPLETED\n\n"
                "No result was returned."
            )

        if not result.get("success"):
            return (
                "❌ CODE GENERATION NOT COMPLETED\n\n"
                f"{result.get(
                    'message',
                    'Unable to generate code.'
                )}"
            )

        return (
            "✨ CODE GENERATED SUCCESSFULLY\n\n"
            f"JARVIS created "
            f"{result['language'].upper()} "
            "code for your request.\n\n"
            "📝 GENERATED CODE:\n"
            f"```{result['language']}\n"
            f"{result['code']}"
            "```\n\n"
            "ℹ️ GENERATION COMPLETE\n"
            "The generated code is ready for execution."
        )

    # ================================================================
    # GENERATE + EXECUTE + VERIFY PYTHON
    # ================================================================

    def generate_and_verify_python(
        self,
        request,
    ):
        """
        Generate Python code,
        execute it,
        and check execution success.
        """

        result = self.generate_code(
            request
        )

        if (
            not result.get("success")
            or result.get("language") != "python"
        ):
            return {
                **result,
                "executed": False,
                "verified": False,
                "execution": None,
                "output": "",
            }

        execution = self.run_python(
            result["code"]
        )

        verified = bool(
            execution.get("success")
        )

        return {
            **result,
            "executed": True,
            "verified": verified,
            "execution": execution,
            "output": execution.get(
                "stdout",
                "",
            ),
        }

    # ================================================================
    # DEBUG CODE
    # ================================================================

    def debug_code(
        self,
        code,
        language=None,
    ):
        language = (
            language
            or self.detect_language(code)
        )

        if not language:
            return {
                "success": False,
                "fixed": False,
                "verified": False,
                "language": None,
                "fixed_code": code,
                "changes": [],
                "errors": [
                    self._error(
                        "language",
                        "error",
                        1,
                        (
                            "I could not confidently "
                            "detect the programming language."
                        ),
                    )
                ],
                "warnings": [],
            }

        language = self.LANGUAGE_ALIASES.get(
            language.lower(),
            language.lower(),
        )

        # First analyze original code
        analysis = self.analyze_code(
            code,
            language,
        )

        # Already valid
        if analysis["valid"]:
            return {
                "success": True,
                "fixed": False,
                "verified": True,
                "language": language,
                "fixed_code": code,
                "changes": [],
                "errors": [],
                "warnings": analysis.get(
                    "warnings",
                    [],
                ),
            }

        # Try safe fix
        fix = self.safe_fix(
            code,
            language,
        )

        candidate = fix["fixed_code"]

        # Verify corrected code
        verification = self.verify_code(
            candidate,
            language,
        )

        return {
            "success": verification["verified"],
            "fixed": fix["fixed"],
            "verified": verification["verified"],
            "language": language,
            "fixed_code": candidate,
            "changes": fix["changes"],
            "errors": (
                []
                if verification["verified"]
                else analysis.get(
                    "errors",
                    [],
                )
            ),
            "warnings": analysis.get(
                "warnings",
                [],
            ),
        }

    # ================================================================
    # VERIFICATION FORMAT
    # ================================================================

    def format_verification(
        self,
        result,
    ):
        if not result:
            return (
                "❌ Coding Agent returned no result."
            )

        language = (
            result.get("language")
            or "unknown"
        )

        errors = (
            result.get("errors")
            or []
        )

        changes = (
            result.get("changes")
            or []
        )

        fixed_code = (
            result.get("fixed_code")
            or ""
        )

        warnings = (
            result.get("warnings")
            or []
        )

        # ------------------------------------------------------------
        # FAILED
        # ------------------------------------------------------------

        if not result.get("verified"):
            lines = [
                "❌ CODE VERIFICATION FAILED",
                "",
                (
                    f"JARVIS could not verify "
                    f"the {language.upper()} code."
                ),
            ]

            if errors:
                lines += [
                    "",
                    "🔎 ERRORS:",
                ]

                for error in errors:
                    lines.append(
                        f"• Line "
                        f"{error.get('line', '?')}: "
                        f"{error.get(
                            'message',
                            'Unknown error'
                        )}"
                    )

                    if error.get("suggestion"):
                        lines.append(
                            "  Suggestion: "
                            f"{error['suggestion']}"
                        )

            if (
                fixed_code
                and result.get("fixed")
            ):
                lines += [
                    "",
                    "📝 ATTEMPTED CORRECTED CODE:",
                    f"```{language}",
                    fixed_code,
                    "```",
                ]

            return "\n".join(lines)

        # ------------------------------------------------------------
        # VERIFIED WITHOUT FIX
        # ------------------------------------------------------------

        if not result.get("fixed"):
            lines = [
                "✅ CODE VERIFIED",
                "",
                (
                    f"JARVIS analyzed "
                    f"the {language.upper()} code."
                ),
                "No blocking errors were detected.",
            ]

            if warnings:
                lines += [
                    "",
                    "⚠️ WARNINGS:",
                ]

                for warning in warnings:

                    if isinstance(
                        warning,
                        dict,
                    ):
                        lines.append(
                            f"• Line "
                            f"{warning.get(
                                'line',
                                '?'
                            )}: "
                            f"{warning.get(
                                'message',
                                ''
                            )}"
                        )

                        if warning.get(
                            "suggestion"
                        ):
                            lines.append(
                                "  Suggestion: "
                                f"{warning['suggestion']}"
                            )

            lines += [
                "",
                "📝 VERIFIED CODE:",
                f"```{language}",
                fixed_code,
                "```",
            ]

            return "\n".join(lines)

        # ------------------------------------------------------------
        # FIXED SUCCESSFULLY
        # ------------------------------------------------------------

        lines = [
            "🔧 CODE FIXED SUCCESSFULLY",
            "",
            (
                f"JARVIS detected an issue "
                f"in the {language.upper()} code, "
                "applied a safe fix, and verified "
                "the corrected code."
            ),
            "",
            "📝 CORRECTED CODE:",
            f"```{language}",
            fixed_code,
            "```",
        ]

        if changes:
            lines += [
                "",
                "🔍 CHANGES APPLIED:",
            ]

            for change in changes:
                lines.append(
                    f"• Line "
                    f"{change.get('line', '?')}: "
                    f"{change.get(
                        'description',
                        ''
                    )}"
                )

        lines += [
            "",
            "✅ VERIFICATION SUCCESSFUL",
            (
                f"The corrected "
                f"{language.upper()} code passed "
                "JARVIS's verification checks."
            ),
        ]

        return "\n".join(lines)

    # ================================================================
    # FILE ANALYSIS
    # ================================================================

    def analyze_file(
        self,
        path,
    ):
        path = Path(path)

        try:
            language = self.EXTENSIONS.get(
                path.suffix.lower()
            )

            code = path.read_text(
                encoding="utf-8"
            )

            return self.analyze_code(
                code,
                language,
            )

        except Exception as error:
            return {
                "language": self.EXTENSIONS.get(
                    path.suffix.lower()
                ),
                "errors": [
                    self._error(
                        "file",
                        "error",
                        1,
                        str(error),
                    )
                ],
                "warnings": [],
                "valid": False,
            }


# Compatibility name used by JARVIS
JarvisCodingAgent = CodingAgent