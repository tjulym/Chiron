# Evaluation

This section provides the instructions of reproducing our evaluation, including [prediction error](https://github.com/tjulym/Chiron/tree/main/Evaluation/prediction), [overall latency](https://github.com/tjulym/Chiron/tree/main/Evaluation/latency) and [resource efficency](https://github.com/tjulym/Chiron/tree/main/Evaluation/resource). We also provide the expected results in our environment.

## Wrap deployment
The following command will build the base images for all workflows and then deploy them:
```
cd wraps
./build.sh
./deploy.sh
```

Note that, application `FINRA-50`, `FINRA-100`, `FINRA-200` in `Chiron` with process pool require 11, 21 and 21 cores for each `wrap`, respectively. You can ignore these workflows if there are not enough resources on a Kubernetes node.