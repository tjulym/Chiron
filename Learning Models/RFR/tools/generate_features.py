import json
import os
from os import path

features = {}

features_path = "./features"
feature_files = os.listdir(features_path)
for ff in feature_files:
    ff_path = path.join(features_path, ff)
    with open(ff_path, "r") as f:
        feature = f.readline().strip()

    func_name = ff.split(".")[0]
    feature = [float(i) for i in feature.split(",")]
    features[func_name] = feature

fs_times = {}
for func_name in features:
    fs_times[func_name] = []
times_path = "./fs_times"
time_files = os.listdir(times_path)
for tf in time_files:
    tf_path = path.join(times_path, tf)
    with open(tf_path, "r") as f:
        lines = f.readlines()
    for line in lines:
        func_name, lats = line.split("\t")
        lats = [float(i) for i in lats.split(",")]
        fs_times[func_name].extend(lats)

for func_name in fs_times:
    sorted_times = sorted(fs_times[func_name])
    features[func_name].append(sorted_times[int(0.95*len(sorted_times))-1])
    print(func_name, features[func_name])

with open("features.json", "w") as f:
    json.dump(features, f)
