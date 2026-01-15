import json
import os
import time
import uuid

import jwt


def lambda_handler(event, context):
    private_key = os.getenv("PRIVATE_KEY")
    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + 600,
        "iss": "book-library-backend",
        "jti": str(uuid.uuid4()),
    }
    token = jwt.encode(payload, private_key, algorithm="RS256")

    return {"statusCode": 200, "body": json.dumps({"token": token})}
