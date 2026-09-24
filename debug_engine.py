import ast
import os
import re
import shutil
import subprocess
import tempfile


def detect_language(code):
    code_lower = code.lower()

    if re.search(r"<(!doctype|html|head|body|div|p|script|style)\b", code_lower):
        return "HTML"

    if re.search(r"[.#]?[a-zA-Z][\w-]*\s*\{[^}]*\}", code):
        if re.search(r"(color|background|margin|padding|font-size|display|position|width|height)\s*:", code):
            return "CSS"

    if re.search(r"\b(public\s+class|private\s+class|protected\s+class|class\s+\w+)", code):
        if re.search(r"\b(public|private|protected|static)\b", code):
            if re.search(r"\bSystem\.out\.|String\[\]|void\s+main", code):
                return "Java"

    if re.search(r"\b(function|const|let|var)\b", code):
        if re.search(r"=>|console\.log|document\.|window\.", code):
            return "JavaScript"

    if re.search(r"\b(def|import|from|print|elif|lambda|self)\b", code):
        return "Python"

    if re.search(r"\b(public\s+static\s+void\s+main|System\.out\.println)\b", code):
        return "Java"

    if re.search(r"\b(console\.log|document\.getElementById|function)\b", code):
        return "JavaScript"

    return "Python"


def debug_python(code):
    result = {
        "language": "Python",
        "status": "PASS",
        "errors": [],
        "warnings": [],
        "fixed_code": code,
        "message": "Python code looks syntactically correct.",
        "explanation": "",
        "suggestion": ""
    }

    try:
        ast.parse(code)

    except SyntaxError as error:
        line_number = error.lineno or 1
        column = error.offset or 1
        message = error.msg or "Python syntax error."

        source_lines = code.splitlines()
        source_line = ""

        if 1 <= line_number <= len(source_lines):
            source_line = source_lines[line_number - 1]

        explanation = ""

        if "expected an indented block" in message:
            explanation = (
                "Python found a line that starts a block, such as a function, "
                "if statement, loop, or class, but the next statement is not "
                "indented. Indent the code inside that block by 4 spaces."
            )

        elif "was never closed" in message:
            explanation = (
                "Python found an opening bracket, parenthesis, or similar "
                "symbol that was not closed. Check the brackets on this line "
                "and the lines immediately before it."
            )

        elif "invalid syntax" in message:
            explanation = (
                "Python could not understand the syntax on this line. "
                "Check keywords, brackets, operators, commas, and indentation."
            )

        elif "unterminated string" in message:
            explanation = (
                "A string starts on this line but does not have a matching "
                "closing quotation mark."
            )

        else:
            explanation = (
                "Python detected a syntax problem on this line. "
                "Check the highlighted line and the line immediately before it."
            )

        fixed_code = code

        if "expected an indented block" in message and source_line:
            lines = code.splitlines()

            if line_number <= len(lines):
                current_line = lines[line_number - 1]

                if current_line.strip():
                    indentation = len(current_line) - len(current_line.lstrip())

                    if indentation == 0:
                        lines[line_number - 1] = "    " + current_line

                    fixed_code = "\n".join(lines)

        result["status"] = "ERROR"

        result["errors"].append({
            "line": line_number,
            "column": column,
            "message": message,
            "source": source_line,
            "explanation": explanation
        })

        result["fixed_code"] = fixed_code
        result["message"] = (
            f"Python syntax error on line {line_number}: {message}"
        )
        result["explanation"] = explanation
        result["suggestion"] = (
            "Check the highlighted line first, then inspect the line "
            "immediately above it."
        )

    return result


