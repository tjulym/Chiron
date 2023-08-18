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

times = 10

def init(not_mpk=True):
    if not_mpk:
        cmd = "faas-cli deploy -f finra-wrap.yml"
    else:
        cmd = "faas-cli deploy -f finra-wrap-mpk.yml"
    subprocess.check_output(cmd, shell=True).strip()
    time.sleep(5)

def deploy(index):
    file_path = f"wraps/{methods[index]}.py"

    if index == 6:
        init(False)

    cmd = "python3 ../../deploy.py finra-wrap %s" % file_path
    subprocess.check_output(cmd, shell=True).strip()
    time.sleep(5)

def get_improvement(all_lats):
    expect_lats = [107, 119, 109,  90, 86, 85, 133, 133]

    print("===improvement===")

    for index, method in enumerate(methods):
        if index == 3 or index == 5 or index == 7:
            continue
        if index < 4:
            expect_improvement = 1 - expect_lats[3]/expect_lats[index]
            actual_improvement = 1 - all_lats[3]/all_lats[index]
        elif index == 4:
            expect_improvement = 1 - expect_lats[5]/expect_lats[index]
            actual_improvement = 1 - all_lats[5]/all_lats[index]
        elif index == 6:
            expect_improvement = 1 - expect_lats[7]/expect_lats[index]
            actual_improvement = 1 - all_lats[7]/all_lats[index]

        print("%s: expect %.2f%%, actual %.2f%%" % (method, (expect_improvement*100), (actual_improvement*100)))

def get_lats():
    init()

    all_lats = []

    for index, method in enumerate(methods):
        lats = []
        if index > 0:
            deploy(index)
            for i in range(times+1):
                res = requests.post(url, data=data).text
                res_j = json.loads(res)
                lats.append((res_j["time"]["workflow"]["end"] - res_j["time"]["workflow"]["start"])*1000)
        else:
            for i in range(times+1):
                lats.append(workflow_OpenFaaS(data, 1))

        avg_lat = sum(lats[1:])/(len(lats)-1)
        print("%s: %f" % (method, avg_lat))
        all_lats.append(avg_lat)

    get_improvement(all_lats)

    init()

if __name__ == '__main__':
    get_lats()