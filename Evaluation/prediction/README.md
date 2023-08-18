# Prediction error

We compare the prediction error of Chiron's `Predictor` of  against `Random Forest Regression (RFR)`, `Long Short-Term Memory (LSTM)`, and `Graph Neural Network (GNN)`.
* `Predictor`: it utilizes a white box method to model the performance of `wrap` and estimates the latency of multiple threads through simulating GIL switching in Python.
* `RFR`: it estimates the latency of multiple threads with `Random Forest Regression` models based on solo-run latency, and 16 system-layer and microarchitecture-layer metrics for each function, including ContextSwitch, L1IMPKI, LIDMKPI, L2MPK2, TLBDMPKI, TLBIMPKI, BranchMPKI, L3MPKI, MLP, CpuUtil, MemUtil, MemBW, LLC, IPC, DiskIO and NetworkIO. Then, it adopts the white model in `Predictor` to calculate the end-to-end latency.
* `LSTM`: it works with the same mode as `RFR` but utilizes `Long Short-Term Memory` model to predict the latency of multiple threads.
* `GNN`: it construct the adjacency matrix based on the edge between thread, process, stage and workflow nodes to encode `wrap`'s structure, and uses above 17 metrics of each node in the graph to build feature matrix. This model output the end-to-end predicted latency of given workflow directly.

Given the time-consuming nature of conducting a complete retraining and characterization, we present the results obtained in our experimental environment for examination purposes. Additionally, we provide tutorials on replicating the experiments to facilitate reproducibility.

## Expected results
Run the script and it will output the prediction error:
```
python3 loss-com.py
```

## Replay tutorial

If want to replicate this experiments, please refer to the following steps.

### Wrap partitions generation

First, need to generate various `wrap` partitions for a workflow. We have provides all `wrap` partitions in `wraps` directory, including `Social Network`, `Movie Reviewing`, `FINRA-5`, `SLApp` and `SLApp-V`. Each line in the file representatives a kind of `wrap` partition.

### Wrap deployment

Next, need to get the orchestrator code of `wrap` partition and deploy it in `OpenFaaS`. For the `wrap` code generation, please call the corresponding implementation of [`Generator`](https://github.com/tjulym/Chiron/tree/main/Generator). And we provide a script to deploy `wrap` directly instead of re-building:
```
python3 ../deploy.py <wrap_name> <wrap_code_file_name>
```
For example, the following command will deploy the code of `sn_wrap.py` into `sn-wrap` function in `OpenFaaS`:
```
python3 ../deploy.py sn-wrap sn_wrap.py
```

### Error calculation
At last, evaluate the [real latency](https://github.com/tjulym/Chiron/tree/main/Evaluation/latency) and compare it with the [predicted latency](https://github.com/tjulym/Chiron/tree/main/Scheduler). We provides a script named `eval.py` as an example to show how to use the `Scheduler` to calculate the prediction error.