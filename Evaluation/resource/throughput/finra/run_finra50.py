import requests
import threading
import random
import string
import json
import time
import subprocess

from OpenFaaS import workflow_OpenFaaS

url = "http://127.0.0.1:31112/function/finra-wrap"
data = '{"body":{ "portfolioType":"S&P", "portfolio":"1234"}}'

methods = ["OpenFaaS", "SAND", "Faastlane", "Chiron", "Faastlane-P", "Chiron-P", "Faastlane-M", "Chiron-M"]
num_wraps = [0, 1, 1, 1, 1, 1, 1, 6]

CPUs =  [51,  50,  50,   6,  50,  11, 50,  6]

times = 10

th_time = 10

TIME_FLAG = True

def timer():
    global TIME_FLAG
    time.sleep(th_time)
    TIME_FLAG = False

def init(not_mpk=True):
    if not_mpk:
        cmd = "faas-cli deploy -f finra-wrap.yml"
    else:
        cmd = "faas-cli deploy -f finra-wrap-mpk-50.yml"
    subprocess.check_output(cmd, shell=True).strip()
    time.sleep(5)

def deploy(index):
    if index == 6:
        init(False)

    num_wrap = num_wraps[index]
    for i in range(1, num_wrap + 1):
        file_path = f"wraps/{methods[index]}-50-wrap{i}.py"
        if i == 1:
            cmd = "python3 ../../../deploy.py finra-wrap %s" % file_path
        else:
            cmd = "python3 ../../../deploy.py finra-wrap%d %s" % (i, file_path)
        subprocess.check_output(cmd, shell=True).strip()
    time.sleep(5)

def get_improvement(all_ths):
    expect_ths = [58.04, 59.2, 60.8, 1026.7, 132.8, 690.9, 52.8, 520.0]

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
                res = workflow_OpenFaaS(data, 10)
            count += 1

        timer_th.join()

        print("%s: %.2f reqs in 1s with %d CPUs" % (method, count * 1.0 / th_time, CPUs[index]))

        TIME_FLAG = True

        all_ths.append(count * 80.0 / CPUs[index])

    get_improvement(all_ths)

    init()

if __name__ == '__main__':
    get_ths()