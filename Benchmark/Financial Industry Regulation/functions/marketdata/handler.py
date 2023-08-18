from function import base
import time
import json

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    event = json.loads(req)

    startTime = time.time()
    externalServicesTime = []
    portfolioType = event['body']['portfolioType']

    tickersForPortfolioTypes = {'S&P': ['GOOG', 'AMZN', 'MSFT']}
    tickers = tickersForPortfolioTypes[portfolioType]

    prices = {}
    for ticker in tickers:
        tickerObj = base.Ticker(ticker)
        #Get last closing price
        tickTime = time.time()
        data = tickerObj.history(period="1")
        externalServicesTime.append(time.time() - tickTime)
        price = data['Close'].unique()[0]
        prices[ticker] = price

    # prices = {'GOOG': 1732.38, 'AMZN': 3185.27, 'MSFT': 221.02}

    endTime = time.time()

    response = {'time': {'start': startTime, 'end': endTime, 'externalServicesTime': externalServicesTime}, 'body': {'marketData':prices}}

    return json.dumps(response)

    return req
