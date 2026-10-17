import hmac

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from logic import aggregate

API_KEY = "ak_9vlx1da6klbcb65x4ahw1s0u"

app = FastAPI(title="Analytics")
# CORS is the outermost layer, so 401/422 responses carry the CORS headers too
# and the browser can read them. Preflight (OPTIONS) is answered here, before auth.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)


@app.get("/")
def root():
    return {"service": "analytics", "try": "POST /analytics with X-API-Key"}


@app.post("/analytics")
async def analytics(request: Request):
    key = request.headers.get("x-api-key") or ""
    if not hmac.compare_digest(key.encode(), API_KEY.encode()):
        return JSONResponse({"detail": "invalid or missing API key"}, status_code=401)
    try:
        body = await request.json()
        events = body["events"]
        if not isinstance(events, list):
            raise ValueError
    except Exception:
        return JSONResponse({"detail": "body must be {\"events\": [...]}"}, status_code=422)
    return aggregate(events)
