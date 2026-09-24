import streamlit as st
import webbrowser
import os
import io
import contextlib
import sqlite3
import hashlib
import secrets
import re
from datetime import datetime, date, time

from debug_engine import debug_code
from code_generator import generate_code


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="JARVIS Infinity",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM LIGHT FUTURISTIC UI
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
            radial-gradient(circle at 8% 12%, rgba(110, 168, 255, 0.32), transparent 26%),
            radial-gradient(circle at 88% 10%, rgba(205, 169, 255, 0.35), transparent 28%),
            radial-gradient(circle at 78% 78%, rgba(255, 177, 221, 0.24), transparent 30%),
            radial-gradient(circle at 18% 88%, rgba(137, 213, 255, 0.22), transparent 28%),
            linear-gradient(135deg, #f8fbff 0%, #edf4ff 35%, #f6efff 68%, #fff5fb 100%);
        color: #18233f;
        min-height: 100vh;
    }

    .main .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    section[data-testid="stSidebar"] {
        background:
            radial-gradient(circle at 50% 0%, rgba(104, 125, 255, 0.20), transparent 32%),
            linear-gradient(180deg, #101a3b 0%, #14234b 48%, #111a38 100%);
        border-right: 1px solid rgba(255,255,255,0.10);
        box-shadow: 8px 0 35px rgba(24, 35, 73, 0.18);
    }

    section[data-testid="stSidebar"] * {
        color: #eef3ff;
    }

    section[data-testid="stSidebar"] .stRadio label {
        border-radius: 12px;
        padding: 8px 10px;
        transition: all .2s ease;
    }

    section[data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(148, 163, 255, 0.14);
        transform: translateX(3px);
    }

    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #d5def8;
    }

    .jarvis-title {
        font-size: 46px;
        font-weight: 900;
        letter-spacing: 1px;
        background: linear-gradient(90deg, #536dff, #8b5cf6, #e879c8, #38a8ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }

    .jarvis-subtitle {
        font-size: 17px;
        color: #65728f;
        margin-top: 4px;
        margin-bottom: 25px;
    }

    .glass-card {
        background: linear-gradient(135deg, rgba(255,255,255,.88), rgba(247,244,255,.70));
        border: 1px solid rgba(126, 145, 205, .20);
        border-radius: 22px;
        padding: 24px;
        box-shadow: 0 16px 45px rgba(74, 91, 145, .13);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        margin-bottom: 18px;
    }

    .status-card {
        position: relative;
        overflow: hidden;
        background: linear-gradient(135deg, rgba(255,255,255,.92), rgba(242,247,255,.78));
        border-radius: 20px;
        padding: 21px;
        border: 1px solid rgba(126, 145, 205, .18);
        box-shadow: 0 12px 32px rgba(74, 91, 145, .11);
        min-height: 125px;
        backdrop-filter: blur(14px);
    }

    .status-card:after {
        content: "";
        position: absolute;
        width: 95px;
        height: 95px;
        right: -28px;
        top: -32px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(125, 154, 255, .22), transparent 68%);
    }

    .status-title {
        font-size: 16px;
        font-weight: 800;
        margin-bottom: 8px;
        color: #1c2948;
    }

    .status-text {
        font-size: 13px;
        color: #697793;
    }

    .overview-card {
        display: flex;
        align-items: center;
        gap: 16px;
        min-height: 105px;
        padding: 20px 22px;
        border-radius: 20px;
        background: linear-gradient(
            135deg,
            rgba(255,255,255,.96),
            rgba(244,247,255,.90),
            rgba(252,241,251,.88)
        );
        border: 1px solid rgba(126,145,205,.22);
        box-shadow: 0 12px 30px rgba(74,91,145,.12);
        color: #1f2d4d;
    }

    .overview-icon {
        width: 52px;
        height: 52px;
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 16px;
        background: linear-gradient(135deg, #e8edff, #f8e8ff);
        font-size: 26px;
        box-shadow: 0 7px 18px rgba(111,92,220,.12);
    }

    .overview-label {
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 1px;
        color: #66739a;
        margin-bottom: 4px;
    }

    .overview-value {
        font-size: 24px;
        line-height: 1.1;
        font-weight: 850;
        color: #27365a;
    }

    .overview-subtitle {
        margin-top: 5px;
        font-size: 11px;
        color: #7885a2;
    }

    .green-dot,.blue-dot,.purple-dot,.orange-dot {
        display:inline-block;
        width:10px;
        height:10px;
        border-radius:50%;
        margin-right:7px;
        box-shadow: 0 0 12px currentColor;
    }
    .green-dot { background:#22c55e; color:#22c55e; }
    .blue-dot { background:#3b82f6; color:#3b82f6; }
    .purple-dot { background:#8b5cf6; color:#8b5cf6; }
    .orange-dot { background:#f59e0b; color:#f59e0b; }

    .page-header {
        position: relative;
        overflow: hidden;
        background:
            radial-gradient(circle at 90% 20%, rgba(226, 174, 255, .42), transparent 28%),
            linear-gradient(135deg, rgba(255,255,255,.94), rgba(235,243,255,.82), rgba(252,239,250,.80));
        border-radius: 26px;
        padding: 30px 32px;
        margin-bottom: 25px;
        border: 1px solid rgba(126,145,205,.18);
        box-shadow: 0 18px 48px rgba(74,91,145,.13);
        backdrop-filter: blur(16px);
    }

    .page-header h1 {
        margin: 0;
        font-size: 34px;
        color: #202d50;
        font-weight: 850;
    }

    .page-header p {
        margin-top: 8px;
        color: #687692;
        font-size: 15px;
    }

    .jarvis-hero {
        position: relative;
        overflow: hidden;
        min-height: 350px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 25px;
        padding: 34px 42px;
        margin-bottom: 28px;
        border-radius: 30px;
        border: 1px solid rgba(119,139,211,.22);
        background:
            radial-gradient(circle at 78% 42%, rgba(178,156,255,.45), transparent 25%),
            radial-gradient(circle at 92% 78%, rgba(255,157,214,.35), transparent 28%),
            linear-gradient(125deg, rgba(255,255,255,.96), rgba(235,243,255,.88), rgba(249,239,255,.88));
        box-shadow: 0 24px 65px rgba(71,87,145,.16);
        backdrop-filter: blur(18px);
    }

    .hero-content {
        position: relative;
        z-index: 2;
        max-width: 65%;
    }

    .hero-badge {
        display: inline-block;
        padding: 7px 13px;
        border-radius: 999px;
        background: rgba(91,95,239,.10);
        border: 1px solid rgba(91,95,239,.16);
        color: #5964cf;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: .8px;
        margin-bottom: 15px;
    }

    .hero-content h1 {
        font-size: clamp(38px, 5vw, 62px);
        line-height: 1.02;
        margin: 0;
        color: #182442;
        font-weight: 900;
        letter-spacing: -1.8px;
    }

    .hero-content h1 span {
        background: linear-gradient(90deg, #536dff, #875cf6, #e879c8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        margin-top: 16px;
        color: #66728e;
        font-size: 17px;
        line-height: 1.65;
        max-width: 720px;
    }

    .hero-features {
        display: flex;
        flex-wrap: wrap;
        gap: 9px;
        margin-top: 22px;
    }

    .hero-feature {
        padding: 9px 13px;
        border-radius: 999px;
        background: rgba(255,255,255,.70);
        border: 1px solid rgba(126,145,205,.18);
        color: #53617d;
        font-size: 12px;
        font-weight: 700;
    }

    .hero-robot {
        position: relative;
        z-index: 2;
        width: 31%;
        min-width: 220px;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    .hero-robot:before {
        content: "";
        position: absolute;
        width: 260px;
        height: 260px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(130,150,255,.30), rgba(222,174,255,.18), transparent 70%);
        filter: blur(4px);
    }

    .hero-icon {
        position: relative;
        z-index: 2;
        font-size: 150px;
        line-height: 1;
        filter: drop-shadow(0 18px 28px rgba(77,91,170,.28));
        animation: jarvisFloat 3s ease-in-out infinite;
    }

    .hero-icon-label {
        position: relative;
        z-index: 2;
        margin-top: 18px;
        font-size: 20px;
        font-weight: 800;
        letter-spacing: 1px;
        color: #334155;
    }

    @keyframes jarvisFloat {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }

    div[data-testid="stCodeBlock"] {
        border-radius: 16px;
        border: 1px solid rgba(126,145,205,.15);
        box-shadow: 0 10px 28px rgba(57,72,120,.10);
    }

    .stButton > button {
        border-radius: 14px;
        border: 1px solid rgba(99,102,241,.18);
        background: linear-gradient(135deg, rgba(255,255,255,.95), rgba(238,243,255,.92));
        color: #33405f;
        font-weight: 750;
        min-height: 44px;
        transition: all .2s ease;
        box-shadow: 0 7px 18px rgba(76,90,150,.08);
    }

    .stButton > button:hover {
        border-color: #9b8cff;
        box-shadow: 0 10px 25px rgba(111,92,220,.17);
        transform: translateY(-2px);
    }

    textarea, input {
        border-radius: 14px !important;
    }

    div[data-testid="stMetric"] {
        background: rgba(255,255,255,.72);
        padding: 16px;
        border-radius: 17px;
        border: 1px solid rgba(126,145,205,.15);
        box-shadow: 0 8px 24px rgba(74,91,145,.08);
    }

    hr {
        border-color: rgba(126,145,205,.18);
    }


    .auth-wrapper {
        max-width: 520px;
        margin: 5vh auto 0 auto;
    }

    .auth-card {
        background: linear-gradient(135deg, rgba(255,255,255,.94), rgba(246,242,255,.84));
        border: 1px solid rgba(126, 145, 205, .22);
        border-radius: 30px;
        padding: 38px;
        box-shadow: 0 24px 70px rgba(72, 86, 145, .18);
        backdrop-filter: blur(18px);
    }

    .auth-logo {
        width: 82px;
        height: 82px;
        margin: 0 auto 16px auto;
        border-radius: 25px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 43px;
        background: linear-gradient(135deg, #dce8ff, #eadcff, #ffdff3);
        box-shadow: 0 12px 35px rgba(113, 92, 220, .18);
    }

    .auth-title {
        text-align: center;
        font-size: 34px;
        font-weight: 900;
        background: linear-gradient(90deg, #536dff, #8b5cf6, #e879c8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }

    .auth-subtitle {
        text-align: center;
        color: #64728f;
        margin-bottom: 25px;
    }

    .auth-note {
        text-align: center;
        color: #7b87a3;
        font-size: 12px;
        margin-top: 18px;
    }

    .user-pill {
        background: rgba(255,255,255,.12);
        border: 1px solid rgba(255,255,255,.12);
        border-radius: 12px;
        padding: 10px 12px;
        color: #eef3ff;
        font-size: 12px;
        margin-bottom: 12px;
        word-break: break-word;
    }
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "history" not in st.session_state:
    st.session_state.history = []

if "generated_code" not in st.session_state:
    st.session_state.generated_code = None

if "debug_result" not in st.session_state:
    st.session_state.debug_result = None

if "last_command" not in st.session_state:
    st.session_state.last_command = ""

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if "pending_action" not in st.session_state:
    st.session_state.pending_action = None


def get_reminder_database_path():
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "jarvis_reminders.db"
    )


def init_reminder_database():
    connection = sqlite3.connect(get_reminder_database_path())
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            reminder_text TEXT NOT NULL,
            reminder_datetime TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    connection.commit()
    connection.close()


def add_reminder(user_email, reminder_text, reminder_datetime):
    connection = sqlite3.connect(get_reminder_database_path())
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO reminders (user_email, reminder_text, reminder_datetime) VALUES (?, ?, ?)",
        (user_email, reminder_text, reminder_datetime)
    )
    connection.commit()
    connection.close()


def get_reminders(user_email):
    connection = sqlite3.connect(get_reminder_database_path())
    cursor = connection.cursor()
    cursor.execute(
        "SELECT id, reminder_text, reminder_datetime, completed FROM reminders WHERE user_email = ? ORDER BY reminder_datetime ASC",
        (user_email,)
    )
    rows = cursor.fetchall()
    connection.close()
    return rows


def complete_reminder(reminder_id):
    connection = sqlite3.connect(get_reminder_database_path())
    cursor = connection.cursor()
    cursor.execute("UPDATE reminders SET completed = 1 WHERE id = ?", (reminder_id,))
    connection.commit()
    connection.close()


def delete_reminder(reminder_id):
    connection = sqlite3.connect(get_reminder_database_path())
    cursor = connection.cursor()
    cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
    connection.commit()
    connection.close()


def get_memory_database_path():
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "jarvis_memory.db"
    )


def init_memory_database():
    connection = sqlite3.connect(get_memory_database_path())
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            memory_text TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    connection.commit()
    connection.close()


def add_memory(user_email, memory_text):
    connection = sqlite3.connect(get_memory_database_path())
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO memories (user_email, memory_text) VALUES (?, ?)",
        (user_email, memory_text.strip())
    )
    connection.commit()
    connection.close()


def get_memories(user_email):
    connection = sqlite3.connect(get_memory_database_path())
    cursor = connection.cursor()
    cursor.execute(
        "SELECT id, memory_text, created_at FROM memories WHERE user_email = ? ORDER BY id DESC",
        (user_email,)
    )
    rows = cursor.fetchall()
    connection.close()
    return rows


def delete_memory(memory_id, user_email):
    connection = sqlite3.connect(get_memory_database_path())
    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM memories WHERE id = ? AND user_email = ?",
        (memory_id, user_email)
    )
    connection.commit()
    connection.close()


def delete_all_memories(user_email):
    connection = sqlite3.connect(get_memory_database_path())
    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM memories WHERE user_email = ?",
        (user_email,)
    )
    connection.commit()
    connection.close()


def get_database_path():
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "jarvis_users.db"
    )


def init_user_database():
    connection = sqlite3.connect(get_database_path())
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    connection.commit()
    connection.close()


def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120000
    ).hex()

    return salt, password_hash


def create_user(email, password):
    salt, password_hash = hash_password(password)

    try:
        connection = sqlite3.connect(get_database_path())
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO users (email, password_hash, salt) VALUES (?, ?, ?)",
            (email, password_hash, salt)
        )
        connection.commit()
        connection.close()
        return True, "Account created successfully."

    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."

    except Exception as error:
        return False, f"Could not create the account: {error}"


def authenticate_user(email, password):
    try:
        connection = sqlite3.connect(get_database_path())
        cursor = connection.cursor()
        cursor.execute(
            "SELECT password_hash, salt FROM users WHERE email = ?",
            (email,)
        )
        user = cursor.fetchone()
        connection.close()

        if not user:
            return False

        stored_hash, salt = user
        _, entered_hash = hash_password(password, salt)

        return secrets.compare_digest(stored_hash, entered_hash)

    except Exception:
        return False


def valid_email(email):
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) is not None


