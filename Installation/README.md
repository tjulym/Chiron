# Installation

Due to the dockershim removal in current Kubernetes, we evaluate this workflow in old versions of Docker and Kubernetes.
* Docker v20.10.7
* Kubernetes v1.23.6
* OpenFaaS v0.21.1

Note that, even with a single node, a Kubernetes cluster can be established, and `Chiron` remains compatible with Kubernetes clusters of any scale, allowing users to select cluster sizes based on their specific requirements. This document provides a tutorial on how to install the above environment in `Ubuntu`.

## Docker
We provide a script to install Docker v20.10.7 through `apt-get`.
```
./install_docker.sh
```
Please execute this script in each worker node.

## Kubernetes

### Kubeadm installation
We provide a script to install Kubernetes v1.23.6 through `apt-get`.
```
./install_k8s.sh
```
Please execute this script in each worker node.

Next, we need to match the docker and kubelet cgroup drivers through modifying file `/etc/docker/daemon.json` in each worker. The following is an example:
```
{
  "exec-opts": ["native.cgroupdriver=systemd"]
}
```
Then, we need to restart the docker service for the configuration to take effect.
```
systemctl daemon-reload && systemctl restart docker
```

### Create cluster
Execute the following command in the master node to create a Kubernetes cluster:
```
kubeadm init \
--pod-network-cidr=10.244.0.0/16 \
--apiserver-advertise-address=<your_master_node_ip>
```

The following instructions can also be found in the output of `kubeadm init`.

To make kubectl work for non-root user, run these commands, which are also part of the kubeadm init output:
```
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

Next, we can deploy a Pod network to the cluster:
```
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
```

Now, we need to allow Pod deployment in our master node:
```
kubectl taint nodes --all node-role.kubernetes.io/master-
```

Finally, we can execute the following command in master node, and the output can help other nodes to join our cluster:
```
kubeadm token create --ttl 0 --print-join-command
```

We can use `kubectl get node` to check if everything is ready.

## OpenFaaS

First, we need to create namespaces:
```
kubectl apply -f ./namespaces.yml
```

Next, create secret for OpenFaaS:
```
kubectl -n openfaas create secret generic basic-auth \
--from-literal=basic-auth-user=admin \
--from-literal=basic-auth-password=admin
```

Then, install other components:
```
kubectl apply -f ./yaml/
```

Now we need to install official CLI for OpenFaaS:
```
curl -sSL https://cli.openfaas.com | sudo sh
```

Finally, we can login into OpenFaaS:
```
export OPENFAAS_URL=http://127.0.0.1:31112
faas-cli login --password admin 
```

We can use `faas-cli list` to check if everything is ready.


## Python dependencies
```
pip install -r requirements.txt
```