import requests

def translator(message, source, target):
    url = 'https://translation.googleapis.com/language/translate/v2'
    params ={'key' : '[Your Key]',
    'q' : message, 'source' : source, 'target' : target}
    response = requests.get(url, params=params)
    translatedText=str(response.json()['data']['translations'][0]['translatedText']).replace("&#39;","'")
    return translatedText
