JARVIS Infinity 2026 — General AI Agent Upgrade
This version changes JARVIS from a command-matching assistant into a general-purpose AI assistant.
What changed
Natural-language questions are handled by a general LLM instead of a fixed command list.
The model can answer general questions, explain concepts, write/debug code, and reason about goals.
JARVIS can use safe local tools for memory, tasks, project status, and allowlisted applications.
Current information can be researched with the model's web-search tool when supported.
Medium-risk application actions require explicit approval in the desktop UI.
Voice input and persistent text-to-speech remain part of the desktop experience.
The existing TF-IDF + Logistic Regression AI brain remains available as a local fallback and evaluation component.
Architecture
```text
User (text / voice)
        ↓
General AI Brain (LLM)
        ↓
Understand request
        ↓
Answer naturally OR select a tool
        ↓
Safety layer
        ↓
Memory / Tasks / Web / Computer / Project tools
        ↓
Verification
        ↓
Natural response + voice
```
Setup
1. Open the project
```powershell
cd C:\Users\Harika\OneDrive\Desktop\jarvis-infinity
```
2. Activate the virtual environment
```powershell
.\venv\Scripts\Activate.ps1
```
3. Install the updated dependencies
```powershell
pip install -r requirements.txt
```
4. Configure the AI key
The key must be stored as an environment variable. Never put a real API key inside Python source code or Git.
For the current PowerShell session:
```powershell
$env:OPENAI_API_KEY="YOUR_API_KEY_HERE"
$env:JARVIS_MODEL="gpt-5.6-luna"
```
Then run:
```powershell
python main.py
```
5. Optional persistent Windows configuration
If you want the key to remain available for future terminals, configure it through Windows environment variables instead of putting it in the project files.
Test
```powershell
python test_general_ai.py
```
Example natural conversations
These are examples, not commands that are hard-coded:
`Explain quantum computing like I'm a beginner.`
`Help me prepare for my project review tomorrow.`
`Write a Python program to analyze student marks.`
`What is the difference between TCP and UDP?`
`Remember that I need to finish my presentation tonight.`
`What do you remember about my project?`
`Open VS Code.`
`What should I work on next?`
`Search the web for the latest developments in agentic AI.`
The LLM decides whether a tool is needed based on the meaning of the request.
Important safety design
JARVIS does not give the model unrestricted computer access. Application launching is an explicit tool and requires user approval. Destructive actions, credential changes, financial actions, and other high-impact operations are intentionally not exposed as tools.
Existing project files
Keep your existing:
`dataset/jarvis_intents.csv`
`assets/jarvis_background.png`
They are project assets and are not replaced by this upgrade.
