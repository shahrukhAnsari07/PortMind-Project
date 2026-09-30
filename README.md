# PortMind AI — Working Hackathon Build

## Start backend
```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

## Start frontend
```powershell
cd frontend
npm install
npm run dev
```

The frontend is organized into separate pages/components with a single SimulationContext. Vessel management, resource inputs, disruption scenarios, playback controls, scheduling, analytics, Monte Carlo, AI Copilot, health, and CSV reporting all use the same simulation state and API layer.
