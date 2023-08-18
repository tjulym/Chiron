import gcn
import json
import torch
import dataset as dataset_mod
import itertools

import time

def get_predictor(predictor_name="predictor"):
    predictor_args = {
        # "num_features": 51,
        "num_features": 19,
        "num_layers": 3,
        # "num_hidden": 600,
        "num_hidden": 19,
        # "num_hidden": 128,
        "dropout_ratio": 0.2,
        "weight_init": "thomas",
        "bias_init": "thomas",
        "binary_classifier": False
    }

    predictor = gcn.GCN(**predictor_args)

    weight_path = "results/accuracy/gcn/%s.pt" % predictor_name

    predictor.load_state_dict(torch.load(weight_path))

    torch.set_grad_enabled(False)
    predictor.eval()
    # predictor.train()

    return predictor

# predictor = get_predictor()
predictor = None

def get_init_partition(workflow_name, num_partitions=2):
    workflow = json.loads(open("workflows/%s.json" % (workflow_name)).read())
    _, indexs, resources, _, _ = dataset_mod.get_adjacency(workflow)

    stateName = workflow["StartAt"]
    state = workflow["States"][stateName]
    over = False
    
    partitions = {}
    stages = {}
    while not over:
        if state["Type"] == "Task":
            partitions[stateName] = 0
            stages[stateName] = [stateName]
        elif state["Type"] == "Parallel":
            groups = [0] * num_partitions
            stages[stateName] = []
            for branch in state["Branches"]:
                stages[stateName].append(branch["StartAt"])
                lat = dataset_mod.metrics[resources[branch["StartAt"]]][-1]
                index = groups.index(min(groups))
                groups[index] = groups[index] + lat
                partitions[branch["StartAt"]] = index
        if "End" in state:
            over = True
        else:
            stateName = state["Next"]
            state = workflow["States"][stateName]

    return stages, partitions

def get_policy_from_partitions(workflow_name, stages, partitions):
    policy = {}
    for stage, funcs in stages.items():
        policy[stage] = [[] for _ in range(len(funcs)-1)]
        for func in funcs:
            if partitions[func] > 0 and len(policy[stage]) > 0:
                if partitions[func] < len(funcs):
                    (policy[stage][partitions[func]-1]).append(func)
                else:
                    (policy[stage][len(funcs)-2]).append(func)
        policy[stage] = [i for i in policy[stage] if len(i) > 0]    

        if len(policy[stage]) == 0:
            policy.pop(stage)
        elif len(policy[stage]) == 1 and len(policy[stage][0]) == len(stages[stage]):
            policy.pop(stage)

        # if  stage in policy and sum([len(i) for i in policy[stage]]) == len(funcs):
        #     policy[stage] = policy[stage][1:]

    g = "\t".join([json.dumps(policy), workflow_name, "0"])
    # print(g)
    # exit(0)
    local_adjacency, local_features, _ = dataset_mod.prepare_tensors([g])
    
    prediction = predictor(local_adjacency, local_features)[0][0]
    return policy, prediction

def get_best_partitions_KL(workflow_name, stages, partitions, subsets=(0,1)):
    partition_index1 = subsets[0]
    partition_index2 = subsets[1]

    _, best_prediction = get_policy_from_partitions(workflow_name, stages, partitions)

    print("init prediction: %f" % best_prediction)

    over = False

    local_partitions = partitions.copy()

    while not over:
        partitions2 = local_partitions.copy()
        partition1, partition2 = set(), set()
        moves1, moves2 = [], []
        predictions = []
        for f, p in partitions2.items():
            if p == partition_index1:
                partition1.add(f)
            elif p == partition_index2:
                partition2.add(f)

        while len(partition1) > 0 or len(partition2) > 0:
            if len(partition1) > 0 and len(partition2) > 0:
                products = itertools.product(partition1, partition2)
            elif len(partition1) > 0:
                products = [(f, None) for f in partition1]
            else:
                products = [(None, f) for f in partition2]

            current_prediction = None
            best_swap = []
            for product in products:
                temp_partitions = partitions2.copy()
                if len(partition1) > 0:
                    temp_partitions[product[0]] = partition_index2
                if len(partition2) > 0:  
                    temp_partitions[product[1]] = partition_index1

                # print(temp_partitions)

                _, temp_prediction = get_policy_from_partitions(workflow_name, stages, temp_partitions)

                if current_prediction is None or current_prediction > temp_prediction:
                    current_prediction = temp_prediction
                    best_swap = (product[0], product[1])

            if len(partition1) > 0 and len(partition2) > 0:
                fs = list(partition1) + list(partition2)

                for f in fs:
                    temp_partitions = partitions2.copy()
                    if partitions2[f] == partition_index1:
                        temp_partitions[f] = partition_index2
                    elif partitions2[f] == partition_index2:
                        temp_partitions[f] = partition_index1

                    _, temp_prediction = get_policy_from_partitions(workflow_name, stages, temp_partitions)

                    if current_prediction is None or current_prediction > temp_prediction:
                        current_prediction = temp_prediction
                        if f in partition1:
                            best_swap = (f, None)
                        else:
                            best_swap = (None, f)

            
            moves1.append(best_swap[0])
            moves2.append(best_swap[1])

            if best_swap[0] is not None:
                partition1.remove(best_swap[0])
                partitions2[best_swap[0]] = partition_index2
            if best_swap[1] is not None:
                partition2.remove(best_swap[1])
                partitions2[best_swap[1]] = partition_index1

            predictions.append(current_prediction)

        if len(predictions) and min(predictions) < best_prediction:
            best_prediction = min(predictions)
            min_index = predictions.index(min(predictions))
            for i in range(min_index+1):
                if moves1[i] is not None:
                    local_partitions[moves1[i]] = partition_index2
                if moves2[i] is not None:
                    local_partitions[moves2[i]] = partition_index1
        else:
            over = True

    print("best prediction: %f under subsets (%d, %d)" % (best_prediction, subsets[0], subsets[1]))
    # print(local_partitions)
    return local_partitions

