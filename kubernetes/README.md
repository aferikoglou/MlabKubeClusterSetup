# Kubernetes Setup Instructions


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
sudo apt-get remove -y docker docker-engine docker.io containerd runc
# set up the repository
sudo apt-get -y update
sudo apt-get -y install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# add docker's official gpg key
sudo mkdir -p /etc/apt/keyrings

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# set up the stable repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
# install docker engine
sudo apt-get -y update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

## Step 2: Install kubectl, kubeadm and kubelet
```bash 
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl
sudo apt-get purge kubeadm kubectl kubelet kubernetes-cni 
sudo apt autoremove
sudo rm -fr /etc/kubernetes/; sudo rm -fr ~/.kube/; sudo rm -fr /var/lib/etcd; sudo rm -rf /var/lib/cni/
sudo curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl
```


## Step 3: Configure the cgroup driver

Add the following line in /etc/systemd/system/kubelet.service.d/10-kubeadm.conf among the rest environment variables:
```
Environment="KUBELET_EXTRA_ARGS=--cgroup-driver=cgroupfs"
```
you can also use the following commands which will do it for you but I highly recommend that you do it on your own since there will probably be issues if the format of the file is changed:
``` bash
START=$(sudo head -n 2 /etc/systemd/system/kubelet.service.d/10-kubeadm.conf) 
END=$(sudo tail -n $(expr $(sudo wc -l /etc/systemd/system/kubelet.service.d/10-kubeadm.conf | cut -c 1-2) - 2) /etc/systemd/system/kubelet.service.d/10-kubeadm.conf) 
sudo truncate -s 0 /etc/systemd/system/kubelet.service.d/10-kubeadm.conf && sudo cat <<EOF | sudo tee -a /etc/systemd/system/kubelet.service.d/10-kubeadm.conf
$START
Environment="KUBELET_EXTRA_ARGS=--cgroup-driver=cgroupfs"
$END
EOF

# verify that extra args environment variable has been added in the third line of your conf file:
sudo cat /etc/systemd/system/kubelet.service.d/10-kubeadm.conf

# And restart docker service:
sudo systemctl daemon-reload
sudo systemctl restart docker
```
cgroupfs is the appropriate cgroup-driver for docker which we will be using as our container runtime for the sake of simplicity. If you want to use a more sophisticated container runtime for further sandboxing you might have to change this configuration (e.g. for containerd you should use systemd).

>Note: For kubernetes version 1.24.0+ the default container runtime is containerd instead of docker. In this case you have to edit the containerd configuration (/etc/containerd/config.toml) and remove "cri" from the disabled_plugins:
```bash
# Enable the overlay and br_netflilter modules
sudo modprobe overlay
sudo modprobe br_netfilter
# Generate config.toml
sudo mkdir -p /etc/containerd
sudo rm /etc/containerd/config.toml
sudo containerd config default | tee -a /etc/containerd/config.toml
# You can either use the following command
sudo sed -i 's/disabled\_plugins\ \=\ \[\"cri\"\]/disabled\_plugins\ \=\ \[\]/g' /etc/containerd/config.toml
# or do it by yourself
sudo vim /etc/containerd/config.toml
``` 

Install CNI plugins for containerd

Download the cni-plugins-<OS>-<ARCH>-<VERSION>.tgz archive from https://github.com/containernetworking/plugins/releases , verify its sha256sum, and extract it under /opt/cni/bin:

```bash
$ mkdir -p /opt/cni/bin
$ tar Cxzvf /opt/cni/bin cni-plugins-linux-amd64-v1.1.1.tgz
```
```
./
./macvlan
./static
./vlan
./portmap
./host-local
./vrf
./bridge
./tuning
./firewall
./host-device
./sbr
./loopback
./dhcp
./ptp
./ipvlan
./bandwidth
```

Finally, if you are using containerd as your container runtime you should change the following configuration in order for containerd to use systemd cgroup driver:
```
[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
  ...
  [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
    SystemdCgroup = true
```

and finally: 
```bash
sudo systemctl restart containerd
```

## Step 4: Initialize the kube cluster:

```bash
# first disable paging and swapping since if memory swapping is allowed this can lead to stability issues when the scheduler tries to deploy a pod:
sudo swapoff -a
sudo sed -i '/ swap / s/^/#/' /etc/fstab
# delete previous plane if it exists:
sudo kubeadm reset -f
# remove previous configurations:
sudo rm -r ~/.kube

# NOTE: In the following command consider using --cri-socket argument to define a specific container runtime
# e.g. docker since it is no longer the default runtime since dockershim got deprecated after kubernetes v1.20.
# If you want to use docker the --cri-socket is unix:///var/run/cri-dockerd.sock but first you have to install
# the docker engine and cri-dockerd.sock as shown here: https://github.com/Mirantis/cri-dockerd.

# initialize new control plane:
sudo kubeadm init --pod-network-cidr=10.244.0.0/16 # --cri-socket unix:///var/run/cri-dockerd.sock
# A couple of notes:
# 1. --pod-network-cidr=10.244.0.0/16 is the appropriate network for flannel cni which we will be using, --pod-network-cidr=192.168.0.0/16 is for calico
# 2. We could have also used --apiserver-advertise-address=<my_addr> to specify which ip we want the control plane to advertise to others, but since we didn't, kubelet will find the default network inteface and use its ip.
# 3. We could have also specified --cri-socket and use another cri socket (e.g. containerd.sock) in order to make kubernetes play with other container runtimes (such as gVisor) too but for now we will just keep things simple.  

# Move the appropriate configuration files in a place where kubernetes can find them, and give them the appropriate privileges: 
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
# Alternatively if you are the root user: $ echo "export KUBECONFIG=/etc/kubernetes/admin.conf" | tee -a ~/.bashrc && source ~/.bashrc
# save the "kubeadm join" command printed in the last line of "kubeadm init" output in a file because you will need it to add workers in the cluster. 
```
> FYI: If you lose the kubeadm join command printed in the output of kubeadm init command you can create a new token and get the related command by running the following :
```
kubeadm token create --print-join-command
```

