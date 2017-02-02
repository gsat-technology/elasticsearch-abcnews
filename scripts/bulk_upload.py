import arrow
import xmltodict
import requests

APIG_ENDPOINT = ''

FORMAT = 'ddd, DD MMM YYYY HH:mm:ss ZZ'

def generate_id(timestr, f):
    return arrow.get(timestr, f).timestamp

def creator_or_blank(item):
    if 'dc:creator' in item:
        return item['dc:creator']
    else:
        return ""


def categories_or_none(item):
    if 'category' in item:
        return item['category']
    else:
        print item['title']
        return None

def send_apig(APIG_ENDPOINT, item):
    r = requests.post(APIG_ENDPOINT, data=item)


def process_item(item):
    return {
        'id': generate_id(item['pubDate'], FORMAT),
        'title': item['title'],
        'link': item['link'],
        'description': item['description'].split('<p>')[1].split('</p>')[0],
        'creator': creator_or_blank(item),
        'pub_date': item['pubDate'],
        'categories': categories_or_none(item)
    }


with open('rss.xml') as fp:
    doc = xmltodict.parse(fp.read())

    item_objects = [ process_item(doc_item) for doc_item in doc['rss']['channel']['item'] ]

    for item in item_objects:
        send_apig(item)
