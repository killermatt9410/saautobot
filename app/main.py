from fastapi import FastAPI, Request
from datetime import datetime

app = FastAPI()
LEADS = []

@app.get("/health")
def health():
    return {"status": "ok", "leads": len(LEADS)}

@app.get("/leads")
def list_leads():
    return {"count": len(LEADS), "items": LEADS}

@app.post("/new-lead")
async def new_lead(req: Request):
    data = await req.json()
    item = {
        "received_at": datetime.utcnow().isoformat() + "Z",
        "name": data.get("name"),
        "description": data.get("description"),
        "url": data.get("url"),
        "list": data.get("list"),
        "board": data.get("board"),
        "raw": data,
    }
    LEADS.append(item)
    print("=== New Lead ===", item)
    return {"ok": True}
