import json
import time
import string
import random

def gen_random_digits(i):
    return "".join(random.sample(string.digits, i))

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    start = time.time()

    event = json.loads(req)
   
    response = {"time": {"upload-unique-id": {"start_time": start}}}
 
    post_type = str(event["body"]["post_type"])
    
    machine_id = gen_random_digits(2)
    timestamp = str(int(time.time()*1000) - 1514764800000)[-11:]
    index_id = gen_random_digits(3)
    post_id = machine_id + timestamp + index_id

    response["body"] = {"post_id": post_id}
    response["time"].update(event["time"])
    
    response["time"]["upload-unique-id"]["end_time"] = time.time()

    return json.dumps(response)
