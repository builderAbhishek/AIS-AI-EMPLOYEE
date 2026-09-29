# AIS AI EMPLOYEE - V1

A complete, local-first business operating system designed for Alag Innovative Solutions (AIS) to manage leads, clients, projects, tasks, knowledge, and daily priorities with an integrated AI Employee.

## Features
- **Dashboard**: Business overview, pipeline tracking, and daily priorities.
- **Leads CRM**: Complete CRUD, AI qualification and pitch generation.
- **Clients & Projects**: Track active clients and project progress.
- **Tasks**: Priority management and deadline tracking.
- **AI Employee**: Integrated AI assistant that can analyze priorities, generate pitches, and break down tasks.
- **Real Gemini Integration**: Connects dynamically to Google's Gemini REST API with actual database context injection.
- **Demo Mode**: Fully functional AI mock mode for offline testing.

## Tech Stack
- **Backend**: Python 3.11+, FastAPI, SQLite, SQLAlchemy, Pydantic, Requests
- **Frontend**: HTML5, CSS3, Vanilla JS
- **AI**: Abstracted AIProvider (Gemini REST API / Demo Mode)

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
   Copy `.env.example` to `.env`. (The `.env` file is excluded from Git for security).
   ```bat
   copy .env.example .env
   ```
6. **Run the Application**:
   Run the startup script:
   ```bat
   run.bat
   ```
7. **Open Browser**: Navigate to `http://localhost:8000/`

## AI Configuration (Demo Mode vs Gemini Mode)

By default, the application runs in `AI_PROVIDER=demo` mode. 

To use real Google Gemini AI:
1. Obtain an API key from Google AI Studio.
2. Open the application in your browser and go to **Settings**.
3. Change **AI Provider** to `Gemini API`.
4. Paste your **Gemini API Key**.
5. Click **Save Configuration**.
6. Click **Test Connection** to verify the key works. 

*Security Warning:* The Gemini API key is stored purely on the backend database/environment and is never transmitted to the browser's frontend JavaScript.

## Modifying AIS AI Rules
Edit the `knowledge/company/ais_brain.md` file. The backend automatically injects this context (along with live leads, tasks, projects) directly into Gemini's system prompt before generating responses.
