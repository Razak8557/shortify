from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3, string, random
from datetime import datetime

app = FastAPI(title="Shortify - URL Shortener by Razak")

conn = sqlite3.connect("urls.db", check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS urls (short_id TEXT PRIMARY KEY, long_url TEXT, clicks INTEGER, created_at TEXT)")
conn.commit()

class URLRequest(BaseModel):
    long_url: str

def gen_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

@app.post("/shorten")
def shorten(req: URLRequest):
    short_id = gen_id()
    conn.execute("INSERT INTO urls VALUES (?,?,?,?)", (short_id, req.long_url, 0, str(datetime.now())))
    conn.commit()
    return {"short_url": f"https://shortify/{short_id}", "original": req.long_url}

@app.get("/{short_id}")
def redirect(short_id: str):
    row = conn.execute("SELECT long_url, clicks FROM urls WHERE short_id=?", (short_id,)).fetchone()
    if not row:
        raise HTTPException(404, "URL not found")
    conn.execute("UPDATE urls SET clicks = clicks + 1 WHERE short_id=?", (short_id,))
    conn.commit()
    return {"redirect_to": row[0], "total_clicks": row[1]+1}

@app.get("/stats/{short_id}")
def stats(short_id: str):
    row = conn.execute("SELECT * FROM urls WHERE short_id=?", (short_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Not found")
    return {"short_code": row[0], "long_url": row[1], "clicks": row[2], "created_at": row[3]}
