from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import json
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "yys_demo.db")

app = FastAPI(title="YYS Backend Demo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Shikigami(BaseModel):
    id: int
    name: str
    slug: str
    rarity: int
    role: str
    skills: dict
    base_stats: dict
    recommended_souls: list
    avatar_url: str

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/api/shikigami", response_model=List[Shikigami])
def list_shikigami():
    conn = get_conn()
    cur = conn.execute("SELECT * FROM shikigami ORDER BY id LIMIT 500")
    rows = cur.fetchall()
    result = []
    for r in rows:
        try:
            skills = json.loads(r["skills"])
        except:
            skills = {}
        try:
            base_stats = json.loads(r["base_stats"])
        except:
            base_stats = {}
        try:
            rec = json.loads(r["recommended_souls"])
        except:
            rec = []
        result.append({
            "id": r["id"],
            "name": r["name"],
            "slug": r["slug"],
            "rarity": r["rarity"],
            "role": r["role"],
            "skills": skills,
            "base_stats": base_stats,
            "recommended_souls": rec,
            "avatar_url": r["avatar_url"]
        })
    conn.close()
    return result

@app.get("/api/shikigami/{slug}", response_model=Shikigami)
def get_shikigami(slug: str):
    conn = get_conn()
    cur = conn.execute("SELECT * FROM shikigami WHERE slug = ?", (slug,))
    r = cur.fetchone()
    conn.close()
    if not r:
        raise HTTPException(status_code=404, detail="not found")
    try:
        skills = json.loads(r["skills"])
    except:
        skills = {}
    try:
        base_stats = json.loads(r["base_stats"])
    except:
        base_stats = {}
    try:
        rec = json.loads(r["recommended_souls"])
    except:
        rec = []
    return {
        "id": r["id"],
        "name": r["name"],
        "slug": r["slug"],
        "rarity": r["rarity"],
        "role": r["role"],
        "skills": skills,
        "base_stats": base_stats,
        "recommended_souls": rec,
        "avatar_url": r["avatar_url"]
    }