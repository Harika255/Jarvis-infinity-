import cv2
import html
import webbrowser
import subprocess
import sys
import sys
import os
import re
import cv2
import cv2

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QLabel,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QScrollArea,
    QSizePolicy,
    QProgressBar,
)

from PySide6.QtCore import Qt, QTimer, QDateTime, QThread, Signal
from PySide6.QtGui import QPixmap, QPainter, QColor, QImage

from ai_brain import JarvisBrain
from coding_agent import CodingAgent
from next_best_action import NextBestActionEngine
from action_planner import ActionPlanner
from safety_engine import SafetyEngine
from computer_control import ComputerController
from voice_control import VoiceController
from voice_response import JarvisSpeaker
from llm_manager import JarvisLLM

try:
    from agent.dashboard_bridge import DashboardAgentBridge
except Exception:
    DashboardAgentBridge = None
from vision_engine import JarvisVision


class VoiceWorker(QThread):
    finished = Signal(str)

    def __init__(self, voice_controller):
        super().__init__()
        self.voice_controller = voice_controller

    def run(self):
        command = self.voice_controller.listen()
        self.finished.emit(command or "")


class SpeechWorker(QThread):
    finished = Signal()

    def __init__(self, speaker, text):
        super().__init__()
        self.speaker = speaker
        self.text = text

    def run(self):
        try:
            self.speaker.speak(self.text)
        finally:
            self.finished.emit()


class LLMWorker(QThread):
    finished = Signal(object)

    def __init__(self, operation, *args):
        super().__init__()
        self.operation = operation
        self.args = args

    def run(self):
        try:
            result = self.operation(*self.args)
        except Exception as exc:
            result = {
                "success": False,
                "message": f"JARVIS background task error: {exc}",
            }
        self.finished.emit(result)


class BackgroundWidget(QWidget):
    """Paints the supplied futuristic JARVIS background image."""

    def __init__(self, image_path):
        super().__init__()

        self.bg = QPixmap(image_path)

    def paintEvent(self, event):
        painter = QPainter(self)

        if not self.bg.isNull():

            scaled = self.bg.scaled(
                self.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )

            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2

            painter.drawPixmap(x, y, scaled)

        else:
            painter.fillRect(
                self.rect(),
                QColor("#07091d")
            )


