import json

with open("features.json") as f:
    features = json.load(f)

workflows = ["sn", "mr", "finra", "SLApp", "SLAppV"]

THREAD_BLOCK = 1.5
MAX_PARALLELISM = 5

data = {}

for workflow in workflows:
    with open("process_times/%s_exec_times.csv" % workflow, "r") as f:
        lines = f.readlines()
    workflow_data = []
    for line in lines:
        fs, lats = line.split("\t")
        fs = fs.split(",")
        lats = sorted([float(i) for i in lats.split(",")])
        #lat = lats[int(0.95*len(lats))-1]
        lat = sum(lats)/len(lats)

        line_data = []
        for index, func_name in enumerate(fs):
            line_data.extend(features[func_name].copy())
            line_data.append(index*THREAD_BLOCK)
        if len(fs) < MAX_PARALLELISM:
            for i in range(MAX_PARALLELISM - len(fs)):
                line_data.extend([0.0] * 18)
        line_data.append(lat)

        line_data_str = ",".join([str(i) for i in line_data])
        workflow_data.append(line_data_str+"\n")

    data[workflow] = workflow_data
    with open("../data/test_%s.csv" % workflow, "w") as f:
        f.writelines(data[workflow])

for workflow in workflows:
    train_data = []
    for data_name in data:
        if not data_name == workflow:
            train_data.extend(data[data_name])

    with open("../data/train_%s.csv" % workflow, "w") as f:
        f.writelines(train_data)
