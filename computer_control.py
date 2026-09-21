import os
import re
import shutil
import subprocess


class ComputerController:
    """Windows application launcher for JARVIS.

    Supports common applications explicitly and falls back to Windows
    PATH / Start Menu shortcuts for other installed applications.
    """

    APP_ALIASES = {
        "notepad": "notepad.exe",
        "note pad": "notepad.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "vscode": r"C:\\Users\\Harika\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
        "vs code": r"C:\\Users\\Harika\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
        "visual studio code": r"C:\\Users\\Harika\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
        "chrome": "chrome.exe",
        "google chrome": "chrome.exe",
        "spotify": "spotify.exe",
        "word": "winword.exe",
        "microsoft word": "winword.exe",
        "powerpoint": "powerpnt.exe",
        "power point": "powerpnt.exe",
        "microsoft powerpoint": "powerpnt.exe",
        "excel": "excel.exe",
        "microsoft excel": "excel.exe",
        "file explorer": "explorer.exe",
        "explorer": "explorer.exe",
        "files": "explorer.exe",
        "command prompt": "cmd.exe",
        "cmd": "cmd.exe",
        "powershell": "powershell.exe",
    }

    def _clean_name(self, application):
        text = re.sub(r"\s+", " ", str(application or "").strip().lower())
        text = re.sub(r"^(?:open|launch|start)\s+(?:my\s+)?", "", text)
        text = re.sub(r"\s+(?:please|for me)$", "", text)
        return text.strip(" .!?")

    def _find_start_menu_shortcut(self, name):
        """Find an installed app's Start Menu shortcut by name."""
        target = self._clean_name(name)
        roots = [
            os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs"),
            os.path.join(os.environ.get("PROGRAMDATA", "C:\\ProgramData"), r"Microsoft\Windows\Start Menu\Programs"),
        ]
        target_words = set(re.findall(r"[a-z0-9]+", target))
        if not target_words:
            return None

        for root in roots:
            if not os.path.isdir(root):
                continue
            try:
                for folder, _, files in os.walk(root):
                    for filename in files:
                        if not filename.lower().endswith(".lnk"):
                            continue
                        stem = os.path.splitext(filename)[0].lower()
                        words = set(re.findall(r"[a-z0-9]+", stem))
                        if target_words.issubset(words) or target in stem:
                            return os.path.join(folder, filename)
            except OSError:
                continue
        return None

    def _launch_executable(self, executable):
        if os.path.isabs(executable):
            if not os.path.exists(executable):
                return False, f"Application was not found at: {executable}"
            subprocess.Popen([executable])
            return True, f"{os.path.basename(executable)} opened successfully."

        resolved = shutil.which(executable)
        if resolved:
            subprocess.Popen([resolved])
            return True, f"{executable} opened successfully."

        # Windows can resolve many installed applications through START.
        try:
            subprocess.Popen(["cmd.exe", "/c", "start", "", executable],
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            return True, f"{executable} launch requested successfully."
        except Exception:
            return False, f"Could not launch {executable}."

    def open_application(self, application):
        name = self._clean_name(application)

        if not name:
            return False, "No application name was provided."

        # Project means the JARVIS project in VS Code.
        if "project" in name and name not in {"project explorer"}:
            name = "vscode"

        # Exact/common aliases first. Longest alias wins.
        alias = None
        for candidate in sorted(self.APP_ALIASES, key=len, reverse=True):
            if name == candidate or candidate in name:
                alias = candidate
                break

        if alias:
            executable = self.APP_ALIASES[alias]
            success, message = self._launch_executable(executable)
            if success:
                return True, message

            # For applications represented by Start Menu shortcuts, try that next.
            shortcut = self._find_start_menu_shortcut(name)
            if shortcut:
                try:
                    os.startfile(shortcut)
                    return True, f"{name.title()} opened successfully."
                except Exception as error:
                    return False, f"Could not open {name.title()}: {error}"
            return False, message

        # Dynamic Start Menu discovery for applications not hard-coded above.
        shortcut = self._find_start_menu_shortcut(name)
        if shortcut:
            try:
                os.startfile(shortcut)
                return True, f"{name.title()} opened successfully."
            except Exception as error:
                return False, f"Could not open {name.title()}: {error}"

        # Last fallback: Windows PATH resolution.
        executable_name = name if name.endswith(".exe") else name + ".exe"
        resolved = shutil.which(executable_name)
        if resolved:
            try:
                subprocess.Popen([resolved])
                return True, f"{name.title()} opened successfully."
            except Exception as error:
                return False, f"Could not open {name.title()}: {error}"

        return False, (
            f"I could not find '{name}'. Make sure the application is installed."
        )
