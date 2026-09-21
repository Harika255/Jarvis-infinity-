from pathlib import Path
from PIL import Image
import pytesseract


class JarvisScreenUnderstanding:

    def __init__(self):
        self.tesseract_path = (
            r"C:\Users\Harika\AppData\Local\Tesseract-OCR\tesseract.exe"
        )

        pytesseract.pytesseract.tesseract_cmd = (
            self.tesseract_path
        )

    def analyze_screenshot(self, image_path):
        """Extract visible text from a screenshot."""

        try:

            image_path = Path(image_path)

            if not image_path.exists():
                return {
                    "success": False,
                    "text": "",
                    "message": "Screenshot not found."
                }

            image = Image.open(image_path)

            text = pytesseract.image_to_string(
                image,
                config="--psm 6"
            ).strip()

            return {
                "success": True,
                "text": text,
                "message": "Screen analyzed successfully."
            }

        except Exception as error:

            return {
                "success": False,
                "text": "",
                "message": f"Screen analysis failed: {error}"
            }


if __name__ == "__main__":

    screenshots = Path("data") / "screenshots"

    files = sorted(
        screenshots.glob("*.png"),
        key=lambda file: file.stat().st_mtime,
        reverse=True
    )

    if not files:

        print("❌ No screenshot found.")

    else:

        analyzer = JarvisScreenUnderstanding()

        result = analyzer.analyze_screenshot(
            files[0]
        )

        print("\nJARVIS SCREEN UNDERSTANDING")
        print("----------------------------")
        print("Success:", result["success"])
        print("Message:", result["message"])
        print("\nDetected Text:")
        print(result["text"])