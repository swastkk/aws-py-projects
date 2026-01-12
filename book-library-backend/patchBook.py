# Used proxy integration Lambda proxy integration Info as True
# For the sake of event to parse without any obsctruction
# This method is for image upload via mutli-part form input and decoding the image to bytes and then upload the object to s3

import base64
import json
import os
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key


def convert_decimal(obj):
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    if isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_decimal(v) for v in obj]
    return obj


def generate_presigned_url(s3, bucket_name, key):
    return s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": bucket_name,
            "Key": key,
        },
        ExpiresIn=36000,
    )


def generate_image_key(name):
    return name.replace(" ", "_").lower() + ".jpeg"


def lambda_handler(event, context):
    book_id = str(event["pathParameters"]["id"])

    image_content = event["body"]
    decoded_bytes = base64.b64decode(image_content)
    header_end = decoded_bytes.find(b"\r\n\r\n") + 4
    image_bytes = decoded_bytes[header_end:]

    try:
        db = boto3.resource("dynamodb")
        s3_client = boto3.client("s3")

        bucket_name = os.getenv("BUCKET_NAME")
        table = db.Table("books")
        response = table.query(KeyConditionExpression=Key("id").eq(book_id))
        response_item = response.get("Items")[0]
        file_name = response_item["name"]
        image_key = generate_image_key(file_name)

        s3_client.put_object(
            Bucket=bucket_name,
            Key=image_key,
            Body=image_bytes,
            ContentType="image/jpeg",
        )

        # save the key against the image key of the book object
        table.update_item(
            Key={"id": response_item["id"], "name": response_item["name"]},
            AttributeUpdates={"image": {"Value": f"{image_key}", "Action": "PUT"}},
        )

        updated_response = table.query(KeyConditionExpression=Key("id").eq(book_id))
        updated_response_item = updated_response.get("Items")[0]
        updated_response_data = convert_decimal(updated_response_item)

        updated_response_data = {
            **updated_response_data,
            "image_url": generate_presigned_url(
                s3_client,
                bucket_name,
                image_key,
            ),
        }

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"message": e})}

    return {
        "statusCode": 200,
        "body": json.dumps(updated_response_data),
    }
