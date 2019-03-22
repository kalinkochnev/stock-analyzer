import requests
import json
from requests.exceptions import HTTPError
from textblob import TextBlob


listOfStocks = {
    'AMD':'AMD',
    'AMZN':'Amazon',
    'TSLA':'Tesla',
    'MSFT':'Microsoft',
    'GOOG': 'Google',
    'INTC':'Intel',
    'NVDA':'NVIDIA',
    }

stockSentiment = {

}


def testURL(link):
    try:
        response = requests.get(link)
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as http_err:
        return(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        return(f'Other error occurred: {err}')  # Python 3.6
    else:
        return ('Success!')

def getStock(function, symbol, startDate, endDate):
    #alphavantage api key 1YWD5OHNOOE4AFEW
    requestStock = requests.get("https://www.alphavantage.co/query?", {
        'function':'GLOBAL_QUOTE',
        'symbol':'TSLA',
        'datatype':'json',
        'apikey':'1YWD5OHNOOE4AFEW'
        })
    jsonResponse = json.dumps(requestStock.json(), indent=4, sort_keys=True)
    return jsonResponse

def getNews(keyword, startDate, endDate): 
    #newsapi api key e038384cef824e32904127401e34bf4b
    requestNews = requests.get('https://newsapi.org/v2/top-headlines?', {
        'apiKey':'e038384cef824e32904127401e34bf4b',
        'country':'us',
        'q':keyword,
    })
    jsonResponse = json.dumps(requestNews.json(), indent=4)
    return jsonResponse

def getSentiment(stockSymbol):
    articleText = getNews(listOfStocks[stockSymbol])['articles']['content']
    sentiment = TextBlob(articleText).sentiment