def debug_html(code):
    result = {
        "language": "HTML",
        "status": "PASS",
        "errors": [],
        "warnings": [],
        "fixed_code": code,
        "message": "HTML structure looks correct.",
        "explanation": "",
        "suggestion": ""
    }

    tag_pattern = re.compile(
        r"<\s*(/?)\s*([a-zA-Z][\w:-]*)[^>]*?>"
    )

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
        "wbr"
    }

    stack = []

    for match in tag_pattern.finditer(code):
        closing = match.group(1)
        tag = match.group(2).lower()

        line = code[:match.start()].count("\n") + 1

        if tag in void_tags:
            continue

        if closing:
            if not stack:
                result["status"] = "ERROR"

                result["errors"].append({
                    "line": line,
                    "column": 1,
                    "message": f"Unexpected closing tag </{tag}>.",
                    "source": code.splitlines()[line - 1]
                    if line <= len(code.splitlines())
                    else "",
                    "explanation": (
                        f"The closing tag </{tag}> does not have a matching "
                        f"opening <{tag}> tag."
                    )
                })

            elif stack[-1][0] == tag:
                stack.pop()

            else:
                result["status"] = "ERROR"

                expected = stack[-1][0]

                result["errors"].append({
                    "line": line,
                    "column": 1,
                    "message": (
                        f"Closing tag </{tag}> does not match "
                        f"<{expected}>."
                    ),
                    "source": code.splitlines()[line - 1]
                    if line <= len(code.splitlines())
                    else "",
                    "explanation": (
                        f"The tag <{expected}> was opened most recently, "
                        f"but </{tag}> was found instead."
                    )
                })

        else:
            stack.append((tag, line))

    if stack:
        result["status"] = "ERROR"

        for tag, line in stack:
            result["errors"].append({
                "line": line,
                "column": 1,
                "message": f"Missing closing tag </{tag}>.",
                "source": code.splitlines()[line - 1]
                if line <= len(code.splitlines())
                else "",
                "explanation": (
                    f"The <{tag}> tag was opened but no matching "
                    f"</{tag}> closing tag was found."
                )
            })

    if result["errors"]:
        result["message"] = (
            f"HTML contains {len(result['errors'])} structural error(s)."
        )
        result["explanation"] = (
            "Check that every opening HTML tag has the correct closing tag."
        )
        result["suggestion"] = (
            "Match each opening tag with its corresponding closing tag."
        )

    return result


def debug_css(code):
    result = {
        "language": "CSS",
        "status": "PASS",
        "errors": [],
        "warnings": [],
        "fixed_code": code,
        "message": "CSS structure looks correct.",
        "explanation": "",
        "suggestion": ""
    }

    brace_count = 0
    quote = None
    escape = False

    for index, char in enumerate(code):
        line = code[:index].count("\n") + 1

        if escape:
            escape = False
            continue

        if char == "\\":
            escape = True
            continue

        if char in ('"', "'"):
            if quote is None:
                quote = char
            elif quote == char:
                quote = None

        elif quote is None:
            if char == "{":
                brace_count += 1

            elif char == "}":
                brace_count -= 1

                if brace_count < 0:
                    result["status"] = "ERROR"

                    result["errors"].append({
                        "line": line,
                        "column": 1,
                        "message": "Unexpected closing brace '}'.",
                        "source": code.splitlines()[line - 1]
                        if line <= len(code.splitlines())
                        else "",
                        "explanation": (
                            "A closing brace was found without a matching "
                            "opening brace."
                        )
                    })

                    brace_count = 0

    if quote is not None:
        result["status"] = "ERROR"

        result["errors"].append({
            "line": len(code.splitlines()),
            "column": 1,
            "message": "Unclosed string in CSS.",
            "source": code.splitlines()[-1]
            if code.splitlines()
            else "",
            "explanation": (
                "A CSS string was opened with a quotation mark but was "
                "not closed."
            )
        })

    if brace_count > 0:
        result["status"] = "ERROR"

        result["errors"].append({
            "line": len(code.splitlines()),
            "column": 1,
            "message": f"Missing {brace_count} closing brace(s).",
            "source": code.splitlines()[-1]
            if code.splitlines()
            else "",
            "explanation": (
                "A CSS block was opened with '{' but the corresponding "
                "closing '}' is missing."
            )
        })

    lines = code.splitlines()

    for index, line_text in enumerate(lines):
        stripped = line_text.strip()

        if not stripped:
            continue

        if ":" in stripped and not stripped.endswith((
            ";",
            "{",
            "}"
        )):
            if not stripped.startswith((
                "/*",
                "*",
                "@media",
                "@keyframes"
            )):
                result["warnings"].append(
                    f"Line {index + 1}: CSS declaration may be missing ';'."
                )

    if result["errors"]:
        result["message"] = (
            f"CSS contains {len(result['errors'])} structural error(s)."
        )
        result["explanation"] = (
            "Check braces, quotation marks, and CSS declarations."
        )
        result["suggestion"] = (
            "Make sure every CSS block has matching braces."
        )

    return result


