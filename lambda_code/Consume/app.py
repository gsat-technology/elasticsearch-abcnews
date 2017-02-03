import os
import json

import boto3

dynamodb_table = os.environ['dynamodb_table']
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodb_table)


def handler(event, context):

    print(event)

    response = {
                "headers": {},
                "statusCode": None,
                "body": None
                }

    if event['httpMethod'] == 'POST':
        payload = json.loads(event['body'])

        result = table.put_item(Item=payload)

        if result['ResponseMetadata']['HTTPStatusCode'] == 200:
            response['statusCode'] = 204

            #identifier for subscriptions filter
            payload['logstream_identifier'] = 'abc_news_data'

            #log to cw logs (subscription will filter this and add to ES)
            print(json.dumps(payload))
        else:
            response['statusCode'] = 200
            response['body'] = json.dumps({'result': 'ERROR'})

        print(response)
    else:
        response = "bad method - use POST"

    return response
