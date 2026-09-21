import cv2
import os

try:
    import pytesseract
except ImportError:
    pytesseract = None


class JarvisVision:

    def __init__(self, camera_index=0):

        self.camera_index = camera_index
        self.camera = None
        self.running = False

        # Face detection
        self.face_detector = None

        # OCR
        self.ocr_available = False
        self.last_detected_text = ""

        # YuNet model path
        self.model_path = os.path.join(
            os.path.dirname(__file__),
            "assets",
            "face_detection_yunet_2023mar.onnx"
        )

        # Tesseract path
        self.tesseract_path = os.path.join(
    os.path.dirname(__file__),
    "tesseract.exe"
)

        self._load_face_detector()
        self._load_ocr()

    # ============================================================
    # FACE DETECTION
    # ============================================================

    def _load_face_detector(self):

        if not os.path.exists(self.model_path):

            print("⚠️ YuNet model not found:")
            print(self.model_path)

            return

        try:

            self.face_detector = cv2.FaceDetectorYN.create(
                self.model_path,
                "",
                (320, 320),
                0.9,
                0.3,
                5000
            )

            print("✅ YuNet face detector loaded")

        except Exception as error:

            print("❌ Face detector error:")
            print(error)

            self.face_detector = None

    # ============================================================
    # OCR
    # ============================================================

    def _load_ocr(self):

        if pytesseract is None:

            print("⚠️ pytesseract is not installed.")
            print("Run: pip install pytesseract")

            return

        if os.path.exists(self.tesseract_path):

            try:

                pytesseract.pytesseract.tesseract_cmd = (
                    self.tesseract_path
                )

                # Test Tesseract
                version = pytesseract.get_tesseract_version()

                print("✅ Tesseract OCR loaded")
                print("OCR Version:", version)

                self.ocr_available = True

            except Exception as error:

                print("❌ Tesseract OCR error:")
                print(error)

                self.ocr_available = False

        else:

            print("⚠️ Tesseract executable not found:")
            print(self.tesseract_path)

            print(
                "Install Tesseract OCR or update "
                "self.tesseract_path."
            )

    def extract_text(self, frame):

        """
        Extract text from the current camera frame.

        Returns:
            str: Detected text.
        """

        if frame is None:
            return ""

        if not self.ocr_available:
            return ""

        try:

            # Convert to grayscale
            gray = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2GRAY
            )

            # Improve contrast
            gray = cv2.GaussianBlur(
                gray,
                (3, 3),
                0
            )

            # Thresholding improves OCR on documents
            _, threshold = cv2.threshold(
                gray,
                0,
                255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )

            text = pytesseract.image_to_string(
                threshold,
                config="--psm 6"
            )

            text = text.strip()

            self.last_detected_text = text

            return text

        except Exception as error:

            print("⚠️ OCR error:", error)

            return ""

    # ============================================================
    # CAMERA
    # ============================================================

    def start_camera(self):

        print("🎥 Starting JARVIS Vision...")

        self.camera = cv2.VideoCapture(
    self.camera_index,
    cv2.CAP_DSHOW
)

        if not self.camera.isOpened():

            print("❌ Could not open camera.")

            self.camera = None

            return False

        self.running = True

        print("✅ Camera connected")
        print("👁️ JARVIS Vision is online")

        if self.ocr_available:
            print("🔤 JARVIS OCR is online")
        else:
            print("⚠️ JARVIS OCR is unavailable")

        return True

    def read_frame(self):

        if self.camera is None:
            return None

        if not self.running:
            return None

        success, frame = self.camera.read()

        if not success:
            return None

        return frame

    # ============================================================
    # FACE DETECTION
    # ============================================================

    def detect_faces(self, frame):

        if frame is None:
            return []

        if self.face_detector is None:
            return []

        try:

            height, width = frame.shape[:2]

            self.face_detector.setInputSize(
                (width, height)
            )

            _, detections = self.face_detector.detect(
                frame
            )

            if detections is None:
                return []

            faces = []

            for detection in detections:

                x, y, w, h = detection[:4]

                faces.append(
                    (
                        int(x),
                        int(y),
                        int(w),
                        int(h)
                    )
                )

            return faces

        except Exception as error:

            print(
                "⚠️ Face detection error:",
                error
            )

            return []

    # ============================================================
    # RELEASE
    # ============================================================

    def release(self):

        self.running = False

        if self.camera is not None:

            self.camera.release()
            self.camera = None

        cv2.destroyAllWindows()

        print("🛑 JARVIS Vision stopped")

    # ============================================================
    # STANDALONE VISION WINDOW
    # ============================================================

    def run(self):

        if not self.start_camera():
            return

        frame_counter = 0
        detected_text = ""

        while self.running:

            frame = self.read_frame()

            if frame is None:
                break

            # ----------------------------------------------------
            # FACE DETECTION
            # ----------------------------------------------------

            faces = self.detect_faces(frame)

            for x, y, w, h in faces:

                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    2
                )

            # ----------------------------------------------------
            # OCR
            # ----------------------------------------------------

            # OCR does not need to run on every single frame.
            # Run once every 15 frames to reduce CPU usage.
            frame_counter += 1

            if frame_counter >= 15:

                detected_text = self.extract_text(
                    frame
                )

                frame_counter = 0

            # ----------------------------------------------------
            # VISION STATUS
            # ----------------------------------------------------

            cv2.putText(
                frame,
                "JARVIS VISION ONLINE",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"Faces: {len(faces)}",
                (20, 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            # ----------------------------------------------------
            # OCR STATUS
            # ----------------------------------------------------

            if self.ocr_available:

                cv2.putText(
                    frame,
                    "OCR: ONLINE",
                    (20, 110),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (0, 255, 0),
                    2
                )

            else:

                cv2.putText(
                    frame,
                    "OCR: OFFLINE",
                    (20, 110),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (0, 0, 255),
                    2
                )

            # ----------------------------------------------------
            # DISPLAY DETECTED TEXT
            # ----------------------------------------------------

            if detected_text:

                # Show only the first few lines on camera
                lines = detected_text.splitlines()

                y_position = 150

                for line in lines[:5]:

                    line = line.strip()

                    if not line:
                        continue

                    # Prevent extremely long text from
                    # overflowing the camera window.
                    if len(line) > 60:
                        line = line[:60] + "..."

                    cv2.putText(
                        frame,
                        "TEXT: " + line,
                        (20, y_position),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.55,
                        (0, 255, 255),
                        2
                    )

                    y_position += 28

            # ----------------------------------------------------
            # CAMERA WINDOW
            # ----------------------------------------------------

            cv2.imshow(
                "JARVIS Vision",
                frame
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        self.release()