def debug_javascript(code):
    result = {
        "language": "JavaScript",
        "status": "PASS",
        "errors": [],
        "warnings": [],
        "fixed_code": code,
        "message": "JavaScript structure looks correct.",
        "explanation": "",
        "suggestion": ""
    }

    pairs = {
        "(": ")",
        "[": "]",
        "{": "}"
    }

    opening = set(pairs.keys())
    closing = set(pairs.values())

    stack = []
    quote = None
    escape = False

    for index, char in enumerate(code):
        line = code[:index].count("\n") + 1

        if escape:
            escape = False
            continue

        if char == "\\":
            escape = True
            continue

        if char in ('"', "'", "`"):
            if quote is None:
                quote = char
            elif quote == char:
                quote = None

            continue

        if quote is not None:
            continue

        if char in opening:
            stack.append((char, line))

        elif char in closing:
            if not stack:
                result["status"] = "ERROR"

                result["errors"].append({
                    "line": line,
                    "column": 1,
                    "message": f"Unexpected '{char}'.",
                    "source": code.splitlines()[line - 1]
                    if line <= len(code.splitlines())
                    else "",
                    "explanation": (
                        f"The closing symbol '{char}' does not have a "
                        "matching opening symbol."
                    )
                })

            else:
                expected = pairs[stack[-1][0]]

                if char == expected:
                    stack.pop()

                else:
                    result["status"] = "ERROR"

                    result["errors"].append({
                        "line": line,
                        "column": 1,
                        "message": (
                            f"Expected '{expected}' but found '{char}'."
                        ),
                        "source": code.splitlines()[line - 1]
                        if line <= len(code.splitlines())
                        else "",
                        "explanation": (
                            f"The opening '{stack[-1][0]}' must be closed "
                            f"with '{expected}'."
                        )
                    })

                    stack.pop()

    if quote is not None:
        result["status"] = "ERROR"

        result["errors"].append({
            "line": len(code.splitlines()),
            "column": 1,
            "message": "Unclosed string.",
            "source": code.splitlines()[-1]
            if code.splitlines()
            else "",
            "explanation": (
                "A JavaScript string was opened but the matching "
                "quotation mark was not found."
            )
        })

    if stack:
        result["status"] = "ERROR"

        for symbol, line in stack:
            result["errors"].append({
                "line": line,
                "column": 1,
                "message": f"Missing closing '{pairs[symbol]}'.",
                "source": code.splitlines()[line - 1]
                if line <= len(code.splitlines())
                else "",
                "explanation": (
                    f"The opening '{symbol}' does not have a matching "
                    f"closing '{pairs[symbol]}'."
                )
            })

    if re.search(r"\bvar\s+\w+", code):
        result["warnings"].append(
            "Consider using let or const instead of var in modern JavaScript."
        )

    if "console.log(" in code:
        result["warnings"].append(
            "console.log() is useful for debugging but can be removed "
            "from production code."
        )

    if result["errors"]:
        result["message"] = (
            f"JavaScript contains {len(result['errors'])} structural error(s)."
        )
        result["explanation"] = (
            "Check brackets, parentheses, braces, and quotation marks."
        )
        result["suggestion"] = (
            "Match every opening symbol with the correct closing symbol."
        )

    return result


