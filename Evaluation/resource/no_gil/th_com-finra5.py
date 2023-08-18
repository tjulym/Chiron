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

th_time = 10

TIME_FLAG = True

def timer():
    global TIME_FLAG
    time.sleep(th_time)
    TIME_FLAG = False

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

def get_ths():
    global TIME_FLAG

    for index, method in enumerate(methods):
        lats = []
        if index > 0:
            bind_cores(CPUs[index])

        count = 0
        timer_th = threading.Thread(target=timer)
        timer_th.start()

        while TIME_FLAG:
            if index > 0:
                res = requests.post(url, data=data).text
            else:
                res = workflow()

            count += 1

        timer_th.join()

        print("%s: %.2f reqs in 1s with %d CPUs" % (method, count * 1.0 / th_time, CPUs[index]))

        TIME_FLAG = True

if __name__ == '__main__':
    get_ths()