import json
import itertools
import copy
from predictor import predict, get_sorted_fs, get_threads_lat, FUNC_EXEC_TIMES

NUM_PROCESS_WRAP1 = 6
RPC_OVERHEAD = 20
REMOTE_OVERHEAD = 4

def get_workflow_info(workflow_name):
    workflow = json.loads(open("workflows/%s.json" % (workflow_name)).read())
    stateName = workflow["StartAt"]
    state = workflow["States"][stateName]
    over = False

    stages = []
    task_fn_mp = {}

    while not over:
        if state["Type"] == "Task":
            stages.append([stateName])
            task_fn_mp[stateName] = state["Resource"]
        elif state["Type"] == "Parallel":
            branches = []
            for branch in state["Branches"]:
                branches.append(branch["StartAt"])
                task_fn_mp[branch["StartAt"]] = branch["States"][branch["StartAt"]]["Resource"]
            stages.append(branches)
        if "End" in state:
            over = True
        else:
            stateName = state["Next"]
            state = workflow["States"][stateName]

    return stages, task_fn_mp

def get_init_partition(stages, num_partitions=1):
    partitions = []
    for stage in stages:
        if len(stage) == 1 or num_partitions == 1:
            partitions.append([stage])
        elif len(stage) < num_partitions:
            partitions.append([[f] for f in stage])
        else:
            stage_partitions = []
            for i in range(num_partitions):
                stage_partitions.append([])
            for i, f in enumerate(stage):
                stage_partitions[i%num_partitions].append(f)
            partitions.append(stage_partitions)
    return partitions


def get_latency_from_partitions(partitions, task_fn_mp, isWrap1=False):
    for i in range(len(partitions[0])):
        partitions[0][i] = get_sorted_fs(partitions[0][i], task_fn_mp)

    latency = predict(partitions, task_fn_mp, isWrap1)
    return latency

def KL_swap(partitions, task_fn_mp, combination):
    local_partitions = partitions.copy()
    index1 = combination[0]
    index2 = combination[1]

    best_latency = get_latency_from_partitions(local_partitions, task_fn_mp, isWrap1=True)

    # print("swap partition (%d, %d): %f" % (index1, index2, best_latency))
    # print(local_partitions)

    while True:
        partition1 = set(local_partitions[0][index1])
        partition2 = set(local_partitions[0][index2])

        available_indexs1 = partition1.copy()
        available_indexs2 = partition2.copy()

        moves1, moves2 = [], []
        predictions = []

        temp_partitions = copy.deepcopy(local_partitions)

        while len(available_indexs1) > 0 or len(available_indexs2) > 0:
            # print(local_partitions)
            if len(available_indexs1) > 0 and len(available_indexs2) > 0:
                products = itertools.product(available_indexs1, available_indexs2)
            elif len(available_indexs1) > 0:
                products = [(f, None) for f in available_indexs1]
            else:
                products = [(None, f) for f in available_indexs2]

            temp_latency = get_latency_from_partitions(temp_partitions, task_fn_mp, isWrap1=True)

            best_gain = None
            best_swap = None
            for product in products:
                current_partitions = copy.deepcopy(temp_partitions)
                current_partition1 = partition1.copy()
                current_partition2 = partition2.copy()

                if len(available_indexs1) > 0:
                    current_partition1.remove(product[0])
                    current_partition2.add(product[0])
                if len(available_indexs2) > 0:  
                    current_partition2.remove(product[1])
                    current_partition1.add(product[1])

                current_partitions[0][index1] = list(current_partition1)
                current_partitions[0][index2] = list(current_partition2)

                latency = get_latency_from_partitions(current_partitions, task_fn_mp, isWrap1=True)
                current_gain = temp_latency - latency

                if best_gain is None or current_gain > best_gain:
                    best_gain = current_gain
                    best_swap = (product[0], product[1])

            moves1.append(best_swap[0])
            moves2.append(best_swap[1])

            if best_swap[0] is not None:
                available_indexs1.remove(best_swap[0])
                partition1.remove(best_swap[0])
                partition2.add(best_swap[0])
            if best_swap[1] is not None:
                available_indexs2.remove(best_swap[1])
                partition2.remove(best_swap[1])
                partition1.add(best_swap[1])

            temp_partitions[0][index1] = list(partition1)
            temp_partitions[0][index2] = list(partition2)
                
            predictions.append(temp_latency - best_gain)

        best_prediction = min(predictions)

        if best_prediction < best_latency:
            # print("down to %f" % best_prediction)
            best_latency = best_prediction
            best_prediction_index = predictions.index(best_prediction)
            local_partition1 = set(local_partitions[0][index1])
            local_partition2 = set(local_partitions[0][index2])

            for i in range(best_prediction_index+1):
                if moves1[i] is not None:
                    local_partition1.remove(moves1[i])
                    local_partition2.add(moves1[i])
                if moves2[i] is not None:
                    local_partition2.remove(moves2[i])
                    local_partition1.add(moves2[i])

                local_partitions[0][index1] = list(local_partition1)
                local_partitions[0][index2] = list(local_partition2)
        else:
            break

    partitions[0][index1] = local_partitions[0][index1].copy()
    partitions[0][index2] = local_partitions[0][index2].copy()

    return best_latency


