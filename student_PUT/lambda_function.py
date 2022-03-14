import boto3
import json
from datetime import datetime


client = boto3.client('lambda')

def lambda_handler(event, context):
    body = event.get('body')
    if not body:
        return {
            'statusCode': 400,
            'body': json.dumps("Not valid payload")
        }

    # Reading events
    student_id = None
    path_parameters = event.get('pathParameters', [])
    student_payload = json.loads(body)

    if path_parameters:
        student_id = path_parameters.get('student_id')
        student_payload["id"] = student_id

    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Students')
    inputParams = {
        "id": student_payload.get('id'),
        "picture" : student_payload.get('picture')
    }
    responsePic = client.invoke(
        FunctionName = 'arn:aws:lambda:us-east-2:889017460304:function:picture_POST',
        InvocationType = 'RequestResponse',
        Payload = json.dumps(inputParams)
    )
    picture = json.load(responsePic['Payload'])
    if not picture.get('URI'):
        return {
            'statusCode': 400,
            'body': json.dumps("No URI found in payload")
        }
    student_payload['picture'] = picture.get('URI')
    response = table.update_item(
        Key={
            'id': student_id
        },
        UpdateExpression="set first_name=:fn, last_name=:ln, updated_at=:ua, student_status=:st, picture=:pt, age=:ag, work_experience=:we, years_experience=:ye, tech_skills=:ts, soft_skills=:ss, description=:ds, observations=:obs",
        ExpressionAttributeValues={
            ':fn': student_payload.get('first_name', ""),
            ':ln': student_payload.get('last_name', ""),
            ':ua': datetime.today().strftime('%Y-%m-%d'),
            ':st': student_payload.get('student_status',"active"),
            ':pt': student_payload.get('picture'),
            ':ag': student_payload.get('age', 0),
            ':we': student_payload.get('work_experience',[""]),
            ':ye': student_payload.get('years_experience', 0),
            ':ts': student_payload.get('tech_skills',[""]),
            ':ss': student_payload.get('soft_skills',[""]),
            ':ds': student_payload.get('description', ""),
            ':obs': student_payload.get('observations', "")
        },
        ReturnValues="UPDATED_NEW"
    )
    print(response)

    # Response for the client
    data = {
        "message": "Student was updated",
        "student_updated": student_payload
    }

    return {
        'statusCode': 200,
        'body': json.dumps(data),
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True
        },
    }