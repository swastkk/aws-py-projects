from uuid import uuid4 as uuid

import boto3
from botocore.exceptions import ClientError


def lambda_handler(event, context):
    db = boto3.resource("dynamodb")
    book_id = event.get("id", str(uuid()))
    try:
        table = db.Table("books")
        table.put_item(
            Item={
                "id": book_id,
                "name": event.get("name"),
                "author": event.get("author", ""),
                "price": event.get("price"),
            }
        )

    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            return {"statusCode": 401, "message": f"Table is not there! sorry!"}
        else:
            return {"statusCode": 500, "message": f"error details: {e}"}

    event = {**event, "id": book_id}
    return {
        "statusCode": 201,
        "body": {"message": "New book added successfully!", "book": event},
    }