def multi_way_KL(workflow_name, stages, partitions):
    combinations = itertools.combinations(range(len(set(partitions.values()))), 2)
    local_partitions = partitions.copy()
    for com in combinations:
        local_partitions = get_best_partitions_KL(workflow_name, stages, local_partitions, com)

    return local_partitions


def get_best_partitions_All(workflow_name, stages, partitions, num_partitions=2):
    _, best_prediction = get_policy_from_partitions(workflow_name, stages, partitions)
    
    print("init prediction: %f" % best_prediction)

    best_prediction_bak = best_prediction

    best_partitions = partitions.copy()

    cases =  [range(num_partitions)] * len(partitions)
    products = itertools.product(*cases)
    funcs = partitions.keys()

    for product in products:
        if len(set(product)) != num_partitions:
            continue

        local_partitions = partitions.copy()

        for i, f in enumerate(funcs):
            local_partitions[f] = product[i]

        # print(local_partitions)
        _, current_prediction = get_policy_from_partitions(workflow_name, stages, local_partitions)

        if current_prediction < best_prediction:
            best_prediction = current_prediction
            best_partitions = local_partitions.copy()

    if best_prediction_bak == best_prediction:
        local_partitions = partitions.copy()

    print("best prediction: %f under %d partitions" % (best_prediction, num_partitions))
    # print(local_partitions)
    return local_partitions


def get_label_from_policy(workflow_name, policy):
    with open("lats/lats_%s_stru.csv" % workflow_name) as f:
        lines = f.readlines()

    for line in lines:
        policy2 = json.loads(line.split("\t")[0])
        
        flag = False

        for stage, ps in policy.items():
            for i in range(len(ps)):
                policy[stage][i] = sorted(ps[i])

        for stage, ps in policy2.items():
            for i in range(len(ps)):
                policy2[stage][i] = sorted(ps[i])

        if policy == policy2:
            print(line)
            break


def graph_partitioning(workflow_name):
    print("Workflow %s" % workflow_name)
    start = time.time()

    global predictor

    predictor = get_predictor(predictor_name="predictor_no_%s" % workflow_name)

    # exit(0)

    # for param in predictor.final_params():
    #     print(param, param.size())
    # exit(0)
    # predictor = get_predictor(predictor_name="predictor")

    stages, partitions = get_init_partition(workflow_name, num_partitions=2)
    # print(stages)
    
    # print(partitions)

    for f in partitions:
        partitions[f] = 0

    mt_policy, mt_prediction = get_policy_from_partitions(workflow_name, stages, partitions)
    print("multi thread prediction: %f" % mt_prediction)

    for fs in stages.values():
        for i, f in enumerate(fs):
            partitions[f] = i

    mp_policy, mp_prediction = get_policy_from_partitions(workflow_name, stages, partitions)
    # mp_prediction = 0.060
    print("multi process prediction: %f" % mp_prediction)
    get_label_from_policy(workflow_name, mt_policy)
    get_label_from_policy(workflow_name, mp_policy)

    SLO = mp_prediction
    # SLO = 0.2

    max_partitions = len(set(partitions.values()))

    if mt_prediction < SLO or max_partitions == 1:
        print("Best partitions is multi-thread")
        print("Policy %s" % json.dumps(mt_policy))
        print("KL use %f" % (time.time()-start))
        get_label_from_policy(workflow_name, mt_policy)
        return mt_policy

    for num_partitions in range(2, max_partitions):
        stages, partitions = get_init_partition(workflow_name, num_partitions=num_partitions)
        best_partitions = multi_way_KL(workflow_name, stages, partitions)
        policy, prediction = get_policy_from_partitions(workflow_name, stages, best_partitions)
        if prediction < SLO:
            print("Best partitions is mixed-process-thread")
            print("Policy %s" % json.dumps(policy))
            print("KL use %f" % (time.time()-start))
            get_label_from_policy(workflow_name, policy)
            return policy

    print("Best partitions is multi-process")
    print("Policy %s" % json.dumps(mp_policy))
    print("KL use %f" % (time.time()-start))
    get_label_from_policy(workflow_name, mp_policy)

    return mp_policy
    exit(0)

    # partitions["fibonacci"] = 1
    # partitions["factorial"] = 0

    # print(partitions)
    # exit(0)

    print("KL algorithm")
    start = time.time()
    partitions = multi_way_KL(workflow_name, stages, partitions)

    print("KL use %f" % (time.time()-start))

    # print("============")
    # print("Traverse algorithm")
    # start = time.time()
    # get_best_partitions_All(workflow_name, stages, partitions, num_partitions=3)
    # print("All use %f" % (time.time()-start))


