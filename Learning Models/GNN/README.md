# GNN model in Chiron's Evaluation
## Model input
We first profile 16 system-layer and microarchitecture-layer metrics for each function, including Context-switches, L1I MPKI, LID MKPI, L2 MPKI, L3MPKI, TLBD MPKI, TLBI MPKI, Branch MPKI,  MLP, CPU utilization, Memory utilization, Network bandwidth, LLC, IPC, Disk IO and Memory IO, which are recommended by the performance predictor Gsight [SC'21]. Then, we use the above metrics and solo-run latencies as the feature of a thread node.
In order to encode the wrap structure, we add virtual nodes to represent process, stage and workflow.
For the process node, we use the features of creatring a new process.
Finally, we construct the adjacency matrix based on the edge between thread, process, stage and workflow nodes in each wrap.

## Model output
This model can output the end-to-end predicted latency of given workflow directly.

## Environment

This model is run with Python 3.7, we list the necessary requirements in the following:

```
pip install numpy
pip install torch torchvision torchaudio
```

## Training dataset
We collect performance of all possible wraps in each workflow, then generate training dataset for each workflow based on data other than it. For example, we train the model for FINRA-5 workflow using the data from social network, moive review, SLApp and SLApp. 
These latencies can be found in lats directory. And the training and validation data can be generated as following:
```
cd tools
python3 generate_train_data.py
python3 generate_val_data.py
```
The datasets can be found in lats directory.

## Training model
We train individual for seperate workflow. The following command will start training and output prediction error:
```
python3 main.py
python3 test.py
```