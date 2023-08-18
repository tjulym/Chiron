import time
import json
import datetime
from function.util import *

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    event = json.loads(req)

    startTime = 1000*time.time()

    portfolio = event['body']['portfolio']
    portfolios = json.loads(open('/home/app/function/portfolios.json', 'r').read())
    data = portfolios[portfolio]

    valid = True

    for trade in data:
        trddate = trade['TradeDate']
        # Tag ID: 75, Tag Name: TradeDate, Format: YYMMDD
        if len(trddate) == 6:
            try:
                datetime.datetime(int(trddate[0:2]), int(trddate[2:4]), int(trddate[4:6]))
            except ValueError:
                valid = False
                break
        else:
            valid = False
            break

    response = {'statusCode': 200, 'body': {'valid':valid, 'portfolio': portfolio}}
    endTime = 1000*time.time()
    return json.dumps(timestamp(response, event, startTime, endTime, 0))
