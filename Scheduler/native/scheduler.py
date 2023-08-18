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

def get_best_latency_from_partitions(partitions, task_fn_mp):
    for i in range(len(partitions[0])):
        partitions[0][i] = get_sorted_fs(partitions[0][i], task_fn_mp)
    latency = get_latency_from_partitions([partitions[0][:NUM_PROCESS_WRAP1]], task_fn_mp, isWrap1=True)
    num_partitions = len(partitions[0])
    if num_partitions > NUM_PROCESS_WRAP1:
        for i in range(NUM_PROCESS_WRAP1, num_partitions):
            latency = max(latency, get_latency_from_partitions([partitions[0][i:i+1]], task_fn_mp) + RPC_OVERHEAD)
    return latency

def KL_swap(partitions, task_fn_mp, combination):
    local_partitions = partitions.copy()
    index1 = combination[0]
    index2 = combination[1]

    best_latency = get_latency_from_partitions(local_partitions, task_fn_mp, isWrap1=True)

    # print("swap partition (%d, %d): %f" % (index1, index2, best_latency))

    while True:
        partition1 = set(local_partitions[0][index1])
        partition2 = set(local_partitions[0][index2])

        available_indexs1 = partition1.copy()
        available_indexs2 = partition2.copy()

        moves1, moves2 = [], []
        predictions = []

        temp_partitions = copy.deepcopy(local_partitions)

        while len(available_indexs1) > 0 or len(available_indexs2) > 0:
            if len(available_indexs1) > 0 and len(available_indexs2) > 0:
                products = itertools.product(available_indexs1, available_indexs2)
            elif len(available_indexs1) > 0:
                products = [(f, None) for f in available_indexs1]
            else:
                products = [(None, f) for f in available_indexs2]

            temp_latency = get_best_latency_from_partitions(temp_partitions, task_fn_mp)

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

                latency = get_best_latency_from_partitions(current_partitions, task_fn_mp)
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

    best_latency = get_latency_from_partitions([partitions[0][:NUM_PROCESS_WRAP1]], task_fn_mp, isWrap1=True)
    if num_partitions > NUM_PROCESS_WRAP1:
        for i in range(NUM_PROCESS_WRAP1, num_partitions):
            best_latency = max(best_latency, get_latency_from_partitions([partitions[0][i:i+1]], task_fn_mp) + RPC_OVERHEAD)
    return partitions[0], best_latency

def split_wraps(partitions, stage_latencys, task_fn_mp, slack):
    overall_latency = 0
    split_indexs = []
    for stage_index, stage_partition in enumerate(partitions):
        # print("================Stage %d==================" % stage_index)

        wraps = [stage_partition[:NUM_PROCESS_WRAP1]]
        wrap_latencys = [get_latency_from_partitions(wraps, task_fn_mp, isWrap1=True)]

        stage_latency = stage_latencys[stage_index] + slack
        if len(stage_partition) > NUM_PROCESS_WRAP1:
            stage_split_indexs = [0, NUM_PROCESS_WRAP1]
            Done = False
            start_index = NUM_PROCESS_WRAP1
            while not Done:
                for process_index in range(start_index, len(stage_partition)):
                    invoke_overhead = REMOTE_OVERHEAD * (len(wraps) - 1)
                    temp_latency = get_latency_from_partitions([stage_partition[start_index: process_index+1]], task_fn_mp) + invoke_overhead
                    if temp_latency + RPC_OVERHEAD > stage_latency:
                        if start_index == process_index:
                            return overall_latency + max(max(wrap_latencys), temp_latency + RPC_OVERHEAD), [], False
                        wraps.append(stage_partition[start_index: process_index])
                        wrap_latencys.append(get_latency_from_partitions([stage_partition[start_index: process_index]], task_fn_mp) + RPC_OVERHEAD + invoke_overhead)
                        start_index = process_index
                        stage_split_indexs.append(process_index)
                        break
                    elif process_index + 1 == len(stage_partition):
                        wraps.append(stage_partition[start_index: process_index+1])
                        wrap_latencys.append(get_latency_from_partitions([stage_partition[start_index: process_index+1]], task_fn_mp) + RPC_OVERHEAD + invoke_overhead)
                        Done = True
                        stage_split_indexs.append(process_index+1)
                        break
            split_indexs.append(stage_split_indexs)
        else:
            split_indexs.append([])

        # for wrap_index, wrap in enumerate(wraps):
        #     print(wrap_index, wrap, wrap_latencys[wrap_index], sum([len(fs) for fs in wrap]))
        #     for pi, pp in enumerate(wrap):
        #         p_lat = get_latency_from_partitions([[pp]], task_fn_mp)
        #         print(pi, p_lat)

        if max(wrap_latencys) < stage_latency:
            slack = stage_latency - max(wrap_latencys)
        else:
            slack = 0

        overall_latency += max(wrap_latencys)

    return overall_latency, split_indexs, True

