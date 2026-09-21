from pathlib import Path
import subprocess
import os


class AgentTools:
    """Safe, explicit tools JARVIS can call. High-impact operations are not included."""

    APP_PATHS = {
        "vscode": Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Microsoft VS Code" / "Code.exe",
        "notepad": Path(os.environ.get("WINDIR", "C:\\Windows")) / "System32" / "notepad.exe",
        "calculator": Path(os.environ.get("WINDIR", "C:\\Windows")) / "System32" / "calc.exe",
    }

    def open_application(self, app_name):
        key = app_name.lower().strip()
        path = self.APP_PATHS.get(key)
        if not path or not path.exists():
            return False, f"Application '{app_name}' was not found."
        try:
            subprocess.Popen([str(path)])
            return True, f"Opened {app_name}."
        except Exception as exc:
            return False, f"Could not open {app_name}: {exc}"

    def open_folder(self, folder):
        """Open a folder only after caller's permission check."""
        path = Path(folder).expanduser().resolve()
        if not path.exists() or not path.is_dir():
            return False, "Folder does not exist."
        try:
            os.startfile(str(path))
            return True, f"Opened folder {path.name}."
        except Exception as exc:
            return False, f"Could not open folder: {exc}"
