import json
import os
import time
import uuid

import jwt
from cryptography.hazmat.primitives import hashes
from dotenv import load_dotenv
from fastapi.responses import JSONResponse

load_dotenv()


def generate_token():
    private_key = os.getenv("PRIVATE_KEY")
    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + 600,
        "iss": "book-library-backend",
        "jti": str(uuid.uuid4()),
    }
    token = jwt.encode(payload, private_key, algorithm="RS256")

    return JSONResponse(status_code=200, content={"token": token})


def validate_token(event):
    public_key = os.getenv("PUBLIC_KEY")
    token = event.get("authorizationToken", "")

    try:
        context_data = jwt.decode(token, public_key, algorithms=["RS256"])
    except Exception as e:
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
    return JSONResponse(
        status_code=200, content={"detail": "Authorized", "context": context_data}
    )
