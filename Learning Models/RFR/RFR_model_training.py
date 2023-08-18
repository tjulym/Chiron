import numpy as np
import pandas as pd
from sklearn import preprocessing, ensemble
import datetime
import joblib

MAX_PARALLELISM = 5
NUM_FEATURE_PER_FUNC = 18
NUM_FEATURE = MAX_PARALLELISM * NUM_FEATURE_PER_FUNC
min_max_scalar = preprocessing.MinMaxScaler()

def generate_data(workflow_name):
    data_train_resource_label = pd.read_csv('data/train_%s.csv' % workflow_name, header=None)
    data_test_resource_label = pd.read_csv('data/test_%s.csv' % workflow_name, header=None)

    train_num = len(data_train_resource_label)
    test_num = len(data_test_resource_label)
    print("train_num:", train_num)
    print("test_num:", test_num)

    data_resource_label = pd.concat([data_train_resource_label, data_test_resource_label])

    data_resource = data_resource_label.values

    for i in range(MAX_PARALLELISM):
        for j in range(NUM_FEATURE_PER_FUNC-2):
            k = i * NUM_FEATURE_PER_FUNC + j
            try:
                data_resource[:, k:(k+1)] = min_max_scalar.fit_transform(data_resource[:, k:(k+1)])
            except Exception as e:
                print(k, e)
                exit(0)
    
    data_train_resource = data_resource[:train_num, 0:-1].astype(float)
    data_train_label = data_resource[:train_num, -1:].astype(float)

    data_test_resource = data_resource[train_num:, 0:-1].astype(float)
    data_test_label = data_resource[train_num:, -1:].astype(float)

    return data_train_resource, data_train_label, data_test_resource, data_test_label 

def generate_data2(workflow_name):
    data_resource_label = pd.read_csv('data/test_%s.csv' % workflow_name, header=None)
    data_resource_label = data_resource_label.sample(frac=1.0)
    data_resource = data_resource_label.values

    total_num = len(data_resource)
    train_num = int(0.8 * total_num)
    #train_num = 20
    test_num = total_num - train_num
    print("train_num:", train_num)
    print("test_num:", test_num)

    for i in range(MAX_PARALLELISM):
        for j in range(NUM_FEATURE_PER_FUNC-2):
            k = i * NUM_FEATURE_PER_FUNC + j
            try:
                data_resource[:, k:(k+1)] = min_max_scalar.fit_transform(data_resource[:, k:(k+1)])
            except Exception as e:
                print(k, e)
                exit(0)

    data_train_resource = data_resource[:train_num, 0:-1].astype(float)
    data_train_label = data_resource[:train_num, -1:].astype(float)

    data_test_resource = data_resource[train_num:, 0:-1].astype(float)
    data_test_label = data_resource[train_num:, -1:].astype(float)

    return data_train_resource, data_train_label, data_test_resource, data_test_label


def train(workflow_name):
    print("=====%s=====" % workflow_name)
    data_train_resource, data_train_label, data_test_resource, data_test_label = generate_data(workflow_name)

    # -----------------RFR--------------------------#
    regr = ensemble.RandomForestRegressor()
    regr.fit(data_train_resource, data_train_label.ravel())
    joblib.dump(regr, "models/RFR_%s" % workflow_name)

    startTime = datetime.datetime.now()
    label_pre_train = regr.predict(data_train_resource)
    label_pre_test = regr.predict(data_test_resource)
    endTime = datetime.datetime.now()

    for i in range(len(label_pre_test)):
        print(label_pre_test[i], data_test_label[i])
        #print('RFR Testing Loss', np.abs((label_pre_test[i] - data_test_label[i])) / data_test_label[i])

    print("#Radom Forest Regression Training Score:%f"%np.mean(np.abs(label_pre_train - data_train_label)))
    print("#Radom Forest Regression Test Score:%f"%np.mean(np.abs(label_pre_test - data_test_label)))

    diffs_train = []
    diffs_test = []
    for i in range(len(label_pre_train)):
        diffs_train.append(np.abs(label_pre_train[i] - data_train_label[i]) / data_train_label[i])
    for i in range(len(label_pre_test)):
        diffs_test.append(np.abs(label_pre_test[i] - data_test_label[i]) / data_test_label[i])
    print("#Ave Training Diff:%f"%np.mean(diffs_train))
    print("#Ave Test Diff:%f"%np.mean(diffs_test))
    print("PredictionTime:", (endTime - startTime))

    # Extract feature importances
    #imports = regr.feature_importances_
    #print(imports)


if __name__ == '__main__':
    train("sn")
    # train("mr")
    # train("finra")
    # train("SLApp")
    # train("SLAppV")
