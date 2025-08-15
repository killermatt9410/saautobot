from fastapi import FastAPI, Request
from datetime import datetime
import json
from urllib.parse import parse_qs

app = FastAPI()
LEADS = []

def normalize(s):
    return s.strip() if isinstance(s, str) else s

@app.post("/new-lead")
async def new_lead(request: Request):
    raw = await request.body()
    data = None

    # 1) Try direct JSON
    try:
        data = json.loads(raw.decode("utf-8"))
    except Exception:
        pass

    # 2) Try unescaping \"...\" JSON Trello sometimes produces
    if data is None:
        try:
            txt = raw.decode("utf-8")
            txt2 = txt.replace('\\"', '"')
            data = json.loads(txt2)
        except Exception:
            pass

    # 3) Try form / querystring (name=a&description=b...)
    if data is None:
        try:
            form = await request.form()
            if form:
                data = {k: normalize(v) for k, v in form.items()}
        except Exception:
            pass
    if data is None:
        try:
            qs = raw.decode("utf-8")
            parsed = {k: v[0] for k, v in parse_qs(qs).items()}
            if parsed:
                data = parsed
        except Exception:
            pass

    if data is None:
        return {"ok": False, "reason": "Could not parse body", "raw": raw.decode("utf-8")[:500]}

    item = {
        "received_at": datetime.utcnow().isoformat() + "Z",
        "name": normalize(data.get("name")),
        "description": normalize(data.get("description")),
        "url": normalize(data.get("url")),
        "list": normalize(data.get("list")),
        "board": normalize(data.get("board")),
        "raw": data,
    }
    LEADS.append(item)
    print("=== New Lead ===", item)
    return {"ok": True, "stored": item}

@app.get("/leads")
def list_leads():
    return {"count": len(LEADS), "items": LEADS}

@app.get("/health")
def health():
    return {"status": "ok", "leads": len(LEADS)}
