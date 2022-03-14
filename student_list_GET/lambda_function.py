import boto3
import json
from boto3.dynamodb.conditions import Key
from decimal import Decimal

def default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError("Object of type '%s' is not JSON serializable" % type(obj).__name__)
    
    
def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Students')
    response = table.query(
        IndexName='student_status-index',
        KeyConditionExpression=Key('student_status').eq("active")
    )
    items = response.get('Items', [])
    print(items)
    return {
        'statusCode': 200,
        'body': json.dumps(items, default=default),
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True
        },
    }
    
