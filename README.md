## UNMAPPED

Skills infrastructure layer for the World Bank Youth Summit Hackathon 2026.

### Quickstart

#### Backend (FastAPI)

1. Create `unmapped/backend/.env`:

```
ANTHROPIC_API_KEY=your_key_here
# Optional override (your account supports Claude 4.x, e.g.):
# ANTHROPIC_MODEL=claude-sonnet-4-6
```

2. Install and run:

```bash
cd unmapped/backend
python -m venv .venv
source .venv/bin/activate  # (Windows PowerShell: .venv\Scripts\Activate.ps1)
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

#### Frontend (Vite + React + Tailwind)

```bash
cd unmapped/frontend
npm install
npm run dev
```

Frontend expects the backend at `http://localhost:8000`.

