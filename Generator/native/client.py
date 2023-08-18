import requests
import json
import sys

url = "http://127.0.0.1:20234/"

def get_task_fn_mp(workflow_name):
    workflow = json.loads(open("workflows/%s.json" % (workflow_name)).read())
    stateName = workflow["StartAt"]
    state = workflow["States"][stateName]
    over = False

    task_fn_mp = {}

    while not over:
        if state["Type"] == "Task":
            task_fn_mp[stateName] = state["Resource"]
        elif state["Type"] == "Parallel":
            for branch in state["Branches"]:
                task_fn_mp[branch["StartAt"]] = branch["States"][branch["StartAt"]]["Resource"]
        if "End" in state:
            over = True
        else:
            stateName = state["Next"]
            state = workflow["States"][stateName]

    return task_fn_mp

def get_wrap_code(wraps, wrap_index, num_wraps, wrap_name):
    wraps["wrap_index"] = wrap_index
    wraps["num_wraps"] = num_wraps

    wrap_code = requests.post(url, json.dumps(wraps)).text

    with open(f"wraps/{wrap_name}.py", "w") as f:
        f.writelines(wrap_code)

if __name__ == '__main__':
    try:
        wraps = json.loads(sys.argv[1])
    except Exception as e:
        raise e

    workflow_name = wraps["workflow"]
    task_fn_mp = get_task_fn_mp(workflow_name)

    wrap_indexs = ["0,0"]
    for stage_index, stage_wraps in enumerate(wraps["wraps"]):
        # print(stage_index, stage_wraps)
        for stage_wrap_index, stage_wrap in enumerate(stage_wraps):
            if stage_wrap_index > 0:
                wrap_indexs.append(f"{stage_index},{stage_wrap_index}")
            # print(stage_index, stage_wrap_index, stage_wrap)
            for process_index, process_fns in enumerate(stage_wrap):
                # print(stage_index, stage_wrap_index, process_index, process_fns)
                for thread_index, thread_fn in enumerate(process_fns):
                    wraps["wraps"][stage_index][stage_wrap_index][process_index][thread_index] = task_fn_mp[thread_fn]

    num_wraps = max([len(stage_wraps) for stage_wraps in wraps["wraps"]])

    get_wrap_code(wraps, wrap_indexs[0], num_wraps, f"{workflow_name}-wrap")
    for index, wrap_index in enumerate(wrap_indexs[1:]):
        get_wrap_code(wraps, wrap_index, num_wraps, f"{workflow_name}-wrap{index+2}")