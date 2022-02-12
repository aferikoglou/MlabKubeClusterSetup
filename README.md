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

## Step 1: Install docker runtime 
By default, Kubernetes uses the Container Runtime Interface (CRI) to interface with your chosen container runtime.

If you don't specify a runtime, kubeadm automatically tries to detect an installed container runtime by scanning through a list of well known Unix domain sockets. The following table lists container runtimes and their associated socket paths:

**Runtime	Path to Unix domain socket**

Docker	/var/run/dockershim.sock

containerd	/run/containerd/containerd.sock

CRI-O	/var/run/crio/crio.sock

If both Docker and containerd are detected, Docker takes precedence. This is needed because Docker 18.09 ships with containerd and both are detectable even if you only installed Docker. If any other two or more runtimes are detected, kubeadm exits with an error.

See [container runtimes](https://kubernetes.io/docs/setup/production-environment/container-runtimes/) for more information.

Let's now continue with the installation:
```bash 
# remove older versions
sudo apt-get remove docker docker-engine docker.io containerd runc
# set up the repository
sudo apt-get update
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
# add docker's official gpg key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
# set up the stable repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
# install docker engine
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io

```

## Step 2: Install kubectl, kubeadm and kubelet
```bash 
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl
sudo curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl
```


**Step 3: Configure the cgroup driver**

Add the following line in /etc/systemd/system/kubelet.service.d/10-kubeadm.conf among the rest environment variables:
```bash
Environment="KUBELET_EXTRA_ARGS=--cgroup-driver=cgroupfs"
```
cgroupfs is the appropriate cgroup-driver for docker which we will be using as our container runtime for the sake of simplicity. If you want to use a more sophisticated container runtime for further sandboxing you might have to change this configuration.


**Step 4: Initialize the kube cluster:**


```bash
# first disable paging and swapping since if memory swapping is allowed this can lead to stability issues when the scheduler tries to deploy a pod:
sudo swapoff -a
# delete previous plane if it exists:
sudo kubeadm reset
# remove previous configurations:
sudo rm -r ~/.kube
# initialize new control plane:
sudo kubeadm init --pod-network-cidr=192.168.0.0/16
# A couple of notes:
# 1.  --pod-network-cidr=192.168.0.0/16 is the appropriate network for calico cni which we will be using, --pod-network-cidr=10.244.0.0/16 is for flannel
# 2. We could have also used --apiserver-advertise-address=<my_addr> to specify which ip we want the control plane to advertise to others, but since we didn't, kubelet will find the default network inteface and use its ip.
# 3. We could have also specified --cri-socket and use another cri socket (e.g. containerd.sock) in order to make kubernetes play with other container runtimes (such as gVisor) too but for now we will just keep things simple.  

# Move the appropriate configuration files in a place where kubernetes can find them, and give them the appropriate privileges:
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
# Alternatively if you are the root user: $ echo "export KUBECONFIG=/etc/kubernetes/admin.conf" | tee -a ~/.bashrc && source ~/.bashrc
# save the "kubeadm join" command printed in the last line of "kubeadm init" output in a file because you will need it to add workers in the cluster. 
```
**Step5: Apply the CNI**
## Calico:
```bash
kubectl create -f https://projectcalico.docs.tigera.io/manifests/tigera-operator.yaml
kubectl create -f https://projectcalico.docs.tigera.io/manifests/custom-resources.yaml
# Alternatively for flannel:
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
```
**Step 6: Create monitoring namespace and add prometheus operator/adapter, grafana, alert manager and exporters in the cluster:**
```bash 
git clone https://github.com/prometheus-operator/kube-prometheus.git
cd kube-prometheus
kubectl apply --server-side -f manifests/setup
until kubectl get servicemonitors --all-namespaces ; do date; sleep 1; echo ""; done
kubectl apply -f manifests

# Port forward grafana:
kubectl --namespace monitoring port-forward svc/grafana 3000
# Port forward prometheus:
kubectl --namespace monitoring port-forward svc/prometheus-k8s 9090
# Port forward alert manager:
kubectl --namespace monitoring port-forward svc/alertmanager-main 9093
# Check this out for more: 
# https://computingforgeeks.com/setup-prometheus-and-grafana-on-kubernetes/
```

## Adding new nodes in your cluster:
In order to join more nodes in the cluster just run the join command you saved before as a root user in the new node

## A couple useful aliases I like to use:
```bash
alias kgp="kubectl get pods --all-namespaces"
alias kgn="kubectl get nodes"
alias kgd="kubectl get deploy"
alias graf="kubectl --namespace monitoring port-forward svc/grafana 3000"
alias prom="kubectl --namespace monitoring port-forward svc/prometheus-k8s 9090"
```

**You can also permanently add all of them in your shell script configuration with the following command:**
```bash
cat <<EOF | tee -a ~/.bashrc && source ~/.bashrc

alias kgp="kubectl get pods --all-namespaces"
alias kgn="kubectl get nodes"
alias kgd="kubectl get deploy"
alias graf="kubectl --namespace monitoring port-forward svc/grafana 3000"
alias prom="kubectl --namespace monitoring port-forward svc/prometheus-k8s 9090"
EOF

# In case you are using zsh as the default shell for your user you could use the same command as above by replacing "bashrc" either with "zshrc" or "profile"
```