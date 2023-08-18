# End-to-end workflow latency

This section evaluates the latency of workflows with various methods. 

## Benchmark deployment
Make sure the [benchmarks](https://github.com/tjulym/Chiron/tree/main/Benchmark) and [wraps](https://github.com/tjulym/Chiron/tree/main/Evaluation) have been deployed in the cluster. Here are two important matters:
1. Make sure every node has the images of benchmarks and `wraps` if do not constraint the location of function with `kubernetes.io/hostname`.
2. Considering the high resource requirements in high parallel configurations of `FINRA`, just depoly `FINRA-5` is OK, which is also used in this section to simulate hiher degree of parallelism in `OpenFaaS`.

## Results
We provide individual script for each workflow with sub-directory to get the end-to-end latency:
```
python3 run.py
```
And it will output the latency in milliseconds of each method, and both the actual and expected improvement.


Especially, we provide individual script for each degree of parallelism in `FINRA`.