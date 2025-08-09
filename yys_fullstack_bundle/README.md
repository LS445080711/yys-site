YYS Fullstack Starter (Frontend + Backend + Docker)
--------------------------------------------------
Components:
- frontend/: Next.js app (fetches API at http://localhost:8000)
- backend/: FastAPI app serving data from SQLite (data/yys_demo.db)
- docker-compose.yml to run both services

Quick start (Docker, recommended):
1. cd to the bundle root
2. docker-compose build
3. docker-compose up
4. Open frontend at http://localhost:3000 and backend at http://localhost:8000/docs

Local dev without Docker:
- Backend:
  cd backend
  python -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  uvicorn main:app --reload --host 0.0.0.0 --port 8000

- Frontend:
  cd frontend
  npm install
  npm run dev

Notes:
- The frontend fetches the backend at http://localhost:8000 by default.
- The SQLite DB is included at backend/data/yys_demo.db