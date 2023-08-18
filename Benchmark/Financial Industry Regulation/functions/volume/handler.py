import time
import json
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
        qty = str(trade['LastQty'])
        # Tag ID: 32, Tag Name: LastQty, Format: max 8 characters, no decimal
        if (len(qty)>8) or ('.'in qty):
            valid = False
            break

    response = {'statusCode': 200, 'body': {'valid':valid, 'portfolio': portfolio}}
    endTime = 1000*time.time()
    return json.dumps(timestamp(response, event, startTime, endTime, 0))
