# GPU-Operator

Kubernetes provides access to special hardware resources such as NVIDIA GPUs, NICs, Infiniband adapters and other devices through the device plugin framework. However, configuring and managing nodes with these hardware resources requires configuration of multiple software components such as drivers, container runtimes or other libraries which are difficult and prone to errors.

The NVIDIA GPU Operator uses the operator framework within Kubernetes to automate the management of all NVIDIA software components needed to provision GPU. These components include the NVIDIA drivers (to enable CUDA), Kubernetes device plugin for GPUs, the NVIDIA Container Runtime, automatic node labelling, DCGM based monitoring and others.

In this tutorial, it is assumed that NVIDIA drivers and NVIDIA container toolkit is already present on all GPU nodes as described [here](https://github.com/aferikoglou/mlab-k8s-cluster-setup/blob/main/prometheus/README.md) in the **first 3 steps**.


## Installing gpu-operator via helm chart:
```bash
helm install --wait --generate-name -n gpu-operator --create-namespace \
     nvidia/gpu-operator \
     --set driver.enabled=false \
     --set toolkit.enabled=false \
     --set mig.strategy=none
```
As seen in the above command -n sets the namespace in which the deployment will be created, driver.enabled=false means that the driver is preinstalled on all nodes and thus the nvidia driver daemonset does not need to be deployed, toolkit.enabled=false means the nvidia container toolkit is preinstalled and thus the corresponding doesn't need to be installed and finally mig.strategy=none means that the operator won't manage MIG partitions. Feel free to configure the helm chart to fulfill your needs.

**mig.strategy** also provides "single" and "mixed" strategies.

If driver.enabled=false is not set then an nvidia driver daemonset will be deployed on all gpu nodes which will install the nvidia drivers. Same for toolkit. It is also possible to explicitly define the version for each component to be installed. There are more information in the links in the end of the tutorial.

Once the gpu-operator is deployed, gpu nodes are labeled with the labels related to their memory, architecture, model, driver memory etc. Among the rest of the labels there are also labels defining which of all the daemonsets will be deployed on this specific node. 

Example:
```bash
kubectl describe node k8s-aferik-gpu-a30 | grep -A 60 Label
```
Output:
```bash
Labels:             beta.kubernetes.io/arch=amd64
                    beta.kubernetes.io/os=linux
                    feature.node.kubernetes.io/cpu-cpuid.ADX=true
                    feature.node.kubernetes.io/cpu-cpuid.AESNI=true
...
                    nvidia.com/cuda.driver.major=460
                    nvidia.com/cuda.driver.minor=73
                    nvidia.com/cuda.driver.rev=01
                    nvidia.com/cuda.runtime.major=11
                    nvidia.com/cuda.runtime.minor=6
                    nvidia.com/gfd.timestamp=1656595567
                    nvidia.com/gpu.compute.major=8
                    nvidia.com/gpu.compute.minor=0
                    nvidia.com/gpu.count=1
...
                    nvidia.com/gpu.deploy.dcgm-exporter=true
```
nvidia.com/gpu.deploy.dcgm-exporter=true, for example, means that the dcgm-exporter daemonset will be deployed on this specific node if the opposite has not be set during the installation.

If for some reason you want the dcgm-exporter to not be deployed on that specific node, then you have to relabel the node with nvidia.com/gpu.deploy.dcgm-exporter=false as below:
```bash
kubectl label nodes <node-name> nvidia.com/gpu.deploy.dcgm-exporter=false --overwrite
```

Same for the rest of the labels and same for <label>=true.

For more information on gpu-operator with mig see [this](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/gpu-operator-mig.html).

For more information on gpu-operator see [this](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/getting-started.html).
