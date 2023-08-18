import json
import hashlib
import time

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    start = time.time()
    thread_start = time.thread_time()

    event = {}
    response = {"time": {"pbkdf2": {"start_time": start, "thread_start_time": thread_start}}}

    count = 10000
    event = json.loads(req)

    hashlib.pbkdf2_hmac('sha512', b'ServerlessAppPerfOpt', b'salt', count)

    response["body"] = event
    response["time"]["pbkdf2"]["thread_end_time"] = time.thread_time()
    response["time"]["pbkdf2"]["end_time"] = time.time()
    return json.dumps(response)
