import requests
import threading
import json
import time

funcs1 = ["factorial", "fibonacci"]
funcs2 = ["network-io", "pi", "pbkdf2", "pi2", "fibonacci"]

def post(func_name, req, l, i):
    url = "http://127.0.0.1:31112/function/%s" % func_name
    r = requests.post(url, req).text
    l[i] = r

def workflow_OpenFaaS(data):
    start = time.time()

    disk_io_res = requests.post("http://127.0.0.1:31112/function/disk-io", data).text

    parallel_res = [''] * 2
    threads = []
    
    for i, func_name in enumerate(funcs1):
        threads.append(threading.Thread(target=post, args=(func_name, disk_io_res, parallel_res, i)))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    parallel_res2 = [''] * 5
    threads = []

    for i, func_name in enumerate(funcs2):
        threads.append(threading.Thread(target=post, args=(func_name, json.dumps(parallel_res), parallel_res2, i)))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    factorial_res = requests.post("http://127.0.0.1:31112/function/factorial", json.dumps(parallel_res)).text

    fibonacci_res = requests.post("http://127.0.0.1:31112/function/fibonacci", factorial_res).text

    return int((time.time() - start) * 1000)
