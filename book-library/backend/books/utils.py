def generate_image_key(name):
    return name.replace(" ", "_").lower() + ".jpeg"


def generate_put_presigned_url(s3, bucket_name, key):
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


def generate_get_presigned_url(s3, bucket_name, key):
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
