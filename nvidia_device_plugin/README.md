# Setting up the nvidia device plugin and dcgm exporter


## Step 1: Install the nvidia cuda driver
See this for more:
https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html

The NVIDIA driver requires that the kernel headers and development packages for the running version of the kernel be installed at the time of the driver installation, as well whenever the driver is rebuilt. For example, if your system is running kernel version 4.4.0, the 4.4.0 kernel headers and development packages must also be installed.
The kernel headers and development packages for the currently running kernel can be installed with:
``` bash
sudo apt-get install linux-headers-$(uname -r)
```
Ensure packages on the CUDA network repository have priority over the Canonical repository.
``` bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID | sed -e 's/\.//g')
wget https://developer.download.nvidia.com/compute/cuda/repos/$distribution/x86_64/cuda-$distribution.pin
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
sudo apt-get -y install cuda-drivers
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


## Step 2: Install nvidia container toolkit(docker has to be installed):
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

```
sudo cat <<EOF > /etc/docker/daemon.json
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

Once you have configured the options above on all the GPU nodes in your cluster, you can enable GPU support by deploying the following Daemonset:
``` bash
kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.10.0/nvidia-device-plugin.yml
```

Install helm:
``` bash
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh
``` 

Installing via helm install from the nvidia-device-plugin helm repository
``` bash
helm repo add nvdp https://nvidia.github.io/k8s-device-plugin
helm repo update
```

Once this repo is updated, you can begin installing packages from it to depoloy the nvidia-device-plugin daemonset. Below are some examples of deploying the plugin with the various flags from above (This is the command I used for the installation in order to keep it as simple as possible with no extra args):
``` bash
helm install \
    --version=0.10.0 \
    --generate-name \
    nvdp/nvidia-device-plugin
```

Enabling compatibility with the CPUManager and running with a request for 100ms of CPU time and a limit of 512MB of memory -- I didn't use that.
``` bash
helm install \
    --version=0.10.0 \
    --generate-name \
    --set compatWithCPUManager=true \
    --set resources.requests.cpu=100m \
    --set resources.limits.memory=512Mi \
    nvdp/nvidia-device-plugin
```

Use the legacy Daemonset API (only available on Kubernetes < v1.16) -- I didn't use that either.
``` bash
helm install \
    --version=0.10.0 \
    --generate-name \
    --set legacyDaemonsetAPI=true \
    nvdp/nvidia-device-plugin
```

Enabling compatibility with the CPUManager and the mixed migStrategy -- I didn't use that either.
``` bash
helm install \
    --version=0.10.0 \
    --generate-name \
    --set compatWithCPUManager=true \
    --set migStrategy=mixed \
    nvdp/nvidia-device-plugin
```

## Building and Running Locally with Docker
``` bash
docker pull nvcr.io/nvidia/k8s-device-plugin:v0.10.0
docker tag nvcr.io/nvidia/k8s-device-plugin:v0.10.0 nvcr.io/nvidia/k8s-device-plugin:devel
```

## Step 3: Install DCGM Exporter

See this for more:
https://developer.nvidia.com/blog/monitoring-gpus-in-kubernetes-with-dcgm/

## You use the Helm chart for setting up dcgm-exporter. First, add the Helm repo:
``` bash
helm repo add gpu-helm-charts \
https://nvidia.github.io/gpu-monitoring-tools/helm-charts
# Update helm:
helm repo update
# Install the chart:
helm install \
   --generate-name \
   gpu-helm-charts/dcgm-exporter -f values.yaml
```

## Where values.yaml contains:
```
# need to set it low so that readiness/liveness probes succeed
extraEnv:
  - name: "DCGM_EXPORTER_INTERVAL"
    value: "5000"
```

## All the chart installation in one command:
```bash
cat <<EOF > values.yaml && helm install   --generate-name gpu-helm-charts dcgm-exporter -f values.yaml
# need to set it low so that readiness/liveness probes succeede
extraEnv:
  - name: "DCGM_EXPORTER_INTERVAL"
    value: "5000"
EOF
```

By running:
``` bash 
kubectl get svc -A
```
You can assure that the service has started. Then you can run:
``` bash
kubectl port-forward svc/<dcgm_exporter_svc_name> 9400
# where <dcgm_exporter_svc_name> is the service you got from the last command
# and export metrics just like in prometheus:
curl -X GET localhost:9400/metrics > gpu_metrics.txt
```

If you want to monitor gpu metrics using dcgm via prometheus, check this out:

https://docs.nvidia.com/datacenter/cloud-native/gpu-telemetry/dcgm-exporter.html#setting-up-dcgm

To run a test gpu-pod and make sure that everything is working properly add in a file named *test-gpu.yaml*:
```
apiVersion: v1
kind: Pod
metadata:
  name: gpu-pod
spec:
  restartPolicy: OnFailure
  containers:
    - name: cuda-container
      image: nvidia/cuda:9.0-devel
      command: ["nvidia-smi"]
      resources:
        limits:
          nvidia.com/gpu: 1 # requesting 1 GPU 
```
and run:
```bash
kubectl apply -f test-gpu.yaml
```
or simply:
```bash
cat <<EOF > test_gpu.yaml  && kubectl apply -f test-gpu.yaml  
apiVersion: v1
kind: Pod
metadata:
  name: gpu-pod
spec:
  restartPolicy: OnFailure
  containers:
    - name: cuda-container
      image: nvidia/cuda:9.0-devel
      command: ["nvidia-smi"]
      resources:
        limits:
          nvidia.com/gpu: 1 # requesting 1 GPU 
EOF
```
and then check the output of the nvidia-smi command using:
```bash
kubectl logs gpu-pod
```
