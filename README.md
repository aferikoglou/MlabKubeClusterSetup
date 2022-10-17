# Microlab Kubernetes Cluster Setup Instructions

## Requirements: 
* A compatible Linux host. The Kubernetes project provides generic instructions for Linux distributions based on Debian and Red Hat, and those distributions without a package manager.
* 2 GB or more of RAM per machine (any less will leave little room for your apps).
* 2 CPUs or more.
* Full network connectivity between all machines in the cluster (public or private network is fine).
* Unique hostname, MAC address, and product_uuid for every node. See [here](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/#verify-mac-address) for more details.
* Certain ports are open on your machines. See [here](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/#check-required-ports) for more details.
* Swap disabled. You MUST disable swap in order for the kubelet to work properly. (We will be covering that in step 4)
 
 **NOTE**: All the bullets except for the last one should already be set by the time you get your virtual machine from microlab.

---
### For a full tutorial on how to setup kubernetes click [here](https://github.com/aferikoglou/mlab-k8s-cluster-setup/blob/main/kubernetes/README.md).

---
### For a full tutorial on how to setup grafana and prometheus monitoring system click [here](https://github.com/aferikoglou/mlab-k8s-cluster-setup/tree/main/prometheus/README.md) (kubernetes required).
---
### For a full tutorial on how to setup  dcgm exporter click [here](https://github.com/aferikoglou/mlab-k8s-cluster-setup/tree/main/dcgm_exporter/README.md) (kubernetes + Prometheus required).
---
### For a full tutorial on how to partition Multi-Instance GPUs (MIG) click [here](https://github.com/aferikoglou/mlab-k8s-cluster-setup/tree/main/MIG/README.md) (NVIDIA driver + CUDA library required).
