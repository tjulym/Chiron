import json
import time

def factorial(n):
    result=1
    for i in range(1,n+1):
        result*=i
    return result

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    start = time.time()
    thread_start = time.thread_time()

    event = {}
    response = {"time": {"factorial": {"start_time": start, "thread_start_time": thread_start}}}
    count = 5000
    event = json.loads(req)

    factorial(count)

    response["body"] = event
    response["time"]["factorial"]["thread_end_time"] = time.thread_time()
    response["time"]["factorial"]["end_time"] = time.time()
    return json.dumps(response)
