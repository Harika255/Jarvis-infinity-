from PIL import ImageGrab
from pathlib import Path
from datetime import datetime


class JarvisScreenCapture:

    def __init__(self):
        self.capture_folder = Path("data") / "screenshots"
        self.capture_folder.mkdir(parents=True, exist_ok=True)

    def capture_screen(self):
        """Capture the current screen and save it."""

        try:
            screenshot = ImageGrab.grab()

            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )

            file_path = (
                self.capture_folder
                / f"jarvis_screen_{timestamp}.png"
            )

            screenshot.save(file_path)

            return {
                "success": True,
                "path": str(file_path),
                "width": screenshot.width,
                "height": screenshot.height,
                "message": "Screen captured successfully."
            }

        except Exception as error:

            return {
                "success": False,
                "path": None,
                "message": f"Screen capture failed: {error}"
            }


if __name__ == "__main__":

    capture = JarvisScreenCapture()

    result = capture.capture_screen()

    print("\nJARVIS SCREEN CAPTURE")
    print("---------------------")
    print("Success:", result["success"])
    print("Path:", result["path"])
    print("Resolution:", result.get("width"),
          "x", result.get("height"))
    print("Message:", result["message"])