class JarvisDashboard(QWidget):

    def __init__(self):
        super().__init__()

        # ==============================
        # AI + COMPUTER CONTROL
        # ==============================

        self.brain = JarvisBrain() 
        self.coding_agent = CodingAgent()
        self.next_action_engine = NextBestActionEngine()
        self.action_planner = ActionPlanner()
        self.safety_engine = SafetyEngine()
        self.pending_safety_action = None
        self.coding_mode = False
        self.coding_operation = None
        self.dataset_size = len(self.brain.training_sentences)
        self.intent_count = len(set(self.brain.training_labels))
        self.computer = ComputerController()
        self.voice = VoiceController()
        self.voice_worker = None
        self.speaker = JarvisSpeaker()
        self.speech_worker = None

        # General-purpose AI brain. It understands open-ended natural language
        # and can use safe tools instead of relying on hard-coded commands.
        self.llm = JarvisLLM()
        self.llm_worker = None
        self.dashboard_agent = DashboardAgentBridge() if DashboardAgentBridge else None

        # Embedded webcam vision: frames are rendered inside the PySide6 UI.
        self.vision = JarvisVision(camera_index=0)
        self.vision_timer = QTimer(self)
        self.vision_timer.timeout.connect(self.update_vision_frame)

        # ==============================
        # WINDOW SETTINGS
        # ==============================

        self.setWindowTitle("JARVIS Infinity 2026")
        self.setMinimumSize(1250, 780)
        self.resize(1500, 900)

        # ==============================
        # GLOBAL STYLE
        # ==============================

        self.setStyleSheet("""
            QWidget {
                color: #eef4ff;
                font-family: "Segoe UI";
            }

            QFrame#glass {
                background: rgba(7, 14, 42, 215);
                border: 1px solid rgba(80, 157, 255, 150);
                border-radius: 18px;
            }

            QFrame#cyanCard {
                background: rgba(5, 42, 91, 215);
                border: 1px solid #00c8ff;
                border-radius: 16px;
            }

            QFrame#purpleCard {
                background: rgba(47, 18, 104, 215);
                border: 1px solid #9d5cff;
                border-radius: 16px;
            }

            QFrame#tealCard {
                background: rgba(0, 67, 73, 215);
                border: 1px solid #00e6d0;
                border-radius: 16px;
            }

            QFrame#orangeCard {
                background: rgba(91, 48, 10, 215);
                border: 1px solid #ffad4d;
                border-radius: 16px;
            }

            QFrame#situationFrame {
                background: rgba(7, 20, 55, 225);
                border: 1px solid #38a9ff;
                border-radius: 16px;
                padding: 8px;
            }

            QFrame#sidebar {
                background: rgba(5, 10, 35, 235);
                border-right: 1px solid rgba(73, 134, 255, 120);
            }

            QLabel#brand {
                color: white;
                font-size: 40px;
                font-weight: 800;
                letter-spacing: 4px;
            }

            QLabel#brandSub {
                color: #72dfff;
                font-size: 14px;
                letter-spacing: 5px;
            }

            QLabel#sectionTitle {
                color: #e8f1ff;
                font-size: 17px;
                font-weight: 700;
            }

            QLabel#muted {
                color: #9fb4d7;
                font-size: 12px;
            }

            QPushButton#nav {
                background: transparent;
                border: 1px solid transparent;
                border-radius: 12px;
                color: #d9e7ff;
                text-align: left;
                padding: 12px 15px;
                font-size: 14px;
            }

            QPushButton#nav:hover {
                background: rgba(45, 115, 255, 90);
                border: 1px solid #368bff;
            }

            QPushButton#navActive {
                background: qlineargradient(
                    x1:0,
                    y1:0,
                    x2:1,
                    y2:0,
                    stop:0 #235cff,
                    stop:1 #5937e8
                );

                border: 1px solid #65c7ff;
                border-radius: 12px;
                color: white;
                text-align: left;
                padding: 12px 15px;
                font-size: 14px;
                font-weight: 700;
            }

            QLineEdit {
                background: rgba(7, 20, 55, 235);
                border: 1px solid #258bff;
                border-radius: 15px;
                color: white;
                padding: 14px 18px;
                font-size: 14px;
            }

            QLineEdit:focus {
                border: 2px solid #00d9ff;
            }

            QPushButton#send {
                background: qlineargradient(
                    x1:0,
                    y1:0,
                    x2:1,
                    y2:1,
                    stop:0 #168dff,
                    stop:0.55 #6848ff,
                    stop:1 #b738ff
                );

                border: 1px solid #8fdcff;
                border-radius: 14px;
                color: white;
                padding: 12px 22px;
                font-size: 14px;
                font-weight: 800;
            }

            QPushButton#send:hover {
                background: qlineargradient(
                    x1:0,
                    y1:0,
                    x2:1,
                    y2:1,
                    stop:0 #28b6ff,
                    stop:0.55 #805cff,
                    stop:1 #d34cff
                );
            }

            QPushButton#mic {
                background: rgba(12, 35, 75, 230);
                border: 1px solid #00c8ff;
                border-radius: 14px;
                color: #7fe8ff;
                font-size: 20px;
                padding: 8px 15px;
            }

            QTextEdit {
                background: rgba(3, 11, 31, 225);
                border: 1px solid rgba(52, 119, 218, 100);
                border-radius: 14px;
                color: #e9f2ff;
                padding: 12px;
                font-size: 13px;
            }

            QProgressBar {
                background: rgba(9, 18, 48, 230);
                border: none;
                border-radius: 6px;
                height: 8px;
                text-align: center;
            }

            QProgressBar::chunk {
                background: qlineargradient(
                    x1:0,
                    y1:0,
                    x2:1,
                    y2:0,
                    stop:0 #00d9ff,
                    stop:0.5 #5d63ff,
                    stop:1 #f04dff
                );

                border-radius: 6px;
            }
        """)

        # ==============================
        # BUILD UI
        # ==============================

        self.build_ui()

        # activity_box now exists, so startup logging is safe.
        self.add_activity(
            "General AI brain configured."
            if self.llm.enabled
            else "General AI brain not configured; local AI fallback active."
        )

        # ==============================
        # CLOCK
        # ==============================

        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)

        self.update_clock()

        # ==============================
        # STARTUP ACTIVITY
        # ==============================

        self.add_activity("System started")
        self.add_activity("AI Core initialized")
        self.add_activity("Computer Control initialized")
        self.add_activity("Safety system active")
        self.add_activity("Waiting for user command...")

        # Start the webcam automatically inside the JARVIS application.
        self.start_embedded_vision()

    # ==========================================================
    # BUILD UI
    # ==========================================================

    def build_ui(self):

        root = QHBoxLayout(self)

        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(0)

        # ==============================
        # BACKGROUND
        # ==============================

        bg = BackgroundWidget(
            "assets/jarvis_background.png"
        )

        bg.setParent(self)
        bg.lower()
        bg.setGeometry(self.rect())

        self.bg = bg

        # ==============================
        # MAIN SHELL
        # ==============================

        shell = QHBoxLayout()

        shell.setContentsMargins(0, 0, 0, 0)
        shell.setSpacing(10)

        # ======================================================
        # SIDEBAR
        # ======================================================

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(165)

        side = QVBoxLayout(sidebar)

        side.setContentsMargins(
            14,
            22,
            14,
            18
        )

        side.setSpacing(10)

        # LOGO

        logo = QLabel("◉")

        logo.setAlignment(Qt.AlignCenter)

        logo.setStyleSheet(
            "color:#27baff; "
            "font-size:55px; "
            "font-weight:900;"
        )

        side.addWidget(logo)

        # BRAND

        brand = QLabel("JARVIS")

        brand.setObjectName("brand")
        brand.setAlignment(Qt.AlignCenter)

        side.addWidget(brand)

        # SUB BRAND

        sub = QLabel("INFINITY 2026")

        sub.setObjectName("brandSub")
        sub.setAlignment(Qt.AlignCenter)

        side.addWidget(sub)

        side.addSpacing(22)

        # NAVIGATION

        self.add_nav(
            side,
            "⌂   Home",
            True
        )

        self.add_nav(
            side,
            "◌   Chat"
        )

        self.add_nav(
            side,
            "☑   Tasks"
        )

        self.add_nav(
            side,
            "▣   Vision"
        )

        self.add_nav(
            side,
            "♩   Voice"
        )

        self.add_nav(
            side,
            "⚙   Settings"
        )

        self.add_nav(
    side,
    "▦   Dataset"
)
        side.addStretch()

        # QUOTE

        quote = QLabel(
            '"A smarter tomorrow\n'
            'starts with a better today."'
        )

        quote.setWordWrap(True)

        quote.setAlignment(Qt.AlignCenter)

        quote.setStyleSheet(
            "color:#a9c9ff; "
            "font-size:11px; "
            "font-style:italic;"
        )

        side.addWidget(quote)

        shell.addWidget(sidebar)

        # ======================================================
        # CENTER
        # ======================================================

        center = QVBoxLayout()

        center.setContentsMargins(
            10,
            10,
            10,
            10
        )

        center.setSpacing(10)

        # ======================================================
        # TOP BAR
        # ======================================================

        top = QHBoxLayout()

        search = QLineEdit()

        search.setPlaceholderText(
            "✦  How can I assist you today?"
        )

        search.setReadOnly(True)

        top.addWidget(search, 1)

        # CLOCK

        self.clock = QLabel()

        self.clock.setAlignment(Qt.AlignCenter)

        self.clock.setMinimumWidth(170)

        self.clock.setStyleSheet(
            "color:#eaf4ff; "
            "font-size:13px; "
            "font-weight:700;"
        )

        top.addWidget(self.clock)

        # ONLINE STATUS

        online = QLabel(
            "● SYSTEM ONLINE"
        )

        online.setStyleSheet(
            "color:#00f5c8; "
            "font-weight:800; "
            "padding:10px 15px; "
            "border:1px solid #00e6d0; "
            "border-radius:12px; "
            "background:rgba(0,70,75,170);"
        )

        top.addWidget(online)

        center.addLayout(top)

        # ======================================================
        # STATUS CARDS
        # ======================================================

        status_row = QHBoxLayout()

        status_row.setSpacing(10)

        # AI CORE
        status_row.addWidget(
            self.status_card(
                "AI CORE",
                "READY",
                "cyan",
                "◉",
                "Intent • Reasoning • Planning"
            )
        )

        # VOICE
        status_row.addWidget(
            self.status_card(
                "VOICE",
                "STANDBY",
                "purple",
                "♩",
                "Speech Interface"
            )
        )

        # VISION
        status_row.addWidget(
            self.status_card(
                "VISION",
                "STANDBY",
                "teal",
                "◈",
                "Camera • OCR • Analysis"
            )
        )

        # SAFETY
        status_row.addWidget(
            self.status_card(
                "SAFETY",
                "ACTIVE",
                "orange",
                "◇",
                "Permission • Secure Actions"
            )
        )

        # DATASET
        status_row.addWidget(
            self.status_card(
                "DATASET",
                f"{self.dataset_size} SAMPLES",
                "teal",
                "▦",
                f"{self.intent_count} Intents • ML Training"
            )
        )

        # ADD STATUS CARDS TO CENTER LAYOUT
        center.addLayout(status_row)

        # ======================================================
        # SITUATION AWARENESS
        # ======================================================

        situation_frame = QFrame()
        situation_frame.setObjectName("situationFrame")

        situation_layout = QVBoxLayout(
            situation_frame
        )

        # Title
        situation_title = QLabel(
            "🧠  WHAT SHOULD I DO NEXT?"
        )

        situation_title.setStyleSheet("""
            QLabel {
                color: #8fdcff;
                font-size: 18px;
                font-weight: bold;
                padding: 5px;
            }
        """)

        situation_layout.addWidget(
            situation_title
        )

        # Recommendation
        self.recommendation_label = QLabel(
            "Analyzing current situation..."
        )

        self.recommendation_label.setWordWrap(True)

        self.recommendation_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 5px;
            }
        """)

        situation_layout.addWidget(
            self.recommendation_label
        )

        # Reason
        self.reason_label = QLabel(
            "Reason: Waiting for situation analysis."
        )

        self.reason_label.setWordWrap(True)

        self.reason_label.setStyleSheet("""
            QLabel {
                color: #b8c9df;
                font-size: 13px;
                padding: 5px;
            }
        """)

        situation_layout.addWidget(
            self.reason_label
        )

        # Priority
        self.priority_label = QLabel(
            "Priority: --"
        )

        self.priority_label.setStyleSheet("""
            QLabel {
                color: #ffb86c;
                font-size: 13px;
                font-weight: bold;
                padding: 5px;
            }
        """)

        situation_layout.addWidget(
            self.priority_label
        )

        # Analyze button
        analyze_button = QPushButton(
            "ANALYZE SITUATION"
        )

        analyze_button.setCursor(
            Qt.PointingHandCursor
        )

        analyze_button.clicked.connect(
            self.update_situation
        )

        situation_layout.addWidget(
            analyze_button
        )

        center.addWidget(
            situation_frame
        )

      
        # ======================================================
        # MAIN CONTENT
        # ======================================================

        middle = QHBoxLayout()

        middle.setSpacing(10)

        # ======================================================
        # CHAT PANEL
        # ======================================================

        chat = QFrame()

        chat.setObjectName("glass")

        chat_layout = QVBoxLayout(chat)

        chat_layout.setContentsMargins(
            15,
            14,
            15,
            14
        )

        # CHAT HEADER

        chat_head = QHBoxLayout()

        title = QLabel(
            "◌  JARVIS CONVERSATION"
        )

        title.setObjectName(
            "sectionTitle"
        )

        chat_head.addWidget(title)

        chat_head.addStretch()

        badge = QLabel(
            "✦ Context-Aware • Safe • Learning"
        )

        badge.setStyleSheet(
            "color:#8fe9ff; "
            "border:1px solid #357fff; "
            "border-radius:10px; "
            "padding:7px 10px; "
            "background:rgba(20,55,120,130);"
        )

        chat_head.addWidget(badge)

        chat_layout.addLayout(chat_head)

        # CHAT BOX

        self.chat_box = QTextEdit()

        self.chat_box.setReadOnly(True)

        self.chat_box.setHtml("""
            <div style="color:#50dcff;font-size:14px;">
                <b>JARVIS</b> &nbsp; 06:23 PM
            </div>

            <div style="margin-top:6px;">
                Hello! I am JARVIS Infinity 2026.<br>
                My AI brain is online and ready.
            </div>

            <br>

            <div style="color:#9ec4ff;">
                Try these commands:
            </div>

            <div style="margin-top:5px;">
                • I have a project review tomorrow<br>
                • Create a plan<br>
                • Show my tasks<br>
                • Open my project
            </div>
        """)

        chat_layout.addWidget(
            self.chat_box,
            1
        )

        # ======================================================
        # COMMAND INPUT
        # ======================================================

        input_row = QHBoxLayout()

        # ATTACH BUTTON

        attach = QPushButton("📎")

        attach.setObjectName("mic")

        attach.setFixedWidth(52)

        input_row.addWidget(attach)

        # COMMAND INPUT

        self.command_input = QLineEdit()

        self.command_input.setPlaceholderText(
            "Type a command..."
        )

        self.command_input.returnPressed.connect(
            self.send_command
        )

        input_row.addWidget(
            self.command_input,
            1
        )

        # MICROPHONE

        mic = QPushButton("🎙")

        mic.setObjectName("mic")

        mic.setFixedWidth(55)

        mic.clicked.connect(
            self.listen_voice
        )

        input_row.addWidget(mic)

        # SEND

        send = QPushButton(
            "➤  SEND"
        )

        send.setObjectName("send")

        send.clicked.connect(
            self.send_command
        )

        input_row.addWidget(send)

        chat_layout.addLayout(input_row)

        middle.addWidget(
            chat,
            2
        )

        # ======================================================
        # RIGHT PANEL
        # ======================================================

        right = QVBoxLayout()

        right.setSpacing(10)

        # ======================================================
        # EMBEDDED VISION PANEL
        # ======================================================
        vision_frame = QFrame()
        vision_frame.setObjectName("tealCard")
        vision_layout = QVBoxLayout(vision_frame)
        vision_layout.setContentsMargins(10, 10, 10, 10)

        vision_head = QHBoxLayout()
        vision_title = QLabel("◈  JARVIS VISION")
        vision_title.setObjectName("sectionTitle")
        vision_head.addWidget(vision_title)
        vision_head.addStretch()

        self.vision_status = QLabel("● CAMERA STARTING")
        self.vision_status.setStyleSheet(
            "color:#7fe8ff; font-size:11px; font-weight:800;"
        )
        vision_head.addWidget(self.vision_status)
        vision_layout.addLayout(vision_head)

        self.camera_view = QLabel("Initializing webcam...\n\nPlease allow camera access if Windows asks.")
        self.camera_view.setAlignment(Qt.AlignCenter)
        self.camera_view.setMinimumHeight(450)
        self.camera_view.setStyleSheet(
            "background:#020713; border:1px solid #00e6d0; "
            "border-radius:12px; color:#75dfff; font-size:13px;"
        )
        self.camera_view.setScaledContents(False)
        vision_layout.addWidget(self.camera_view)

        vision_controls = QHBoxLayout()
        self.vision_toggle = QPushButton("◉  CAMERA ONLINE")
        self.vision_toggle.setObjectName("mic")
        self.vision_toggle.clicked.connect(self.toggle_embedded_vision)
        vision_controls.addWidget(self.vision_toggle)

        self.face_count_label = QLabel("Faces: 0")
        self.face_count_label.setStyleSheet(
            "color:#bcefff; font-weight:700; padding:8px;"
        )
        vision_controls.addWidget(self.face_count_label)
        vision_controls.addStretch()
        vision_layout.addLayout(vision_controls)

        right.addWidget(vision_frame)

        # ======================================================
        # CURRENT TASK
        # ======================================================

        task = QFrame()

        task.setObjectName(
            "purpleCard"
        )

        task_layout = QVBoxLayout(task)

        task_title = QLabel(
            "◉  CURRENT TASK"
        )

        task_title.setObjectName(
            "sectionTitle"
        )

        task_layout.addWidget(
            task_title
        )

        task_sub = QLabel(
            "AI-generated preparation plan"
        )

        task_sub.setObjectName(
            "muted"
        )

        task_layout.addWidget(
            task_sub
        )

        self.task_label = QLabel(
            "No active task\n\n"
            "Waiting for your command..."
        )

        self.task_label.setWordWrap(True)

        self.task_label.setStyleSheet(
            "background:rgba(20,35,95,180); "
            "border:1px solid #6b53ff; "
            "border-radius:12px; "
            "padding:15px; "
            "color:#eaf2ff;"
        )

        task_layout.addWidget(
            self.task_label
        )

        # PROGRESS BAR

        self.task_progress = QProgressBar()

        self.task_progress.setValue(0)

        task_layout.addWidget(
            self.task_progress
        )

        right.addWidget(task)

        # ======================================================
        # ACTIVITY LOG
        # ======================================================

        activity = QFrame()

        activity.setObjectName(
            "glass"
        )

        activity_layout = QVBoxLayout(
            activity
        )

        activity_head = QHBoxLayout()

        activity_title = QLabel(
            "〽  ACTIVITY LOG"
        )

        activity_title.setObjectName(
            "sectionTitle"
        )

        activity_head.addWidget(
            activity_title
        )

        activity_head.addStretch()

        clear = QPushButton(
            "Clear"
        )

        clear.setStyleSheet(
            "background:rgba(130,30,180,150); "
            "border:1px solid #c35cff; "
            "border-radius:9px; "
            "padding:7px 12px;"
        )

        clear.clicked.connect(
            lambda: self.activity_box.clear()
        )

        activity_head.addWidget(clear)

        activity_layout.addLayout(
            activity_head
        )

        self.activity_box = QTextEdit()

        self.activity_box.setReadOnly(True)

        activity_layout.addWidget(
            self.activity_box
        )

        right.addWidget(
            activity,
            1
        )

        middle.addLayout(
            right,
            1
        )

        center.addLayout(
            middle,
            1
        )

        # ======================================================
        # FOOTER
        # ======================================================

        bottom = QHBoxLayout()

        footer = QLabel(
            "JARVIS INFINITY 2026  •  "
            "Context-Aware AI  •  Safety Active"
        )

        footer.setStyleSheet(
            "color:#7fa4d5; "
            "font-size:11px;"
        )

        bottom.addWidget(
            footer
        )

        bottom.addStretch()

        center.addLayout(
            bottom
        )

        shell.addLayout(
            center,
            1
        )

        root.addLayout(
            shell
        )

        # Initial situation analysis
        self.update_situation()

    # ==========================================================
    # NAVIGATION BUTTON
    # ==========================================================

    def add_nav(
        self,
        layout,
        text,
        active=False
    ):

        button = QPushButton(text)

        button.setObjectName(
            "navActive"
            if active
            else "nav"
        )

        button.setCursor(
            Qt.PointingHandCursor
        )

        layout.addWidget(button)

        if "Dataset" in text:
            button.clicked.connect(self.show_dataset)

        if "Voice" in text:
            button.clicked.connect(self.listen_voice)

    # ==========================================================
    # STATUS CARD
    # ==========================================================

    def status_card(
        self,
        name,
        value,
        theme,
        icon,
        description
    ):

        card = QFrame()

        card.setObjectName({
            "cyan": "cyanCard",
            "purple": "purpleCard",
            "teal": "tealCard",
            "orange": "orangeCard"
        }[theme])

        layout = QHBoxLayout(card)

        layout.setContentsMargins(
            12,
            10,
            12,
            10
        )

        # ICON

        icon_label = QLabel(icon)

        icon_label.setAlignment(
            Qt.AlignCenter
        )

        icon_label.setFixedSize(
            52,
            52
        )

        icon_label.setStyleSheet(
            "font-size:27px; "
            "border:1px solid rgba(255,255,255,100); "
            "border-radius:26px; "
            "background:rgba(255,255,255,25);"
        )

        layout.addWidget(
            icon_label
        )

        # TEXT

        text = QVBoxLayout()

        n = QLabel(name)

        n.setStyleSheet(
            "color:#c8d9f7; "
            "font-size:11px; "
            "font-weight:700;"
        )

        text.addWidget(n)

        v = QLabel(value)

        v.setStyleSheet(
            "color:#ffffff; "
            "font-size:18px; "
            "font-weight:900;"
        )

        text.addWidget(v)

        d = QLabel(description)

        d.setStyleSheet(
            "color:#9db8df; "
            "font-size:9px;"
        )

        d.setWordWrap(True)

        text.addWidget(d)

        layout.addLayout(
            text,
            1
        )

        return card

    # ==========================================================
    # VOICE CONTROL
    # ==========================================================

    def listen_voice(self):

        if self.voice_worker is not None and self.voice_worker.isRunning():
            return

        self.add_chat_message(
            "JARVIS",
            "🎤 Listening... Please speak your command."
        )

        self.add_activity(
            "Voice control activated."
        )

        self.voice_worker = VoiceWorker(
            self.voice
        )

        self.voice_worker.finished.connect(
            self.voice_command_received
        )

        self.voice_worker.start()

    def voice_command_received(self, command):

        # The previous QThread has finished. Clear the reference so the
        # microphone can be used again and again.
        self.voice_worker = None

        if not command:
            message = "I couldn't understand the voice command. Please try again."
            self.add_chat_message("JARVIS", message)
            self.add_activity("Voice command was empty or not understood.")
            self.speak_response(message)
            return

        self.add_chat_message(
            "YOU",
            f"🎤 {command}"
        )

        self.add_activity(
            f"Voice command received: {command}"
        )

        self.process_command(command)

    # ==========================================================
    # TEXT-TO-SPEECH
    # ==========================================================

    def speak_response(self, text):
        """Speak every JARVIS response without blocking the dashboard."""
        if not text:
            return

        self.add_activity("🔊 JARVIS voice response queued.")

        try:
            self.speaker.speak(text)
        except Exception as error:
            print("TTS ERROR:", repr(error))
            self.add_activity(f"❌ TTS ERROR: {error}")

    # ==========================================================
    # SEND COMMAND
    # ==========================================================

    def send_command(self):

        message = (
            self.command_input
            .text()
            .strip()
        )

        if not message:
            return

        self.add_chat_message(
            "YOU",
            message
        )

        self.command_input.clear()

        self.process_command(
            message
        )

    # ==========================================================
    # PROCESS COMMAND
    # ==========================================================

    def process_command(self, message):
        """Route a user command through direct app control, local web actions, AI, and ML fallback."""
        message = (message or "").strip()
        if not message:
            return

        lower = message.lower().strip()

        # ======================================================
        # SAFETY + PERMISSION GATE
        # ======================================================
        # A user can approve a pending action by replying "yes" or
        # "approve". High-risk actions are never executed silently.
        if self.pending_safety_action is not None and lower in {
            "yes", "yes please", "approve", "approved", "allow", "proceed"
        }:
            pending = self.pending_safety_action
            self.pending_safety_action = None

            self.add_activity("🛡️ User permission granted")
            self.status_card("AI CORE", "PERMISSION GRANTED", "User approval received")

            # Keep high-risk execution explicit and safe. The current
            # project has no destructive file/system executor wired in.
            response = (
                "✅ PERMISSION GRANTED\n\n"
                f"Action: {pending['action']}\n"
                f"Risk Level: {pending['risk']}\n\n"
                "JARVIS can now continue to the execution stage. "
                "No destructive system action was performed because "
                "a dedicated safe executor is not yet connected."
            )
            self.add_chat_message("JARVIS", response)
            self.speaker.speak(response)
            return

        if self.pending_safety_action is not None and lower in {
            "no", "no thanks", "deny", "denied", "cancel", "stop"
        }:
            pending = self.pending_safety_action
            self.pending_safety_action = None

            self.add_activity("🛡️ User permission denied")
            self.status_card("AI CORE", "ACTION BLOCKED", "User permission denied")

            response = (
                "🛑 ACTION BLOCKED\n\n"
                f"Action: {pending['action']}\n"
                "Reason: User denied permission."
            )
            self.add_chat_message("JARVIS", response)
            self.speaker.speak(response)
            return

        safety_assessment = self.safety_engine.assess_action(message)

        if safety_assessment["risk"] == "HIGH":
            self.pending_safety_action = safety_assessment

            self.add_activity("🛡️ High-risk action detected")
            self.status_card("SAFETY", "PERMISSION REQUIRED", "Waiting for user approval")

            permission = self.safety_engine.request_permission(
                safety_assessment
            )
            response = permission["message"]

            self.add_chat_message("JARVIS", response)
            self.speaker.speak(response)
            return

        self.add_activity(
            f"🛡️ Safety check: {safety_assessment['risk']} risk"
        )
        self.add_activity(f"Command received: {message}")
        self.task_progress.setValue(20)
        self.task_label.setText(
            "JARVIS AI\n\n"
            "Understanding your request..."
        )
        self.add_activity("🧠 JARVIS reasoning started")

        # ======================================================
        # DIRECT APPLICATION ROUTING
        # ======================================================
        # These simple commands must be handled locally before the LLM.
        app_commands = {
            "notepad": "notepad",
            "note pad": "notepad",
            "calculator": "calculator",
            "calc": "calculator",
            "vs code": "vscode",
            "vscode": "vscode",
            "visual studio code": "vscode",
            "chrome": "chrome",
            "google chrome": "chrome",
            "spotify": "spotify",
            "word": "word",
            "microsoft word": "word",
            "powerpoint": "powerpoint",
            "power point": "powerpoint",
            "excel": "excel",
            "microsoft excel": "excel",
            "file explorer": "explorer",
            "explorer": "explorer",
            "command prompt": "cmd",
            "cmd": "cmd",
            "powershell": "powershell",
        }

        requested_app = None
        if lower.startswith(("open ", "launch ", "start ")):
            target = re.sub(r"^(open|launch|start)\s+", "", lower).strip()
            for app_name in sorted(app_commands, key=len, reverse=True):
                if target == app_name or target.startswith(app_name + " "):
                    requested_app = app_commands[app_name]
                    break

        if requested_app:
            self.task_progress.setValue(40)
            self.task_label.setText(
                "APPLICATION REQUEST\n\n"
                f"Opening {requested_app.upper()}..."
            )
            self.add_activity(f"🖥 Direct application route: {requested_app}")

            success, result_message = self.computer.open_application(requested_app)

            if success:
                self.task_progress.setValue(100)
                self.task_label.setText(
                    "APPLICATION OPENED\n\n"
                    f"{requested_app.upper()} is running."
                )
                response = f"Permission-free local action completed. {result_message}"
                self.add_chat_message("JARVIS", response)
                self.speak_response(response)
                self.add_activity(f"✅ {requested_app} opened successfully")
            else:
                self.task_progress.setValue(0)
                self.task_label.setText(
                    "APPLICATION ERROR\n\n"
                    "The application could not be opened."
                )
                response = f"I couldn't open {requested_app}. {result_message}"
                self.add_chat_message("JARVIS", response)
                self.speak_response(response)
                self.add_activity(f"❌ Failed to open {requested_app}: {result_message}")
            return

        # ======================================================
        # MEMORY
        # ======================================================
        memory_request = (
            "memory" in lower
            and any(word in lower for word in ("open", "show", "view", "check", "my"))
        )
        if memory_request and hasattr(self, "show_memory"):
            self.show_memory()
            return

        # ======================================================
        # LOCAL WEBSITE ROUTING
        # ======================================================
        try:
            natural_web_result = self._handle_natural_web_command(message)
        except Exception:
            natural_web_result = None

        if natural_web_result:
            self._show_ai_response(
                natural_web_result.get("message", ""),
                natural_web_result
            )
            return

        try:
            local_result = self.llm._local_web_action(message)
        except Exception as error:
            local_result = None
            self.add_activity(f"⚠ Local web routing error: {error}")

        if local_result:
            self._show_ai_response(
                local_result.get("message", ""),
                local_result
            )
            return

        # ======================================================
        # CODING AGENT
        # ======================================================

        # ------------------------------------------------------
        # SECOND MESSAGE: DEBUG SUBMITTED CODE
        # ------------------------------------------------------
        if self.coding_mode and self.coding_operation == "debug":
            self.coding_mode = False
            self.coding_operation = None

            self.task_progress.setValue(35)
            self.task_label.setText("CODING AGENT\n\nAnalyzing your code...")
            self.add_activity("💻 Coding Debugger analyzing submitted code")

            try:
                result = self.coding_agent.debug_code(message)
                response = self.coding_agent.format_verification(result)
                if result.get("verified"):
                    self.task_progress.setValue(100)
                    self.task_label.setText("CODING DEBUGGER COMPLETE\n\nCode verified.")
                else:
                    self.task_progress.setValue(0)
                    self.task_label.setText("CODING DEBUGGER\n\nReview required.")
                self.add_chat_message("JARVIS", response)
                self.speak_response(response)
                self.add_activity("💻 Coding Debugger completed")
            except Exception as error:
                response = f"Coding Debugger error: {error}"
                self.task_progress.setValue(0)
                self.task_label.setText("CODING DEBUGGER ERROR")
                self.add_chat_message("JARVIS", response)
                self.speak_response(response)
                self.add_activity(f"❌ Coding Debugger error: {error}")
            return

        # ------------------------------------------------------
        # CODE WRITER: GENERATE CODE IMMEDIATELY
        # ------------------------------------------------------
        # Accept natural-language variations such as:
        # "Write a Python calculator", "Create a Java student program",
        # "Generate JavaScript for a todo list", etc.
        writer_request = bool(re.search(
            r"\b(?:write|create|generate|build|make)\b.*\b(?:code|program|script|python|java|javascript|js|html|css)\b",
            lower,
            re.IGNORECASE
        ))

        writer_language_request = bool(re.search(
            r"\b(?:python|java|javascript|js|html|css)\b",
            lower,
            re.IGNORECASE
        ))

        if writer_request and writer_language_request:
            self.task_progress.setValue(40)
            self.task_label.setText("CODE WRITER\n\nGenerating your code...")
            self.add_activity("✨ JARVIS Code Writer activated")
            try:
                result = self.coding_agent.generate_code(message)
                response = self.coding_agent.format_generation(result)
                self.task_progress.setValue(100 if result.get("success") else 0)
                self.task_label.setText("CODE WRITER COMPLETE" if result.get("success") else "CODE WRITER\n\nRequest needs clarification.")
                self.add_chat_message("JARVIS", response)
                self.speak_response(response)
                self.add_activity("✨ Code generation completed" if result.get("success") else "❌ Code generation failed")
            except Exception as error:
                response = f"Code Writer error: {error}"
                self.task_progress.setValue(0)
                self.add_chat_message("JARVIS", response)
                self.speak_response(response)
                self.add_activity(f"❌ Code Writer error: {error}")
            return

        # ------------------------------------------------------
        # FIRST MESSAGE: ACTIVATE CODING DEBUGGER
        # ------------------------------------------------------
        coding_request = any(
            keyword in lower
            for keyword in (
                "debug this code", "debug code", "fix this code",
                "fix code", "analyze this code", "analyze code",
                "check this code", "check code", "run this code",
            )
        )

        if coding_request:
            self.coding_mode = True
            self.coding_operation = "debug"
            self.task_progress.setValue(20)
            self.task_label.setText("CODING DEBUGGER\n\nWaiting for code...")
            self.add_activity("🔧 Coding Debugger activated")
            response = (
                "Coding Debugger activated. "
                "Please paste the Python, Java, JavaScript, HTML, or CSS code you want me to debug."
            )
            self.add_chat_message("JARVIS", response)
            self.speak_response(response)
            self.add_activity("🔧 Waiting for code input")
            return

        # ======================================================
        # NEXT-BEST-ACTION ENGINE
        # ======================================================
        # ---------------------------------------------------------
        # ACTION PLAN REQUEST
        # ---------------------------------------------------------
        action_plan_request = any(
            phrase in lower
            for phrase in (
                "create a plan",
                "make a plan",
                "create action plan",
                "make an action plan",
                "plan my next action",
                "plan what i should do next",
                "give me a plan",
                "what is the plan",
                "action plan",
            )
        )

        if action_plan_request:
            plan_action = "Complete Voice Control"

            # If the user mentions a specific project component,
            # use that component when the planner has a matching plan.
            if "vision" in lower or "webcam" in lower or "camera" in lower:
                plan_action = "Complete Vision Integration"
            elif "coding" in lower or "code" in lower or "debug" in lower:
                plan_action = "Review Coding Agent"
            elif "demo" in lower or "presentation" in lower:
                plan_action = "Prepare Project Demo"
            elif "module" in lower or "modules" in lower:
                plan_action = "Review Project Modules"
            elif "voice" in lower or "speech" in lower or "microphone" in lower:
                plan_action = "Complete Voice Control"

            plan = self.action_planner.create_plan(plan_action)
            response = self.action_planner.format_plan(plan)

            self.add_chat_message("JARVIS", response)
            self.status_card("AI CORE", "ACTION PLAN READY", "Execution plan prepared")
            return

        next_action_request = any(
            phrase in lower
            for phrase in (
                "what should i do next",
                "what do i do next",
                "what should i do now",
                "what should i work on next",
                "recommend my next action",
                "recommend next action",
                "next best action",
                "what is my next action",
                "what should jarvis do next",
            )
        )

        if next_action_request:
            self.task_progress.setValue(40)
            self.task_label.setText(
                "NEXT-BEST-ACTION ENGINE\n\n"
                "Analyzing context..."
            )
            self.add_activity("🎯 Next-Best-Action Engine activated")

            try:
                project_status = (
                    "Dashboard and Coding Agent are working. "
                    "The project contains Voice Control, Vision, Memory, "
                    "Safety, Verification, and Next-Best-Action modules."
                )

                result = self.next_action_engine.recommend(
                    goal="Complete JARVIS Infinity project",
                    context=message,
                    project_status=project_status,
                    previous_actions=[]
                )

                response = self.next_action_engine.format_recommendation(result)

                self.task_progress.setValue(100)
                self.task_label.setText(
                    "NEXT-BEST-ACTION READY\n\n"
                    f"Recommended: {result['action']}"
                )
                self.add_chat_message("JARVIS", response)
                self.speak_response(response)
                self.add_activity(
                    f"🎯 Recommendation: {result['action']}"
                )
            except Exception as error:
                response = f"Next-Best-Action error: {error}"
                self.task_progress.setValue(0)
                self.task_label.setText("NEXT-BEST-ACTION ERROR")
                self.add_chat_message("JARVIS", response)
                self.speak_response(response)
                self.add_activity(
                    f"❌ Next-Best-Action error: {error}"
                )
            return

        # ======================================================
        # UNIVERSAL AGENT
        # ======================================================
        if self.dashboard_agent is not None:
            try:
                self.task_progress.setValue(35)
                self.task_label.setText(
                    "UNIVERSAL AGENT\n\n"
                    "Understanding goal • Planning • Safety check..."
                )
                self.add_activity("🤖 Universal Agent activated")

                agent_result = self.dashboard_agent.process(
                    message,
                    permission_granted=False
                )
                summary = self.dashboard_agent.get_summary(agent_result)
                status = str(summary.get("status", "UNKNOWN")).upper()
                stage = str(summary.get("stage", "UNKNOWN")).upper()
                safety = str(summary.get("safety", "UNKNOWN")).upper()
                agent_message = summary.get(
                    "message",
                    "No Universal Agent response was returned."
                )

                self.add_activity("🎯 Goal Engine: processed")
                self.add_activity("📋 Dynamic Planner: plan generated")
                self.add_activity(f"🛡 Safety Engine: {safety}")
                self.add_activity(f"⚙ Executor stage: {stage}")

                if status in {"WAITING", "PERMISSION_REQUIRED"}:
                    reply = QMessageBox.question(
                        self,
                        "JARVIS Permission Required",
                        "🛡️ JARVIS wants to perform an external action.\n\n"
                        "This action requires your permission.\n\n"
                        "Do you want to allow it?",
                        QMessageBox.Yes | QMessageBox.No
                    )

                    if reply == QMessageBox.Yes:
                        self.add_activity("✅ User granted permission")
                        approved_result = self.dashboard_agent.process(
                            message,
                            permission_granted=True
                        )
                        approved_summary = self.dashboard_agent.get_summary(approved_result)
                        approved_status = str(
                            approved_summary.get("status", "UNKNOWN")
                        ).upper()
                        approved_message = approved_summary.get(
                            "message",
                            "No response returned."
                        )
                        if approved_status == "SUCCESS":
                            self.task_progress.setValue(100)
                            self.task_label.setText(
                                "UNIVERSAL AGENT COMPLETE\n\n"
                                "Task completed and verified."
                            )
                            self.add_activity("✅ Action executed successfully")
                            self.add_activity("🔍 Verification successful")
                            self._show_ai_response(approved_message, approved_result)
                            return

                        self.task_progress.setValue(90)
                        self.task_label.setText(
                            "ACTION FAILED\n\n"
                            "The approved action could not be completed."
                        )
                        self._show_ai_response(approved_message, approved_result)
                        return

                    self.task_progress.setValue(0)
                    self.task_label.setText(
                        "ACTION CANCELLED\n\n"
                        "Permission denied by user."
                    )
                    response = (
                        "Action cancelled. I will not perform the action without your permission."
                    )
                    self.add_chat_message("JARVIS", response)
                    self.speak_response(response)
                    self.add_activity("❌ User denied permission")
                    return

                if status == "SUCCESS":
                    self.task_progress.setValue(100)
                    self.task_label.setText(
                        "UNIVERSAL AGENT COMPLETE\n\n"
                        "Task completed and verified."
                    )
                    self.add_activity("✅ Universal Agent completed the task")
                    self.add_activity("🔍 Verification successful")
                    self._show_ai_response(agent_message, agent_result)
                    return

                if status == "FAILED":
                    self.task_progress.setValue(90)
                    self.task_label.setText(
                        "UNIVERSAL AGENT\n\n"
                        "Task could not be completed."
                    )
                    self.add_activity("❌ Universal Agent task failed")
                    self._show_ai_response(agent_message, agent_result)
                    return

            except Exception as error:
                self.add_activity(f"⚠ Universal Agent error: {error}")

        # ======================================================
        # GENERAL AI
        # ======================================================
        if self.llm.enabled:
            self.task_progress.setValue(50)
            self.task_label.setText(
                "GENERAL AI\n\n"
                "Processing your request..."
            )
            self.llm_worker = LLMWorker(self.llm.ask, message)
            self.llm_worker.finished.connect(self._llm_result_received)
            self.llm_worker.start()
            return

        # ======================================================
        # LOCAL ML FALLBACK
        # ======================================================
        self.add_activity("⚠ General AI unavailable; using local fallback")
        self._legacy_process_command(message)

    def _llm_result_received(self, result):
        self.llm_worker = None

        message = result.get("message", "") if isinstance(result, dict) else str(result)
        approval_required = bool(result.get("approval_required")) if isinstance(result, dict) else False

        if approval_required:
            self.task_progress.setValue(45)
            self.task_label.setText(
                "🛡 SAFETY CHECK\n\n"
                "MEDIUM-RISK ACTION\n\n"
                "Waiting for your approval."
            )
            self.add_activity("🛡 Medium-risk action requires user approval")

            reply = QMessageBox.question(
                self,
                "JARVIS Permission Required",
                message + "\n\nDo you want to allow this action?",
                QMessageBox.Yes | QMessageBox.No,
            )

            operation = (
                self.llm.approve_pending_action
                if reply == QMessageBox.Yes
                else self.llm.deny_pending_action
            )

            self.add_activity(
                "Permission granted by user"
                if reply == QMessageBox.Yes
                else "User denied permission"
            )

            self.llm_worker = LLMWorker(operation)
            self.llm_worker.finished.connect(self._approval_result_received)
            self.llm_worker.start()
            return

        self._show_ai_response(message, result)

    def _approval_result_received(self, result):
        self.llm_worker = None
        message = result.get("message", "") if isinstance(result, dict) else str(result)
        self.task_progress.setValue(100 if result.get("action_success", True) else 0)
        self.task_label.setText(
            "ACTION VERIFIED ✓" if result.get("action_success", True)
            else "ACTION COMPLETED / DENIED"
        )
        self._show_ai_response(message, result)

    def _show_ai_response(self, message, result=None):
        if not message:
            message = "I completed the request, but I don't have a text summary."

        self.task_progress.setValue(100)
        self.task_label.setText(
            "AI RESPONSE\n\n"
            "Request processed successfully."
        )

        # Keep the chat useful for a showcase while also speaking the answer.
        self.add_chat_message("JARVIS", message)
        self.speak_response(message)
        self.add_activity("✅ General AI response delivered")

        if isinstance(result, dict):
            if result.get("configured"):
                self.add_activity(f"AI model: {self.llm.model}")
            if result.get("approval_required"):
                self.add_activity("Action paused for safety approval")

    def _legacy_process_command(self, message):

        # ----------------------------------
        # AI BRAIN
        # ----------------------------------

        result = self.brain.process(
            message
        )

        intent = str(
            result["intent"]
        )

        confidence = float(
            result["confidence"]
        )

        context = result["context"]

        safety = result["safety"]

        plan = result["plan"]

        # ----------------------------------
        # ACTIVITY LOG
        # ----------------------------------

        self.add_activity(
            f"Command received: {message}"
        )

        self.add_activity(
            f"Intent: {intent} | "
            f"Confidence: {confidence:.2f}"
        )

        # ======================================================
        # GREETING
        # ======================================================

        if intent == "GREETING":

            self.task_progress.setValue(
                10
            )

            self.task_label.setText(
                "SYSTEM READY\n\n"
                "JARVIS is ready for your next command."
            )

            response = (
                "Hello! I am JARVIS Infinity 2026. "
                "My AI brain is online and ready."
            )

            self.add_chat_message("JARVIS", response)
            self.speak_response(response)

        # ======================================================
        # PROJECT REVIEW
        # ======================================================

        elif intent == "PROJECT_REVIEW":

            deadline = context.get(
                "deadline"
            )

            self.task_label.setText(
                "PROJECT REVIEW\n\n"
                f"Deadline: "
                f"{deadline or 'Not specified'}\n\n"
                "AI-generated preparation plan"
            )

            self.task_progress.setValue(
                80
            )

            response = (
                "I detected a project review request. "
                f"Confidence is {confidence:.2f}. "
                f"Deadline: {deadline or 'not specified'}. "
                "I created a preparation plan for you."
            )

            self.add_chat_message("JARVIS", response)
            self.speak_response(response)

            self.show_plan(
                plan
            )

        # ======================================================
        # CREATE PLAN
        # ======================================================

        elif intent == "CREATE_PLAN":

            self.task_label.setText(
                "AI GENERATED PLAN\n\n"
                "Preparing your task plan..."
            )

            self.task_progress.setValue(
                60
            )

            response = (
                "Planning intent detected. "
                f"Confidence is {confidence:.2f}. "
                "I created a structured plan for you."
            )

            self.add_chat_message("JARVIS", response)
            self.speak_response(response)

            self.show_plan(
                plan
            )

        # ======================================================
        # TASK STATUS
        # ======================================================

        elif intent == "TASK_STATUS":

            self.task_label.setText(
                "TASK STATUS\n\n"
                "Checking your pending tasks..."
            )

            self.task_progress.setValue(
                50
            )

            response = (
                "I detected a task status request. "
                f"Confidence is {confidence:.2f}."
            )

            self.add_chat_message("JARVIS", response)
            self.speak_response(response)

            self.show_plan(
                plan
            )

        # ======================================================
        # OPEN APPLICATION
        # ======================================================

        elif intent == "OPEN_APPLICATION":

            # ----------------------------------
            # SAFETY DISPLAY
            # ----------------------------------

            self.task_label.setText(
                "🛡 SAFETY CHECK\n\n"
                "MEDIUM-RISK ACTION\n\n"
                "Permission required before execution."
            )

            self.task_progress.setValue(
                25
            )

            response = (
                "I detected an application opening request. "
                f"Confidence is {confidence:.2f}. "
                "This is a medium risk action. "
                "Permission is required before I execute it."
            )

            self.add_chat_message("JARVIS", response)
            self.speak_response(response)

            self.add_activity(
                "🛡 Action waiting for user permission"
            )

            # ----------------------------------
            # PERMISSION POPUP
            # ----------------------------------

            reply = QMessageBox.question(
                self,
                "JARVIS Permission Required",
                "🛡️ JARVIS wants to open an application.\n\n"
                "This is a MEDIUM-RISK action.\n\n"
                "Do you want to allow this action?",
                QMessageBox.Yes | QMessageBox.No
            )

            # ==================================================
            # USER ALLOWED
            # ==================================================

            if reply == QMessageBox.Yes:

                self.add_activity(
                    "Permission granted by user"
                )

                # ----------------------------------
                # EXECUTE COMPUTER ACTION
                # ----------------------------------

                success, result_message = (
    self.computer.open_application("vscode")
)
                    
                

                # ----------------------------------
                # SUCCESS
                # ----------------------------------

                if success:

                    self.task_progress.setValue(
                        100
                    )

                    self.task_label.setText(
                        "APPLICATION OPENED\n\n"
                        "Action completed successfully."
                    )

                    response = "Permission granted. " + result_message
                    self.add_chat_message("JARVIS", response)
                    self.speak_response(response)

                    self.add_activity(
                        "Application opened successfully"
                    )

                # ----------------------------------
                # FAILED
                # ----------------------------------

                else:

                    self.task_progress.setValue(
                        0
                    )

                    self.task_label.setText(
                        "ACTION FAILED\n\n"
                        "Could not open the requested application."
                    )

                    response = "I could not open the application. " + result_message
                    self.add_chat_message("JARVIS", response)
                    self.speak_response(response)

                    self.add_activity(
                        "Application opening failed"
                    )

            # ==================================================
            # USER DENIED
            # ==================================================

            else:

                self.task_progress.setValue(
                    0
                )

                self.task_label.setText(
                    "ACTION CANCELLED\n\n"
                    "User denied permission."
                )

                response = (
                    "Action cancelled. "
                    "I will not open the application without your permission."
                )
                self.add_chat_message("JARVIS", response)
                self.speak_response(response)

                self.add_activity(
                    "User denied permission"
                )

        # ======================================================
        # GENERAL QUESTION
        # ======================================================

        elif intent == "GENERAL_QUESTION":

            self.task_progress.setValue(
                20
            )

            self.task_label.setText(
                "GENERAL QUESTION\n\n"
                "Knowledge module detected."
            )

            response = (
                "I detected a general question. "
                f"Confidence is {confidence:.2f}. "
                "My knowledge and reasoning module will be connected next."
            )

            self.add_chat_message("JARVIS", response)
            self.speak_response(response)

        # ======================================================
        # UNKNOWN
        # ======================================================

        else:

            self.task_progress.setValue(
                0
            )

            self.task_label.setText(
                "UNKNOWN INTENT\n\n"
                "Waiting for clarification..."
            )

            response = (
                "I'm not confident enough to understand your request. "
                f"Confidence is {confidence:.2f}. "
                "Please explain your request in more detail."
            )

            self.add_chat_message("JARVIS", response)
            self.speak_response(response)

            self.add_activity(
                "Unknown intent detected"
            )

        # ======================================================
        # SAFETY LOG
        # ======================================================

        self.add_activity(
            f"Safety Level: {safety['level']}"
        )

        self.add_activity(
            "Permission required: "
            + (
                "YES"
                if safety["permission_required"]
                else "NO"
            )
        )

    # ==========================================================
    # EMBEDDED VISION
    # ==========================================================

    def start_embedded_vision(self):
        """Start the webcam without creating a separate OpenCV window."""
        try:
            if self.vision.start_camera():
                self.vision_timer.start(33)  # ~30 FPS
                self.vision_status.setText("● VISION ONLINE")
                self.vision_status.setStyleSheet(
                    "color:#00f5c8; font-size:11px; font-weight:800;"
                )
                self.vision_toggle.setText("◉  CAMERA ONLINE")
                self.add_activity("👁 Embedded webcam vision started")
            else:
                self.vision_status.setText("● CAMERA OFFLINE")
                self.vision_toggle.setText("◉  CAMERA OFFLINE")
                self.camera_view.setText(
                    "Webcam could not be opened.\n\n"
                    "Check Windows camera permissions and try again."
                )
                self.add_activity("⚠ Webcam could not be opened")
        except Exception as error:
            self.vision_status.setText("● VISION ERROR")
            self.camera_view.setText(f"Vision error:\n{error}")
            self.add_activity(f"❌ Vision startup error: {error}")

    def update_vision_frame(self):
        """Read, detect faces, and render the current frame in QLabel."""
        try:
            frame = self.vision.read_frame()
            if frame is None:
                return

            faces = self.vision.detect_faces(frame)

            for x, y, w, h in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 180), 2)
                cv2.putText(
                    frame,
                    "FACE DETECTED",
                    (x, max(y - 10, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (0, 255, 180),
                    2,
                )

            cv2.putText(
                frame,
                "JARVIS VISION ONLINE",
                (15, 28),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2,
            )

            self.face_count_label.setText(f"Faces: {len(faces)}")

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channels = rgb.shape
            bytes_per_line = channels * width
            image = QImage(
                rgb.data,
                width,
                height,
                bytes_per_line,
                QImage.Format_RGB888,
            ).copy()

            pixmap = QPixmap.fromImage(image)
            self.camera_view.setPixmap(
                pixmap.scaled(
                    self.camera_view.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )
        except Exception as error:
            self.add_activity(f"⚠ Vision frame error: {error}")
            self.vision_timer.stop()

    def toggle_embedded_vision(self):
        """Toggle the embedded webcam on/off."""
        if self.vision.running:
            self.stop_embedded_vision()
        else:
            self.start_embedded_vision()

    def stop_embedded_vision(self):
        self.vision_timer.stop()
        self.vision.release()
        self.camera_view.clear()
        self.camera_view.setText("Camera offline\n\nClick CAMERA OFFLINE to restart.")
        self.vision_status.setText("● CAMERA OFFLINE")
        self.vision_status.setStyleSheet(
            "color:#ff8a8a; font-size:11px; font-weight:800;"
        )
        self.vision_toggle.setText("◉  CAMERA OFFLINE")
        self.face_count_label.setText("Faces: 0")
        self.add_activity("👁 Embedded webcam vision stopped")

    # ==========================================================
    # SITUATION AWARENESS
    # ==========================================================

    def update_situation(self):

        try:
            situation = self.brain.analyze_situation()

            recommendation = situation.get(
                "recommendation",
                situation.get(
                    "recommended_action",
                    "No recommendation available"
                )
            )

            reason = situation.get(
                "reason",
                "JARVIS analyzed the current project situation."
            )

            priority = situation.get("priority", "MEDIUM")

            self.recommendation_label.setText(
                f"Next Action: {recommendation}"
            )

            self.reason_label.setText(
                f"Reason: {reason}"
            )

            self.priority_label.setText(
                f"Priority: {priority}"
            )

            self.add_activity(
                f"Situation analyzed: {recommendation}"
            )

        except Exception as error:

            self.recommendation_label.setText(
                "Next Action: Unable to analyze situation"
            )

            self.reason_label.setText(
                f"Reason: {error}"
            )

            self.priority_label.setText(
                "Priority: CHECK"
            )

    # ==========================================================
    # SHOW AI PLAN
    # ==========================================================

    def show_plan(self, plan):

        if not plan:
            return

        plan_text = (
            "<b style='color:#72e7ff;'>"
            "✦ AI PLAN"
            "</b>"
            "<br><br>"
        )

        for number, step in enumerate(
            plan,
            start=1
        ):

            plan_text += (
                f"<span style='color:#7fdcff;'>"
                f"<b>{number}.</b>"
                f"</span> "
                f"{step}"
                f"<br>"
            )

        self.task_label.setText(
            plan_text
        )

        self.add_activity(
            f"AI generated "
            f"{len(plan)} planning steps"
        )

    # ==========================================================
    # ADD CHAT MESSAGE
    # ==========================================================

    def add_chat_message(
        self,
        sender,
        message
    ):

        color = (
            "#ffe066"
            if sender == "YOU"
            else "#45ddff"
        )

        formatted = html.escape(
            message or ""
        ).replace(
            "\n",
            "<br>"
        )

        self.chat_box.append(
            f"""
            <div style="margin-top:12px;">

                <span style="color:{color};">
                    <b>{sender}</b>
                </span>

                <br>

                <span style="color:#e7efff;">
                    {formatted}
                </span>

            </div>
            """
        )

    # ==========================================================
    # ADD ACTIVITY
    # ==========================================================

    def add_activity(
        self,
        message
    ):

        now = (
            QDateTime
            .currentDateTime()
            .toString("hh:mm:ss")
        )

        self.activity_box.append(
            f'<span style="color:#55e6ff;">●</span> '
            f'<span style="color:#7896bd;">'
            f'{now}'
            f'</span> '
            f'{message}'
        )

    # ==========================================================
    # UPDATE CLOCK
    # ==========================================================

    def update_clock(self):

        now = QDateTime.currentDateTime()

        self.clock.setText(
            now.toString(
                "ddd, d MMM yyyy"
            )
            +
            "\n"
            +
            now.toString(
                "hh:mm AP"
            )
        )

    # ==========================================================
    # RESIZE BACKGROUND
    # ==========================================================

    def resizeEvent(self, event):

        super().resizeEvent(
            event
        )

        if hasattr(
            self,
            "bg"
        ):

            self.bg.setGeometry(
                self.rect()
            )
            
                
    
    def closeEvent(self, event):
        try:
            if self.voice_worker is not None and self.voice_worker.isRunning():
                self.voice_worker.quit()
                self.voice_worker.wait(1000)
        except Exception:
            pass

        try:
            self.stop_embedded_vision()
        except Exception:
            pass

        try:
            self.speaker.stop()
        except Exception:
            pass

        event.accept()

    # ==========================================================
    # DATASET VIEWER
    # ==========================================================

    def show_dataset(self):

        dialog = QDialog(self)

        dialog.setWindowTitle("JARVIS Infinity 2026 - Dataset Viewer")
        dialog.resize(850, 600)

        # ------------------------------------------------------
        # MAIN LAYOUT
        # ------------------------------------------------------

        layout = QVBoxLayout(dialog)

        # ------------------------------------------------------
        # TITLE
        # ------------------------------------------------------

        title = QLabel("▦  JARVIS TRAINING DATASET")

        title.setStyleSheet("""
            QLabel {
                color: #8fdcff;
                font-size: 22px;
                font-weight: bold;
                padding: 10px;
            }
        """)

        layout.addWidget(title)

        # ------------------------------------------------------
        # DATASET INFORMATION
        # ------------------------------------------------------

        info = QLabel(
            f"Training Samples: {self.dataset_size}     |     "
            f"Intents: {self.intent_count}     |     "
            "Model: TF-IDF + Logistic Regression"
        )

        info.setStyleSheet("""
            QLabel {
                color: #d8eaff;
                font-size: 13px;
                padding: 5px 10px;
            }
        """)

        layout.addWidget(info)

        # ------------------------------------------------------
        # TABLE
        # ------------------------------------------------------

        table = QTableWidget()

        table.setRowCount(self.dataset_size)
        table.setColumnCount(3)

        table.setHorizontalHeaderLabels([
            "#",
            "Command",
            "Intent"
        ])

        # ------------------------------------------------------
        # LOAD DATASET INTO TABLE
        # ------------------------------------------------------

        for row in range(self.dataset_size):

            command = self.brain.training_sentences[row]
            intent = self.brain.training_labels[row]

            # Number
            table.setItem(
                row,
                0,
                QTableWidgetItem(str(row + 1))
            )

            # Command
            table.setItem(
                row,
                1,
                QTableWidgetItem(command)
            )

            # Intent
            table.setItem(
                row,
                2,
                QTableWidgetItem(intent)
            )

        # ------------------------------------------------------
        # TABLE DESIGN
        # ------------------------------------------------------

        table.setStyleSheet("""
            QTableWidget {
                background-color: #071126;
                color: #eaf6ff;
                gridline-color: #263b63;
                border: 1px solid #2196f3;
                font-size: 13px;
            }

            QTableWidget::item {
                padding: 8px;
            }

            QTableWidget::item:selected {
                background-color: #123b66;
                color: white;
            }

            QHeaderView::section {
                background-color: #0b1c3d;
                color: #8fdcff;
                padding: 8px;
                border: 1px solid #263b63;
                font-weight: bold;
            }
        """)

        # Column widths
        table.setColumnWidth(0, 60)
        table.setColumnWidth(1, 500)
        table.setColumnWidth(2, 220)

        # Allow scrolling
        table.setAlternatingRowColors(True)

        layout.addWidget(table)

        # ------------------------------------------------------
        # CLOSE BUTTON
        # ------------------------------------------------------

        close_button = QPushButton("CLOSE")

        close_button.setStyleSheet("""
            QPushButton {
                background-color: #071b38;
                color: #8fdcff;
                border: 1px solid #2196f3;
                border-radius: 6px;
                padding: 9px 30px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #12345c;
            }
        """)

        close_button.clicked.connect(dialog.close)

        layout.addWidget(close_button)

        # ------------------------------------------------------
        # SHOW WINDOW
        # ------------------------------------------------------

        dialog.exec()
