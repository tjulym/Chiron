import json
from predictor import predict

def get_workflow_info(workflow_name):
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


def get_workflow_lats(workflow_name):
    with open("data/%s_workflow_times.csv" % workflow_name, "r") as f:
        lines = f.readlines()

    res = [line.split("\t") for line in lines]
    return res

def eval_workflow(workflow_name):
    task_fn_mp = get_workflow_info(workflow_name)

    data = get_workflow_lats(workflow_name)
    diffs = []
    for policy_data in data:
        policy = json.loads(policy_data[0])
        partitions = []
        for v in policy.values():
            partitions.append(v[0])
        lat = float(policy_data[1])
        pred = predict(partitions, task_fn_mp)

        diffs.append((pred-lat)*100/lat)

    diffs_str = [str(i/100)+"\n" for i in diffs]
    with open("loss/loss_%s.csv" % workflow_name, "w") as f:
        f.writelines(diffs_str)
    
if __name__ == '__main__':
    workflows = ["sn", "mr", "finra5", "SLApp", "SLApp-V"]
    for workflow in workflows:
        eval_workflow(workflow)
