import os
import requests

bc_url = os.environ['bitcoin_url']
apig = 'https://{}.execute-api.{}.amazonaws.com/{}/consume'.format(os.environ['apig_id'], os.environ['region'], os.environ['apig_stage'])


def handler(event, context):

    bc_data = requests.get(bc_url).text

    print(bc_data)

    r = requests.post(apig, data=bc_data)

    if str(r.status_code)[0] == '2':
        print('apig result OK')
    else:
        print('ERROR. status code {}'.format(r.status_code))
        print('reason: {}'.format(r.text))

    return 'done'
