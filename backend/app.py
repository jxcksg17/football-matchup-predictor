import os
import sys

# Ensure backend directory is in Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from model import ApexScoutEngine

app = FastAPI(title="MatchPulse Predictive API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

base_dir = os.path.dirname(os.path.abspath(__file__))
intl_path = os.path.join(base_dir, "../data/results.csv")
club_path = os.path.join(base_dir, "../data/club_results.csv")

engines = {}

if os.path.exists(intl_path):
    engines["international"] = ApexScoutEngine(intl_path)
    print("Loaded International Dataset.")

if os.path.exists(club_path):
    engines["club"] = ApexScoutEngine(club_path)
    print("Loaded Club Dataset.")

@app.get("/api/teams")
def get_teams(scope: str = Query("international", enum=["club", "international"])):
    if scope not in engines:
        fallback = next(iter(engines.keys()), None)
        if not fallback:
            raise HTTPException(status_code=500, detail="No dataset files found in data/ folder.")
        scope = fallback
    return {"scope": scope, "teams": engines[scope].teams}

@app.get("/api/predict")
def predict_match(home: str, away: str, scope: str = Query("international", enum=["club", "international"])):
    if scope not in engines:
        scope = next(iter(engines.keys()), None)
        if not scope:
            raise HTTPException(status_code=500, detail="No dataset loaded.")
    try:
        return engines[scope].predict(home, away)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
