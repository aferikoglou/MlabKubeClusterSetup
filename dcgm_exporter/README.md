## Install DCGM Exporter (nvidia cuda driver and nvidia device plugin are required, if you don't know how to install them watch [this](https://github.com/aferikoglou/mlab-k8s-cluster-setup/tree/main/prometheus/README.md))

See this for more:
https://developer.nvidia.com/blog/monitoring-gpus-in-kubernetes-with-dcgm/

### First create a values.yaml file containing:
```
# extra args that will be used during dcgm exporter installation
extraConfigMapVolumes:
- name: exporter-metrics-volume
  configMap:
    name: exporter-metrics-config-map

# need to set it low so that readiness/liveness probes succeede
extraEnv:
- name: DCGM_EXPORTER_CONFIGMAP_DATA
  value: "default:exporter-metrics-volume"
- name: "DCGM_EXPORTER_INTERVAL"
  value: "1000"
```

### We will use the Helm chart for setting up dcgm-exporter and values.yaml for setting its extra arguments. First, add the Helm repo:
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

### All the chart installation in one command:
```bash
cat <<EOF > values.yaml && helm install --generate-name gpu-helm-charts/dcgm-exporter -f values.yaml
# extra args that will be used during dcgm exporter installation
extraConfigMapVolumes:
- name: exporter-metrics-volume
  configMap:
    name: exporter-metrics-config-map

# need to set it low so that readiness/liveness probes succeede
extraEnv:
- name: DCGM_EXPORTER_CONFIGMAP_DATA
  value: "default:exporter-metrics-volume"
- name: "DCGM_EXPORTER_INTERVAL"
  value: "1000"
EOF
```

### There is one last configuration step to go: configure dcgm-exporter's service monitor in order for prometheus to scrape its metrics every 1 second.
To do this we have to edit the service monitor's yaml file which can be done in 2 ways:

**First way:**
```bash
kubectl edit $(kubectl get servicemonitor -l "app.kubernetes.io/name=dcgm-exporter" -o name)
```
The above command will open a yaml file using the vi editor. Within this file you have to locate the field {.items[0].spec.endpoints[0].interval} and change it to 1s instead of 15s which is the default. In other words you have to find the first field under the spec.endpoints section and change the interval definied in this field. Then you just same and once out of the editor, press enter.

**Second way:**
```bash
kubectl get servicemonitor -l "app.kubernetes.io/name=dcgm-exporter" -o yaml > dcgm_monitor.yml
```
This command will export the yaml file related to dcgm service monitor. What you have to do next is open the dcgm_monitor.yaml with an editor, change the same field as before and then just apply this new configuration like that:
```bash
kubectl apply -f dcgm_monitor.yml
```

Finally in order to let prometheus know about these new change you have to signal him in one of the two ways that follow:
```bash
# send SIGHUP to the prom process
kill -HUP $(cat /var/run/prometheus.pid)
# or post to the /-/reload/ endpoint
curl -X POST http://localhost:30090/-/reload
```

By running:
``` bash
kubectl get svc -A
```
You can assure that the service has started. You can try port forwarding the service and using curl to extract metrics or you can always find the metrics on the dashboard of prometheus.

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
or simply all in one command:
```bash
cat <<EOF > test_gpu.yaml  && kubectl apply -f test_gpu.yaml
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
---
## DCGM Dashboard in Grafana

### To access the dashboard, navigate from the Grafana home page to Dashboards -> Browse -> Import:
### Import the NVIDIA dashboard from https://grafana.com/grafana/dashboards/12239 (copy paste this link in the form), choose Prometheus as the data source in the drop down list and hit Import.

### See more here:
https://docs.nvidia.com/datacenter/cloud-native/gpu-telemetry/dcgm-exporter.html#setting-up-dcgm