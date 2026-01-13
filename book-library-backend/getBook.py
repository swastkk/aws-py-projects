# Used proxy integration Lambda proxy integration Info as True
# For the sake of event to parse without any obsctruction

import json
import traceback
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


def lambda_handler(event, context):
    book_id = str(event["pathParameters"]["id"])
    try:
        db = boto3.resource("dynamodb")
        table = db.Table("books")
        response = table.query(KeyConditionExpression=Key("id").eq(book_id))
        response_item = response.get("Items")[0]
        response_data = convert_decimal(response_item)

    except IndexError:
        return {
            "statusCode": 404,
            "body": json.dumps({"message": f"Book with id {book_id} not found!"}),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(e), "trace": traceback.format_exc()}),
        }
    return {"statusCode": 200, "body": json.dumps(response_data)}
