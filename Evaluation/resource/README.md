# Resource efficiency

This section evaluates the resource efficiency of workflows with various methods. 

## Benchmark deployment
Make sure the [benchmarks](https://github.com/tjulym/Chiron/tree/main/Benchmark) and [wraps](https://github.com/tjulym/Chiron/tree/main/Evaluation) have been deployed in the cluster. Here are two important matters:
1. Make sure every node has the images of benchmarks and `wraps` if do not constraint the location of function with `kubernetes.io/hostname`.
2. Considering the high resource requirements in high parallel configurations of `FINRA`, just depoly `FINRA-5` is OK, which is also used in this section to simulate hiher degree of parallelism in `OpenFaaS`.

## CPU costs
Run the following script to output the CPU required by each method:
```
python3 cpu_com.py
```
The CPU costs of `Chiron` shown here are that used by the [`wraps`](https://github.com/tjulym/Chiron/tree/main/Evaluation/latency) evaluated for latency.

## Memory costs
Run the following script to output the memory used by each method:
```
python3 mem_com.py
```
We also provide a script to get memory usage of the given function:
```
python3 mem_profile.py <function_name>
```
Note that, this script need to execute in the worker node that the function is deployed.

## Throughput
We provide individual script for each workflow to get the throughput of 1 second:
```
cd throughput/<function_nameme>
python3 run.py
```
For simplicity, this script only evaluates the throughput of a single instance for each function and `wrap`.

## No GIL
We provide `SLApp` and `FINRA-5` workflows implemented by Java in the `no_gil` directory, which can be evaluated to get the latency and throughput through corresponding scripts.

First, build and deploy functions and `wraps`:
```
cd no_gil/functions
./deploy.sh
```

Then, run the scripts:
```
cd no_gil

python3 lat_com-SLApp.py
python3 lat_com-finra5.py

python3 th_com-SLApp.py
python3 th_com-finra5.py
```

## Cost efficiency
Run the following script to output the dollar cost of each method:
```
python3 cost_com.py
```