# Project Aegis — Native AI Operating System Controller for Windows

Project Aegis is a privacy-first, local AI-powered controller for Windows that allows users to perform selected system operations using natural-language commands.

The system uses a local LLM through Ollama to understand user intent and convert it into structured tool calls. These calls pass through a security and validation layer before controlled Python functions interact with Windows.

## Features

### Core Features
- Smart process monitoring
- Safe process termination with protected-process checks
- CPU, RAM, disk and battery monitoring
- Application Launcher
- Volume and mute control
- Screen brightness control
- Workstation control
- AI-powered resource optimization
- Semantic file search

### Planned Additional Features
- Floating Ctrl+Space command overlay
- Multi-step routine automation
- Voice input and spoken responses
- AI Command History
- Scheduled Routines

## Architecture

```text
User
  ↓
Natural Language Input
  ↓
Python Controller
  ↓
Local LLM
  ↓
Tool Registry
  ↓
Security & Validation
  ↓
Windows OS Control
  ↓
Windows
  ↓
Result
```

The LLM does not receive unrestricted access to Windows. It can invoke only predefined tools, which are validated before execution.

## Project Structure

```text
Project-Aegis/
│
├── main.py
├── config.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── controller/
├── ai_core/
├── os_control/
├── security/
├── search/
├── ui/
├── data/
└── tests/
```

### Main Modules

| Module | Responsibility |
|---|---|
| `ai_core/` | Local LLM, prompts, intent understanding and Tool Registry |
| `os_control/` | Windows processes, resources, applications and hardware |
| `security/` | Validation, risk checks, protected processes and confirmation |
| `search/` | Semantic file indexing and search |
| `ui/` | User interface and command/result display |
| `controller/` | Coordinates the complete execution pipeline |
| `tests/` | Unit and integration tests |

## Technology Stack

- **Python 3.10+**
- **Ollama** — local LLM inference
- **psutil** — process and system-resource monitoring
- **pycaw** — Windows audio control
- **screen-brightness-control** — display brightness control
- **CustomTkinter** — desktop UI
- **ChromaDB** — vector storage
- **Sentence Transformers** — semantic embeddings

## Installation

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd Project-Aegis
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Ollama

Install Ollama and download the local model selected by the team.

Example:

```bash
ollama pull llama3.1:8b
```

## Running the Project

Once the core modules are integrated:

```bash
python main.py
```

## Security

Project Aegis follows a controlled execution architecture:

```text
LLM
 ↓
Tool Registry
 ↓
Security & Validation
 ↓
Controlled Windows Function
 ↓
Windows
```

Key principles:

- No unrestricted shell execution by the LLM
- Protected Windows processes
- Argument validation
- Risk-based checks
- User confirmation for sensitive operations
- Local-first AI processing