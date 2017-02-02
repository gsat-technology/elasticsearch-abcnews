import os
import json

import boto3

dynamodb_table = os.environ['dynamodb_table']
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodb_table)


def handler(event, context):

    response = {
                "headers": {},
                "statusCode": None,
                "body": None
                }

    if event['httpMethod'] == 'POST':
        payload = json.loads(event['body'])
        print(payload)

        #payload sample:  {"time": {"updated":"Feb 2, 2017 00:25:00 UTC","updatedISO":"2017-02-02T00:25:00+00:00","updateduk":"Feb 2, 2017 at 00:25 GMT"},"disclaimer":"This data was produced from the CoinDesk Bitcoin Price Index (USD). Non-USD currency data converted using hourly conversion rate from openexchangerates.org","bpi":{"USD":{"code":"USD","rate":"989.2125","description":"United States Dollar","rate_float":989.2125},"AUD":{"code":"AUD","rate":"1,304.5082","description":"Australian Dollar","rate_float":1304.5082}}

        #format data to put in db
        payload['updatedISO'] = payload['time']['updatedISO']
        payload.pop('disclaimer', None) #disclaimer not required
        payload.pop('time', None) #time not required (we'll just use updatedISO)
        payload['bpi']['AUD'].pop('rate_float', None)
        payload['bpi']['USD'].pop('rate_float', None)

        result = table.put_item(Item=payload)

        if result['ResponseMetadata']['HTTPStatusCode'] == 200:
            response['statusCode'] = 204
        else:
            response['statusCode'] = 200
            response['body'] = json.dumps({'result': 'ERROR'})

        print(response)
    else:
        response = "bad method - use POST"

    return response
