import requests
import json
import sys

url = "http://127.0.0.1:20237/"

FUNC_EXEC_TIMES = {
    "compose-post": 0.121996,
    "upload-user-mentions": 9.765100,
    "upload-creator": 8.815116,
    "upload-media": 0.380701,
    "upload-text": 1.637130,
    "upload-unique-id": 0.651283,
    "compose-and-upload": 0.320979,
    "post-storage": 12.879182,
    "upload-home-timeline": 19.059915,
    "upload-user-timeline": 16.112567,

    "compose-review": 0.107390,
    "upload-user-id": 8.396033,
    "upload-movie-id": 8.539929,
    "mr-upload-text": 0.319250,
    "mr-upload-unique-id": 0.605604,
    "mr-compose-and-upload": 0.230004,
    "store-review": 12.117567,
    "upload-user-review": 14.946811,
    "upload-movie-review": 15.873351,
    
    "marketdata": 92,
    "lastpx": 0.735458,
    "side": 0.722307,
    "trddate": 0.772194,
    "volume": 0.730984,
    "margin-balance": 0.807867,
    "factorial": 10.017771,
    "disk-io": 17.706046,
    "fibonacci": 17.387075,
    "network-io": 29.186283,
    "pi": 16.154195,
    "pbkdf2": 15.793819,
}

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

def get_wrap_code(wraps, indexs, wrap_name):
    wraps["indexs"] = indexs

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

    workflow_fns = []
    indexs = []
    for stage_index, stage_shares in enumerate(wraps["wraps"]):
        # print(stage_index, stage_shares)
        stage_fns = []
        stage_indexs = []

        fns_info = []
        total_share = len(stage_shares)
        for share_index, share_fns in enumerate(stage_shares):
            for fn in share_fns:
                fns_info.append((task_fn_mp[fn], FUNC_EXEC_TIMES[task_fn_mp[fn]], (share_index + 1) % total_share))
            
        fns_info.sort(key=lambda x: x[1], reverse=True)

        for fn_info in fns_info:
            stage_fns.append(fn_info[0])
            stage_indexs.append(fn_info[2])

        workflow_fns.append(stage_fns)
        indexs.append(stage_indexs)

    wraps["wraps"] = workflow_fns
    
    get_wrap_code(wraps, indexs, f"{workflow_name}-wrap")