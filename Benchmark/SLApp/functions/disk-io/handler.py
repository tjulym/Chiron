import json
import os
from time import time

path = '/tmp/1MB'

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    start = time()

    event = {}
    response = {"time": {"disk-io": {"start_time": start}}}
    count = 1
    try:
        event = json.loads(req)
        count = event["disk-io"]
    except Exception as e:
        pass

    file_indicator = os.path.isfile(path)
    if file_indicator:
        os.remove(path)
    for i in range(count):
        f = open(path, 'wb')
        f.write(os.urandom(1048576))
        f.flush() 
        os.fsync(f.fileno()) 
        f.close()

    response["body"] = event
    response["time"]["disk-io"]["end_time"] = time()
    return json.dumps(response)
