import json

import boto3
from boto3.dynamodb.conditions import Key


def lambda_handler(event, context):
    book_id = str(event["pathParameters"]["id"])
    try:
        db = boto3.resource("dynamodb")

        table = db.Table("books")
        response = table.query(KeyConditionExpression=Key("id").eq(book_id))

        obj_to_delete = response.get("Items")[0]
        table.delete_item(
            Key={"id": obj_to_delete["id"], "name": obj_to_delete["name"]}
        )

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"message": e})}
    return {
        "statusCode": 200,
        "body": json.dumps({"message": f"Book with id {book_id} deleted succesfully!"}),
    }
