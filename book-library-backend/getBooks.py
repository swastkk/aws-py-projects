import json
import os

import boto3
from botocore.exceptions import ClientError


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


def lambda_handler(event, context):
    try:
        db = boto3.resource("dynamodb")
        table = db.Table("books")
        table.load()

    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            table = db.create_table(
                TableName="books",
                KeySchema=[
                    {"AttributeName": "id", "KeyType": "HASH"},
                    {"AttributeName": "name", "KeyType": "RANGE"},
                ],
                AttributeDefinitions=[
                    {"AttributeName": "id", "AttributeType": "S"},
                    {"AttributeName": "name", "AttributeType": "S"},
                ],
                BillingMode="PAY_PER_REQUEST",
            )
            table.wait_until_exists()
        else:
            return {
                "statusCode": 500,
                "body": json.dumps({"message": e.response}),
            }

    response = table.scan()
    book_data = response.get("Items", [])

    bucket_name = os.getenv("BUCKET_NAME")
    try:
        s3_client = boto3.client("s3")
        for book in book_data:
            book["image_url"] = generate_presigned_url(
                s3_client, bucket_name, book.get("image", "")
            )
    except ClientError as e:
        return {"statusCode": 500, "body": json.dumps({"message": e.response})}
    return {
        "statusCode": 200,
        "body": book_data,
    }
