import requests
import threading
import json
import time
import subprocess

url = "http://127.0.0.1:31112/function/finra5-java"

data = '{"body":{ "portfolioType":"S&P", "portfolio":"1234"}}'

methods = ["One-to-One", "Many-to-One", "Chiron"]

CPUs = [6, 5, 1]

times = 10

margin_balance_url = "http://127.0.0.1:31112/function/margin-balance-java"

funcs = ["marketdata", "lastpx", "side", "trddate", "volume"]

def post(func_name, req, l, i):
    local_url = "http://127.0.0.1:31112/function/%s-java" % func_name
    r = requests.post(local_url, req).text
    l[i] = r

def bind_cores(num_CPUs):
    cmd = "docker update `docker ps | grep slapp-java_slapp-java | awk '{print $1}'` --cpuset-cpus=0-%d" % (num_CPUs - 1)
    subprocess.check_output(cmd, shell=True)

def workflow():
    start = time.time()

    threads = []
    parallel_res = [''] * 5
    
    for i, func_name in enumerate(funcs):
        t = threading.Thread(target=post, args=(func_name, data, parallel_res, i))
        threads.append(t)
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
   
    res = requests.post(margin_balance_url, data=json.dumps(parallel_res)).text

    return int((time.time() - start) * 1000)

def get_lats():
    for index, method in enumerate(methods):
        lats = []
        if index > 0:
            bind_cores(CPUs[index])
            for i in range(times+1):
                res = requests.post(url, data=data).text
                res_j = json.loads(res)
                lats.append((res_j["end"] - res_j["start"])*1000)
        else:
            for i in range(times+1):
                lats.append(workflow())

        print("%s: %f" % (method, sum(lats[1:])/(len(lats)-1)))

if __name__ == '__main__':
    get_lats()