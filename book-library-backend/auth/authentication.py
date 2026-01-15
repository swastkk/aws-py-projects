import json
import os

import jwt
from cryptography.hazmat.primitives import hashes


def lambda_handler(event, context):
    public_key = os.getenv("PUBLIC_KEY")
    token = event.get("authorizationToken", "").replace("Bearer ", "")
    method_arn = event["methodArn"]
    action = "Deny"
    context_data = {}

    arn_parts = method_arn.split("/")
    api_gateway_arn = "/".join(arn_parts[0:2]) + "/*"

    try:
        context_data = jwt.decode(token, public_key, algorithms=["RS256"])
        action = "Allow"
    except Exception as e:
        action = "Deny"
    return {
        "principalId": "user_Swastik",
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": action,
                    "Resource": api_gateway_arn,
                }
            ],
        },
        "context": {
            "jti": str(context_data.get("jti", "")),
            "iss": context_data.get("iss", ""),
        },
    }
