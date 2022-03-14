import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    studen_id = event['id']
    picture  = event['picture']
    name = "assets/"+studen_id+".png"
    image = picture
    image = image[image.find(",")+1:]
    dec = base64.b64decode(image + "===")
    s3.put_object(Bucket='students-static', Key=name, Body=dec,ACL='public-read')
    # TODO implement
    return {
        'URI' : 'https://students-static.s3.us-east-2.amazonaws.com/'+name
    }
