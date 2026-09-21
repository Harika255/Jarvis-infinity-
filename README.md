# 🤖 JARVIS Infinity

### AI-Powered Situation Awareness & Next-Action Engine

> **Understand the situation. Decide what matters. Suggest what to do next.**

JARVIS Infinity is a multimodal AI assistant designed to combine **AI reasoning, voice interaction, computer vision, automation, safety controls, and situation awareness** into one intelligent system.

Instead of simply responding to commands, JARVIS is designed to understand the user's current situation and determine a useful **next action**.

---

## ✨ Key Features

### 🧠 AI Brain

* Intent classification using machine learning
* TF-IDF based text understanding
* Logistic Regression intent prediction
* Confidence-based decision making
* Situation analysis

### 🎯 What Should I Do Next?

JARVIS includes a **Next Best Action Engine** that analyzes the current situation and recommends an appropriate next step.

Example:

```text
Situation:
Project review is tomorrow.

JARVIS:
Priority: HIGH
Risk: LOW

Recommended Action:
Complete the Voice Control module.
```

---

### 🎙️ Voice Control

JARVIS can interact with the user through voice.

Features include:

* Microphone input
* Speech recognition
* Voice commands
* Command interpretation
* Voice response integration

---

### 👁️ Computer Vision

JARVIS includes a vision layer for understanding the user's environment.

Capabilities include:

* Camera integration
* Face detection
* Screen capture
* OCR support
* Visual analysis

---

### 💻 Computer Automation

JARVIS can interact with computer applications through its computer-control layer.

Examples include:

* Opening applications
* Executing approved actions
* Interacting with the desktop
* Application-level automation

---

### 🔐 Safety & Permission Layer

JARVIS is designed with safety controls before executing potentially sensitive computer actions.

The system can:

```text
User Request
     ↓
Intent Detection
     ↓
Situation Analysis
     ↓
Permission Check
     ↓
Action Planning
     ↓
Execution
     ↓
Verification
```

---

### 📋 Task & Goal Management

JARVIS contains multiple modules for:

* Task management
* Goal planning
* Action planning
* Situation analysis
* Action verification
* Next-action recommendations

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │       USER          │
                    └──────────┬──────────┘
                               │
                    Voice / Text / Vision
                               │
                               ▼
                    ┌─────────────────────┐
                    │   JARVIS INTERFACE  │
                    │      Dashboard      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      AI BRAIN       │
                    │ Intent Recognition  │
                    │ Situation Analysis  │
                    └──────────┬──────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
        ┌────────────┐ ┌────────────┐ ┌────────────┐
        │   Voice    │ │   Vision   │ │   Memory   │
        │   Engine   │ │   Engine   │ │   System   │
        └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                    ┌─────────────────────┐
                    │  SITUATION ENGINE   │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │  NEXT ACTION ENGINE │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │   SAFETY ENGINE     │
                    │ Permission / Checks │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ ACTION EXECUTION    │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │     VERIFIER        │
                    └─────────────────────┘
```

---

## 🛠️ Technologies Used

| Technology          | Purpose                  |
| ------------------- | ------------------------ |
| Python              | Core development         |
| PySide6             | Desktop GUI              |
| Scikit-learn        | Machine learning         |
| TF-IDF              | Text feature extraction  |
| Logistic Regression | Intent classification    |
| OpenCV              | Computer vision          |
| OCR / Tesseract     | Text recognition         |
| NumPy               | Data processing          |
| CSV / JSON          | Dataset and task storage |
| SQLite              | Local memory storage     |
| Git & GitHub        | Version control          |

---

## 📂 Project Structure

```text
JARVIS-INFINITY/
│
├── agent/
│   ├── dashboard_bridge.py
│   ├── executor.py
│   ├── goal_engine.py
│   ├── next_action_engine.py
│   ├── planner.py
│   ├── safety_engine.py
│   ├── situation_engine.py
│   ├── tool_registry.py
│   ├── universal_agent.py
│   └── verifier.py
│
├── assets/
│   ├── face_detection_yunet_2023mar.onnx
│   └── jarvis_background.png
│
├── dataset/
│   └── jarvis_intents.csv
│
├── ui/
│   ├── dashboard.py
│   ├── next_best_action.py
│   ├── screen_capture.py
│   └── screen_understanding.py
│
├── ai_brain.py
├── action_planner.py
├── coding_agent.py
├── computer_control.py
├── llm_manager.py
├── main.py
├── memory_store.py
├── next_best_action.py
├── real_world_agent.py
├── safety_engine.py
├── task_manager.py
├── verifier.py
├── vision_engine.py
├── voice_control.py
├── voice_response.py
│
├── dataset/
├── requirements.txt
├── run_jarvis.bat
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Harika255/Jarvis-infinity-.git
cd Jarvis-infinity-
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the environment

