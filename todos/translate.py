import os
import json

from todos import decimalencoder
import boto3
dynamodb = boto3.resource('dynamodb')
translate = boto3.client('translate')
comprehend = boto3.client(service_name='comprehend', region_name='us-east-1')


def en(event, context):
    return translateRequest('en',event['pathParameters']['id'])
    
def fr(event, context):
    return translateRequest('fr',event['pathParameters']['id'])

def translateRequest(destLang,id):
    try:
        item = getTableReg(id)
        textRequest = item['text']
        langResponse = detectLanguage(textRequest)
        lang = langResponse['Languages'][0]['LanguageCode']
        if destLang == 'en':
            translatedText = translateText(textRequest,lang,"en")
        elif destLang == 'fr':
            translatedText = translateText(textRequest,lang,"fr")
        else:
            translatedText = translateText(textRequest,lang,"en")
        
        response = {
            "statusCode": 200,
            "body": json.dumps(translatedText)
        }
    except KeyError:
        textResponse = {
            "text": "Id no pudo ser traducido."
        }
        response = {
            "statusCode": 400,
            "body": json.dumps(textResponse)
        }
    return response
    
def getTableReg(key):
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    # fetch todo from the database
    result = table.get_item(
        Key={
            'id': key
        }
    )
    return result['Item']
    
def detectLanguage(text):
    return comprehend.detect_dominant_language(Text = text)
    
def translateText(text,sourceLang,destLang):
    textTranslated = translate.translate_text(Text=text , SourceLanguageCode=sourceLang, TargetLanguageCode=destLang)
    data = {
        "languageOrigin": sourceLang,
        "textOrigin": text,
        "languageTranslated": destLang,
        "textTranslated": textTranslated['TranslatedText']
    }
    return data