import boto3
import json
import uuid
from decimal import Decimal
from datetime import datetime


# Define the client to interact with AWS Lambda
client = boto3.client('lambda')

def default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError("Object of type '%s' is not JSON serializable" % type(obj).__name__)

def lambda_handler(event, context):

    # Reading `body` from event
    body = event.get('body')
    if not body:
        return {
            'statusCode': 400,
            'body': json.dumps("Not valid payload")
        }

    student_payload = json.loads(body)
    student_payload["id"] = str(uuid.uuid4())

    # Return error messages if the student does not have enough info
    if not student_payload.get('first_name'):
        return {
            'statusCode': 400,
            'body': json.dumps("No first name found in payload")
        }

    if not student_payload.get('last_name'):
        return {
            'statusCode': 400,
            'body': json.dumps("No last name found in payload")
        }

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Students')
    response = table.get_item(
        Key={
            'id': student_payload["id"],
        }
    )
    student = response.get('Item', {})
    
    if student.get('last_name'):
        return {
            'statusCode': 409,
            'body': json.dumps("Student ID already exists in our system")
        }
    if student_payload.get('picture'):
        inputParams = {
            "id": student_payload['id'],
            "picture" : student_payload['picture']
        }
        
        responsePic = client.invoke(
            FunctionName = 'arn:aws:lambda:us-east-2:889017460304:function:picture_POST',
            InvocationType = 'RequestResponse',
            Payload = json.dumps(inputParams)
        )
        print(responsePic)
        picture = json.load(responsePic['Payload'])
        print(picture)
        if not picture.get('URI'):
            return {
                'statusCode': 400,
                'body': json.dumps("No URI found in payload")
            }
        student_payload['picture'] = picture.get('URI')
    else:
        student_payload['picture']="https://students-static.s3.us-east-2.amazonaws.com/assets/image-default.png"
    
    student_payload['student_status']='active'
    date= datetime.today().strftime('%Y-%m-%d')
    student_payload['created_at']=date
    student_payload['updated_at']=date
    
    response = table.put_item(
        Item=student_payload
    )
    print(response)

    # Response for the client
    data = {
        "message": "Student was created",
        "student_created": student_payload
    }

    return {
        'statusCode': 200,
        'body': json.dumps(data),
        'headers': {
            "Access-Control-Allow-Origin" : "*",
            "Access-Control-Allow-Credentials" : True
        },
    }