## Step 5: Untaint master node:
You can find all node's taints from this command:
```bash
kubectl get node -o json | jq '.items[].spec.taints' # in the key field
```
And then run the following command for all the node's taints:
```bash
kubectl taint nodes $(kubectl get nodes -l node-role.kubernetes.io/control-plane= -o name) <taint-key>:<taint-effect>-
# Don't forget the '-' in the end
```
Example:
```bash
# Usually this is the case:
kubectl taint nodes $(kubectl get nodes -l node-role.kubernetes.io/control-plane= -o name) node-role.kubernetes.io/control-plane:NoSchedule- node-role.kubernetes.io/master:NoSchedule-  node.kubernetes.io/not-ready:NoSchedule-
```

## Step 6: Apply the CNI 
**Flannel:**
```bash
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
# Alternatively for calico:
# kubectl create -f https://projectcalico.docs.tigera.io/manifests/tigera-operator.yaml
# kubectl create -f https://projectcalico.docs.tigera.io/manifests/custom-resources.yaml
```

## Adding new nodes in your cluster:
In order to join more nodes in the cluster you have to repeat the first 3 steps on the new node and then run the join command you saved before as a root user in the new node.
>Note: before adding new nodes in the cluster you have to first make sure that you have reset the previous kubeadm configurations and delete all cni config files like demonstrated in the "Uninstalling" section later. 

## A couple useful aliases I like to use for kubectl:
```bash
alias kgp="kubectl get pods --all-namespaces"
alias kgn="kubectl get nodes --all-namespaces -o wide"
alias kgd="kubectl get deploy"
```

**You can also permanently add all of them in your shell script configuration with the following command:**
```bash
cat <<EOF | tee -a ~/.bashrc && source ~/.bashrc

alias kgp="kubectl get pods --all-namespaces"
alias kgn="kubectl get nodes --all-namespaces -o wide"
alias kgd="kubectl get deploy --all-namespaces"
EOF

# In case you are using zsh as the default shell for your user you could use the same command as above by replacing "bashrc" either with "zshrc" or "profile"
```

## Uninstalling
**In order to gracefully remove a single node from the cluster**, 

run the following commands on the master node:
```bash
kubectl cordon <node-name>  
kubectl drain <node-name> --ignore-daemonsets
kubectl delete node <node-name>
```

and the following on the deleted node in order to reset all the configurations:
```bash
sudo kubeadm reset -f
sudo rm -fr /etc/kubernetes/; sudo rm -fr ~/.kube/; sudo rm -fr /var/lib/etcd; sudo rm -rf /var/lib/cni/; sudo rm -rf /etc/cni/net.d
sudo systemctl daemon-reload
sudo iptables -F && sudo iptables -t nat -F && sudo iptables -t mangle -F && sudo iptables -X
sudo docker rm -f `sudo docker ps -a | grep "k8s_" | awk '{print $1}'` 2>&1 > /dev/null
sudo ip link delete cni0
```
If you were using flannel then delete the following interface:
```bash
sudo ip link delete flannel.1
```
else if you were using calico then delete the following:
```bash
sudo ip link delete vxlan.calico
``` 
Run the following command and make sure that are no unused interfaces left from the previous cni:
```bash
ip addr
```

**In order to completely delete the cluster** and the kubernetes tools run the following commands on each node:
```
sudo kubeadm reset -f

sudo apt purge kubectl kubeadm kubelet kubernetes-cni -y --allow-change-held-packages
sudo apt autoremove -y
sudo rm -fr /etc/kubernetes/; sudo rm -fr ~/.kube/; sudo rm -fr /var/lib/etcd; sudo rm -rf /var/lib/cni/; sudo rm -rf /etc/cni/net.d

sudo systemctl daemon-reload

sudo iptables -F && sudo iptables -t nat -F && sudo iptables -t mangle -F && sudo iptables -X

# remove all running docker containers
sudo docker rm -f `sudo docker ps -a | grep "k8s_" | awk '{print $1}'` 2>&1 > /dev/null
sudo ip link delete cni0
```
If you were using flannel then delete the following interface:
```bash
sudo ip link delete flannel.1
```
else if you were using calico then delete the following:
```bash
sudo ip link delete vxlan.calico
``` 

Run the following command and make sure that are no unused interfaces left from the previous cni:
```bash
ip addr
```

**To completely uninstall docker** run the following commands:  
```bash
sudo apt-get purge -y docker-engine docker docker.io docker-ce docker-ce-cli
sudo apt-get autoremove -y --purge docker-engine docker docker.io docker-ce  
sudo rm -rf /var/lib/docker /etc/docker
sudo rm /etc/apparmor.d/docker
sudo groupdel docker
sudo rm -rf /var/run/docker.sock
```
---
>Note: the above commands should be ran on each node that has joined the cluster.
>Note: If you are getting the following error when joining nodes in your cluster or when initializing the cluster:
```
Unimplemented desc = unknown service runtime.v1alpha2.RuntimeService
```
>Then you should probably try the following fix:
```
sudo rm /etc/containerd/config.toml
sudo systemctl restart containerd
```