def get_wraps_from_partitions(partitions, split_indexs=None):
    wraps = []
    if split_indexs is None:
        for stage_partition in partitions:
            wraps.append([stage_partition])
    else:
        for stage_partition, stage_split_indexs in zip(partitions, split_indexs):
            if len(stage_split_indexs) == 0:
                wraps.append([stage_partition])
            else:
                stage_wraps = []
                for i in range(len(stage_split_indexs) - 1):
                    stage_wraps.append(stage_partition[stage_split_indexs[i]:stage_split_indexs[i+1]])
                wraps.append(stage_wraps)
    return wraps

def schedule(req):
    try:
        event = json.loads(req)
        workflow_name = event["workflow"]
        SLO = event["SLO"]
    except Exception as e:
        raise e

    stages, task_fn_mp = get_workflow_info(workflow_name)

    # init workflow partition for only 1 process
    partitions = get_init_partition(stages, num_partitions=1)

    # record the predicted latency of only thread isolation
    best_partitions = {}
    for index, stage_partition in enumerate(partitions):
        if len(stage_partition[0]) > 1:
            stage_latency = get_latency_from_partitions([stage_partition], task_fn_mp)
            best_partitions[str(index)] = (stage_partition, stage_latency)

    max_parallelism = max([len(stage) for stage in stages])

    # predict latency of only 1 process
    latency = predict(partitions, task_fn_mp)
    # print("multi-thread:", latency)

    if latency < SLO:
        print("Best solution is multi-thread: %.2f" % latency)
        wraps = get_wraps_from_partitions(partitions)
        return json.dumps({"workflow": workflow_name, "wraps": wraps})
    # print("------------------")

    for num_partitions in range(2, max_parallelism+1):
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

        print("Best solution in %d-process: %.2f" % (num_partitions, latency))
        if latency < SLO:
            overall_latency, split_indexs, success = split_wraps(partitions, stage_latencys, task_fn_mp, SLO - latency)
            if success:
                print("Best solution in %d-process: %.2f" % (num_partitions, overall_latency))
                # print("Partitions: ", partitions)
                # print("------------------")
                # exit(0)
                wraps = get_wraps_from_partitions(partitions, split_indexs)
                return json.dumps({"workflow": workflow_name, "wraps": wraps})
            else:
                print("Split wraps fails")

    return f'Not wraps can achieve SLO {SLO} ms for workflow {workflow_name}'


if __name__ == '__main__':
    # print(schedule('{"workflow": "sn", "SLO": 72}'))
    # print(schedule('{"workflow": "mr", "SLO": 63}'))
    # print(schedule('{"workflow": "finra5", "SLO": 119}'))
    # print(schedule('{"workflow": "finra50", "SLO": 255}'))
    # print(schedule('{"workflow": "finra100", "SLO": 350}'))
    # print(schedule('{"workflow": "finra200", "SLO": 492}'))
    print(schedule('{"workflow": "SLApp", "SLO": 104}'))
    # print(schedule('{"workflow": "SLApp-V", "SLO": 138}'))
