import requests
import threading
import json
import time

funcs1 = ["network-io", "factorial", "disk-io", "fibonacci"]
funcs2 = ["network-io", "pi", "pbkdf2"]

def post(func_name, req, l, i):
    url = "http://127.0.0.1:31112/function/%s" % func_name
    r = requests.post(url, req).text
    l[i] = r

def workflow_OpenFaaS(data):
    start = time.time()

    parallel_res = [''] * 4
    threads = []
    
    for i, func_name in enumerate(funcs1):
        threads.append(threading.Thread(target=post, args=(func_name, data, parallel_res, i)))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    next_input = json.dumps(parallel_res)

    parallel_res2 = [''] * 3
    threads = []

    for i, func_name in enumerate(funcs2):
        threads.append(threading.Thread(target=post, args=(func_name, next_input, parallel_res2, i)))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    return int((time.time() - start) * 1000)
