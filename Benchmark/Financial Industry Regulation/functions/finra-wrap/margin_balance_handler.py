import time
import json
from function.util import *

def checkMarginBalance(portfolioData, marketData, portfolio):
    marginAccountBalance = json.loads(open('/home/app/function/marginBalance.json', 'r').read())[portfolio]

    portfolioMarketValue = 0
    for trade in portfolioData:
        security = trade['Security']
        qty = trade['LastQty']
        portfolioMarketValue += qty*marketData[security]

    #Maintenance Margin should be atleast 25% of market value for "long" securities
    #https://www.finra.org/rules-guidance/rulebooks/finra-rules/4210#the-rule
    result = False
    if marginAccountBalance >= 0.25*portfolioMarketValue:
        result = True

    return result

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    events = json.loads(req)
    events = [json.loads(event) for event in events]

    startTime = 1000*time.time()
    marketData = {}
    validFormat = True

    for event in events:
        body = event['body']
        if 'marketData' in body:
            marketData = body['marketData']
        elif 'valid' in body:
            portfolio = event['body']['portfolio']
            validFormat = validFormat and body['valid']

    portfolios = json.loads(open('/home/app/function/portfolios.json', 'r').read())
    portfolioData = portfolios[portfolio]
    marginSatisfied = checkMarginBalance(portfolioData, marketData, portfolio)

    response = {'statusCode': 200,
                'body': {'validFormat': validFormat, 'marginSatisfied': marginSatisfied}}

    endTime = 1000*time.time()
    return json.dumps(agg_timestamp(response, events, startTime, endTime, 0))

