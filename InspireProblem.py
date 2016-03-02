import boto3
import json
import decimal
import time
import random
from boto3.dynamodb.conditions import Key
import urllib


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


dynamodb = boto3.resource('dynamodb', region_name='us-east-1', endpoint_url="https://dynamodb.us-east-1.amazonaws.com")
table = dynamodb.Table('Problems')


def lambda_handler(event, context):
    if event['action'] == 'submitProblem':
        return save_a_problem(event['problem'])
    elif event['action'] == 'saveAWord':
        code = event['id']
        response = save_a_word(code, event['word'], event['inspiration'])
        print(response)
        return code
    elif event['action'] == 'saveAWordAndGetAnother':
        code = event['id']
        response = save_a_word(code, event['word'], event['inspiration'])
        print(response)
        word = get_a_word()
        return json.dumps({'word': word})
    elif event['action'] == 'getAWord':
        word = get_a_word()
        return json.dumps({'word': word})
    elif event['action'] == 'showASolution':
        return show_all_words(event['id'])
    elif event['action'] == 'saveAWordAndShowASolution':
        code = event['id']
        response = save_a_word(code, event['word'], event['inspiration'])
        print(response)
        return show_all_words(event['id'])


def save_a_problem(problem):
    code = time.strftime('%Y%m%d%H%M%S')
    return table.put_item(
        Item={
            'id': int(code),
            'problem': problem,
        }
    )


def get_a_word():
    opener = urllib.URLopener()
    word_url = "https://s3.amazonaws.com/rocky-feo-inspiration/dictionary.txt"
    words = list(line.strip() for line in opener.open(word_url))
    return random.choice(words)


def save_a_word(code, word, inspiration):
    return table.update_item(
        Key={
            'id': code
        },
        UpdateExpression="set #w = :i",
        ExpressionAttributeValues={
            ':i': inspiration
        },
        ExpressionAttributeNames={
            '#w': word
        },
        ReturnValues="UPDATED_NEW"
    )


def show_all_words(code):
    response = table.query(
        KeyConditionExpression=Key('id').eq(code)
    )
    return response
