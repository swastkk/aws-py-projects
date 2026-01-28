import json
import traceback
from uuid import uuid4 as uuid

import boto3
from botocore.exceptions import ClientError


def lambda_handler(event, context):
    db = boto3.resource("dynamodb")
    event_body = json.loads(event["body"])
    book_id = event_body.get("id", str(uuid()))

    try:
        table = db.Table("books")
        table.put_item(
            Item={
                "id": book_id,
                "name": event_body.get("name"),
                "author": event_body.get("author", ""),
                "price": event_body.get("price"),
            }
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            return {
                "statusCode": 404,
                "body": json.dumps({"message": "Table not found!"}),
            }
        else:
            return {"statusCode": 500, "body": json.dumps({"message": str(e)})}
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(e), "trace": traceback.format_exc()}),
        }

    event_body = {**event_body, "id": book_id}
    return {
        "statusCode": 201,
        "body": json.dumps(
            {"message": "New book added successfully!", "book": event_body}
        ),
    }
