# Movie Reviewing
This workflow is generated from [Media Microservices of DeathStarBench](https://github.com/delimitrou/DeathStarBench/tree/master/mediaMicroservices). We re-implement the action of reviewing a movie using 9 Python functions.

## Pre-requirements
Due to the dockershim removal in current Kubernetes, we evaluate this workflow in old versions of Docker and Kubernetes.
* Docker v20.10.7
* Kubernetes v1.23.6
* OpenFaaS v0.21.1

## Database deployment
First, we need to deploy databases used in Movie Reviewing, including Redis, MongoDB and MemoryCache.
```
cd yaml
kubectl apply -f namespaces.yml
kubectl apply -f yaml-db/
```

## Database initialization
Second, we need to register users and movies for the workflow. We provide a dedicated OpenFaaS function called `mr-db-op` for executing database operations.
```
cd functions
faas-cli build -f mr-db-op.yml
faas-cli deploy -f mr-db-op.yml
```
Subsequently, we can invoke this function to accomplish the operation of database initialization.
```
curl http://127.0.0.1:31112/function/mr-db-op -d 1
```
Furthermore, we can employ the following command to remove the intermediate results of workflow execution from the databases in order to release resources.
```
curl http://127.0.0.1:31112/function/mr-db-op -d 0
```

## Function deployment
Then, we need to execute the following command in each worker of the cluster to deploy OpenFaaS functions.
```
cd functions
./deploy_mr.sh
```
Alternatively, we can choose to execute the deployment command on a single worker and synchronize the compiled function images to other workers.

For rapid reproduction, we can also specify fixed worker that functions can are deployed. For example, the following content of function's yml allows deployment of function `compose-review` only on `worker1`:
```
version: 1.0
provider:
  name: openfaas
  gateway: http://127.0.0.1:31112
functions:
  compose-review:
    lang: python3-flask
    handler: ./compose-review
    image: compose-review:latest
    constraints:
     - "kubernetes.io/hostname=worker1"
```

We can also remove all functions as following:
```
./rm_mr.sh
```

## Workflow invocation
Finally, the following command will output details of workflow execution:
```
python3 OpenFaaS.py
```