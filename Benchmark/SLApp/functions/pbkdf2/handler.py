import json
import hashlib
from time import time

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    start = time()

    event = {}
    response = {"time": {"pbkdf2": {"start_time": start}}}
    count = 10000
    try:
        event = json.loads(req)
        count = event["pbkdf2"]
    except Exception as e:
        pass

    hashlib.pbkdf2_hmac('sha512', b'ServerlessAppPerfOpt', b'salt', count)

    response["body"] = event
    response["time"]["pbkdf2"]["end_time"] = time()
    return json.dumps(response)
