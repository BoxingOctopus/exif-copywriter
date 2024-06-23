import json
import boto3
from PIL import Image
from PIL.ExifTags import TAGS
import io
import piexif

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Parse the request body
    body = json.loads(event['body'])
    bucket = body['bucket']
    key = body['key']
    copyright_info = body['copyright']

    # Download the image from S3
    response = s3.get_object(Bucket=bucket, Key=key)
    img_data = response['Body'].read()

    # Open the image
    image = Image.open(io.BytesIO(img_data))

    # Get existing EXIF data
    exif_data = image.info.get('exif')
    exif_dict = image._getexif()
    if exif_dict:
        exif = {TAGS.get(tag, tag): value for tag, value in exif_dict.items()}
    else:
        exif = {}

    # Add or update the copyright information
    exif['Copyright'] = copyright_info

    # Convert the EXIF dictionary back to bytes
    exif_bytes = piexif.dump(exif)

    # Save the image with the updated EXIF data
    output = io.BytesIO()
    image.save(output, format='JPEG', exif=exif_bytes)
    output.seek(0)

    # Upload the updated image back to S3
    s3.put_object(Bucket=bucket, Key=key, Body=output, ContentType='image/jpeg')

    return {
        'statusCode': 200,
        'body': json.dumps('EXIF data updated successfully')
    }