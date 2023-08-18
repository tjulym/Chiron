import json
from time import time
import string
import random

def gen_random_digits(i):
    return "".join(random.sample(string.digits, i))


def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    start = time()

    event = json.loads(req)
    
    response = {"time": {"mr-upload-unique-id": {"start_time": start}}}
    
    machine_id = gen_random_digits(2)
    timestamp = str(int(time()*1000) - 1514764800000)[-11:]
    index_id = gen_random_digits(3)
    review_id = machine_id + timestamp + index_id

    response["body"] = {"review_id": review_id}
    response["time"]["mr-upload-unique-id"]["end_time"] = time()
    return json.dumps(response)
