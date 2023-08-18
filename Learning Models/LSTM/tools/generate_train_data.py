import json

with open("features.json") as f:
    features = json.load(f)

workflows = ["sn", "mr", "finra", "SLApp", "SLAppV"]

MAX_PARALLELISM = 5

data = {}

for workflow in workflows:
    with open("process_times/%s_exec_times.csv" % workflow, "r") as f:
        lines = f.readlines()
    workflow_data = []
    for line in lines:
        fs, lats = line.split("\t")
        fs = fs.split(",")
        lats = [[float(j) for j in i.split(",")] for i in lats.split(";")]
        lats.sort(key=lambda x: max(x))
        lat = lats[int(0.95*len(lats))-1]

        line_data = []
        for index, func_name in enumerate(fs):
            #line_data.extend(features[func_name].copy())
            features_str = ",".join([str(i) for i in features[func_name]])
            line_data.append(features_str)
            #lat[index] = round(lat[index]/features[func_name][-1], 2)
        if len(fs) < MAX_PARALLELISM:
            for i in range(MAX_PARALLELISM - len(fs)):
                #line_data.extend([0.0] * 17)
                line_data.append(",".join(['0.0' for _ in range(17)]))
                lat.append(0.0)
                #lat.insert(0, 1.0)
        line_data.append(",".join([str(i) for i in lat]))

        #line_data_str = ",".join([str(i) for i in line_data])
        line_data_str = "\t".join([str(i) for i in line_data])
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
