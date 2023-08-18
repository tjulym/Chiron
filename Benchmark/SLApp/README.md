# SLApp
This workflow is generated from [SLApp-PerfCost-MdlOpt](https://github.com/pacslab/SLApp-PerfCost-MdlOpt), which is composed of various number of functions with mixed types of workload, namely CPU intensive, disk I/O intensive, and network I/O intensive.
We develop SLApp and SLApp-V based on 6 functions, including `factorial`, `fibonacci`, `pbkdf2`, `pi`, `disk-io` and `network-io`.

## Pre-requirements
Due to the dockershim removal in current Kubernetes, we evaluate this workflow in old versions of Docker and Kubernetes.
* Docker v20.10.7
* Kubernetes v1.23.6
* OpenFaaS v0.21.1

## MinIO deployment
First, we need to deploy `MinIO` used for downloading and uploading file in `network-io` function. 
```
kubectl apply -f yaml/minio-service.yaml
```
`MinIO` is an object storage that provides an AWS S3-compatible API and supports all core S3 features. And there are the following important options in the yaml file:
* `volumes.minio-volume.hostPath.path`: path to a local drive or volume on the Kubernetes worker node
* `containers.minio.env.MINIO_ROOT_USER & MINIO_ROOT_PASSWORD`: username and password used for connecting to MinIO from client


## Function deployment
Then, we need to execute the following command in each worker of the cluster to deploy OpenFaaS functions.
```
cd functions
./deploy_SLApp.sh

./deploy_SLApp-V.sh
```
Alternatively, we can choose to execute the deployment command on a single worker and synchronize the compiled function images to other workers.

For rapid reproduction, we can also specify fixed worker that functions can are deployed. For example, the following content of function's yml allows deployment of function `factorial` only on `worker1`:
```
version: 1.0
provider:
  name: openfaas
  gateway: http://127.0.0.1:31112
functions:
  factorial:
    lang: python3-flask
    handler: ./factorial
    image: factorial:latest
    constraints:
     - "kubernetes.io/hostname=worker1"
```

We can also remove all functions as following:
```
./rm_SLApp.sh

./rm_SLApp-V.sh
```

## Workflow invocation
Finally, the following command will output details of workflow execution:
```
python3 OpenFaaS-SLApp.py

python3 OpenFaaS-SLApp-V.py
```
Note that, we can develop workflows with different latencies by setting different parameters for functions, i.e., `data` variable in `OpenFaaS.py`.