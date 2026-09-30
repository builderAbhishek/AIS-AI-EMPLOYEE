# AIS AI EMPLOYEE - V1

A complete, local-first business operating system designed for Alag Innovative Solutions (AIS) to manage leads, clients, projects, tasks, knowledge, and daily priorities with an integrated AI Employee.

## Features
- **Dashboard**: Business overview, pipeline tracking, and daily priorities.
- **Leads CRM**: Complete CRUD, AI qualification and pitch generation.
- **Clients & Projects**: Track active clients and project progress.
- **Tasks**: Priority management and deadline tracking.
- **AI Employee**: Integrated AI assistant that can analyze priorities, generate pitches, and break down tasks.
- **Local AI Integration**: Connects dynamically to local Ollama API with actual database context injection.
- **100% Private**: AIS business data is never sent to the cloud.

## Tech Stack
- **Backend**: Python 3.11+, FastAPI, SQLite, SQLAlchemy, Pydantic, Requests
- **Frontend**: HTML5, CSS3, Vanilla JS
- **AI**: Abstracted AIProvider (Local Ollama)

## Installation & Setup

1. **Install Python 3.11+** if not already installed.
2. **Install Ollama** and pull models (e.g. `qwen3:4b` or `qwen2.5:0.5b`).
3. **Open Terminal** in the project directory.
4. **Create Virtual Environment**:
   ```bat
   python -m venv venv
   call venv\Scripts\activate
   ```
5. **Install Requirements**:
   ```bat
   pip install -r requirements.txt
   ```
6. **Configure Environment Variables**:
   Copy `.env.example` to `.env`.
   ```bat
   copy .env.example .env
   ```
7. **Run the Application**:
   Run the startup script:
   ```bat
   run.bat
   ```
8. **Open Browser**: Navigate to `http://localhost:8000/`

## AI Configuration (Ollama Setup)

The application uses `AI_PROVIDER=ollama`.

1. Start your local Ollama server (defaults to `http://127.0.0.1:11434`).
2. Open the application in your browser and go to **Settings**.
3. Select your installed **Ollama Model** (e.g., `qwen3:4b`).
4. Click **Save AI Settings**.
5. Click **Test Connection** to verify Ollama is responding.

## Modifying AIS AI Rules
Edit the `knowledge/company/ais_brain.md` file. The backend automatically injects this context (along with live leads, tasks, projects) directly into Ollama's system prompt before generating responses.
