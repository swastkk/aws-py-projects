# Approach: Method Type: GET
# Return -> a presigned url that will be used to make a PUT request directly so that the image is directly uploaded to the S3 storage


import json
import os
import traceback
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError


def convert_decimal(obj):
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    if isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_decimal(v) for v in obj]
    return obj


def generate_presigned_url(s3, bucket_name, key):
    try:
        image_url = s3.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": bucket_name,
                "Key": key,
            },
            ExpiresIn=36000,
        )
    except Exception as e:
        return None
    return image_url


def generate_image_key(name):
    return name.replace(" ", "_").lower() + ".jpeg"


def lambda_handler(event, context):
    book_id = str(event["pathParameters"]["id"])
    try:
        db = boto3.resource("dynamodb")
        table = db.Table("books")
        response = table.query(KeyConditionExpression=Key("id").eq(book_id))
        response_item = response.get("Items")[0]

        # Assign a presign url for the Image upload purpose.
        s3_client = boto3.client("s3")

        bucket_name = os.getenv("BUCKET_NAME")
        image_key = generate_image_key(response_item["name"])
        response_item["upload_image_url"] = generate_presigned_url(
            s3_client, bucket_name, image_key
        )

        # save the key against the image key of the book object
        table.update_item(
            Key={"id": response_item["id"], "name": response_item["name"]},
            AttributeUpdates={"image": {"Value": f"{image_key}", "Action": "PUT"}},
        )
        response_data = convert_decimal(response_item)
        response_data = {**response_data, "image": image_key}

    except ClientError as client_error:
        return {
            "statusCode": 503,
            "body": json.dumps(
                {"message": f"Service Unavailable: Error Details: {client_error}"}
            ),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(e), "trace": traceback.format_exc()}),
        }

    return {"statusCode": 200, "body": json.dumps(response_data)}
