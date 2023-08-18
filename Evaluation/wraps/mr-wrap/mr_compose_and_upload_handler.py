from time import time
import json

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    start = time()

    events = json.loads(req)
    events = [json.loads(event) for event in events]

    body = {}
    response = {"time": {"mr-compose-and-upload": {"start_time": start}}}

    if len(events) < 4:
        body = 'Incomplete arguments'
    else:
        try:
            for event in events:
                body.update(event["body"])
                response["time"].update(event["time"])
            body["timestamp"] = int(time()*1000)
        except Exception as e:
            body = 'Incomplete arguments'

    response["body"] = body
    response["time"]["mr-compose-and-upload"]["end_time"] = time()
    return json.dumps(response)
