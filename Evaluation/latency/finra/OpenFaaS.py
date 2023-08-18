import requests
import threading
import json
import time

margin_balance_url = "http://127.0.0.1:31112/function/margin-balance"

funcs = ["marketdata", "lastpx", "side", "trddate", "volume"]

urls = [f"http://127.0.0.1:31112/function/{func}" for func in funcs]

def post(url, data, l, i):
    res = requests.post(url, data).text
    l[i] = res

def workflow_OpenFaaS(data, times=1):
    current_urls = urls * times
    parallel_res = [""] * len(current_urls)

    start = time.time()

    threads = []
    
    for i, url in enumerate(current_urls):
        t = threading.Thread(target=post, args=(url, data, parallel_res, i))
        threads.append(t)
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
   
    res = requests.post(margin_balance_url, data=json.dumps(parallel_res)).text

    return int((time.time() - start) * 1000)
