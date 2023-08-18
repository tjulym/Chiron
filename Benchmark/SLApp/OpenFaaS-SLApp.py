import threading
import requests
import time
import json

data = '{"disk-io": 1, "factorial": 5000, "fibonacci": 23, "pbkdf2": 10000, "pi": 1000}'

funcs1 = ["network-io", "factorial", "disk-io", "fibonacci"]
funcs2 = ["network-io", "pi", "pbkdf2"]

def post(func_name, req, l, i):
    url = "http://127.0.0.1:31112/function/%s" % func_name
    r = requests.post(url, req).text
    l[i] = r

def get_duration(res, func_name):
    event = json.loads(res)
    return (event["time"][func_name]["end_time"] - event["time"][func_name]["start_time"]) * 1000

def workflow():
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

    # return int((time.time()-start)*1000)
    print("This request uses %d ms" % int((time.time() - start) * 1000))
    try:
        print("Stage 1")
        for res, func_name in zip(parallel_res, funcs1):
            print("  %s: %f ms" % (func_name, get_duration(res, func_name)))
        print("Stage 2")
        for res, func_name in zip(parallel_res2, funcs2):
            print("  %s: %f ms" % (func_name, get_duration(res, func_name)))
    except Exception as e:
        raise e

if __name__ == '__main__':
    workflow()