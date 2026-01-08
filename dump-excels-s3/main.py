import json
import os

import boto3
import pyexcel


def main(event, context):
    event_data = event.get("Records")[0]
    bucket_name = event_data["s3"]["bucket"]["name"]
    obj_key = event_data["s3"]["object"]["key"]
    client = boto3.client("s3")
    file = client.get_object(Bucket=bucket_name, Key=obj_key)
    file_content = file["Body"].read()
    sheet_data = pyexcel.get_records(file_content=file_content, file_type="xlsx")

    response_data = {}

    for row in sheet_data:
        songs = [v for k, v in row.items() if k.startswith("Songs")]
        songs = [song for song in songs if song]
        response_data[row.get("Artist")] = songs

    response = client.send_email(
        Destination={"ToAddresses": [os.getenv("RecipientEmailAddress")]},
        Message={
            "Body": {
                "Text": {
                    "Charset": "UTF-8",
                    "Data": f"{response_data}",
                }
            },
            "Subject": {
                "Charset": "UTF-8",
                "Data": f"Data received from file uploaded in S3 bucket {bucket_name} {obj_key}",
            },
        },
        Source=os.getenv("SourceEmailAddress"),
    )

    return {
        "statusCode": 200,
        "body": json.dumps(
            "Email Sent Successfully. MessageId is: " + response["MessageId"]
        ),
    }