def debug_java(code):
    result = {
        "language": "Java",
        "status": "PASS",
        "errors": [],
        "warnings": [],
        "fixed_code": code,
        "message": "",
        "explanation": "",
        "suggestion": ""
    }

    lines = code.splitlines()

    brace_count = code.count("{") - code.count("}")

    if brace_count > 0:
        result["status"] = "ERROR"

        result["errors"].append({
            "line": len(lines),
            "column": 1,
            "message": f"Missing {brace_count} closing brace(s).",
            "source": lines[-1] if lines else "",
            "explanation": (
                "Java contains opening braces that do not have matching "
                "closing braces."
            )
        })

    elif brace_count < 0:
        result["status"] = "ERROR"

        result["errors"].append({
            "line": len(lines),
            "column": 1,
            "message": f"Extra {-brace_count} closing brace(s).",
            "source": lines[-1] if lines else "",
            "explanation": (
                "Java contains more closing braces than opening braces."
            )
        })

    if not re.search(r"\bclass\s+\w+", code):
        result["warnings"].append(
            "No Java class declaration was detected."
        )

    temp_dir = None

    try:
        temp_dir = tempfile.mkdtemp()

        class_match = re.search(
            r"\bpublic\s+class\s+(\w+)",
            code
        )

        if class_match:
            class_name = class_match.group(1)
        else:
            class_match = re.search(
                r"\bclass\s+(\w+)",
                code
            )

            if class_match:
                class_name = class_match.group(1)
            else:
                class_name = "JarvisDebug"

        if re.search(
            r"\bpublic\s+class\s+" + re.escape(class_name),
            code
        ):
            file_name = f"{class_name}.java"
        else:
            file_name = f"{class_name}.java"

        java_file = os.path.join(temp_dir, file_name)

        with open(
            java_file,
            "w",
            encoding="utf-8"
        ) as file:
            file.write(code)

        process = subprocess.run(
            ["javac", java_file],
            capture_output=True,
            text=True,
            timeout=10
        )

        if process.returncode != 0:
            compiler_output = (
                process.stderr.strip()
                or process.stdout.strip()
            )

            compiler_output = re.sub(
                r"Picked up JAVA_TOOL_OPTIONS:.*?(?=C:\\|[A-Za-z]:\\)",
                "",
                compiler_output,
                flags=re.DOTALL
            ).strip()

            error_match = re.search(
                r"\.java:(\d+):\s*error:\s*(.+)",
                compiler_output
            )

            if error_match:
                line_number = int(error_match.group(1))
                compiler_message = error_match.group(2).strip()

                source_line = ""

                if 1 <= line_number <= len(lines):
                    source_line = lines[line_number - 1]

                explanation = (
                    "The Java compiler found a syntax or code error "
                    "on this line."
                )

                fixed_code = code
                suggestion = (
                    "Check the highlighted line and the line immediately "
                    "before it."
                )

                if "';' expected" in compiler_message:
                    explanation = (
                        "Java statements normally end with a semicolon. "
                        "This line appears to be missing ';'."
                    )

                    suggestion = (
                        "Add a semicolon at the end of the statement."
                    )

                    if source_line.strip():
                        stripped = source_line.rstrip()

                        if not stripped.endswith((
                            ";",
                            "{",
                            "}",
                            ":"
                        )):
                            fixed_lines = lines.copy()
                            fixed_lines[line_number - 1] = (
                                stripped + ";"
                            )
                            fixed_code = "\n".join(fixed_lines)

                elif "cannot find symbol" in compiler_message:
                    explanation = (
                        "Java cannot find the class, method, variable, "
                        "or symbol used in this code."
                    )

                    suggestion = (
                        "Check the spelling, declaration, import, and scope "
                        "of the referenced symbol."
                    )

                elif "unclosed string literal" in compiler_message:
                    explanation = (
                        "A Java string starts with a quotation mark but "
                        "does not have a matching closing quotation mark."
                    )

                    suggestion = (
                        "Check the quotation marks on the highlighted line."
                    )

                elif "incompatible types" in compiler_message:
                    explanation = (
                        "A value of one data type is being used where "
                        "another incompatible type is required."
                    )

                    suggestion = (
                        "Check the variable types and convert or assign "
                        "compatible values."
                    )

                result["status"] = "ERROR"

                result["errors"].append({
                    "line": line_number,
                    "column": 1,
                    "message": compiler_message,
                    "source": source_line,
                    "explanation": explanation
                })

                result["fixed_code"] = fixed_code
                result["message"] = (
                    f"Java compiler error on line "
                    f"{line_number}: {compiler_message}"
                )
                result["explanation"] = explanation
                result["suggestion"] = suggestion

            else:
                result["status"] = "ERROR"

                result["errors"].append({
                    "line": None,
                    "column": None,
                    "message": compiler_output,
                    "source": "",
                    "explanation": (
                        "The Java compiler rejected the code, but the "
                        "compiler output could not be mapped to a specific "
                        "line."
                    )
                })

                result["message"] = (
                    "Java compiler found an error."
                )

                result["explanation"] = (
                    "Read the compiler message for the exact syntax, "
                    "type, or declaration problem."
                )

                result["suggestion"] = (
                    "Check the compiler message and inspect the reported "
                    "source line."
                )

        else:
            if not result["errors"]:
                result["status"] = "PASS"
                result["message"] = (
                    "Java code compiled successfully."
                )
                result["explanation"] = (
                    "The Java compiler accepted the code without errors."
                )
                result["suggestion"] = (
                    "Your Java code is syntactically valid."
                )

    except FileNotFoundError:
        result["message"] = (
            "Basic Java structure checked, but javac is not installed "
            "or is not available in PATH."
        )

        result["suggestion"] = (
            "Install a JDK and make sure javac is available in PATH."
        )

        if result["errors"]:
            result["status"] = "ERROR"

    except subprocess.TimeoutExpired:
        result["status"] = "ERROR"

        result["errors"].append({
            "line": None,
            "column": None,
            "message": "Java compiler timed out.",
            "source": "",
            "explanation": (
                "The Java compiler did not finish within the allowed time."
            )
        })

        result["message"] = (
            "Java compiler check timed out."
        )

        result["suggestion"] = (
            "Check the Java installation and try the code again."
        )

    except Exception as error:
        result["warnings"].append(
            f"Java compiler check unavailable: {error}"
        )

    finally:
        if temp_dir:
            shutil.rmtree(
                temp_dir,
                ignore_errors=True
            )

    if result["errors"]:
        result["status"] = "ERROR"

    elif result["status"] != "ERROR" and not result["message"]:
        result["status"] = "PASS"
        result["message"] = (
            "Java structure looks correct."
        )

    return result


