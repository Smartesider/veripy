import os
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from src.validator import validate_article
from datetime import datetime

# Last inn miljøvariabler fra .env
load_dotenv()
API_KEY = os.getenv("API_KEY")

app = FastAPI(
    title="Guffen-API v1",
    description="Validerer artikler mot alle kravfiler og gir maskinlesbar rapport.",
    version="1.0"
)

# Funksjon for logging av alle events
def log_event(event_type, user_ip, status_msg):
    log_msg = f"{datetime.now().isoformat()} | {event_type} | {user_ip} | {status_msg}\n"
    with open("validation.log", "a", encoding="utf-8") as f:
        f.write(log_msg)

@app.post("/validate")
async def validate(request: Request):
    # 1. Sjekk API-nøkkel i headers (Authorization: Bearer ...)
    auth = request.headers.get("Authorization")
    client_ip = request.client.host
    if not auth or not auth.startswith("Bearer "):
        log_event("AUTH_FAIL", client_ip, "Mangler Authorization header")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Mangler API-nøkkel (Authorization header)")
    key = auth.split(" ")[1]
    if key != API_KEY:
        log_event("AUTH_FAIL", client_ip, "Feil API-nøkkel")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Ugyldig API-nøkkel")
    # 2. Forsøk å parse json fra request-body
    try:
        data = await request.json()
    except Exception as e:
        log_event("REQUEST_FAIL", client_ip, f"Feil i JSON: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Feil i JSON-format eller manglende data")
    # 3. Valider artikkelen mot alle krav
    try:
        report = validate_article(data)
        log_event("VALIDATION_OK", client_ip, "Artikkel validert")
        return JSONResponse(content=report)
    except Exception as e:
        log_event("VALIDATION_FAIL", client_ip, f"Valideringsfeil: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Feil under validering: {e}")
