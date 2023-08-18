import json
import time
import re
import string
import random

HOSTNAME = "http://short-url/"

def gen_random_string(i):
    return "".join(random.sample(string.ascii_letters + string.digits, i))

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    start = time.time()

    event = json.loads(req)

    response = {"time": {"upload-text": {"start_time": start}}}
    
    text = event["body"]["text"]
    
    urls_pattern = re.compile(r"(http://|https://)([a-zA-Z0-9_!~*'().&=+$%/-]+)")
    urls_match = urls_pattern.findall(text)
    urls = []
    for m in urls_match:
        url = m[0] + m[1]
        shortened_url = HOSTNAME + gen_random_string(10)
        urls.append({"shortened_url": shortened_url, "expanded_url": url})
        text = text.replace(url, shortened_url)

    response["body"] = {"text": text, "urls": urls}
    response["time"].update(event["time"])

    response["time"]["upload-text"]["end_time"] = time.time()

    return json.dumps(response)
