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

@app.get("/new-lead")
@app.post("/new-lead")
async def new_lead(data: dict = None):
    return {"status": "lead received", "data": data}
