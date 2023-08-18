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

th_time = 10

TIME_FLAG = True

def timer():
    global TIME_FLAG
    time.sleep(th_time)
    TIME_FLAG = False

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