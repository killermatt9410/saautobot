from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import re
from typing import Dict, Any, List

app = FastAPI(title="SA Automotors Bot", version="0.0.2")

LEADS: List[Dict[str, Any]] = []

@app.get("/health")
def health():
    return {"status": "ok", "leads": len(LEADS)}

def normalize_phone_za(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("+27"):
        return raw
    digits = re.sub(r"\D", "", raw)
    if digits.startswith("27"):
        return f"+{digits}"
    if digits.startswith("0"):
        return f"+27{digits[1:]}"
    return f"+{digits}" if digits else raw

def parse_card_desc(desc: str) -> Dict[str, str]:
    fields = {"client_name": "", "phone": "", "car": "", "notes": ""}
    if not desc:
        return fields
    for line in desc.splitlines():
        m = re.match(r"\s*([A-Za-z ]+)\s*:\s*(.+)\s*$", line)
        if not m:
            continue
        key = m.group(1).strip().lower()
        val = m.group(2).strip()
        if key in ("client name", "name", "seller"):
            fields["client_name"] = val
        elif key in ("phone", "cell", "cellphone", "mobile", "number"):
            fields["phone"] = normalize_phone_za(val)
        elif key in ("car", "vehicle", "make/model", "vehicle info"):
            fields["car"] = val
        elif key in ("notes", "note", "comments"):
            fields["notes"] = val
    return fields

@app.post("/trello/inbound")
async def trello_inbound(request: Request):
    try:
        data = await request.json()
    except Exception:
        body = await request.body()
        return JSONResponse({"ok": True, "raw": body.decode("utf-8")})

    parsed = parse_card_desc(data.get("desc", ""))

    lead = {
        "card_id": data.get("card_id"),
        "card_name": data.get("card_name"),
        "card_url": data.get("card_url"),
        "board": data.get("board_name"),
        "list": data.get("list_name"),
        "client_name": parsed["client_name"],
        "phone": parsed["phone"],
        "car": parsed["car"],
        "notes": parsed["notes"],
    }
    LEADS.append(lead)

    print("=== New Lead Parsed ===")
    for k, v in lead.items():
        print(f"{k}: {v}")

    return {"ok": True, "parsed": lead}

@app.get("/leads")
def list_leads():
    return {"count": len(LEADS), "items": LEADS}