### Windows

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Copy:

```text
.env.example
```

to:

```text
.env
```

Then add any required configuration values.

### 6. Run JARVIS

```bash
python main.py
```

---

## 🧪 Example AI Interaction

### User

```text
I have a project review tomorrow.
```

### JARVIS

```text
Intent: PROJECT_REVIEW
Deadline: Tomorrow
Risk: LOW

Recommended Plan:
Prepare project
Review implementation
Complete pending modules
Practice presentation
```

Another example:

```text
User:
What should I do next?

JARVIS:
Recommendation:
Complete the Voice Control module.

Reason:
Voice interaction is a major multimodal component
and is currently incomplete.
```

---

## 🧠 Core Intelligence Pipeline

JARVIS follows a modular reasoning pipeline:

```text
Input
  ↓
Intent Recognition
  ↓
Context Extraction
  ↓
Situation Awareness
  ↓
Risk Assessment
  ↓
Goal Analysis
  ↓
Next Best Action
  ↓
Permission Check
  ↓
Action Execution
  ↓
Verification
```

This architecture allows individual components to be developed and tested independently.

---

## 🔒 Safety Philosophy

JARVIS is designed to avoid blindly executing computer actions.

Sensitive operations can pass through:

```text
Request
   ↓
Permission Required?
   ↓
Safety Check
   ↓
Approved?
  ↙     ↘
YES      NO
 ↓        ↓
Execute   Reject
 ↓
Verify
```

---

## 📊 Dataset

The project contains an intent dataset used for machine-learning based classification.

Current intent categories include examples related to:

* Project review
* Opening applications
* Tasks
* Planning
* General interaction
* Next-action recommendations

The dataset can be expanded as JARVIS gains additional capabilities.

---

## 🔮 Future Enhancements

Planned improvements include:

* [ ] More advanced conversational AI
* [ ] Improved speech recognition
* [ ] Wake-word activation
* [ ] Expanded computer vision
* [ ] Real-time environment awareness
* [ ] Better long-term memory
* [ ] More intelligent task prioritization
* [ ] Enhanced autonomous planning
* [ ] Improved action verification
* [ ] Expanded intent dataset
* [ ] More computer automation tools
* [ ] Cloud-based AI integration

---

## 🎓 Project Purpose

JARVIS Infinity was developed as an academic and experimental AI project exploring the combination of:

**Artificial Intelligence + Machine Learning + Computer Vision + Voice Interaction + Automation + Situation Awareness**

The project focuses on moving from a traditional command-based assistant toward a system capable of understanding context and recommending meaningful next actions.

---

## 👩‍💻 Author

### Harika Karankot

**B.Tech — Computer Science & Engineering**

Interested in:

* Artificial Intelligence
* Machine Learning
* Software Development
* Automation
* Emerging Technologies

---

## ⭐ Support the Project

If you find the project interesting:

⭐ Star the repository
🍴 Fork the project
💡 Explore the architecture
🐛 Report issues
🚀 Build your own improvements

---

## 📜 License

This project is intended for educational and experimental purposes.
