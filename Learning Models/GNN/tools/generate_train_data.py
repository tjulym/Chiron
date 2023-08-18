import json
import itertools
import copy

workflow_names = ["mr", "sn", "finra", "SLApp", "SLAppV"]

def get_data(workflow_name):
    with open("../lats/lats_no_%s.csv" % (workflow_name), "r") as f:
        lines = f.readlines()

    return lines

workflow_infos = {}
workflow_stages = {}

def get_workflow_stru(workflow):
    stateName = workflow["StartAt"]
    state = workflow["States"][stateName]
    over = False
    # stages = {}
    stages = []
    index_stages = []
    resources = {}
    indexs = {}
    while not over:
        index_stages.append(stateName)
        if state["Type"] == "Task":
            # stages[stateName] = stateName
            resources[stateName] = state["Resource"]
            current_num_nodes = len(indexs)
            indexs[stateName] = current_num_nodes
            stages.append((len(index_stages)-1, 1))
        elif state["Type"] == "Parallel":
            stages.append((len(index_stages)-1, len(state["Branches"])))
            for branch in state["Branches"]:
                # stages[branch["StartAt"]] = stateName
                resources[branch["StartAt"]] = branch["States"][branch["StartAt"]]["Resource"]
                current_num_nodes = len(indexs)
                indexs[branch["StartAt"]] = current_num_nodes
        if "End" in state:
            over = True
        else:
            stateName = state["Next"]
            state = workflow["States"][stateName]

    stages.sort(key=lambda x: x[1], reverse=True)

    return indexs, resources, stages, index_stages

for workflow_name in workflow_names:
    workflow2 = json.loads(open("../workflows/%s.json" % (workflow_name)).read())
    indexs, resources, stages, index_stages = get_workflow_stru(workflow2)

    workflow_infos[workflow_name] = {
        "indexs": copy.deepcopy(indexs),
        "resources": copy.deepcopy(resources),
        "index_stages": copy.deepcopy(index_stages)
    }
    workflow_stages[workflow_name] = copy.deepcopy(stages)

print(workflow_stages)

for target_workflow_name in workflow_names:
    lines = get_data(target_workflow_name)

    res = []

    for l in lines:
        [policy, workflow_name, latency] = l.split("\t")

        #if workflow_name == "finra":
        #    continue

        info = workflow_infos[workflow_name]
        resources = info["resources"]
        stages = workflow_stages[workflow_name]
        index_stages = info["index_stages"]

        num_stages = 5
        for i in range(num_stages-len(index_stages)+1):
            temp_map = {}
            for index, stage_info in enumerate(stages):
                temp_map[stage_info[0]] = index + i

            # print(temp_map)

            res.append("\t".join([policy, workflow_name, json.dumps(temp_map), latency]))

    with open("../lats/lats_no_%s_stru.csv" % (target_workflow_name), "w") as f:
        f.writelines(res)

    print(len(res))
