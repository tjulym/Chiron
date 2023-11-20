# Chiron

## Introduction
Chiron is a serverless deployment system that implements `wrap`, a novel abstraction for the "m-to-n" serverless deployment model aiming at optimizing performance and resource efficiency by function partition and function execution mode selection, atop OpenFaaS with combined processes and threads.

## Installation
We implement the Chiron system in OpenFaas v0.21.1, and run it on a Kubernetes v1.23.6 cluster. The [Installation](https://github.com/tjulym/Chiron/tree/main/Installation) shows the instruction to install the environment.

## Benchmark
We provide some benchmark for evaluating our system. The [Benchmark](https://github.com/tjulym/Chiron/tree/main/Benchmark) shows the instruction to build and deploy several serverless workflows.

## Profiler
This module shows how Chiron profiles a function for further performance prediction. The details can be found in [Profiler](https://github.com/tjulym/Chiron/tree/main/Profiler).

## Scheduler
This module is core of Chiron, which determines the `wraps` of workflow based on the given SLO. The details can be found in [Scheduler](https://github.com/tjulym/Chiron/tree/main/Scheduler).

## Generator
This module produces the orchestrator code of `wraps` based on the result of `Scheduler`. The details can be found in [Generator](https://github.com/tjulym/Chiron/tree/main/Generator).


## Evaluation
This sections contains a simple instruction for replaying our evaluation. The details can be found in [Envaluation](https://github.com/tjulym/Chiron/tree/main/Evaluation).

## Cite
Welcome to cite [Chiron](https://dl.acm.org/doi/10.1145/3581784.3613211) in SC'23 by:
```
@inproceedings{10.1145/3581784.3613211,
   author = {Li, Yiming and Zhao, Laiping and Yang, Yanan and Qu, Wenyu},
   title = {Rethinking Deployment for Serverless Functions: A Performance-First Perspective},
   year = {2023},
   address = {New York, NY, USA},
   url = {https://doi.org/10.1145/3581784.3613211},
   doi = {10.1145/3581784.3613211},
   booktitle = {Proceedings of the International Conference for High Performance Computing, Networking, Storage and Analysis},
   numpages = {14},
   location = {Denver, CO, USA},
   series = {SC '23}
}
``` 