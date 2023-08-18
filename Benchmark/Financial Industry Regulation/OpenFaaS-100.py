import requests
import threading

import json
import time

margin_balance_url = "http://127.0.0.1:31112/function/margin-balance"

funcs = ["marketdata", "lastpx", "side", "trddate", "volume"] * 20

for i in range(1, 20):
    for j in range(5):
        funcs[i * 5 + j] = "%s%d" % (funcs[i * 5 + j], i + 1)

urls = [f"http://127.0.0.1:31112/function/{func}" for func in funcs]

req = '{"body":{ "portfolioType":"S&P", "portfolio":"1234"}}'

def post(url, data, l, i):
    res = requests.post(url, data).text
    l[i] = res

def get_times(res, events):
    duration = json.loads(res)["duration"]
    startTime = json.loads(res)["workflowStartTime"]

    priorEndTime = 0

    for event in events:
        event_j = json.loads(event)
        if 'workflowEndTime' in event_j and event_j['workflowEndTime'] > priorEndTime:
            priorEndTime = event_j['workflowEndTime']

    prior = priorEndTime - startTime
    return duration - prior


def workflow():
    start = time.time()
    
    parallel_res = [''] * 100
    threads = []
    
    for i, url in enumerate(urls):
        t = threading.Thread(target=post, args=(url, req, parallel_res, i))
        threads.append(t)
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
   
    res = requests.post(margin_balance_url, data=json.dumps(parallel_res)).text
   
    # return int((time.time()-start)*1000) 
    print("This request uses %d ms" % int((time.time() - start) * 1000))
    try:
        for i, temp_res in enumerate(parallel_res):
            temp_json = json.loads(temp_res)
            if "duration" in temp_json:
                print("  %s: %f ms" % (funcs[i], temp_json["duration"]))
            else:
                print("  %s: %f ms" % (funcs[i], (temp_json["time"]["end"] - temp_json["time"]["start"]) * 1000))
        print("  margin-balance: %f ms" % get_times(res, parallel_res))
    except Exception as e:
        raise e

if __name__ == '__main__':
    workflow()
