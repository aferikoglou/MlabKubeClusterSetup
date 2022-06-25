## Let's first install nvidia graphics card drivers(same way on each gpu node), nvidia cuda driver(same way on each gpu node) and nvidia device plugin(using kubectl i.e. on master node) since we will be requiring prometheus to record gpu-metrics too
---
## Step 1: Install the nvidia graphics card driver
Visit this site: https://www.nvidia.com/en-us/drivers/unix/ in order to realise which is the newest nvidia driver, let's call it XXXX.
``` bash
# clear existing driver
sudo apt-get -y purge nvidia*
# let us go ahead and add the graphics-driver PPA -
sudo add-apt-repository ppa:graphics-drivers
# update apt
sudo apt-get update
# go ahead and install driver which in my case is 510
sudo apt-get -y install nvidia-driver-510
```
>Note: In the case of a [mig gpu](https://www.nvidia.com/en-us/technologies/multi-instance-gpu/) you have to install datacenter drivers [NVIDIA R450+ datacenter driver: 450.80.02+](https://www.nvidia.com/download/driverResults.aspx/165294/). Specifically for NVIDIA A30  GPU you will be needing the [460.73.01](https://www.nvidia.com/Download/driverResults.aspx/173142/) driver version. Learn more here: https://docs.nvidia.com/datacenter/cloud-native/kubernetes/mig-k8s.html.
>Note: In order to install nvidia driver on your pc or VM you first need to make sure it is supported by your gpu.

Reboot and make sure everything was installed fine:
``` bash
lsmod | grep nvidia
nvidia-smi
```
and before going on install cuda toolkit:
```bash
sudo apt -y install nvidia-cuda-toolkit
```
## Step 2: Install the nvidia cuda driver
See this for more:
https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html

The NVIDIA driver requires that the kernel headers and development packages for the running version of the kernel be installed at the time of the driver installation, as well whenever the driver is rebuilt. For example, if your system is running kernel version 4.4.0, the 4.4.0 kernel headers and development packages must also be installed.
The kernel headers and development packages for the currently running kernel can be installed with:
``` bash
sudo apt-get -y install linux-headers-$(uname -r)
```
Ensure packages on the CUDA network repository have priority over the Canonical repository.
``` bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID | sed -e 's/\.//g')
sudo wget https://developer.download.nvidia.com/compute/cuda/repos/$distribution/x86_64/cuda-$distribution.pin
sudo mv cuda-$distribution.pin /etc/apt/preferences.d/cuda-repository-pin-600
```
Install the CUDA repository public GPG key. Note that on Ubuntu 16.04, replace https with http in the command below.
``` bash
sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/$distribution/x86_64/7fa2af80.pub
#Setup the CUDA network repository.
echo "deb http://developer.download.nvidia.com/compute/cuda/repos/$distribution/x86_64 /" | sudo tee /etc/apt/sources.list.d/cuda.list
```

Update the APT repository cache and install the driver using the cuda-drivers meta-package. Use the --no-install-recommends option for a lean driver install without any dependencies on X packages. This is particularly useful for headless installations on cloud instances.
``` bash
sudo apt-get update
sudo apt-get -y install cuda-drivers-510
```

The PATH variable needs to include

 \$ export PATH=/usr/local/cuda-11.6/bin${PATH:+:${PATH}}. Nsight Compute has moved to */opt/nvidia/nsight-compute/* only in rpm/deb installation method. When using .run installer it is still located under /usr/local/cuda-11.6/.

To add this path to the PATH variable:
``` bash
export PATH=/usr/local/cuda-11.6/bin${PATH:+:${PATH}}
```
In addition, when using the runfile installation method, the LD_LIBRARY_PATH variable needs to contain /usr/local/cuda-11.6/lib64 on a 64-bit system, or /usr/local/cuda-11.6/lib on a 32-bit system
``` bash
export LD_LIBRARY_PATH=/usr/local/cuda-11.6/lib64\
${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
```

The NVIDIA Persistence Daemon should be automatically started for POWER9 installations. Check that it is running with the following command:
``` bash
systemctl status nvidia-persistenced
# If it is not active, run the following command:
sudo systemctl enable nvidia-persistenced
```
Disable a udev rule installed by default in some Linux distributions that cause hot-pluggable memory to be automatically onlined when it is physically probed. This behavior prevents NVIDIA software from bringing NVIDIA device memory online with non-default settings. This udev rule must be disabled in order for the NVIDIA CUDA driver to function properly on POWER9 systems.
On Ubuntu 18.04, this rule can be found in:
*/lib/udev/rules.d/40-vm-hotadd.rules*
The rule generally takes a form where it detects the addition of a memory block and changes the 'state' attribute to online. For example, in RHEL8, the rule looks like this:
SUBSYSTEM=="memory", ACTION=="add", PROGRAM="/bin/uname -p", RESULT!="s390*", ATTR{state}=="offline", ATTR{state}="online"
This rule must be disabled by copying the file to /etc/udev/rules.d and commenting out, removing, or changing the hot-pluggable memory rule in the /etc copy so that it does not apply to POWER9 NVIDIA systems. For example, on RHEL 7.5 and earlier:
``` bash
sudo cp /lib/udev/rules.d/40-vm-hotadd.rules /etc/udev/rules.d

sudo sed -i '/SUBSYSTEM=="memory", ACTION=="add"/d' /etc/udev/rules.d/40-vm-hotadd.rules
```
See this for more recommended actions:
https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#recommended-post


## Step 3: Installing nvidia container toolkit(docker has to be installed):
See this for more:
https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker

``` bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
&& curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - \
&& curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
```

To get access to experimental features such as CUDA on WSL or the new MIG capability on A100, you may want to add the experimental branch to the repository listing:
``` bash
curl -s -L https://nvidia.github.io/nvidia-container-runtime/experimental/$distribution/nvidia-container-runtime.list | sudo tee /etc/apt/sources.list.d/nvidia-container-runtime.list

sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
# At this point, a working setup can be tested by running a base CUDA container:
sudo docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

You will need to enable the nvidia runtime as your default runtime on your node. We will be editing the docker daemon config file which is usually present at */etc/docker/daemon.json*:

``` bash
sudo chmod 777 /etc/docker/daemon.json && cat <<EOF > /etc/docker/daemon.json
{
    "default-runtime": "nvidia",
    "runtimes": {
        "nvidia": {
            "path": "/usr/bin/nvidia-container-runtime",
            "runtimeArgs": []
        }
    }
}
EOF
```
Now, if you want you can put permissions back to 644
``` bash
sudo chmod 644 /etc/docker/daemon.json
```
and now you have to restart docker:
``` bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

Once you have configured the options above on all the GPU nodes in your cluster, you can enable GPU support by deploying the following Daemonset (**Non-mig gpu only**):
``` bash
kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.10.0/nvidia-device-plugin.yml
```

Install helm:
``` bash
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh
```

Installing from the nvidia-device-plugin helm repository
``` bash
helm repo add nvdp https://nvidia.github.io/k8s-device-plugin
helm repo update
```

Once this repo is updated, install nvidia device plugin with no extra arguments for the sake of simplicity:
``` bash
helm install \
    --version=0.10.0 \
    --generate-name \
    nvdp/nvidia-device-plugin
```

Here are a couple more examples extra arguments you can use (feel free to skip):
``` bash
# Enabling compatibility with the CPUManager and running with a request for 100ms of CPU time and a limit of 512MB of memory
helm install \
    --version=0.10.0 \
    --generate-name \
    --set compatWithCPUManager=true \
    --set resources.requests.cpu=100m \
    --set resources.limits.memory=512Mi \
    nvdp/nvidia-device-plugin
```

``` bash
# Use the legacy Daemonset API (only available on Kubernetes < v1.16)
helm install \
    --version=0.10.0 \
    --generate-name \
    --set legacyDaemonsetAPI=true \
    nvdp/nvidia-device-plugin
```

``` bash
# Enabling compatibility with the CPUManager and the mixed migStrategy
helm install \
    --version=0.10.0 \
    --generate-name \
    --set compatWithCPUManager=true \
    --set migStrategy=mixed \
    nvdp/nvidia-device-plugin
```

### NOTE:
In the case of a mig gpu you have to install the nvidia device plugin like so:
```bash
helm repo add nvdp https://nvidia.github.io/k8s-device-plugin
helm repo add nvgfd https://nvidia.github.io/gpu-feature-discovery
helm repo update
# Verify thath package versions are v0.7.0 and v0.2.0 or later respectively 
helm search repo nvdp --devel
helm search repo nvgfd --devel
# In this tutorial we will be using the "single" MIG_STRATEGY but there are also the following options: <none | single | mixed>


helm install \
   --version=0.7.0 \
   --generate-name \
   --set migStrategy=single \
   nvdp/nvidia-device-plugin
helm install \
   --version=0.2.0 \
   --generate-name \
   --set migStrategy=single \
   nvgfd/gpu-feature-discovery
```
Verify that all pods are running:
```bash
kubectl get pods -A
```
and that labels have been added to gpu nodes:
```bash
kubectl get node -o json | jq '.items[].metadata.labels'
```

### Building and Running locally with Docker
``` bash
docker pull nvcr.io/nvidia/k8s-device-plugin:v0.10.0
docker tag nvcr.io/nvidia/k8s-device-plugin:v0.10.0 nvcr.io/nvidia/k8s-device-plugin:devel
```


# Step 4: Installing Prometheus:

###  First add helm repo:
``` bash
helm repo add prometheus-community \
   https://prometheus-community.github.io/helm-charts
```

### Now search for the available prometheus charts:
``` bash
helm search repo kube-prometheus
```

### Once you’ve located which version of the chart to use, you have to modify the settings:

### You can directly replace values on the helm command:
``` bash
# Create file to hold the additionalScrapeConfigs
cat <<EOF > additionalScrapeConfigs
- job_name: gpu-metrics
  scrape_interval: 1s
  metrics_path: /metrics
  scheme: http
  kubernetes_sd_configs:
  - role: endpoints
    namespaces:
      names:
      - gpu-operator
  relabel_configs:
  - source_labels: [__meta_kubernetes_pod_node_name]
    action: replace
    target_label: kubernetes_node
EOF

# Now install prometheus with the required configurations
helm install prometheus-community/kube-prometheus-stack \
   --create-namespace --namespace prometheus \
   --generate-name \
   --set prometheus.service.type=NodePort \
   --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
   --set prometheus.PrometheusSpec.additionalScrapeConfigs="$(cat additionalScrapeConfigs)"
```

### Or you can modify the values manually:
``` bash
helm inspect values prometheus-community/kube-prometheus-stack > /tmp/kube-prometheus-stack.values

vim /tmp/kube-prometheus-stack.values
```

## And change the lines:
From:
```
# Port to expose on each node
# Only used if service.type is 'NodePort'
#
 nodePort: 30090
# Loadbalancer IP
# Only use if service.type is "loadbalancer"
 loadBalancerIP: ""
 loadBalancerSourceRanges: []
# Service type
#
 type: ClusterIP
```

To:
```
# Port to expose on each node
# Only used if service.type is 'NodePort'
#
 nodePort: 30090
# Loadbalancer IP
# Only use if service.type is "loadbalancer"
 loadBalancerIP: ""
 loadBalancerSourceRanges: []
# Service type
#
 type: NodePort
```

### Then search for:
```
"serviceMonitorSelectorNilUsesHelmValues"
```
and make it false
___
and finally add:
```
- job_name: gpu-metrics
  scrape_interval: 1s
  metrics_path: /metrics
  scheme: http
  kubernetes_sd_configs:
  - role: endpoints
    namespaces:
      names:
      - gpu-operator
  relabel_configs:
  - source_labels: [__meta_kubernetes_pod_node_name]
    action: replace
    target_label: kubernetes_node
```
To:  "additionalScrapeConfigs" option.

### And just install using the modified values file:
``` bash
helm install prometheus-community/kube-prometheus-stack \
   --create-namespace --namespace prometheus \
   --generate-name \
   --values /tmp/kube-prometheus-stack.values
```

### Step 5: Patching the Grafana Service

By default, Grafana uses a ClusterIP to expose the ports on which the service is accessible. This can be changed to a NodePort instead, so the page is accessible from the browser, similar to the Prometheus dashboard.

You can use kubectl patch to update the service API object to expose a NodePort instead.

### First, modify the spec to change the service type:
``` bash
cat << EOF | tee grafana-patch.yaml
spec:
  type: NodePort
  nodePort: 32322
EOF
```

### And now use kubectl patch:
#### *Note* : here you have to replace the grafana service with your own (i.e. the one you see when you execute: "$ kubectl get svc -A | grep grafana")
``` bash
kubectl patch svc kube-prometheus-stack-1603211794-grafana \
   -n prometheus \
   --patch "$(cat grafana-patch.yaml)"
```

### You could do something like that:
``` bash
GRAFANA_SERVICE=$(kubectl get svc -A -l "app.kubernetes.io/name=grafana" -o jsonpath="{.items[*].metadata.name}")

# and:
kubectl patch svc $GRAFANA_SERVICE \
   -n prometheus \
   --patch "$(cat grafana-patch.yaml)"
```

### But I strongly recommend that you copy the service on your own.

### The output should look like that:
```
service/kube-prometheus-stack-1603211794-grafana patched
```

### Make sure that the Grafana svc is running:
``` bash
kubectl get svc -A | grep grafana
# After running the above command, take a note of the service's port
```

---
Now, you can open your browser to http://<machine_ip_address>:<grafana_port> and view the Grafana login page.
Access Grafana home using the admin username.
The password credentials for the login are available in the prometheus.values file we edited in the earlier section of the doc for prometheus.
Usually it is "prom-operator".
___
Finally, you can always extract metrics using curl commands like that:
curl -X GET <machines_ip>:<prom_or_graf_port>/metrics > metrics.txt

>**Note** : Since we use NodePorts there is no need for port forwards and Prometheus and Grafana dashboards are always available to the respective ports of their services (you can find them using "$ kubectl get svc -A") and at your master's IP.
---
### See more here: https://docs.nvidia.com/datacenter/cloud-native/gpu-telemetry/dcgm-exporter.html.