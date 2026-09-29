# AIS AI EMPLOYEE - V1

A complete, local-first business operating system designed for Alag Innovative Solutions (AIS) to manage leads, clients, projects, tasks, knowledge, and daily priorities with an integrated AI Employee.

## Features
- **Dashboard**: Business overview, pipeline tracking, and daily priorities.
- **Leads CRM**: Complete CRUD, AI qualification and pitch generation.
- **Clients & Projects**: Track active clients and project progress.
- **Tasks**: Priority management and deadline tracking.
- **AI Employee**: Integrated AI assistant that can analyze priorities, generate pitches, and break down tasks.
- **Demo Mode**: Fully functional AI mock mode when API keys are not provided.

## Tech Stack
- **Backend**: Python 3.11+, FastAPI, SQLite, SQLAlchemy, Pydantic
- **Frontend**: HTML5, CSS3, Vanilla JS
- **AI**: Abstracted AIProvider (Default: OpenAI compatible or Demo mode)

## Installation & Setup

1. **Install Python 3.11+** if not already installed.
2. **Open Terminal** in the project directory.
3. **Create Virtual Environment**:
   ```bat
   python -m venv venv
   call venv\Scripts\activate
   ```
4. **Install Requirements**:
   ```bat
   pip install -r requirements.txt
   ```
5. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and fill in your API key if you have one.
   ```bat
   copy .env.example .env
   ```
6. **Run the Application**:
   Run the startup script:
   ```bat
   run.bat
   ```
   Or run manually:
   ```bat
   uvicorn backend.app.main:app --reload --port 8000
   ```
7. **Open Browser**: Navigate to `http://localhost:8000/`

## First Run Experience
On the first run, the SQLite database is automatically initialized, tables are created, and realistic local business demo data (Leads, Clients, Tasks, Projects) is seeded into the database.

## AI Configuration (Demo Mode vs API Mode)
By default, the application runs in `AI_PROVIDER=demo` mode (set in `.env`). This provides realistic, deterministic AI responses so you can test the entire workflow without spending money on API calls.

To use real AI:
1. Open `.env`
2. Set `AI_PROVIDER=api`
3. Provide an `API_KEY` (e.g., from OpenAI).
4. Restart the server.
