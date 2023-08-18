import sys
import json
import subprocess

def get_pod_name(func_name):
    cmd = "docker ps | grep %s_%s- | awk '{print $NF}'" % (func_name, func_name)
    name = subprocess.check_output(cmd, shell=True).strip()
    return name

def get_mem_usage(pod_name):
    cmd = 'docker stats %s --no-stream --format "{{ json . }}"' % (func_name)
    result = subprocess.check_output(cmd, shell=True).strip()
    return json.loads(result)

def extract_mem(stats_json):
    mem_usage_str = stats_json["MemUsage"]
    return mem_usage_str.split("/")[0].strip()

if __name__ == '__main__':
    try:
        func_name = sys.argv[1]
    except Exception as e:
        raise e

    pod_name = get_pod_name(func_name)
    stats_json = get_mem_usage(pod_name)

    print(extract_mem(stats_json))