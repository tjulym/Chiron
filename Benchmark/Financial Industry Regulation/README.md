# Financial Industry Regulation
This workflow is generated from [FINRA Application of Faastlane](https://github.com/csl-iisc/faastlane/tree/master/benchmarks/finra). We can configure various parallelism based on 7 functions, including `marketdata`, `lastpx`, `side`, `trddate`, `volume`, `margin-balance` and `yfinance`.

## Pre-requirements
Due to the dockershim removal in current Kubernetes, we evaluate this workflow in old versions of Docker and Kubernetes.
* Docker v20.10.7
* Kubernetes v1.23.6
* OpenFaaS v0.21.1

## Function deployment
We need to execute the following command in each worker of the cluster to deploy OpenFaaS functions.
```
cd functions
./deploy_finra.sh
```
Alternatively, we can choose to execute the deployment command on a single worker and synchronize the compiled function images to other workers.

For rapid reproduction, we can also specify fixed worker that functions can are deployed. For example, the following content of function's yml allows deployment of function `marketdata` only on `worker1`:
```
version: 1.0
provider:
  name: openfaas
  gateway: http://127.0.0.1:31112
functions:
  marketdata:
    lang: python3-flask-debian
    handler: ./marketdata
    image: marketdata:latest
    constraints:
     - "kubernetes.io/hostname=worker1"
```

We can also remove all functions as following:
```
./rm_finra.sh
```

## Workflow invocation
The following command will output details of workflow execution:
```
python3 OpenFaaS-5.py
```

## Parallelism configuration
We achieve varying degrees of parallelism by configuring five functions, including `marketdata`, `lastpx`, `side`, `trddate` and `volume`. And the new functions can directly reuse existing container images instead of redundant building. 
For example, the following content of yml can deploy function `marketdata2` and `marketdata3` based on image of `marketdata`:
```
version: 1.0
provider:
  name: openfaas
  gateway: http://127.0.0.1:31112
functions:
  marketdata2:
    lang: python3-flask-debian
    handler: ./marketdata
    image: marketdata:latest
  marketdata3:
    lang: python3-flask-debian
    handler: ./marketdata
    image: marketdata:latest
```

We provide scripts used for deploying and removing functions of FINRA with 50, 100 and 200 degrees of parallelism.
For example, the following commands serve as examples for `FINRA-50`:
```
./deploy_finra-50.sh

./rm_finra-50.sh
```