import requests
import threading
import random
import string
import json
import time
import subprocess

from OpenFaaS import workflow_OpenFaaS

url = "http://127.0.0.1:31112/function/slapp-v-wrap"
data = '{"disk-io": 1, "factorial": 5000, "fibonacci": 23, "pbkdf2": 10000, "pi": 1000}'

methods = ["OpenFaaS", "SAND", "Faastlane", "Chiron", "Faastlane-P", "Chiron-P", "Faastlane-M", "Chiron-M"]
CPUs =     [10,  5,   5,   3,  5,  4, 5,   3]

times = 10

th_time = 10

TIME_FLAG = True

def timer():
    global TIME_FLAG
    time.sleep(th_time)
    TIME_FLAG = False

def init(not_mpk=True):
    if not_mpk:
        cmd = "faas-cli deploy -f slapp-v-wrap.yml"
    else:
        cmd = "faas-cli deploy -f slapp-v-wrap-mpk.yml"
    subprocess.check_output(cmd, shell=True).strip()
    time.sleep(5)

def deploy(index):
    file_path = f"wraps/{methods[index]}.py"

    if index == 6:
        init(False)

    cmd = "python3 ../../../deploy.py slapp-v-wrap %s" % file_path
    subprocess.check_output(cmd, shell=True).strip()
    time.sleep(5)

def get_improvement(all_ths):
    expect_ths = [384.0, 1152.0, 1280.0, 2106.7, 1680.0, 2100.0, 704.0, 1120.0]

    print("===improvement===")

    for index, method in enumerate(methods):
        if index == 3 or index == 5 or index == 7:
            continue
        if index < 4:
            expect_improvement = expect_ths[3]/expect_ths[index] - 1
            actual_improvement = all_ths[3]/all_ths[index]  - 1
        elif index == 4:
            expect_improvement = expect_ths[5]/expect_ths[index] - 1
            actual_improvement = all_ths[5]/all_ths[index] - 1
        elif index == 6:
            expect_improvement = expect_ths[7]/expect_ths[index] - 1
            actual_improvement = all_ths[7]/all_ths[index] - 1

        print("%s: expect %.2f%%, actual %.2f%%" % (method, (expect_improvement*100), (actual_improvement*100)))

def get_ths():
    global TIME_FLAG
    init()

    all_ths = []

    for index, method in enumerate(methods):
        if index > 0:
            deploy(index)

        count = 0
        timer_th = threading.Thread(target=timer)
        timer_th.start()

        while TIME_FLAG:
            if index > 0:
                res = requests.post(url, data=data).text
            else:
                res = workflow_OpenFaaS(data)
            count += 1

        timer_th.join()

        print("%s: %.2f reqs in 1s with %d CPUs" % (method, count * 1.0 / th_time, CPUs[index]))

        TIME_FLAG = True

        all_ths.append(count * 80.0 / CPUs[index])

    get_improvement(all_ths)

    init()

if __name__ == '__main__':
    get_ths()