def KL_graph_partition(fs, task_fn_mp, num_partitions=2, partitions=None):
    full = True
    if partitions is None:
        partitions = get_init_partition([fs], num_partitions)
        full = False
    combinations = itertools.combinations(range(num_partitions), 2)

    best_latency = None

    # print("Before KL-%d:" % num_partitions, partitions)
    for com in combinations:
        KL_swap(partitions, task_fn_mp, com)
    # print("After KL-%d:" % num_partitions, partitions)

    best_latency = get_latency_from_partitions(partitions, task_fn_mp, isWrap1=True)

    return partitions[0], best_latency

def schedule(req):
    try:
        event = json.loads(req)
        workflow_name = event["workflow"]
        SLO = event["SLO"]
    except Exception as e:
        raise e

    stages, task_fn_mp = get_workflow_info(workflow_name)

    partitions = get_init_partition(stages, num_partitions=1)

    best_partitions = {}
    for index, stage_partition in enumerate(partitions):
        if len(stage_partition[0]) > 1:
            stage_latency = get_latency_from_partitions([stage_partition], task_fn_mp)
            best_partitions[str(index)] = (stage_partition, stage_latency)

    max_parallelism = max([len(stage) for stage in stages])

    latency = predict(partitions, task_fn_mp)
    # print("multi-thread:", latency)

    if latency < SLO:
        print("Best solution is multi-thread: %.2f" % latency)
        return json.dumps({"workflow": workflow_name, "wraps": partitions})
    # print("------------------")

    # for num_partitions in range(2, max_parallelism+1):
    for num_partitions in range(NUM_PROCESS_WRAP1, max_parallelism+1):
        partitions = []
        latency = 0
        stage_latencys = []
        for index, stage in enumerate(stages):
            if len(stage) == 1:
                partitions.append([stage])
                
                stage_latencys.append(FUNC_EXEC_TIMES[task_fn_mp[stage[0]]])
                latency += stage_latencys[-1]
            else:

                best_stage_partitions, best_stage_latency =\
                    KL_graph_partition(stage, task_fn_mp, min(num_partitions, len(stage)))

                if best_stage_latency < best_partitions[str(index)][1]:
                    partitions.append(best_stage_partitions)
                    best_partitions[str(index)] = (best_stage_partitions, best_stage_latency)
                else:
                    partitions.append(best_partitions[str(index)][0])

                stage_latencys.append(best_stage_latency)
                latency += best_stage_latency

        if latency < SLO:
            print("Best solution in %d-process (wraps): %.2f" % (num_partitions, latency))
            return json.dumps({"workflow": workflow_name, "wraps": partitions})

if __name__ == '__main__':
    print(schedule('{"workflow": "finra50", "SLO": 348}'))
    # print(schedule('{"workflow": "finra100", "SLO": 383}'))
    # print(schedule('{"workflow": "finra200", "SLO": 532}'))
