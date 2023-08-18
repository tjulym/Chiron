import requests
import threading
import random
import string
import json
import time

GATEWAY = "http://127.0.0.1:31112/function/"

def generate_req(workflow_name):
    if workflow_name == "sn":
        return generate_req_sn()
    elif workflow_name == "mr":
        return generate_req_mr()
    elif workflow_name == "finra":
        return generate_req_finra()
    elif workflow_name == "SLApp":
        return generate_req_SLApp()

def invoke_workflow(workflow_name, func_name, req):
    if workflow_name == "sn":
        return invoke_sn(func_name, req)
    elif workflow_name == "mr":
        return invoke_mr(func_name, req)
    elif workflow_name == "finra":
        return invoke_finra(func_name, req)
    elif workflow_name == "SLApp":
        return invoke_SLApp(func_name, req)

def post(func_name, data, l):
    res = requests.post(f"{GATEWAY}{func_name}", data).text
    l.append(res)

def post_index(func_name, data, l, i):
    res = requests.post(f"{GATEWAY}{func_name}", data).text
    l[i] = res

def gen_random_string(i):
    choices = string.ascii_letters + string.digits
    return "".join([choices[random.randint(0, len(choices)-1)] for j in range(i)])

def generate_req_sn():
    user_index = random.randint(1, 1000)
    
    num_user_mentions = random.randint(1, 5)
    num_urls = random.randint(1, 5)
    num_media = random.randint(1, 4)
    text = ""
    
    user_mentions = []
    for i in range(num_user_mentions):
        while True:
            user_mention_id = random.randint(1, 1000)
            if user_mention_id != user_index and user_mention_id not in user_mentions:
                user_mentions.append(user_mention_id)
                break
    
    text += " ".join(["@username_"+str(i) for i in user_mentions])
    text += " "
    
    for i in range(num_urls):
        text += ("http://"+gen_random_string(64)+" ")
    
    media_ids = []
    media_types = ["png"] * num_media
    for i in range(num_media):
        media_ids.append(gen_random_string(5))
    
    data = {
        "username": "username_" + str(user_index),
        "user_id": user_index,
        "post_type": 0,
        "text": text,
        "media_ids": ",".join(media_ids),
        "media_types": ",".join(media_types)
    }

    return json.dumps(data)

def invoke_sn(target_func, req):
    compose_res = requests.post(GATEWAY+"compose-post", data=req).text
    
    parallel_res = []
    threads = []
    for func_name in ["upload-user-mentions", "upload-creator", "upload-media", "upload-text", "upload-unique-id"]:
        t = threading.Thread(target=post, args=(func_name, compose_res, parallel_res))
        threads.append(t)
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
    
    compose_and_upload_res = requests.post(GATEWAY+"compose-and-upload", data=json.dumps(parallel_res)).text
    
    parallel_res = []
    threads = []
    for func_name in ["post-storage", "upload-home-timeline", "upload-user-timeline"]:
        t = threading.Thread(target=post, args=(func_name, compose_and_upload_res, parallel_res))
        threads.append(t)
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()

    for res in parallel_res:
        res = json.loads(res)
        if target_func in res["time"]:
            return res["time"][target_func]["start_time"] * 1000, res["time"][target_func]["end_time"] * 1000

def generate_req_mr():
    movie_titles = []
    with open("movie_titles.csv", "r") as f:
        movie_titles = f.readlines()

    user_index = str(random.randint(1, 1000))
    review = {
        "username": "username_" + user_index,
        "password": "password_" + user_index,
        "title": movie_titles[random.randint(0, len(movie_titles)-1)].strip(),
        "rating": random.randint(0, 10),
        "text": gen_random_string(256) 
    }

    return json.dumps(review)

def invoke_mr(target_func, req):
    compose_res = requests.post(GATEWAY+"compose-review", data=req).text
    
    parallel_res = []
    threads = []
    for func_name in ["upload-user-id", "upload-movie-id", "mr-upload-text", "mr-upload-unique-id"]:
        t = threading.Thread(target=post, args=(func_name, compose_res, parallel_res))
        threads.append(t)
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
    
    compose_and_upload_res = requests.post(GATEWAY+"mr-compose-and-upload", data=json.dumps(parallel_res)).text
    
    parallel_res = []
    threads = []
    for func_name in ["store-review", "upload-user-review", "upload-movie-review"]:
        t = threading.Thread(target=post, args=(func_name, compose_and_upload_res, parallel_res))
        threads.append(t)
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()

    for res in parallel_res:
        res = json.loads(res)
        if target_func in res["time"]:
            return res["time"][target_func]["start_time"] * 1000, res["time"][target_func]["end_time"] * 1000

def generate_req_finra():
    return '{"body":{ "portfolioType":"S&P", "portfolio":"1234"}}'

def get_finra_times(res, events):
    duration = json.loads(res)["duration"]
    startTime = json.loads(res)["workflowStartTime"]
    endTime = json.loads(res)["workflowEndTime"]

    priorEndTime = 0

    for event in events:
        event_j = json.loads(event)
        if 'workflowEndTime' in event_j and event_j['workflowEndTime'] > priorEndTime:
            priorEndTime = event_j['workflowEndTime']

    prior = priorEndTime - startTime
    return endTime - (duration - prior), endTime

def invoke_finra(target_func, req):
    finra_funcs = ["marketdata", "lastpx", "side", "trddate", "volume"]
    
    parallel_res = [''] * 5
    threads = []
    
    for i, func_name in enumerate(finra_funcs):
        t = threading.Thread(target=post_index, args=(func_name, req, parallel_res, i))
        threads.append(t)
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
   
    res = requests.post(GATEWAY+"margin-balance", data=json.dumps(parallel_res)).text

    if target_func in finra_funcs:
        func_json = json.loads(parallel_res[finra_funcs.index(target_func)])
        if "duration" in func_json:
            return func_json["workflowStartTime"], func_json["workflowEndTime"]
        else:
            return func_json["time"]["start"] * 1000, func_json["time"]["end"] * 1000
    else:
        return get_finra_times(res, parallel_res)

def generate_req_SLApp():
    return '{"disk-io": 1, "factorial": 5000, "fibonacci": 23, "pbkdf2": 10000, "pi": 1000}'

def invoke_SLApp(target_func, req):
    parallel_res = []
    threads = []
    
    for func_name in ["factorial", "fibonacci", "pbkdf2", "pi", "disk-io", "network-io"]:
        t = threading.Thread(target=post, args=(func_name, req, parallel_res))
        threads.append(t)
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()

    for res in parallel_res:
        res = json.loads(res)
        if target_func in res["time"]:
            return res["time"][target_func]["start_time"] * 1000, res["time"][target_func]["end_time"] * 1000