def test(workflow_name):
    global predictor
    predictor = get_predictor(predictor_name="predictor_no_%s" % workflow_name)

    # validation
    with open("lats/lats_%s_stru.csv" % workflow_name) as f:
        lines = f.readlines()

    lines = [l.split("\t") for l in lines]
    lines = [["\t".join(l[:-1]), l[-1]] for l in lines]

    loss = []
    loss2 = []

    # workflow_mp_latency = {"mr": 51.32, "sn": 59.21, "finra": 199.26, "App7": 152.54, "App10": 174.41}

    for l in lines:
        adjacency, features, latency = dataset_mod.prepare_tensors([l[0]], [l[1]])
        predictions = predictor(adjacency, features)
        # print(predictions[0][0], latency[0][0], l)
        # print("%f, %f, %s" % (predictions[0][0], latency[0][0], l))
        # exit(0)
        loss.append(abs(predictions[0][0] - latency[0][0]) / latency)
        loss2.append((predictions[0][0] - latency[0][0]) / latency)
    
    print(workflow_name, "validation (abs):", sum(loss) / len(loss))
    print(workflow_name, "validation:", sum(loss2) / len(loss2))

    with open("loss/loss_validation_%s.csv" % (workflow_name), "w") as f:
        loss2 = [str(float(i))+"\n" for i in loss2]
        f.writelines(loss2)
        
    # print(",".join([str(float(i)) for i in loss]))

    # exit(0)
    # train loss
    with open("lats/lats_no_%s_stru.csv" % workflow_name) as f:
        lines = f.readlines()

    lines = [l.split("\t") for l in lines]
    lines = [["\t".join(l[:-1]), l[-1]] for l in lines]

    loss = []
    loss2 = []

    for l in lines:
        adjacency, features, latency = dataset_mod.prepare_tensors([l[0]], [l[1]])
        predictions = predictor(adjacency, features)
        # print("%f, %f, %s" % (predictions[0][0], latency[0][0], l))
        loss.append(abs(predictions[0][0] - latency[0][0]) / latency)
        loss2.append((predictions[0][0] - latency[0][0]) / latency)
    
    print(workflow_name, "training (abs):", sum(loss) / len(loss))
    print(workflow_name, "training:", sum(loss2) / len(loss2))

    with open("loss/loss_train_%s.csv" % (workflow_name), "w") as f:
        loss2 = [str(float(i))+"\n" for i in loss2]
        f.writelines(loss2)

# graph_partitioning("mr")
graph_partitioning("sn")
# graph_partitioning("finra")
# graph_partitioning("App7")
# graph_partitioning("App10")

# test("mr")
# test("sn")
# test("finra")
# test("App7")
# test("App10")

# test_mr()
# if __name__ == '__main__':
#     predictor = get_predictor()

#     g = '{"parallel": [["pi"], ["fibonacci"]], "parallel2": [["fibonacci2", "marketdata2"]]}\tworkflow1'
    
#     latency = '392.0'

#     adjacency, features, latency = dataset_mod.prepare_tensors([g], [latency])

#     predictions = predictor(adjacency, features)

#     print(predictions)
#     print(latency)

#     g = '{"parallel": [["pi"], ["fibonacci", "marketdata"]], "parallel2": [["fibonacci2", "marketdata2"]]}\tworkflow1'
#     adjacency, features, _ = dataset_mod.prepare_tensors([g])

#     predictions = predictor(adjacency, features)

#     print(predictions)
#     