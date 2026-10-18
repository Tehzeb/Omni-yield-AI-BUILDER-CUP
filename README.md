# OmniYield — The Ultimate Manufacturing Solution

OmniYield is a multi-modal AI industrial diagnostic app. It fuses a defective part's image, live machine telemetry (temperature, vibration, pressure), and a machine manual excerpt into a single diagnosis: root cause + a specific repair action.

## Architecture

- **backend/** — FastAPI service. `POST /analyze` validates an image and telemetry, flags out-of-range sensor readings, and sends the image + context to Gemini (`gemini-3.8-flash` by default via the Interactions API) for a validated `{root_cause, repair_action, confidence}` diagnosis.
- **frontend/** — Vite-powered React dashboard with a dark neon aesthetic (black background, cyan→purple gradient borders, glassmorphism). Split-screen: left side for image + telemetry input, right side displays the fetched diagnosis.

## Running locally

Prerequisites: Python 3.12, Node.js 20.19 or newer, npm, and a Gemini API key.

### Backend

```powershell
cd C:\AIBuilderCupSubmission\backend
if (-not (Test-Path .\venv\Scripts\python.exe)) { py -3.12 -m venv venv }
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Before starting the backend, create `backend/.env` from the template and edit it to add a newly rotated Gemini API key:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
notepad .env
```

Then start the backend in that terminal:

```powershell
uvicorn main:app --reload --port 8080
```

Do not commit or share the `.env` file.

Keep this terminal open. In a **second PowerShell terminal**, start the frontend:

```powershell
cd C:\AIBuilderCupSubmission\frontend
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
npm install
npm start
```

Open `http://localhost:3000`. The backend health check is at `http://localhost:8080/`.
To run the backend checks, open a third terminal:

```powershell
cd C:\AIBuilderCupSubmission\backend
.\venv\Scripts\Activate.ps1
python -m unittest discover -s tests -v
```

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal and activate again. Alternatively, use `.\venv\Scripts\python.exe -m uvicorn main:app --reload --port 8080` without activating.

## Deployment

- **Backend → Google Cloud Run**: `backend/Dockerfile` builds on `python:3.12-slim`, exposes port 8080. Store `GEMINI_API_KEY` in Secret Manager and set `FRONTEND_ORIGINS` to the deployed Firebase URL.
  ```bash
  gcloud run deploy omniyield-backend --source backend --region <region> --set-env-vars FRONTEND_ORIGINS=https://<your-project>.web.app --set-secrets GEMINI_API_KEY=gemini-api-key:latest
  ```
- **Frontend → Firebase Hosting**: `frontend/firebase.json` serves the Vite `dist/` directory.
  ```bash
  cd frontend
  npm run build
  firebase deploy
  ```

## Environment variables

| Location | Variable | Purpose |
|---|---|---|
| backend | `GEMINI_API_KEY` | Google Gemini API key for the vision+text diagnostic agent (keep it private) |
| backend | `GEMINI_MODEL` | Gemini model name; defaults to `gemini-3.8-flash` |
| backend | `FRONTEND_ORIGINS` | Comma-separated allowed frontend origins; defaults to local development origins |
| frontend | `VITE_API_URL` | URL of the deployed/local backend |
