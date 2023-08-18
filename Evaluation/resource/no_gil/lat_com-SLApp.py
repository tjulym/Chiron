import requests
import threading
import json
import time
import subprocess

url = "http://127.0.0.1:31112/function/slapp-java"

data = '{"disk-io": 1, "factorial": 5000, "fibonacci": 23, "pbkdf2": 10000, "pi": 1000}'

methods = ["One-to-One", "Many-to-One", "Chiron"]

CPUs = [7, 4, 3]

times = 10

funcs1 = ["network-io", "factorial", "disk-io", "fibonacci"]
funcs2 = ["network-io", "pi", "pbkdf2"]

def post(func_name, req, l, i):
    local_url = "http://127.0.0.1:31112/function/%s-java" % func_name
    r = requests.post(local_url, req).text
    l[i] = r

def bind_cores(num_CPUs):
    cmd = "docker update `docker ps | grep slapp-java_slapp-java | awk '{print $1}'` --cpuset-cpus=0-%d" % (num_CPUs - 1)
    subprocess.check_output(cmd, shell=True)

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