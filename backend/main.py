
from fastapi import FastAPI, HTTPException, Depends, Body
from pydantic import BaseModel
import sqlite3, json, os, csv, hashlib, time
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

# Config
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "yys_demo.db")
JWT_SECRET = os.environ.get("YYS_JWT_SECRET", "change_this_secret")
API_PAGE_DEFAULT = 1
API_PAGE_SIZE_DEFAULT = 20

app = FastAPI(title="YYS Backend Demo (Enhanced)")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

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

class UserIn(BaseModel):
    username: str
    password: str

class TeamIn(BaseModel):
    title: str
    author: str
    shikigami_order: list
    strategy: Optional[str] = None

security = HTTPBearer()

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.on_event("startup")
def ensure_tables():
    conn = get_conn()
    cur = conn.cursor()
    # users table
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password_hash TEXT
    )""")
    # teams table
    cur.execute("""CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, author TEXT, shikigami_order TEXT, strategy TEXT, created_at INTEGER
    )""")
    conn.commit()
    conn.close()

# Utility: simple password hashing (not production-grade)
def hash_pw(pw):
    return hashlib.sha256(pw.encode('utf-8')).hexdigest()

# Auth endpoints
@app.post("/api/auth/register")
def register(u: UserIn):
    conn = get_conn()
    try:
        conn.execute("INSERT INTO users (username,password_hash) VALUES (?,?)", (u.username, hash_pw(u.password)))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="username_exists")
    conn.close()
    return {"status":"ok"}

@app.post("/api/auth/login")
def login(u: UserIn):
    conn = get_conn()
    cur = conn.execute("SELECT * FROM users WHERE username = ?", (u.username,))
    row = cur.fetchone()
    conn.close()
    if not row or row["password_hash"] != hash_pw(u.password):
        raise HTTPException(status_code=401, detail="invalid_credentials")
    payload = {"sub": row["id"], "username": row["username"], "iat": int(time.time())}
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return {"access_token": token}

def require_auth(creds: HTTPAuthorizationCredentials = Depends(security)):
    token = creds.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except Exception as e:
        raise HTTPException(status_code=401, detail="invalid_token")
    return payload

# Teams endpoint (submit a team) - requires auth
@app.post("/api/teams")
def post_team(team: TeamIn, user=Depends(require_auth)):
    conn = get_conn()
    conn.execute("INSERT INTO teams (title,author,shikigami_order,strategy,created_at) VALUES (?,?,?,?,?)",
                 (team.title, team.author, json.dumps(team.shikigami_order, ensure_ascii=False), team.strategy or "", int(time.time())))
    conn.commit()
    conn.close()
    return {"status":"ok"}

# Enhanced shikigami list with pagination & filters
@app.get("/api/shikigami", response_model=List[Shikigami])
def list_shikigami(role: Optional[str] = None, rarity: Optional[int] = None, q: Optional[str] = None, page: int = API_PAGE_DEFAULT, page_size: int = API_PAGE_SIZE_DEFAULT):
    conn = get_conn()
    sql = "SELECT * FROM shikigami WHERE 1=1"
    params = []
    if role:
        sql += " AND role = ?"
        params.append(role)
    if rarity:
        sql += " AND rarity = ?"
        params.append(rarity)
    if q:
        sql += " AND (name LIKE ? OR slug LIKE ? OR skills LIKE ?)"
        likeq = f"%{q}%"
        params.extend([likeq, likeq, likeq])
    sql += " ORDER BY id LIMIT ? OFFSET ?"
    params.extend([page_size, (page-1)*page_size])
    cur = conn.execute(sql, params)
    rows = cur.fetchall()
    result = []
    for r in rows:
        try: skills = json.loads(r["skills"])
        except: skills = {}
        try: base_stats = json.loads(r["base_stats"])
        except: base_stats = {}
        try: rec = json.loads(r["recommended_souls"])
        except: rec = []
        result.append({"id": r["id"], "name": r["name"], "slug": r["slug"], "rarity": r["rarity"], "role": r["role"], "skills": skills, "base_stats": base_stats, "recommended_souls": rec, "avatar_url": r["avatar_url"]})
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
    try: skills = json.loads(r["skills"])
    except: skills = {}
    try: base_stats = json.loads(r["base_stats"])
    except: base_stats = {}
    try: rec = json.loads(r["recommended_souls"])
    except: rec = []
    return {"id": r["id"], "name": r["name"], "slug": r["slug"], "rarity": r["rarity"], "role": r["role"], "skills": skills, "base_stats": base_stats, "recommended_souls": rec, "avatar_url": r["avatar_url"]}

# CSV import utility endpoint (for demo) - load CSV from content_templates if present
@app.post("/api/admin/import_csv")
def import_csv():
    # possible locations
    cand = [
        os.path.join(os.path.dirname(__file__), "..", "content_templates", "shikigami_template_50.csv"),
        os.path.join(os.path.dirname(__file__), "data", "shikigami_template_50.csv")
    ]
    csvpath = None
    for c in cand:
        if os.path.exists(c):
            csvpath = c
            break
    if not csvpath:
        raise HTTPException(status_code=404, detail="csv_not_found")
    conn = get_conn()
    cur = conn.cursor()
    with open(csvpath, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                cur.execute("INSERT OR REPLACE INTO shikigami (id,name,slug,rarity,role,skills,base_stats,recommended_souls,avatar_url) VALUES (?,?,?,?,?,?,?,?,?)",
                            (int(row['id']), row['name'], row['slug'], int(row['rarity']), row['role'], row['skills_json'], row['base_stats_json'], row['recommended_souls_json'], row.get('avatar_url','/images/shiki/placeholder.png')))
            except Exception as e:
                print("err", e, row.get('id'))
    conn.commit()
    conn.close()
    return {"status":"imported"}
