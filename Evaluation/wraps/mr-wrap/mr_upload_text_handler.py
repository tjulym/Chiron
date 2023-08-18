from time import time
import json

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    start = time()

    event = json.loads(req)

    response = {"time": {"mr-upload-text": {"start_time": start}}}
    text = ''
    try:
        text = event["body"]["text"]
        response["time"].update(event["time"])
    except Exception as e:
        response["body"] = 'Incomplete arguments'

    if text:
        response["body"] = {"text": text}
    
    response["time"]["mr-upload-text"]["end_time"] = time()

    return json.dumps(response)