def debug_code(code, language="Auto Detect"):
    if not code or not code.strip():
        return {
            "language": language if language != "Auto Detect" else "Unknown",
            "status": "ERROR",
            "errors": [{
                "line": 1,
                "column": 1,
                "message": "No code was provided.",
                "source": "",
                "explanation": (
                    "JARVIS needs source code before it can analyze it."
                )
            }],
            "warnings": [],
            "fixed_code": code,
            "message": "No code provided.",
            "explanation": (
                "Paste your code into the debugger and try again."
            ),
            "suggestion": "Paste the complete code."
        }

    if language == "Auto Detect":
        language = detect_language(code)

    normalized = language.strip().lower()

    if normalized == "python":
        return debug_python(code)

    if normalized == "html":
        return debug_html(code)

    if normalized == "css":
        return debug_css(code)

    if normalized in ("javascript", "java script", "js"):
        return debug_javascript(code)

    if normalized == "java":
        return debug_java(code)

    return {
        "language": language,
        "status": "ERROR",
        "errors": [{
            "line": None,
            "column": None,
            "message": "Unsupported programming language.",
            "source": "",
            "explanation": (
                "JARVIS currently supports Python, Java, JavaScript, "
                "HTML, and CSS."
            )
        }],
        "warnings": [],
        "fixed_code": code,
        "message": "Unsupported programming language.",
        "explanation": (
            "Choose Python, Java, JavaScript, HTML, or CSS."
        ),
        "suggestion": (
            "Select a supported language from the debugger."
        )
    }


def format_debug_result(result):
    lines = []

    lines.append(
        f"Language: {result.get('language', 'Unknown')}"
    )

    lines.append(
        f"Status: {result.get('status', 'UNKNOWN')}"
    )

    if result.get("message"):
        lines.append(
            f"Message: {result['message']}"
        )

    if result.get("explanation"):
        lines.append(
            f"Explanation: {result['explanation']}"
        )

    errors = result.get("errors", [])

    if errors:
        lines.append("")
        lines.append("Errors:")

        for index, error in enumerate(errors, 1):
            line = error.get("line")

            if line:
                lines.append(
                    f"{index}. Line {line}: "
                    f"{error.get('message', 'Unknown error')}"
                )
            else:
                lines.append(
                    f"{index}. "
                    f"{error.get('message', 'Unknown error')}"
                )

            if error.get("explanation"):
                lines.append(
                    f"   Explanation: {error['explanation']}"
                )

    warnings = result.get("warnings", [])

    if warnings:
        lines.append("")
        lines.append("Warnings:")

        for index, warning in enumerate(warnings, 1):
            lines.append(
                f"{index}. {warning}"
            )

    if result.get("suggestion"):
        lines.append("")
        lines.append(
            f"Suggestion: {result['suggestion']}"
        )

    if result.get("fixed_code") is not None:
        lines.append("")
        lines.append("Fixed Code:")
        lines.append(result["fixed_code"])

    return "\n".join(lines)