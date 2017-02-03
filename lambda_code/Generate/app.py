import os
import json

import boto3
import arrow
import xmltodict
import requests

#environment variables
abc_rss_feed = os.environ['abc_rss_feed']
apig_stage = os.environ['apig_stage']
region = os.environ['region']
apig_id = os.environ['apig_id']
s3_latest_record_bucket = os.environ['s3_latest_record_bucket']

apig_endpoint = 'https://{}.execute-api.{}.amazonaws.com/{}/consume'.format(apig_id, region, apig_stage)
record_object = 'record.txt'

FORMAT = 'ddd, DD MMM YYYY HH:mm:ss ZZ'


s3 = boto3.resource('s3')
s3_client = boto3.client('s3')

def generate_id(timestr, f):
    return arrow.get(timestr, f).timestamp


def creator_or_blank(item):
    if 'dc:creator' in item:
        return item['dc:creator']
    else:
        return "-"


def categories_or_blank(item):
    if 'category' in item:
        return item['category']
    else:
        return "-"


def send_to_apig(endpoint, item):
    print(item)
    r = requests.post(endpoint, data=json.dumps(item))
    print('result status: {}'.format(r.status_code))
    print('result: {}'.format(r.text))



def process_item(item, previous_record):

    _id = generate_id(item['pubDate'], FORMAT)

    if _id > previous_record or previous_record == None:

        print('processing item with id: {}'.format(_id))

        return {
            'id': _id,
            'title': item['title'],
            'link': item['link'],
            'description': item['description'].split('<p>')[1].split('</p>')[0],
            'creator': creator_or_blank(item),
            'pub_date': item['pubDate'],
            'categories': categories_or_blank(item)
        }
    else:
        return None


#get the latest record (which is a timestamp) from when this function was last run
def get_previous_record(bucket, key):

    try:
        obj = s3.Object(s3_latest_record_bucket, key)
        record_str = obj.get()['Body'].read().decode('utf-8')
        record = int(record_str)
        return record
    except:
        return None


#write the current record to s3
def write_current_record(timestamp, bucket, key):

    print('writing new record to s3: {}'.format(timestamp))
    open('/tmp/' + key, 'w').write(str(timestamp))
    result = s3_client.upload_file('/tmp/' + key, bucket, key)
    print(result)


def handler(event, context):

    previous_record = get_previous_record(s3_latest_record_bucket, record_object)

    if previous_record:
        print('previous record timestamp: {}'.format(previous_record))
    else:
        print('no previous record')

    r = requests.get(abc_rss_feed)
    doc = xmltodict.parse(r.text)

    item_objects = [ process_item(doc_item, previous_record) for doc_item in doc['rss']['channel']['item'] ]
    item_objects = filter(None, item_objects) #remove 'None'

    if item_objects:
        print('{} objects'.format(len(item_objects))) #print item count

        #write latest timestamp to s3
        timestamps = [ i['id'] for i in item_objects ]
        max_timestamp = max(timestamps)
        write_current_record(max_timestamp, s3_latest_record_bucket, record_object )
    else:
        print('0 new items')

    #sent to APIG
    for item in item_objects:
        send_to_apig(apig_endpoint, item)
