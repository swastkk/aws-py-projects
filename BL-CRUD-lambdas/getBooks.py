import json
import os
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()


def generate_presigned_url(s3, bucket_name, key):
    try:
        image_obj = s3.get_object(Bucket=bucket_name, Key=key)
        image_url = s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": bucket_name,
                "Key": key,
            },
            ExpiresIn=36000,
        )
    except Exception as e:
        return None
    return image_url


def convert_decimal(obj):
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    if isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_decimal(v) for v in obj]
    return obj


def lambda_handler(event, context):
    limit = int(event.get("queryStringParameters", {}).get("limit", 10))
    offset = str(event.get("queryStringParameters", {}).get("offset"))

    book_data = {}

    try:
        db = boto3.resource(
            "dynamodb",
            region_name="ap-south-1",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
        table = db.Table("books")
        db.meta.client.describe_table(TableName="books")
        if offset is None:
            response = table.scan(Limit=limit)
        else:
            response = table.scan(Limit=limit, ExclusiveStartKey={"id": offset})
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            table = db.create_table(
                TableName="books",
                KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
                AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
                BillingMode="PAY_PER_REQUEST",
            )
            table.wait_until_exists()
        else:
            return {
                "statusCode": 500,
                "body": json.dumps({"message": e.response}),
            }
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"message": str(e)})}

    book_data["last_evaluated_key"] = response.get("LastEvaluatedKey", None)
    book_data["books"] = convert_decimal(response.get("Items", []))

    bucket_name = os.getenv("BUCKET_NAME")
    try:
        s3_client = boto3.client(
            "s3",
            region_name="ap-south-1",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
        for book in book_data["books"]:
            book["image_url"] = generate_presigned_url(
                s3_client, bucket_name, book.get("image", "")
            )
    except ClientError as e:
        return {"statusCode": 403, "body": json.dumps({"message": e.response})}

    return {
        "statusCode": 200,
        "body": json.dumps(book_data),
    }
