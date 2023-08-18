import threading
import requests
import time
import json

data = '{"disk-io": 1, "factorial": 5000, "fibonacci": 23, "pbkdf2": 10000, "pi": 1000}'

funcs1 = ["factorial", "fibonacci"]
funcs2 = ["network-io", "pi", "pbkdf2", "pi2", "fibonacci"]

def post(func_name, req, l, i):
    url = "http://127.0.0.1:31112/function/%s" % func_name
    r = requests.post(url, req).text
    l[i] = r

def get_duration(res, func_name):
    event = json.loads(res)
    return (event["time"][func_name]["end_time"] - event["time"][func_name]["start_time"]) * 1000

def workflow():
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

    # return int((time.time()-start)*1000)
    print("This request uses %d ms" % int((time.time() - start)*1000))

    try:
        print("Stage 1")
        print("  %s: %f ms" % ("disk-io", get_duration(disk_io_res, "disk-io")))
        print("Stage 2")
        for res, func_name in zip(parallel_res, funcs1):
            print("  %s: %f ms" % (func_name, get_duration(res, func_name)))
        print("Stage 3")
        funcs2[3] = "pi"
        for res, func_name in zip(parallel_res2, funcs2):
            print("  %s: %f ms" % (func_name, get_duration(res, func_name)))
        print("Stage 4")
        print("  %s: %f ms" % ("factorial", get_duration(factorial_res, "factorial")))
        print("Stage 5")
        print("  %s: %f ms" % ("fibonacci", get_duration(fibonacci_res, "fibonacci")))
    except Exception as e:
        raise e

if __name__ == '__main__':
    workflow()
