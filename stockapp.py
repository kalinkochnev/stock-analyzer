import requests
import json
from requests.exceptions import HTTPError
from textblob import TextBlob
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from langdetect import detect
import twitter
import re

with open('keys.json') as f:
    data = json.load(f)

#Stock symbol : Company name
listOfStocks = {
    'AMD':'AMD',
    'AMZN':'Amazon',
    'TSLA':'Tesla',
    'MSFT':'Microsoft',
    'GOOG': 'Google',
    'INTC':'Intel',
    'NVDA':'NVIDIA',
    }

#Stock Symbol : (sentiment, number of values)
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

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True, timeout=3.05)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                print('Closing error or timeout')

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        print('Error during requestse')

def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)

def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)
    
def getStock(function, symbol, startDate, endDate):
    #alphavantage api key 1YWD5OHNOOE4AFEW
    requestStock = requests.get("https://www.alphavantage.co/query?", {
        'function':'GLOBAL_QUOTE',
        'symbol':'TSLA',
        'datatype':'json',
        'apikey':data['alphavantage'][0],
        'pageSize':100,
        })
    jsonResponse = json.dumps(requestStock.json(), indent=4, sort_keys=True)
    return jsonResponse

#TODO add start and end date parameters
def getNews(keyword, page): 
    #newsapi api key e038384cef824e32904127401e34bf4b
    requestNewsSource = requests.get('https://newsapi.org/v2/everything?', {
        'apiKey':data['newsapi'][0],
        'q':keyword,
        'pageSize':100,
        'page':page,
    })
    response = requestNewsSource.content
    jsonResponse = json.loads(response.decode('utf-8'))
    
    return jsonResponse
    
#key search term, from date and to date using YYYY-MM-DD format
def calcNewsSentiment(keyword, headlineBool, contentBool):
    pageNum = 1
    hasArticles = True
    responseJson = getNews(keyword, pageNum)
    if responseJson['status'] == 'ok':
        print("File was recieved without error")
        print('There are %s results found' % str(responseJson['totalResults']))

        #these are some variables that are accessed throughout the function
        numResults = responseJson['totalResults']
        articleNumber = 0
        totalArticlesDone = 0
        polarity = 0
        subjectivity = 0       
        
        #loops through the given page
        while (pageNum < numResults/100 and hasArticles):
            if responseJson['status'] != 'ok':
                    print('MAX ARTICLES REACHED')
                    hasArticles = False
                    break

            for article in responseJson['articles']:    
                if responseJson['status'] == 'ok':
                    #increments page number, resets article number, outputs new json and gets the next page
                    if articleNumber >= len(responseJson['articles'])-1:
                        pageNum += 1
                        articleNumber = 0
                        print('On page %s of %s' % (pageNum, (numResults/100)))
                        responseJson = getNews(keyword, pageNum)
                        break

                    print('\n----- Article #%s %s-----' % (totalArticlesDone, articleNumber))
                    headline = str(responseJson['articles'][articleNumber]['title'])
                    content = ''    
                    print(headline)
                    
                    #checks if the content is english
                    if detect(headline) == "en":
                        #If the user wants to analyze content, this will run
                        if contentBool == True:
                            try:
                                url = str(responseJson['articles'][articleNumber]['url'])
                            except:
                                print('Returned a null url')
                            
                            #gets the article contents from p tags using BS4
                            #TODO add exception catching
                            raw_html = get(url)
                            html = BeautifulSoup(raw_html.text, 'html.parser')
                            content = [p.text for p in html.select('p')]
                            print('Got article website and parsed its text for')

                        if headlineBool == True:
                            #collects headline from json
                            try:
                                headline = str(responseJson['articles'][articleNumber]['title'])
                            except:
                                print('Returned a null headline')
                                totalArticlesDone += 1
                                articleNumber = articleNumber + 1
                                break
                
                        #gets the sentiment using TextBlob
                        text = ('%s\n%s' % (headline, content))
                            
                        sentiment = TextBlob(text).sentiment
                        articlePolarity, articleSubjectivity = sentiment
                        print('Got sentiment for article')

                        #updates values of article
                        polarity += articlePolarity
                        subjectivity += articleSubjectivity
                        articleNumber = articleNumber + 1
                        totalArticlesDone += 1

                        #calculates average sentiment and subjectivity of articles
                        avgSentiment = polarity/totalArticlesDone
                        avgSubjectivity = subjectivity/totalArticlesDone
                        print('Updating polarity value')
                        print(articlePolarity, articleSubjectivity)
                        

                    else:
                        print("Language not english")
                        articleNumber = articleNumber + 1
                        break
                   
            #print(responseJson)

        #outputs what was analyzed
        if headlineBool == True and contentBool == False:
            print('-- Headline analysis --')
        elif headlineBool == False and contentBool == True:
            print('-- Content analysis')    
        elif headlineBool == True and contentBool == True:
            print('-- Headline and content analysis --')
        
        #outputs some information about the numbers
        if avgSentiment > 0:
            print(' %s -- %s has a positive sentiment ' % (avgSentiment, keyword))
        elif avgSentiment < 0:
            print(' %s -- %s has a negative sentiment ' % (avgSentiment, keyword))
        elif avgSentiment == 0:
            print(' %s -- %s has a neutral sentiment ' % (avgSentiment, keyword))
        
        if avgSubjectivity < 0.5 and avgSubjectivity > 0:
            print(" %s -- The opinions were more objective than subjective " % avgSubjectivity)
        elif avgSubjectivity > 0.5 and avgSubjectivity > 0:
            print( + " %s -- The opinions were more subjective than objective " % avgSubjectivity)
        
    else:
        print('There was an error retrieving the file')
    
    #updates sentiment record of the stock
    stockSentiment[keyword] = avgSentiment, avgSubjectivity, articleNumber
    return stockSentiment[keyword]

def getTweets(keyword):
    api = twitter.Api(
        consumer_key=data['twitter'][0], 
        consumer_secret=data['twitter'][1],
        access_token_key=data['twitter'][2],
        access_token_secret=data['twitter'][3],
        )
    results = api.GetSearch(term=keyword, result_type='popular', return_json=True, count=100, lang='en')
    rateLimit = api.get_limit()
    
    for num in range(9):
        print(json.dumps(results['statuses'][num]['text'], indent=3))
    return results

def calcTwitterSentiment(keyword):

#print(getNewsSentiment('Tesla', True, False))
getTweets('tesla')