def show_auth_page():
    st.markdown(
        """
        <div class="auth-wrapper">
            <div class="auth-card">
                <div class="auth-logo">🤖</div>
                <div class="auth-title">JARVIS INFINITY</div>
                <div class="auth-subtitle">Your intelligent digital assistant</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    left, center, right = st.columns([1, 2.4, 1])

    with center:
        login_tab, signup_tab = st.tabs(["🔐 Login", "✨ Create Account"])

        with login_tab:
            st.markdown("### Welcome back")
            st.caption("Login to continue to your JARVIS workspace.")

            login_email = st.text_input(
                "Email ID",
                placeholder="you@example.com",
                key="login_email"
            )

            login_password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                key="login_password"
            )

            if st.button(
                "🚀 Login to JARVIS",
                use_container_width=True,
                key="login_button"
            ):
                email = login_email.strip().lower()

                if not email or not login_password:
                    st.warning("Please enter your email ID and password.")

                elif not valid_email(email):
                    st.warning("Please enter a valid email ID.")

                elif authenticate_user(email, login_password):
                    st.session_state.authenticated = True
                    st.session_state.user_email = email
                    st.rerun()

                else:
                    st.error("Incorrect email ID or password.")

        with signup_tab:
            st.markdown("### Create your JARVIS account")
            st.caption("Create an email ID and password to access the assistant.")

            signup_email = st.text_input(
                "Email ID",
                placeholder="you@example.com",
                key="signup_email"
            )

            signup_password = st.text_input(
                "Create Password",
                type="password",
                placeholder="At least 6 characters",
                key="signup_password"
            )

            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Re-enter your password",
                key="confirm_password"
            )

            if st.button(
                "✨ Create Account",
                use_container_width=True,
                key="signup_button"
            ):
                email = signup_email.strip().lower()

                if not email or not signup_password or not confirm_password:
                    st.warning("Please fill in all fields.")

                elif not valid_email(email):
                    st.warning("Please enter a valid email ID.")

                elif len(signup_password) < 6:
                    st.warning("Password must contain at least 6 characters.")

                elif signup_password != confirm_password:
                    st.error("Passwords do not match.")

                else:
                    created, message = create_user(email, signup_password)

                    if created:
                        st.success(message + " You can now login.")
                    else:
                        st.error(message)

    st.markdown(
        """
        <div class="auth-note">
            🔒 Your password is stored as a secure hash.
            &nbsp;•&nbsp; JARVIS Infinity Authentication
        </div>
        """,
        unsafe_allow_html=True
    )


init_user_database()
init_reminder_database()
init_memory_database()

if not st.session_state.authenticated:
    show_auth_page()
    st.stop()


# ============================================================
# VOICE FUNCTIONS
# ============================================================

def recognize_voice(audio_bytes):
    try:
        import speech_recognition as sr

        recognizer = sr.Recognizer()

        audio_file = io.BytesIO(audio_bytes)

        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio)

        return text

    except Exception as e:
        return f"ERROR: {str(e)}"


def jarvis_speak(text):
    try:
        import pyttsx3

        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    except Exception:
        pass


# ============================================================
# COMPUTER ACTIONS
# ============================================================

def open_chrome():
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(
            r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
        )
    ]

    for path in chrome_paths:
        if os.path.exists(path):
            os.startfile(path)
            return True

    try:
        webbrowser.open("https://www.google.com")
        return True
    except Exception:
        return False


def perform_action(action):
    """Execute an approved computer/web action."""
    action_type = action.get("type")

    if action_type == "youtube":
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube."

    if action_type == "spotify":
        webbrowser.open("https://open.spotify.com")
        return "Opening Spotify."

    if action_type == "google":
        webbrowser.open("https://www.google.com")
        return "Opening Google."

    if action_type == "chrome":
        if open_chrome():
            return "Opening Chrome."
        return "I could not open Chrome."

    if action_type == "notepad":
        try:
            os.system("start notepad")
            return "Opening Notepad."
        except Exception:
            return "I could not open Notepad."

    if action_type == "website":
        url = action.get("url", "")
        if url:
            try:
                webbrowser.open(url)
                return f"Opening {action.get('target', 'website')}."
            except Exception:
                return "I could not open that website."

    if action_type == "application":
        target = action.get("target", "application")
        try:
            os.system(f'start "" "{target}"')
            return f"Opening {target}."
        except Exception:
            return f"I could not open {target}."

    return "The requested action is not available."


def request_confirmation(command, action_type, title, description):
    """Store an action until the user explicitly confirms it."""
    pending = {
        "command": command,
        "type": action_type,
        "title": title,
        "description": description
    }

    if action_type == "website":
        target = command[5:].strip() if command.startswith("open ") else ""
        pending["target"] = target
        pending["url"] = target if target.startswith(("http://", "https://")) else "https://" + target

    if action_type == "application":
        pending["target"] = command[5:].strip() if command.startswith("open ") else command

    st.session_state.pending_action = pending
    return f"Confirmation required before {description.lower()}."


def execute_command(command):
    command = command.lower().strip()

    if not command:
        return "Please give me a command."

    st.session_state.history.append(command)
    st.session_state.last_command = command

    # These five common actions open immediately without confirmation.
    if "open youtube" in command or command == "youtube":
        return perform_action({"type": "youtube"})

    if "open spotify" in command or command == "spotify":
        return perform_action({"type": "spotify"})

    if (
        "open chrome" in command
        or "open browser" in command
        or command == "chrome"
    ):
        return perform_action({"type": "chrome"})

    if "open notepad" in command or command == "notepad":
        return perform_action({"type": "notepad"})

    if "open google" in command or command == "google":
        return perform_action({"type": "google"})

    # Any other explicit website/application opening requires confirmation.
    if command.startswith("open "):
        target = command[5:].strip()
        if target:
            if target.startswith(("http://", "https://")) or "." in target:
                url = target if target.startswith(("http://", "https://")) else "https://" + target
                return request_confirmation(
                    command, "website", f"Open {target}",
                    f"opening {target} in your browser"
                )

            return request_confirmation(
                command, "application", f"Open {target}",
                f"opening the application {target}"
            )

    # ========================================================
    # MEMORY COMMANDS
    # ========================================================
    if command.startswith("remember that ") or command.startswith("remember "):
        memory_text = command.split("remember", 1)[1].strip()
        memory_text = memory_text.removeprefix("that ").strip()
        if not memory_text:
            return "Please tell me what you want me to remember."
        add_memory(st.session_state.user_email, memory_text)
        return f"🧠 Memory saved: {memory_text}"

    if (
        "what do you remember" in command
        or "show my memories" in command
        or "show memories" in command
    ):
        memories = get_memories(st.session_state.user_email)
        if not memories:
            return "I do not have any saved memories for your account yet."
        return "🧠 Saved memories:\n" + "\n".join(
            f"{index}. {row[1]}" for index, row in enumerate(memories, start=1)
        )

    if command.startswith("forget "):
        target = command[len("forget "):].strip()
        memories = get_memories(st.session_state.user_email)
        matches = [row for row in memories if target in row[1].lower()]
        if not matches:
            return f"I could not find a memory matching '{target}'."
        delete_memory(matches[0][0], st.session_state.user_email)
        return f"🗑️ I forgot: {matches[0][1]}"

    # Greeting
    if command in ["hello", "hi", "hey jarvis", "hey"]:
        return "Hello! I am JARVIS. How can I help you?"

    # Identity
    if "who are you" in command:
        return (
            "I am JARVIS Infinity, an AI assistant with "
            "voice control, code generation, debugging and automation."
        )

    # Capabilities
    if "what can you do" in command:
        return (
            "I can control applications, respond to voice commands, "
            "generate code, debug code and help you with tasks."
        )

    # Thanks
    if "thank" in command or command == "thanks":
        return "You're welcome!"

    return (
        "I understood your command, but I do not have an action "
        "configured for it yet."
    )


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="text-align:center; padding:10px 0 20px 0;">
            <div style="font-size:42px;">🤖</div>
            <div style="font-size:23px; font-weight:800;">
                JARVIS INFINITY
            </div>
            <div style="font-size:12px; color:#64748b;">
                AI Assistant System
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="user-pill">
            👤 <b>Logged in</b><br>
            {st.session_state.user_email}
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_email = ""
        st.rerun()

    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "🏠 Dashboard",
            "🎤 Voice Assistant",
            "🎙️ Hey JARVIS",
            "💻 Code Generator",
            "🛠️ Code Debugger",
            "⚡ What Should I Do Next?",
            "⏰ Smart Reminders",
            "🧠 JARVIS Memory",
            "🛡️ Safety & System",
            "📜 Command History"
        ]
    )

    st.divider()

    st.markdown(
        """
        <div style="
            padding:15px;
            border-radius:15px;
            background:#ffffff;
            border:1px solid rgba(148,163,184,0.15);
        ">
            <b>● SYSTEM ONLINE</b>
            <br>
            <span style="font-size:12px;color:#64748b;">
                JARVIS Infinity is ready
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# DASHBOARD PAGE
# ============================================================

if page == "🏠 Dashboard":

    hero_visual = '<div class="hero-robot"><div class="hero-icon">🤖</div><div class="hero-icon-label">JARVIS AI</div></div>'

    st.markdown(
        f"""
        <div class="jarvis-hero">
            <div class="hero-content">
                <div class="hero-badge">◉ JARVIS INFINITY • AI ASSISTANT SYSTEM</div>
                <h1>Meet <span>JARVIS</span><br>your intelligent digital assistant.</h1>
                <div class="hero-subtitle">
                    Situation awareness, voice control, computer automation,
                    code generation and intelligent debugging — brought together
                    in one futuristic assistant.
                </div>
                <div class="hero-features">
                    <div class="hero-feature">🎤 Voice Control</div>
                    <div class="hero-feature">🧠 AI Reasoning</div>
                    <div class="hero-feature">💻 Code Intelligence</div>
                    <div class="hero-feature">🛡️ Safety First</div>
                </div>
            </div>
            {hero_visual}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="page-header">
            <h1>🤖 JARVIS Infinity</h1>
            <p>
                Situation Awareness • AI Reasoning • Voice Control •
                Code Intelligence
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            """
            <div class="status-card">
                <div class="status-title">
                    <span class="green-dot"></span>
                    AI CORE READY
                </div>
                <div class="status-text">
                    Intent • Reasoning • Planning
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="status-card">
                <div class="status-title">
                    <span class="blue-dot"></span>
                    VOICE READY
                </div>
                <div class="status-text">
                    Speech Interface
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="status-card">
                <div class="status-title">
                    <span class="purple-dot"></span>
                    CODE AI READY
                </div>
                <div class="status-text">
                    Generation • Debugging
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            """
            <div class="status-card">
                <div class="status-title">
                    <span class="orange-dot"></span>
                    SAFETY ACTIVE
                </div>
                <div class="status-text">
                    Permission • Secure Actions
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="glass-card">
            <h2>✨ What can JARVIS do?</h2>
            <p>
                JARVIS Infinity combines voice interaction, computer
                control, code generation and intelligent debugging
                into one assistant.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="glass-card">
                <h3>🎤 Voice Assistant</h3>
                <p>
                    Speak naturally and JARVIS can execute supported
                    commands such as opening YouTube, Spotify,
                    Chrome and Notepad.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="glass-card">
                <h3>💻 Code Intelligence</h3>
                <p>
                    Generate and debug Python, Java, JavaScript,
                    HTML and CSS from dedicated pages.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("### 📊 System Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="overview-card">
                <div class="overview-icon">🎤</div>
                <div>
                    <div class="overview-label">COMMANDS</div>
                    <div class="overview-value">{len(st.session_state.history)}</div>
                    <div class="overview-subtitle">Commands processed</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="overview-card">
                <div class="overview-icon">💻</div>
                <div>
                    <div class="overview-label">CODE GENERATOR</div>
                    <div class="overview-value">READY</div>
                    <div class="overview-subtitle">Python • Java • JS • HTML • CSS</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="overview-card">
                <div class="overview-icon">🛠️</div>
                <div>
                    <div class="overview-label">CODE DEBUGGER</div>
                    <div class="overview-value">READY</div>
                    <div class="overview-subtitle">Detect • Explain • Fix</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# WAKE WORD PAGE
# ============================================================

elif page == "🎙️ Hey JARVIS":

    st.markdown(
        """
        <div class="page-header">
            <h1>🎙️ Hey JARVIS</h1>
            <p>
                Activate JARVIS by saying <b>“Hey JARVIS”</b> before your command.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="glass-card">
            <h3>✨ Wake Word Detection</h3>
            <p>
                Record a short phrase such as
                <b>“Hey JARVIS, open YouTube”</b>.
                JARVIS will only process the command when the wake phrase is detected.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    wake_col1, wake_col2 = st.columns(2)

    with wake_col1:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-number">🎙️</div>
                <div class="metric-label">WAKE WORD</div>
                <div style="margin-top:8px;font-weight:700;color:#4c43a6;">HEY JARVIS</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with wake_col2:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-number">🔒</div>
                <div class="metric-label">COMMAND GATE</div>
                <div style="margin-top:8px;font-weight:700;color:#4c43a6;">WAKE PHRASE REQUIRED</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("### 🎤 Say the wake word + command")
    st.caption("Example: Hey JARVIS, open YouTube")

    wake_audio = st.audio_input("🎙️ Record: Hey JARVIS + your command", key="wake_word_audio")

    if wake_audio is not None:

        with st.spinner("JARVIS is checking for the wake word..."):
            wake_text = recognize_voice(wake_audio.getvalue())

        if wake_text.startswith("ERROR:"):
            st.error(wake_text)
        else:
            normalized_wake = re.sub(r"[^a-zA-Z0-9 ]", " ", wake_text.lower())
            normalized_wake = " ".join(normalized_wake.split())

            wake_phrases = [
                "hey jarvis",
                "hey jarvis",
                "hey jarvis"
            ]

            wake_detected = any(phrase in normalized_wake for phrase in wake_phrases)

            st.write(f"**Heard:** {wake_text}")

            if wake_detected:
                wake_index = normalized_wake.find("hey jarvis")
                command_text = normalized_wake[wake_index + len("hey jarvis"):].strip(" ,.!?")

                st.success("🟢 Wake word detected — JARVIS is active.")
                jarvis_speak("Yes, I am listening.")

                if command_text:
                    st.info(f"🎯 Command detected: {command_text}")
                    st.session_state.last_command = command_text
                    response = execute_command(command_text)
                    st.success(f"🤖 JARVIS: {response}")
                else:
                    st.warning("Wake word detected. Please record the command after saying “Hey JARVIS”.")
            else:
                st.warning("🔴 Wake word not detected. Please start your phrase with “Hey JARVIS”.")

    st.divider()

    st.markdown("### 🧪 Wake Word Test")
    test_phrase = st.text_input(
        "Test the detector without using the microphone",
        placeholder="Example: Hey JARVIS, open Chrome",
        key="wake_word_test"
    )

    if st.button("🔎 Test Wake Word", use_container_width=True):
        normalized_test = re.sub(r"[^a-zA-Z0-9 ]", " ", test_phrase.lower())
        normalized_test = " ".join(normalized_test.split())

        if "hey jarvis" in normalized_test:
            command_text = normalized_test.split("hey jarvis", 1)[1].strip(" ,.!?")
            st.success("🟢 Wake word detected successfully.")
            if command_text:
                st.info(f"Command after wake word: **{command_text}**")
            else:
                st.info("Wake word detected. No command was included.")
        else:
            st.warning("🔴 Wake word not detected.")

    st.markdown(
        """
        <div class="glass-card" style="margin-top:20px;">
            <h3>ℹ️ How this web-demo version works</h3>
            <p>
                Your browser microphone is activated when you record audio.
                JARVIS transcribes that short recording, checks for the wake phrase,
                and then processes the command. A true always-listening wake word
                requires a background microphone service, which is better suited to
                the desktop JARVIS application.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# VOICE ASSISTANT PAGE
# ============================================================

elif page == "🎤 Voice Assistant":

    st.markdown(
        """
        <div class="page-header">
            <h1>🎤 Voice Assistant</h1>
            <p>
                Talk to JARVIS using your microphone or type a command.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="glass-card">
            <h3>🎙️ Voice Command</h3>
            <p>
                Try saying:
                <b>"Open YouTube"</b>,
                <b>"Open Chrome"</b>,
                <b>"Open Notepad"</b>,
                or
                <b>"Open Spotify"</b>.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    audio = st.audio_input("🎙️ Record your command")

    if audio is not None:

        audio_bytes = audio.getvalue()

        with st.spinner("JARVIS is listening..."):
            voice_text = recognize_voice(audio_bytes)

        if voice_text.startswith("ERROR:"):

            st.error(voice_text)

        else:

            st.success(f"You said: {voice_text}")

            response = execute_command(voice_text)

            st.info(f"🤖 JARVIS: {response}")

            jarvis_speak(response)

    st.divider()

    st.markdown("### ⌨️ Type a Command")

    typed_command = st.text_input(
        "Enter command",
        placeholder="Example: open YouTube"
    )

    if st.button("🚀 Execute Command", use_container_width=True):

        if typed_command.strip():

            response = execute_command(typed_command)

            st.success(response)

            jarvis_speak(response)

    st.divider()

    st.markdown("### ⚡ Quick Actions")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("▶️ YouTube", use_container_width=True):
            response = execute_command("open youtube")
            st.success(response)

    with col2:
        if st.button("🎵 Spotify", use_container_width=True):
            response = execute_command("open spotify")
            st.success(response)

    with col3:
        if st.button("🌐 Chrome", use_container_width=True):
            response = execute_command("open chrome")
            st.success(response)

    with col4:
        if st.button("📝 Notepad", use_container_width=True):
            response = execute_command("open notepad")
            st.success(response)

    with col5:
        if st.button("🔎 Google", use_container_width=True):
            response = execute_command("open google")
            st.success(response)


# ============================================================
# CODE GENERATOR PAGE
# ============================================================

elif page == "💻 Code Generator":

    st.markdown(
        """
        <div class="page-header">
            <h1>💻 JARVIS Code Generator</h1>
            <p>
                Describe what you want to build and JARVIS will
                generate the code for you.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="glass-card">
            <h3>✨ AI Code Generation</h3>
            <p>
                Supported languages:
                <b>Python • Java • JavaScript • HTML • CSS</b>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    language = st.selectbox(
        "🧩 Select Programming Language",
        [
            "Python",
            "Java",
            "JavaScript",
            "HTML",
            "CSS"
        ]
    )

    question = st.text_area(
        "📝 What code do you want?",
        placeholder=(
            "Example: Write a Python program to check "
            "whether a number is prime"
        ),
        height=150
    )

    if st.button(
        "✨ Generate Code",
        use_container_width=True
    ):

        if not question.strip():

            st.warning("Please describe what code you want.")

        else:

            with st.spinner("JARVIS is generating your code..."):

                try:

                    generated = generate_code(
                        question,
                        language
                    )

                    st.session_state.generated_code = generated

                except Exception as e:

                    st.error(
                        f"Code generation error: {str(e)}"
                    )

    if st.session_state.generated_code:

        generated = st.session_state.generated_code

        st.divider()

        st.markdown("### 📌 Generated Result")

        st.info(
            f"Language: {generated['language']}"
        )

        st.markdown(
            f"### {generated['title']}"
        )

        st.code(
            generated["code"],
            language=generated["language"].lower()
        )

        st.markdown("### 🧠 Explanation")

        st.markdown(
            generated["explanation"]
        )

        st.divider()

        st.markdown("### 🔧 Next Step")

        st.info(
            "If you want to check this code for errors, "
            "open the separate 🛠️ Code Debugger page from "
            "the sidebar."
        )

        if st.button(
            "🗑️ Clear Generated Code",
            use_container_width=True
        ):

            st.session_state.generated_code = None
            st.rerun()


# ============================================================
# CODE DEBUGGER PAGE
# ============================================================

elif page == "🛠️ Code Debugger":

    st.markdown(
        """
        <div class="page-header">
            <h1>🛠️ JARVIS Code Debugger</h1>
            <p>
                Detect errors, understand problems and generate
                corrected code.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="glass-card">
            <h3>🔍 Intelligent Code Analysis</h3>
            <p>
                JARVIS can analyze:
                <b>Python • Java • JavaScript • HTML • CSS</b>
            </p>
            <p>
                Workflow:
                Code → Language Detection → Error Analysis →
                Explanation → Corrected Code
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    debug_language = st.selectbox(
        "🧩 Select Language",
        [
            "Auto Detect",
            "Python",
            "Java",
            "JavaScript",
            "HTML",
            "CSS"
        ],
        key="debug_language"
    )

    code_input = st.text_area(
        "💻 Paste your code here",
        placeholder=(
            "Example:\n\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        System.out.println(\"Hello JARVIS\")\n"
            "    }\n"
            "}"
        ),
        height=350,
        key="debug_code_input"
    )

    st.markdown("### ⚙️ Debugging Options")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        debug_button = st.button(
            "🔍 Debug Code",
            use_container_width=True
        )

    with col2:
        fix_button = st.button(
            "🔧 Fix Automatically",
            use_container_width=True
        )

    with col3:
        explain_button = st.button(
            "💡 Explain Error",
            use_container_width=True
        )

    with col4:
        improve_button = st.button(
            "✨ Improve Code",
            use_container_width=True
        )

    if (
        debug_button
        or fix_button
        or explain_button
        or improve_button
    ):

        if not code_input.strip():

            st.warning("Please paste some code first.")

        else:

            try:

                language_to_use = debug_language

                if language_to_use == "Auto Detect":
                    language_to_use = None

                with st.spinner(
                    "JARVIS is analyzing your code..."
                ):

                    result = debug_code(
                        code_input,
                        language_to_use
                    )

                st.session_state.debug_result = result

            except Exception as e:

                st.error(
                    f"Debugger error: {str(e)}"
                )

    if st.session_state.debug_result:

        result = st.session_state.debug_result

        st.divider()

        st.markdown("## 📊 Debugging Result")

        language_result = result.get(
            "language",
            "Unknown"
        )

        status = result.get(
            "status",
            "UNKNOWN"
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Detected Language",
                language_result
            )

        with col2:
            st.metric(
                "Status",
                status
            )

        if status == "ERROR":

            st.error(
                "❌ Errors were found in your code."
            )

        elif status == "WARNING":

            st.warning(
                "⚠️ The code has warnings."
            )

        else:

            st.success(
                "✅ No major errors detected."
            )

        errors = result.get(
            "errors",
            []
        )

        if errors:

            st.markdown("### ❌ Errors")

            for index, error in enumerate(
                errors,
                start=1
            ):

                line = error.get(
                    "line",
                    "Unknown"
                )

                column = error.get(
                    "column",
                    "Unknown"
                )

                message = error.get(
                    "message",
                    "Unknown error"
                )

                explanation = error.get(
                    "explanation",
                    ""
                )

                st.markdown(
                    f"""
                    <div class="glass-card">
                        <h4>Error {index}</h4>
                        <b>Line:</b> {line}<br>
                        <b>Column:</b> {column}<br>
                        <b>Problem:</b> {message}<br>
                        <br>
                        <b>Explanation:</b><br>
                        {explanation}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        warnings = result.get(
            "warnings",
            []
        )

        if warnings:

            st.markdown("### ⚠️ Warnings")

            for warning in warnings:

                if isinstance(
                    warning,
                    dict
                ):

                    st.warning(
                        warning.get(
                            "message",
                            str(warning)
                        )
                    )

                else:

                    st.warning(
                        str(warning)
                    )

        explanation = result.get(
            "explanation",
            ""
        )

        if explanation:

            st.markdown("### 💡 Explanation")

            st.info(explanation)

        message = result.get(
            "message",
            ""
        )

        if message:

            st.markdown("### 📌 JARVIS Analysis")

            st.info(message)

        fixed_code = result.get(
            "fixed_code",
            ""
        )

        if fixed_code:

            st.markdown(
                "### 🔧 Corrected Code"
            )

            st.code(
                fixed_code,
                language=language_result.lower()
            )

        suggestion = result.get(
            "suggestion",
            ""
        )

        if suggestion:

            st.markdown(
                "### 💡 Suggested Fix"
            )

            st.success(suggestion)

        st.divider()

        if st.button(
            "🗑️ Clear Debugger",
            use_container_width=True
        ):

            st.session_state.debug_result = None
            st.rerun()


# ============================================================
# WHAT SHOULD I DO NEXT PAGE
# ============================================================

elif page == "⚡ What Should I Do Next?":

    st.markdown(
        """
        <div class="page-header">
            <h1>⚡ What Should I Do Next?</h1>
            <p>
                Tell JARVIS what is happening and it will identify the
                priority, recommend a practical next action and explain why.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="glass-card">
            <h3>🧠 Situation Awareness</h3>
            <p>
                JARVIS analyzes deadlines, unfinished work, meetings,
                exams and other situations to help you decide what to do next.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    situation = st.text_area(
        "💭 What is happening?",
        placeholder=(
            "Example: My project review is tomorrow and my voice module "
            "is incomplete."
        ),
        height=150,
        key="next_action_situation"
    )

    if st.button("🚀 Analyze Situation", use_container_width=True):

        if not situation.strip():
            st.warning("Please describe your situation first.")
        else:
            text = situation.lower()

            if any(word in text for word in ["tomorrow", "deadline", "due", "presentation", "review"]):
                priority = "HIGH"
                action = "Complete the most important unfinished task first."
                reason = "A deadline or important event is approaching, so the highest-impact unfinished task should be handled first."
                steps = [
                    "Identify the most important unfinished component.",
                    "Complete that component before lower-priority tasks.",
                    "Test the completed work.",
                    "Prepare a final review or backup."
                ]
                intent = "DEADLINE / PROJECT PRIORITY"

            elif any(word in text for word in ["exam", "study", "test"]):
                priority = "HIGH"
                action = "Start with the highest-weight or weakest topic and study it in a focused session."
                reason = "Exam preparation benefits from prioritizing important topics instead of studying everything equally."
                steps = [
                    "List the topics you need to cover.",
                    "Choose the highest-priority topic.",
                    "Study it in a focused session.",
                    "Review yourself with questions or practice problems."
                ]
                intent = "STUDY / EXAM PREPARATION"

            elif "meeting" in text:
                priority = "MEDIUM"
                action = "Prepare the key notes, questions and required materials before the meeting."
                reason = "Preparing the important information first reduces last-minute work."
                steps = [
                    "Review the meeting purpose.",
                    "Prepare important notes and questions.",
                    "Collect required files or links.",
                    "Check everything once before the meeting."
                ]
                intent = "MEETING PREPARATION"

            elif any(word in text for word in ["incomplete", "unfinished", "not working", "error", "problem"]):
                priority = "MEDIUM"
                action = "Fix the most important unfinished or broken component first."
                reason = "Resolving the main blocker can make the remaining tasks easier to complete."
                steps = [
                    "Identify the main blocker.",
                    "Work on that blocker first.",
                    "Test the result.",
                    "Continue with the remaining tasks."
                ]
                intent = "TASK / PROBLEM PRIORITY"

            else:
                priority = "MEDIUM"
                action = "Break the situation into smaller tasks and start with the most important one."
                reason = "Breaking a broad situation into smaller actions makes it easier to decide what to do next."
                steps = [
                    "List the tasks involved.",
                    "Identify which task has the greatest impact.",
                    "Start that task now.",
                    "Review the remaining tasks after completing it."
                ]
                intent = "GENERAL SITUATION"

            st.divider()

            st.markdown("### 🧠 Situation Analysis")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Detected Intent", intent)

            with col2:
                st.metric("Priority", priority)

            with col3:
                st.metric("Decision", "NEXT ACTION")

            st.markdown("### ⚡ Recommended Next Action")
            st.success(action)

            st.markdown("### 💡 Why JARVIS recommends this")
            st.info(reason)

            st.markdown("### 🗺️ Suggested Steps")
            for number, step in enumerate(steps, start=1):
                st.markdown(f"**{number}.** {step}")

            st.markdown("### 🛡️ Human Control")
            st.caption("JARVIS recommends an action; you decide whether to follow it.")


# ============================================================
# SMART REMINDERS PAGE
# ============================================================

elif page == "⏰ Smart Reminders":

    st.markdown(
        """
        <div class="page-header">
            <h1>⏰ Smart Reminders</h1>
            <p>
                Create, store and manage your personal reminders with JARVIS.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="glass-card">
            <h3>📝 Create a Reminder</h3>
            <p>Store a reminder with a specific date and time. Your reminders are saved for your logged-in account.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    reminder_text = st.text_input(
        "📝 Reminder text",
        placeholder="Example: Complete JARVIS presentation",
        key="reminder_text_input"
    )

    col1, col2 = st.columns(2)

    with col1:
        reminder_date = st.date_input(
            "📅 Date",
            value=date.today(),
            min_value=date.today(),
            key="reminder_date_input"
        )

    with col2:
        reminder_time = st.time_input(
            "⏰ Time",
            value=time(9, 0),
            key="reminder_time_input"
        )

    if st.button("➕ Create Reminder", use_container_width=True):
        if not reminder_text.strip():
            st.warning("Please enter reminder text first.")
        else:
            reminder_datetime = datetime.combine(
                reminder_date,
                reminder_time
            )

            if reminder_datetime <= datetime.now():
                st.warning("Please choose a future date and time.")
            else:
                add_reminder(
                    st.session_state.user_email,
                    reminder_text.strip(),
                    reminder_datetime.isoformat(timespec="minutes")
                )
                st.success("✅ Reminder created successfully!")
                st.rerun()

    st.divider()

    reminders = get_reminders(st.session_state.user_email)
    now = datetime.now()

    upcoming = []
    overdue = []
    completed = []

    for reminder in reminders:
        reminder_id, text_value, datetime_value, is_completed = reminder
        reminder_dt = datetime.fromisoformat(datetime_value)

        if is_completed:
            completed.append((reminder_id, text_value, reminder_dt))
        elif reminder_dt < now:
            overdue.append((reminder_id, text_value, reminder_dt))
        else:
            upcoming.append((reminder_id, text_value, reminder_dt))

    st.markdown("### 🟢 Upcoming Reminders")

    if upcoming:
        for reminder_id, text_value, reminder_dt in upcoming:
            col1, col2 = st.columns([5, 1])

            with col1:
                st.markdown(
                    f"""
                    <div class="glass-card">
                        <h4>🟢 {text_value}</h4>
                        <p>📅 {reminder_dt.strftime('%d %B %Y')} &nbsp; ⏰ {reminder_dt.strftime('%I:%M %p')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col2:
                if st.button("✅ Done", key=f"complete_{reminder_id}", use_container_width=True):
                    complete_reminder(reminder_id)
                    st.rerun()

                if st.button("🗑️ Delete", key=f"delete_upcoming_{reminder_id}", use_container_width=True):
                    delete_reminder(reminder_id)
                    st.rerun()
    else:
        st.info("No upcoming reminders.")

    st.markdown("### 🔴 Overdue Reminders")

    if overdue:
        for reminder_id, text_value, reminder_dt in overdue:
            col1, col2 = st.columns([5, 1])

            with col1:
                st.markdown(
                    f"""
                    <div class="glass-card">
                        <h4>🔴 {text_value}</h4>
                        <p>Was due: 📅 {reminder_dt.strftime('%d %B %Y')} &nbsp; ⏰ {reminder_dt.strftime('%I:%M %p')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col2:
                if st.button("✅ Done", key=f"complete_overdue_{reminder_id}", use_container_width=True):
                    complete_reminder(reminder_id)
                    st.rerun()

                if st.button("🗑️ Delete", key=f"delete_overdue_{reminder_id}", use_container_width=True):
                    delete_reminder(reminder_id)
                    st.rerun()
    else:
        st.success("No overdue reminders. 🎉")

    st.markdown("### ✅ Completed Reminders")

    if completed:
        for reminder_id, text_value, reminder_dt in reversed(completed):
            col1, col2 = st.columns([5, 1])

            with col1:
                st.markdown(
                    f"""
                    <div class="glass-card">
                        <h4>✅ {text_value}</h4>
                        <p>Scheduled for: 📅 {reminder_dt.strftime('%d %B %Y')} &nbsp; ⏰ {reminder_dt.strftime('%I:%M %p')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col2:
                if st.button("🗑️ Delete", key=f"delete_completed_{reminder_id}", use_container_width=True):
                    delete_reminder(reminder_id)
                    st.rerun()
    else:
        st.info("No completed reminders yet.")


# ============================================================
# JARVIS MEMORY PAGE
# ============================================================

elif page == "🧠 JARVIS Memory":

    st.markdown(
        """
        <div class="page-header">
            <h1>🧠 JARVIS Memory</h1>
            <p>Save information you explicitly want JARVIS to remember for your account.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="glass-card">
            <h3>💾 Save a Memory</h3>
            <p>Example: My project presentation is on October 10.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    memory_text = st.text_area(
        "What should JARVIS remember?",
        placeholder="Example: My project presentation is on October 10.",
        key="memory_text_input"
    )

    if st.button("💾 Save Memory", use_container_width=True):
        if memory_text.strip():
            add_memory(st.session_state.user_email, memory_text.strip())
            st.success("🧠 Memory saved successfully!")
            st.rerun()
        else:
            st.warning("Please enter something for JARVIS to remember.")

    st.divider()

    memories = get_memories(st.session_state.user_email)
    st.markdown("### 📚 Saved Memories")

    if memories:
        for memory_id, text_value, created_at in memories:
            col1, col2 = st.columns([6, 1])
            with col1:
                st.markdown(
                    f"""
                    <div class="glass-card">
                        <h4>🧠 {text_value}</h4>
                        <p>Saved: {created_at}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with col2:
                if st.button("🗑️ Delete", key=f"delete_memory_{memory_id}", use_container_width=True):
                    delete_memory(memory_id, st.session_state.user_email)
                    st.rerun()

        if st.button("🗑️ Delete All Memories", use_container_width=True):
            delete_all_memories(st.session_state.user_email)
            st.success("All memories deleted.")
            st.rerun()
    else:
        st.info("No saved memories yet.")


# ============================================================
# SAFETY & SYSTEM PAGE
# ============================================================

elif page == "🛡️ Safety & System":

    st.markdown(
        """
        <div class="page-header">
            <h1>🛡️ Safety & System</h1>
            <p>
                JARVIS system status, permissions and supported
                capabilities.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            """
            <div class="glass-card">
                <h3>🟢 System Status</h3>
                <p>
                    <b>AI Core:</b> Online
                </p>
                <p>
                    <b>Voice:</b> Ready
                </p>
                <p>
                    <b>Code Generator:</b> Ready
                </p>
                <p>
                    <b>Code Debugger:</b> Ready
                </p>
                <p>
                    <b>Action Confirmation:</b> Active
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            """
            <div class="glass-card">
                <h3>🔐 Safety</h3>
                <p>
                    JARVIS only executes the computer actions
                    explicitly supported by the application.
                </p>
                <p>
                    Code generation and debugging do not
                    automatically execute generated code.
                </p>
                <p>
                    Opening websites or applications requires explicit
                    user confirmation before execution.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("### 🧩 Supported Code Languages")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.info("🐍 Python")

    with col2:
        st.info("☕ Java")

    with col3:
        st.info("🟨 JavaScript")

    with col4:
        st.info("🌐 HTML")

    with col5:
        st.info("🎨 CSS")


# ============================================================
# COMMAND HISTORY PAGE
# ============================================================

elif page == "📜 Command History":

    st.markdown(
        """
        <div class="page-header">
            <h1>📜 Command History</h1>
            <p>
                View commands previously processed by JARVIS.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.session_state.history:

        st.markdown(
            f"### Total Commands: {len(st.session_state.history)}"
        )

        for index, command in enumerate(
            reversed(st.session_state.history),
            start=1
        ):

            st.markdown(
                f"""
                <div class="glass-card">
                    <b>#{index}</b>
                    &nbsp;&nbsp;
                    🎤 {command}
                </div>
                """,
                unsafe_allow_html=True
            )

        if st.button(
            "🗑️ Clear Command History",
            use_container_width=True
        ):

            st.session_state.history = []
            st.rerun()

    else:

        st.info(
            "No commands have been executed yet."
        )


# ============================================================
# ACTION CONFIRMATION
# ============================================================

if st.session_state.pending_action is not None:

    pending = st.session_state.pending_action

    st.markdown(
        f"""
        <div class=\"glass-card\" style=\"border:2px solid #f0b429; background:linear-gradient(135deg,#fffaf0,#fff4d6);\">
            <h2>🛡️ JARVIS Action Confirmation</h2>
            <p style=\"font-size:16px;\"><b>JARVIS is ready to:</b> {pending['description']}</p>
            <p style=\"color:#64748b;\">Command: <b>{pending['command']}</b></p>
        </div>
        """,
        unsafe_allow_html=True
    )

    confirm_col, cancel_col = st.columns(2)

    with confirm_col:
        if st.button("✅ Confirm & Continue", use_container_width=True, type="primary", key="confirm_pending_action"):
            action = st.session_state.pending_action
            st.session_state.pending_action = None
            result = perform_action(action)
            st.success(f"🤖 JARVIS: {result}")
            jarvis_speak(result)

    with cancel_col:
        if st.button("❌ Cancel Action", use_container_width=True, key="cancel_pending_action"):
            action = st.session_state.pending_action
            st.session_state.pending_action = None
            st.info(f"🛡️ Action cancelled: {action['title']}")

    st.divider()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <br><br>
    <div style="
        text-align:center;
        color:#94a3b8;
        font-size:12px;
        padding:20px;
    ">
        🤖 JARVIS Infinity • AI Assistant System
        <br>
        Voice • Automation • Code Intelligence • Debugging
    </div>
    """,
    unsafe_allow_html=True
)